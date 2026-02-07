# Ví Dụ Code - Bot Ghi Chép Thu Chi

## 1. NLP Processor (Python)

```python
import re
from typing import Dict, Optional

class NLPProcessor:
    """Xử lý ngôn ngữ tự nhiên để trích xuất thông tin giao dịch"""
    
    # Danh sách từ khóa cho loại giao dịch
    THU_KEYWORDS = ['thu', 'nhận', 'nhận được', 'lương', 'tiền lương']
    CHI_KEYWORDS = ['chi', 'chi tiêu', 'mua', 'trả', 'thanh toán']
    
    # Danh sách danh mục
    CATEGORIES = {
        'ăn uống': ['ăn', 'ăn uống', 'ăn trưa', 'ăn sáng', 'ăn tối', 'ăn vặt', 'cơm', 'nhà hàng'],
        'lương': ['lương', 'tiền lương', 'lương tháng'],
        'mua sắm': ['mua sắm', 'mua', 'quần áo', 'đồ dùng', 'shopping'],
        'giao thông': ['xe', 'taxi', 'grab', 'xăng', 'gửi xe'],
        'giải trí': ['xem phim', 'cafe', 'game', 'giải trí'],
        'khác': []
    }
    
    def process(self, message: str) -> Dict[str, any]:
        """
        Xử lý tin nhắn và trích xuất thông tin
        
        Args:
            message: Tin nhắn từ người dùng
            
        Returns:
            Dict chứa: loai, so_tien, danh_muc, ghi_chu
        """
        message = message.lower().strip()
        
        # Trích xuất loại giao dịch
        loai = self._extract_loai(message)
        
        # Trích xuất số tiền
        so_tien = self._extract_so_tien(message)
        
        # Trích xuất danh mục
        danh_muc = self._extract_danh_muc(message)
        
        # Trích xuất ghi chú
        ghi_chu = self._extract_ghi_chu(message, so_tien, danh_muc)
        
        return {
            'loai': loai,
            'so_tien': so_tien,
            'danh_muc': danh_muc,
            'ghi_chu': ghi_chu,
            'raw_message': message
        }
    
    def _extract_loai(self, message: str) -> Optional[str]:
        """Trích xuất loại giao dịch (Thu/Chi)"""
        # Kiểm tra từ khóa Thu trước
        for keyword in self.THU_KEYWORDS:
            if keyword in message:
                return 'Thu'
        
        # Kiểm tra từ khóa Chi
        for keyword in self.CHI_KEYWORDS:
            if keyword in message:
                return 'Chi'
        
        return None
    
    def _extract_so_tien(self, message: str) -> Optional[float]:
        """Trích xuất số tiền từ tin nhắn"""
        # Pattern 1: "50k", "100k", "1k"
        pattern1 = r'(\d+(?:\.\d+)?)\s*k\b'
        match = re.search(pattern1, message)
        if match:
            return float(match.group(1)) * 1000
        
        # Pattern 2: "5 triệu", "1.5 triệu"
        pattern2 = r'(\d+(?:\.\d+)?)\s*tr[iiệ]u'
        match = re.search(pattern2, message)
        if match:
            return float(match.group(1)) * 1000000
        
        # Pattern 3: "30 nghìn", "100 nghìn"
        pattern3 = r'(\d+(?:\.\d+)?)\s*ngh[ìi]n'
        match = re.search(pattern3, message)
        if match:
            return float(match.group(1)) * 1000
        
        # Pattern 4: Số thuần túy "50000", "1000000"
        pattern4 = r'\b(\d{4,})\b'
        match = re.search(pattern4, message)
        if match:
            return float(match.group(1))
        
        return None
    
    def _extract_danh_muc(self, message: str) -> str:
        """Trích xuất danh mục từ tin nhắn"""
        for category, keywords in self.CATEGORIES.items():
            for keyword in keywords:
                if keyword in message:
                    return category.capitalize()
        
        return 'Khác'
    
    def _extract_ghi_chu(self, message: str, so_tien: Optional[float], danh_muc: str) -> str:
        """Trích xuất ghi chú từ tin nhắn"""
        # Loại bỏ các phần đã trích xuất
        ghi_chu = message
        
        # Loại bỏ số tiền
        if so_tien:
            ghi_chu = re.sub(r'(\d+(?:\.\d+)?)\s*(k|tr[iiệ]u|ngh[ìi]n)', '', ghi_chu, flags=re.IGNORECASE)
            ghi_chu = re.sub(r'\b\d{4,}\b', '', ghi_chu)
        
        # Loại bỏ từ khóa loại
        for keyword in self.THU_KEYWORDS + self.CHI_KEYWORDS:
            ghi_chu = ghi_chu.replace(keyword, '')
        
        # Loại bỏ từ khóa danh mục
        for keywords in self.CATEGORIES.values():
            for keyword in keywords:
                ghi_chu = ghi_chu.replace(keyword, '')
        
        # Loại bỏ các từ thừa
        ghi_chu = re.sub(r'\s+', ' ', ghi_chu).strip()
        ghi_chu = re.sub(r'^(cho|để|với|về)\s+', '', ghi_chu, flags=re.IGNORECASE)
        
        return ghi_chu if ghi_chu else ''

# Ví dụ sử dụng
if __name__ == '__main__':
    processor = NLPProcessor()
    
    test_cases = [
        "Chi 50k ăn trưa",
        "Thu 5 triệu lương tháng 1",
        "Hôm nay chi 200k mua quần áo",
        "Chi tiền ăn sáng 30 nghìn",
        "Thu tiền lương 10 triệu"
    ]
    
    for test in test_cases:
        result = processor.process(test)
        print(f"Input: {test}")
        print(f"Output: {result}\n")
```

## 2. Google Sheets Service (Python)

```python
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import Dict, List

class GoogleSheetsService:
    """Service để tương tác với Google Sheets"""
    
    def __init__(self, credentials_path: str, sheet_id: str):
        """
        Khởi tạo service
        
        Args:
            credentials_path: Đường dẫn đến file JSON credentials
            sheet_id: ID của Google Sheet
        """
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(sheet_id).sheet1
    
    def add_transaction(self, transaction: Dict[str, any], user_id: str) -> bool:
        """
        Thêm giao dịch vào sheet
        
        Args:
            transaction: Dict chứa loai, so_tien, danh_muc, ghi_chu
            user_id: ID của người dùng
            
        Returns:
            True nếu thành công, False nếu có lỗi
        """
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row = [
                now,                          # Ngày giờ
                transaction.get('loai', ''),  # Loại
                transaction.get('so_tien', 0), # Số tiền
                transaction.get('danh_muc', ''), # Danh mục
                transaction.get('ghi_chu', ''),  # Ghi chú
                user_id                        # User ID
            ]
            self.sheet.append_row(row)
            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def get_transactions(self, user_id: str = None, limit: int = 10) -> List[Dict]:
        """
        Lấy danh sách giao dịch
        
        Args:
            user_id: Lọc theo user (None = tất cả)
            limit: Số lượng giao dịch cần lấy
            
        Returns:
            List các giao dịch
        """
        try:
            records = self.sheet.get_all_records()
            
            if user_id:
                records = [r for r in records if r.get('User ID') == user_id]
            
            # Sắp xếp theo ngày giờ (mới nhất trước)
            records.sort(key=lambda x: x.get('Ngày giờ', ''), reverse=True)
            
            return records[:limit]
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
```

## 3. Zalo Bot Webhook Handler (Python Flask)

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import json
import os
from dotenv import load_dotenv
from services.nlp_processor import NLPProcessor
from services.google_sheets import GoogleSheetsService

load_dotenv()

app = Flask(__name__)

# Khởi tạo services
nlp_processor = NLPProcessor()
sheets_service = GoogleSheetsService(
    credentials_path=os.getenv('GOOGLE_CREDENTIALS_PATH'),
    sheet_id=os.getenv('GOOGLE_SHEET_ID')
)

# Zalo Bot config
ZALO_SECRET_KEY = os.getenv('ZALO_SECRET_KEY')
ZALO_ACCESS_TOKEN = os.getenv('ZALO_ACCESS_TOKEN')
ZALO_OA_ID = os.getenv('ZALO_OA_ID')

def verify_zalo_signature(data: bytes, signature: str) -> bool:
    """Xác thực signature từ Zalo"""
    if not ZALO_SECRET_KEY:
        return True  # Skip verification nếu không có secret key
    
    expected_signature = hmac.new(
        ZALO_SECRET_KEY.encode(),
        data,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

def send_zalo_message(user_id: str, message: str):
    """Gửi tin nhắn về Zalo"""
    import requests
    
    url = 'https://openapi.zalo.me/v2.0/oa/message'
    headers = {
        'access_token': ZALO_ACCESS_TOKEN,
        'Content-Type': 'application/json'
    }
    data = {
        'recipient': {'user_id': user_id},
        'message': {'text': message}
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Zalo message: {e}")
        return False

@app.route('/webhook/zalo', methods=['POST'])
def zalo_webhook():
    """Xử lý webhook từ Zalo"""
    try:
        # Lấy raw data để verify signature
        raw_data = request.get_data()
        signature = request.headers.get('X-Zalo-Signature', '')
        
        # Verify signature
        if not verify_zalo_signature(raw_data, signature):
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse JSON data
        data = request.get_json()
        
        # Kiểm tra event type
        if data.get('event') != 'user_send_text':
            return jsonify({'status': 'ok'})
        
        # Lấy thông tin tin nhắn
        message_text = data.get('message', {}).get('text', '')
        user_id = data.get('sender', {}).get('id', '')
        
        if not message_text or not user_id:
            return jsonify({'status': 'ok'})
        
        # Xử lý tin nhắn bằng NLP
        transaction = nlp_processor.process(message_text)
        
        # Kiểm tra xem có đủ thông tin không
        if not transaction.get('loai') or not transaction.get('so_tien'):
            response_msg = (
                "Xin lỗi, tôi không hiểu. "
                "Vui lòng nhập theo format:\n"
                "• Chi 50k ăn trưa\n"
                "• Thu 5 triệu lương"
            )
            send_zalo_message(user_id, response_msg)
            return jsonify({'status': 'ok'})
        
        # Ghi vào Google Sheets
        success = sheets_service.add_transaction(transaction, user_id)
        
        if success:
            # Phản hồi thành công
            response_msg = (
                f"✅ Đã ghi nhận:\n"
                f"• Loại: {transaction['loai']}\n"
                f"• Số tiền: {transaction['so_tien']:,.0f} VNĐ\n"
                f"• Danh mục: {transaction['danh_muc']}\n"
                f"• Ghi chú: {transaction['ghi_chu'] or 'Không có'}"
            )
        else:
            response_msg = "❌ Có lỗi xảy ra khi ghi dữ liệu. Vui lòng thử lại sau."
        
        send_zalo_message(user_id, response_msg)
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

## 4. File .env mẫu

```env
# Zalo Bot
ZALO_ACCESS_TOKEN=your_zalo_access_token_here
ZALO_SECRET_KEY=your_zalo_secret_key_here
ZALO_OA_ID=your_zalo_oa_id_here

# Google Sheets
GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json
GOOGLE_SHEET_ID=your_google_sheet_id_here

# Server
PORT=5000
DEBUG=True
```

## 5. requirements.txt

```txt
flask==2.3.0
gspread==5.12.0
google-auth==2.23.0
python-dotenv==1.0.0
requests==2.31.0
```

## 6. .gitignore

```gitignore
# Environment variables
.env

# Google credentials
credentials/
*.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
```

