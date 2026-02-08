"""
Vercel entry point - FastAPI app cho Vercel
Lazy load services để tránh lỗi khi import
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import hmac
import hashlib
import os

# Import từ root (Vercel tự động thêm root vào PYTHONPATH)
from config import ZALO_SECRET_KEY, validate_config

# Validate config khi khởi tạo
try:
    validate_config()
except ValueError as e:
    print(f"⚠️  Config validation warning: {e}")
    # Không raise để tránh fail build, nhưng sẽ fail khi runtime

# Khởi tạo FastAPI app
app = FastAPI(title="Bot Chi Tieu", description="Zalo Bot for expense tracking")

# Lazy load services (chỉ khởi tạo khi cần)
_sheets_service = None
_zalo_service = None

def get_sheets_service():
    """Lazy load Google Sheets service"""
    global _sheets_service
    if _sheets_service is None:
        from services.google_sheets import GoogleSheetsService
        _sheets_service = GoogleSheetsService()
    return _sheets_service

def get_zalo_service():
    """Lazy load Zalo service"""
    global _zalo_service
    if _zalo_service is None:
        from services.zalo_bot import ZaloBotService
        _zalo_service = ZaloBotService()
    return _zalo_service

def verify_zalo_signature(data: bytes, signature: str) -> bool:
    """Xác thực signature từ Zalo"""
    # Nếu không có secret key, bỏ qua verification (tạm thời để test)
    if not ZALO_SECRET_KEY or ZALO_SECRET_KEY.strip() == '':
        print("⚠️  Warning: ZALO_SECRET_KEY not set - skipping verification (for testing)")
        # Tạm thời cho phép pass để test, sau đó nên set secret key
        return True
    
    if not signature:
        print("⚠️  Warning: No signature in request header")
        # Nếu không có signature và không có secret key, cho phép pass để test
        return True
    
    try:
        expected_signature = hmac.new(
            ZALO_SECRET_KEY.encode(),
            data,
            hashlib.sha256
        ).hexdigest()
        is_valid = hmac.compare_digest(signature, expected_signature)
        if not is_valid:
            print(f"❌ Signature mismatch. Expected: {expected_signature[:20]}..., Got: {signature[:20]}...")
        return is_valid
    except Exception as e:
        print(f"Error verifying signature: {e}")
        import traceback
        traceback.print_exc()
        # Tạm thời cho phép pass để test
        return True

def handle_statistics_command(user_id: str, message: str) -> str:
    """Xử lý lệnh thống kê"""
    try:
        import re
        print(f"📊 Processing statistics - user_id: {user_id}, message: {message}")
        
        # Khởi tạo service
        try:
            sheets_service = get_sheets_service()
            print("✅ Google Sheets service initialized")
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error initializing Google Sheets: {error_msg}")
            import traceback
            traceback.print_exc()
            # Trả về thông báo lỗi cụ thể
            if "credentials" in error_msg.lower() or "credential" in error_msg.lower():
                return "❌ Lỗi: Google Credentials không hợp lệ. Kiểm tra GOOGLE_CREDENTIALS_BASE64"
            elif "sheet" in error_msg.lower() or "spreadsheet" in error_msg.lower():
                return "❌ Lỗi: Không thể kết nối Google Sheets. Kiểm tra GOOGLE_SHEET_ID và quyền truy cập"
            else:
                return f"❌ Lỗi kết nối Google Sheets: {error_msg[:100]}"
        
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
        
        print(f"📊 Getting statistics - month: {month}, year: {year}")
        
        # Lấy thống kê
        try:
            stats = sheets_service.get_statistics(user_id=user_id, month=month, year=year)
            print(f"✅ Statistics retrieved: {stats.get('so_luong', 0)} transactions")
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error getting statistics: {error_msg}")
            import traceback
            traceback.print_exc()
            return f"❌ Lỗi khi lấy thống kê: {error_msg[:100]}"
        
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
        else:
            response += "📋 Chưa có dữ liệu theo danh mục\n"
        
        return response
    except Exception as e:
        print(f"❌ Error handling statistics: {e}")
        import traceback
        traceback.print_exc()
        return f"❌ Có lỗi xảy ra: {str(e)[:100]}"

def handle_transaction(user_id: str, message: str) -> str:
    """Xử lý giao dịch thu chi"""
    try:
        sheets_service = get_sheets_service()
        categories = sheets_service.get_categories()
        
        from services.nlp_processor import NLPProcessor
        nlp_processor = NLPProcessor(categories=categories)
        transaction = nlp_processor.process(message)
        
        if not transaction.get('is_valid'):
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

@app.post('/webhook')
async def webhook(request: Request):
    """Webhook endpoint cho Zalo Bot"""
    try:
        # Log tất cả headers để debug
        print(f"📥 Headers: {dict(request.headers)}")
        
        # Đọc raw body để verify signature
        raw_data = await request.body()
        signature = request.headers.get('X-Zalo-Signature', '')
        
        print(f"📥 Signature from header: {signature}")
        print(f"📥 Raw data length: {len(raw_data)}")
        
        if not verify_zalo_signature(raw_data, signature):
            print("❌ Signature verification failed")
            raise HTTPException(status_code=401, detail='Invalid signature')
        
        print("✅ Signature verified")
        
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
            zalo_service = get_zalo_service()
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

@app.post('/test-webhook')
async def test_webhook(request: Request):
    """Test endpoint - không cần signature (chỉ để debug)"""
    try:
        # Đọc body, có thể rỗng
        body = await request.body()
        if body:
            try:
                data = await request.json()
                print(f"🧪 Test webhook received JSON: {json.dumps(data, ensure_ascii=False, indent=2)}")
                return JSONResponse(content={'status': 'ok', 'received': data})
            except:
                print(f"🧪 Test webhook received raw body: {body.decode('utf-8', errors='ignore')}")
                return JSONResponse(content={'status': 'ok', 'received_raw': body.decode('utf-8', errors='ignore')})
        else:
            print("🧪 Test webhook received empty body")
            return JSONResponse(content={'status': 'ok', 'message': 'Empty body received'})
    except Exception as e:
        print(f"🧪 Test webhook error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={'status': 'error', 'error': str(e)}, status_code=500)
