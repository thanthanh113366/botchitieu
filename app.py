"""
Local development server (FastAPI) - Dùng để test trước khi deploy lên Vercel
Chạy: python app.py hoặc uvicorn app:app --reload

Lưu ý: Cần cài fastapi và uvicorn cho local dev:
  pip install fastapi uvicorn
"""
try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠️  FastAPI not installed. Install with: pip install fastapi uvicorn")

import json
import hmac
import hashlib
from services.nlp_processor import NLPProcessor
from services.google_sheets import GoogleSheetsService
from services.zalo_bot import ZaloBotService
# from utils.statistics_image import create_statistics_image  # Comment out để giảm dependencies
from config import ZALO_SECRET_KEY

if FASTAPI_AVAILABLE:
    app = FastAPI(title="Bot Chi Tieu", description="Zalo Bot for expense tracking")
else:
    app = None

# Khởi tạo services
sheets_service = GoogleSheetsService()
zalo_service = ZaloBotService()

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
        import re
        
        month = None
        year = None
        
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
        
        stats = sheets_service.get_statistics(user_id=user_id, month=month, year=year)
        
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
        categories = sheets_service.get_categories()
        nlp_processor = NLPProcessor(categories=categories)
        transaction = nlp_processor.process(message)
        
        if not transaction.get('is_valid'):
            missing = []
            if not transaction.get('loai'):
                missing.append("loại giao dịch (Thu/Chi)")
            if not transaction.get('so_tien'):
                missing.append("số tiền")
            if not transaction.get('danh_muc'):
                missing.append("danh mục")
            
            return (
                f"❌ Không match được danh mục!\n\n"
                f"💡 Format: 'Chi 50k ăn trưa' hoặc 'Thu 5 triệu lương'\n"
                f"📋 Danh mục có sẵn: {', '.join(categories[:10])}"
            )
        
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
        import traceback
        traceback.print_exc()
        return "❌ Có lỗi xảy ra. Vui lòng thử lại sau."

if FASTAPI_AVAILABLE:
    @app.post('/webhook')
    async def webhook(request: Request):
        """Webhook endpoint cho Zalo Bot"""
        try:
            # Đọc raw body để verify signature
            raw_data = await request.body()
            signature = request.headers.get('X-Zalo-Signature', '')
            
            if not verify_zalo_signature(raw_data, signature):
                raise HTTPException(status_code=401, detail='Invalid signature')
            
            data = await request.json()
            print(f"📥 Received webhook data: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # Hỗ trợ cả Zalo Bot Platform mới và API cũ
            event = data.get('event') or data.get('event_name')
            
            # Zalo Bot Platform: "message.text.received"
            # API cũ: "user_send_text"
            if event not in ['user_send_text', 'message.text.received']:
                print(f"⚠️  Ignoring event: {event}")
                return JSONResponse(content={'status': 'ok'})
            
            # Lấy message text và user_id (hỗ trợ cả 2 format)
            message_obj = data.get('message', {})
            
            # Zalo Bot Platform format
            if 'text' in message_obj:
                message_text = message_obj.get('text', '').strip()
                # Lấy user_id từ from.id hoặc chat.id
                from_obj = message_obj.get('from', {})
                user_id = str(from_obj.get('id', '') or message_obj.get('chat', {}).get('id', ''))
            else:
                # API cũ format
                message_text = message_obj.get('text', '').strip()
                user_id = str(data.get('sender', {}).get('id', ''))
            
            print(f"💬 Message from user {user_id}: {message_text}")
            
            if not message_text or not user_id:
                print("⚠️  Missing message_text or user_id")
                return JSONResponse(content={'status': 'ok'})
            
            response_message = ""
            
            # Kiểm tra lệnh thống kê
            if any(keyword in message_text.lower() for keyword in ['thống kê', 'thong ke', 'tk', 'stat']):
                print("📊 Processing statistics command")
                response_message = handle_statistics_command(user_id, message_text)
            else:
                print("💰 Processing transaction")
                response_message = handle_transaction(user_id, message_text)
            
            if response_message:
                print(f"📤 Sending response: {response_message[:100]}...")
                success = zalo_service.send_text_message(user_id, response_message)
                if success:
                    print("✅ Message sent successfully")
                else:
                    print("❌ Failed to send message")
            else:
                print("⚠️  No response message to send")
            
            return JSONResponse(content={'status': 'ok'})
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in webhook: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    @app.post('/')
    async def root_webhook(request: Request):
        """Webhook endpoint tại root path (fallback)"""
        print("📥 Received request at root path /")
        # Redirect đến webhook handler
        return await webhook(request)

    @app.get('/')
    async def root():
        """Root endpoint"""
        return JSONResponse(content={
            'status': 'ok',
            'message': 'Bot Chi Tieu API',
            'endpoints': {
                'webhook': '/webhook (POST)',
                'health': '/health (GET)'
            }
        })

    @app.get('/health')
    async def health():
        """Health check endpoint"""
        return JSONResponse(content={'status': 'ok'})

    if __name__ == '__main__':
        try:
            import uvicorn
            uvicorn.run(app, host='0.0.0.0', port=5000)
        except ImportError:
            print("❌ uvicorn not installed. Install with: pip install uvicorn")
else:
    if __name__ == '__main__':
        print("⚠️  FastAPI not available. This file is for local development only.")
        print("   For Vercel deployment, use api/webhook.py")
        print("   To run locally, install: pip install fastapi uvicorn")

