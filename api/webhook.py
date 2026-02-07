"""
Vercel Serverless Function để xử lý webhook từ Zalo Bot
"""
import json
import hmac
import hashlib
import os
import sys
from typing import Dict, Any

# Thêm path để import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.nlp_processor import NLPProcessor
from services.google_sheets import GoogleSheetsService
from services.zalo_bot import ZaloBotService
# from utils.statistics_image import create_statistics_image  # Comment out để giảm size
from config import ZALO_SECRET_KEY

# Khởi tạo services (có thể cache trong production)
_sheets_service = None
_zalo_service = None

def get_sheets_service():
    """Lazy load Google Sheets service"""
    global _sheets_service
    if _sheets_service is None:
        _sheets_service = GoogleSheetsService()
    return _sheets_service

def get_zalo_service():
    """Lazy load Zalo service"""
    global _zalo_service
    if _zalo_service is None:
        _zalo_service = ZaloBotService()
    return _zalo_service

def verify_zalo_signature(data: bytes, signature: str) -> bool:
    """
    Xác thực signature từ Zalo
    Nếu không có ZALO_SECRET_KEY thì bỏ qua verification (cho phép test local)
    """
    # Bỏ qua verify nếu không có secret key (cho phép test local)
    if not ZALO_SECRET_KEY or ZALO_SECRET_KEY.strip() == '':
        print("⚠️  Warning: ZALO_SECRET_KEY không có, bỏ qua verification")
        return True
    
    try:
        expected_signature = hmac.new(
            ZALO_SECRET_KEY.encode(),
            data,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        print(f"Error verifying signature: {e}")
        # Nếu có lỗi, cho phép pass (cho phép test)
        return True

def handle_statistics_command(user_id: str, message: str) -> str:
    """Xử lý lệnh thống kê"""
    try:
        sheets_service = get_sheets_service()
        
        # Parse tháng/năm nếu có (ví dụ: "thống kê 1/2024" hoặc "thống kê tháng 1")
        month = None
        year = None
        
        import re
        month_match = re.search(r'th[áa]ng\s*(\d+)', message, re.IGNORECASE)
        year_match = re.search(r'n[ăa]m\s*(\d{4})', message, re.IGNORECASE)
        date_match = re.search(r'(\d{1,2})/(\d{4})', message)
        
        if date_match:
            month = int(date_match.group(1))
            year = int(date_match.group(2))
        elif month_match:
            month = int(month_match.group(1))
        if year_match:
            year = int(year_match.group(1))
        
        # Lấy thống kê
        stats = sheets_service.get_statistics(user_id=user_id, month=month, year=year)
        
        # Trả về text (không tạo hình ảnh để giảm size cho Vercel)
        total_thu = stats.get('total_thu', 0)
        total_chi = stats.get('total_chi', 0)
        chenh_lech = total_thu - total_chi
        
        response = f"📊 THỐNG KÊ THU CHI"
        if month and year:
            response += f" - {month}/{year}\n\n"
        elif year:
            response += f" - Năm {year}\n\n"
        else:
            response += "\n\n"
        
        response += f"💰 Tổng Thu: {total_thu:,.0f} VNĐ\n"
        response += f"💸 Tổng Chi: {total_chi:,.0f} VNĐ\n"
        response += f"📈 Chênh lệch: {chenh_lech:,.0f} VNĐ\n"
        response += f"📝 Số giao dịch: {stats.get('so_luong', 0)}\n\n"
        
        # Thống kê theo danh mục
        danh_muc_stats = stats.get('danh_muc_stats', {})
        if danh_muc_stats:
            response += "📋 Theo danh mục:\n"
            for danh_muc, data in sorted(danh_muc_stats.items(), 
                                        key=lambda x: x[1]['Thu'] + x[1]['Chi'], 
                                        reverse=True)[:5]:
                thu = data.get('Thu', 0)
                chi = data.get('Chi', 0)
                if thu > 0 or chi > 0:
                    response += f"• {danh_muc}: Thu {thu:,.0f} | Chi {chi:,.0f}\n"
        
        return response
        
    except Exception as e:
        print(f"Error handling statistics: {e}")
        return "❌ Có lỗi xảy ra khi lấy thống kê. Vui lòng thử lại sau."

def handle_transaction(user_id: str, message: str) -> str:
    """Xử lý giao dịch thu chi"""
    try:
        sheets_service = get_sheets_service()
        zalo_service = get_zalo_service()
        
        # Lấy danh sách danh mục từ sheet
        categories = sheets_service.get_categories()
        
        # Xử lý NLP
        nlp_processor = NLPProcessor(categories=categories)
        transaction = nlp_processor.process(message)
        
        # Kiểm tra validation
        if not transaction.get('is_valid'):
            missing = []
            if not transaction.get('loai'):
                missing.append("loại giao dịch (Thu/Chi)")
            if not transaction.get('so_tien'):
                missing.append("số tiền")
            if not transaction.get('danh_muc'):
                missing.append("danh mục")
            
            return (
                f"❌ Thiếu thông tin: {', '.join(missing)}\n\n"
                f"💡 Format: 'Chi 50k ăn trưa' hoặc 'Thu 5 triệu lương'\n"
                f"📋 Danh mục có sẵn: {', '.join(categories[:10])}"
            )
        
        # Ghi vào Google Sheets
        success = sheets_service.add_transaction(transaction, user_id=user_id)
        
        if success:
            response = (
                f"✅ Đã ghi nhận:\n"
                f"• Loại: {transaction['loai']}\n"
                f"• Số tiền: {transaction['so_tien']:,.0f} VNĐ\n"
                f"• Danh mục: {transaction['danh_muc']}\n"
            )
            if transaction.get('ghi_chu'):
                response += f"• Ghi chú: {transaction['ghi_chu']}\n"
            return response
        else:
            return "❌ Có lỗi xảy ra khi ghi dữ liệu. Vui lòng thử lại sau."
            
    except Exception as e:
        print(f"Error handling transaction: {e}")
        return "❌ Có lỗi xảy ra. Vui lòng thử lại sau."

# Vercel có thể dùng FastAPI với adapter
try:
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

if FASTAPI_AVAILABLE:
    # Dùng FastAPI cho Vercel
    app = FastAPI()
    
    @app.post('/api/webhook')
    @app.post('/')
    async def webhook_handler(request: Request):
        """Webhook handler với FastAPI"""
        try:
            # Đọc raw body
            raw_data = await request.body()
            signature = request.headers.get('X-Zalo-Signature', '')
            
            # Verify signature
            if not verify_zalo_signature(raw_data, signature):
                return JSONResponse(content={'error': 'Invalid signature'}, status_code=401)
            
            # Parse JSON
            data = await request.json()
            
            # Kiểm tra event type
            event = data.get('event') or data.get('event_name')
            if event not in ['user_send_text', 'message.text.received']:
                return JSONResponse(content={'status': 'ok'})
            
            # Lấy thông tin tin nhắn
            message_obj = data.get('message', {})
            if 'text' in message_obj:
                message_text = message_obj.get('text', '').strip()
                from_obj = message_obj.get('from', {})
                user_id = str(from_obj.get('id', '') or message_obj.get('chat', {}).get('id', ''))
            else:
                message_text = message_obj.get('text', '').strip()
                user_id = str(data.get('sender', {}).get('id', ''))
            
            if not message_text or not user_id:
                return JSONResponse(content={'status': 'ok'})
            
            # Xử lý lệnh
            zalo_service = get_zalo_service()
            response_message = ""
            
            if any(keyword in message_text.lower() for keyword in ['thống kê', 'thong ke', 'tk', 'stat']):
                response_message = handle_statistics_command(user_id, message_text)
            else:
                response_message = handle_transaction(user_id, message_text)
            
            if response_message:
                zalo_service.send_text_message(user_id, response_message)
            
            return JSONResponse(content={'status': 'ok'})
            
        except Exception as e:
            print(f"Error in handler: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse(content={'error': str(e)}, status_code=500)
    
    @app.get('/health')
    async def health():
        return JSONResponse(content={'status': 'ok'})
    
    # Vercel sẽ tự động detect FastAPI app
    handler = app
    
else:
    # Fallback: Dùng BaseHTTPRequestHandler nếu không có FastAPI
    from http.server import BaseHTTPRequestHandler
    import json as json_module

    class handler(BaseHTTPRequestHandler):
        """Vercel Serverless Function Handler (fallback)"""
        
        def do_POST(self):
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                raw_body = self.rfile.read(content_length)
                raw_body_str = raw_body.decode('utf-8')
                
                signature = self.headers.get('X-Zalo-Signature', '')
                if not verify_zalo_signature(raw_body, signature):
                    self.send_response(401)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json_module.dumps({'error': 'Invalid signature'}).encode())
                    return
                
                data = json_module.loads(raw_body_str)
                event = data.get('event') or data.get('event_name')
                
                if event not in ['user_send_text', 'message.text.received']:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json_module.dumps({'status': 'ok'}).encode())
                    return
                
                message_obj = data.get('message', {})
                if 'text' in message_obj:
                    message_text = message_obj.get('text', '').strip()
                    from_obj = message_obj.get('from', {})
                    user_id = str(from_obj.get('id', '') or message_obj.get('chat', {}).get('id', ''))
                else:
                    message_text = message_obj.get('text', '').strip()
                    user_id = str(data.get('sender', {}).get('id', ''))
                
                if not message_text or not user_id:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json_module.dumps({'status': 'ok'}).encode())
                    return
                
                zalo_service = get_zalo_service()
                response_message = ""
                
                if any(keyword in message_text.lower() for keyword in ['thống kê', 'thong ke', 'tk', 'stat']):
                    response_message = handle_statistics_command(user_id, message_text)
                else:
                    response_message = handle_transaction(user_id, message_text)
                
                if response_message:
                    zalo_service.send_text_message(user_id, response_message)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json_module.dumps({'status': 'ok'}).encode())
                
            except Exception as e:
                print(f"Error in handler: {e}")
                import traceback
                traceback.print_exc()
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json_module.dumps({'error': str(e)}).encode())
        
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json_module.dumps({'status': 'ok'}).encode())
        
        def log_message(self, format, *args):
            pass

