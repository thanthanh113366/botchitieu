import requests
from typing import Optional
import os
from config import ZALO_ACCESS_TOKEN, ZALO_OA_ID

class ZaloBotService:
    """Service để tương tác với Zalo Bot API"""
    
    def __init__(self):
        """Khởi tạo service"""
        self.access_token = ZALO_ACCESS_TOKEN
        self.oa_id = ZALO_OA_ID
        
        # Hỗ trợ cả Zalo Bot Platform mới và API cũ
        # Zalo Bot Platform: https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/sendMessage
        # API cũ: https://openapi.zalo.me/v2.0/oa/message
        use_new_api = os.getenv('ZALO_USE_NEW_API', 'false').lower() == 'true'
        if use_new_api:
            # URL sẽ được tạo động với BOT_TOKEN trong send_text_message
            self.api_base = 'https://bot-api.zaloplatforms.com'
        else:
            self.api_url = 'https://openapi.zalo.me/v2.0/oa/message'
    
    def send_text_message(self, user_id: str, message: str) -> bool:
        """
        Gửi tin nhắn text về Zalo
        
        Args:
            user_id: ID người dùng
            message: Nội dung tin nhắn
            
        Returns:
            True nếu thành công, False nếu có lỗi
        """
        if not self.access_token:
            print("ZALO_ACCESS_TOKEN not configured")
            return False
        
        # Hỗ trợ cả API mới và cũ
        use_new_api = os.getenv('ZALO_USE_NEW_API', 'false').lower() == 'true'
        
        if use_new_api:
            # Zalo Bot Platform API mới theo tài liệu chính thức
            # URL: https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/sendMessage
            api_url = f'{self.api_base}/bot{self.access_token}/sendMessage'
            headers = {
                'Content-Type': 'application/json'
            }
            data = {
                'chat_id': user_id,
                'text': message
            }
        else:
            api_url = self.api_url
            # API cũ
            headers = {
                'access_token': self.access_token,
                'Content-Type': 'application/json'
            }
            data = {
                'recipient': {'user_id': user_id},
                'message': {'text': message}
            }
        
        try:
            print(f"🔗 Sending to: {api_url}")
            print(f"📤 Headers: {headers}")
            print(f"📤 Data: {data}")
            
            response = requests.post(api_url, json=data, headers=headers, timeout=10)
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response body: {response.text[:500]}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok') == True:
                    print("✅ Message sent successfully")
                    return True
                else:
                    print(f"⚠️  API returned ok=false: {result}")
                    return False
            else:
                print(f"❌ Error response: {response.status_code} - {response.text[:500]}")
                return False
        except Exception as e:
            print(f"❌ Error sending Zalo message: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_image(self, user_id: str, image_url: str) -> bool:
        """
        Gửi hình ảnh về Zalo
        
        Args:
            user_id: ID người dùng
            image_url: URL của hình ảnh (phải là public URL)
            
        Returns:
            True nếu thành công, False nếu có lỗi
        """
        if not self.access_token:
            print("ZALO_ACCESS_TOKEN not configured")
            return False
        
        headers = {
            'access_token': self.access_token,
            'Content-Type': 'application/json'
        }
        
        data = {
            'recipient': {'user_id': user_id},
            'message': {
                'attachment': {
                    'type': 'image',
                    'payload': {
                        'url': image_url
                    }
                }
            }
        }
        
        try:
            response = requests.post(self.api_url, json=data, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Zalo image: {e}")
            return False

