import os

# Chỉ load dotenv khi local (không phải Vercel)
# Vercel tự inject env vars, không cần dotenv
if os.getenv('VERCEL') != '1':
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv không bắt buộc

# Zalo Bot Config
ZALO_ACCESS_TOKEN = os.getenv('ZALO_ACCESS_TOKEN')
ZALO_SECRET_KEY = os.getenv('ZALO_SECRET_KEY')
ZALO_OA_ID = os.getenv('ZALO_OA_ID')
ZALO_USE_NEW_API = os.getenv('ZALO_USE_NEW_API', 'false').lower() == 'true'

# Google Sheets Config
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', './credentials/service_account.json')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

# Sheet names
SHEET_NAME_TRANSACTIONS = 'Giao dịch'
SHEET_NAME_CATEGORIES = 'Danh mục'

def validate_config():
    """Validate config khi cần (lazy validation)"""
    errors = []
    if not ZALO_ACCESS_TOKEN:
        errors.append("ZALO_ACCESS_TOKEN is required")
    if not GOOGLE_SHEET_ID:
        errors.append("GOOGLE_SHEET_ID is required")
    if errors:
        raise ValueError("Config errors: " + ", ".join(errors))

