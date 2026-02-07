import os
from dotenv import load_dotenv

load_dotenv()

# Zalo Bot Config
ZALO_ACCESS_TOKEN = os.getenv('ZALO_ACCESS_TOKEN')  # Hoặc ZALO_BOT_TOKEN cho Zalo Bot Platform
ZALO_SECRET_KEY = os.getenv('ZALO_SECRET_KEY')  # Webhook secret
ZALO_OA_ID = os.getenv('ZALO_OA_ID')  # Không bắt buộc cho Zalo Bot Platform
ZALO_USE_NEW_API = os.getenv('ZALO_USE_NEW_API', 'false').lower() == 'true'  # Dùng Zalo Bot Platform mới

# Google Sheets Config
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', './credentials/service_account.json')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

# Sheet names
SHEET_NAME_TRANSACTIONS = 'Giao dịch'
SHEET_NAME_CATEGORIES = 'Danh mục'

# Validate required config
if not ZALO_ACCESS_TOKEN:
    raise ValueError("ZALO_ACCESS_TOKEN is required")
if not GOOGLE_SHEET_ID:
    raise ValueError("GOOGLE_SHEET_ID is required")

