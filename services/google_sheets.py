import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import Dict, List, Optional
import os
import base64
import tempfile
import json
from config import GOOGLE_CREDENTIALS_PATH, GOOGLE_SHEET_ID, SHEET_NAME_TRANSACTIONS, SHEET_NAME_CATEGORIES

class GoogleSheetsService:
    """Service để tương tác với Google Sheets"""
    
    def __init__(self):
        """Khởi tạo service và kết nối với Google Sheets"""
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Hỗ trợ cả file và base64 (cho Vercel)
        credentials_path = self._get_credentials_path()
        
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_key(GOOGLE_SHEET_ID)
        
        # Lấy hoặc tạo sheets
        self._init_sheets()
        
        # Cleanup temp file nếu có
        self._temp_creds_file = credentials_path if credentials_path != GOOGLE_CREDENTIALS_PATH else None
    
    def _get_credentials_path(self) -> str:
        """Lấy đường dẫn credentials, hỗ trợ base64 cho Vercel"""
        # Kiểm tra base64 từ environment variable (cho Vercel)
        creds_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
        if creds_base64:
            try:
                # Decode base64
                creds_json = base64.b64decode(creds_base64).decode('utf-8')
                
                # Tạo file tạm
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                temp_file.write(creds_json)
                temp_file.close()
                
                return temp_file.name
            except Exception as e:
                print(f"Error decoding base64 credentials: {e}")
                raise
        
        # Fallback: sử dụng file path
        if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
            raise FileNotFoundError(
                f"Credentials not found. Either set GOOGLE_CREDENTIALS_BASE64 "
                f"or ensure file exists: {GOOGLE_CREDENTIALS_PATH}"
            )
        
        return GOOGLE_CREDENTIALS_PATH
    
    def _init_sheets(self):
        """Khởi tạo các sheet nếu chưa có"""
        try:
            # Sheet giao dịch
            try:
                self.sheet_transactions = self.spreadsheet.worksheet(SHEET_NAME_TRANSACTIONS)
            except gspread.exceptions.WorksheetNotFound:
                self.sheet_transactions = self.spreadsheet.add_worksheet(
                    title=SHEET_NAME_TRANSACTIONS,
                    rows=1000,
                    cols=10
                )
                # Tạo header
                self.sheet_transactions.append_row([
                    'Ngày giờ', 'Loại', 'Số tiền', 'Danh mục', 'Ghi chú', 'User ID'
                ])
            
            # Sheet danh mục
            try:
                self.sheet_categories = self.spreadsheet.worksheet(SHEET_NAME_CATEGORIES)
            except gspread.exceptions.WorksheetNotFound:
                self.sheet_categories = self.spreadsheet.add_worksheet(
                    title=SHEET_NAME_CATEGORIES,
                    rows=100,
                    cols=3
                )
                # Tạo header và danh mục mặc định
                self.sheet_categories.append_row(['Tên danh mục', 'Loại', 'Mô tả'])
                default_categories = [
                    ['Ăn uống', 'Chi', ''],
                    ['Lương', 'Thu', ''],
                    ['Mua sắm', 'Chi', ''],
                    ['Giao thông', 'Chi', ''],
                    ['Giải trí', 'Chi', ''],
                    ['Khác', 'Cả hai', '']
                ]
                for cat in default_categories:
                    self.sheet_categories.append_row(cat)
        
        except Exception as e:
            raise Exception(f"Error initializing sheets: {e}")
    
    def get_categories(self) -> List[str]:
        """
        Lấy danh sách danh mục từ sheet
        
        Returns:
            List tên danh mục
        """
        try:
            records = self.sheet_categories.get_all_records()
            categories = [record.get('Tên danh mục', '') for record in records if record.get('Tên danh mục')]
            return [cat for cat in categories if cat]  # Loại bỏ empty
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def add_transaction(self, transaction: Dict[str, any], user_id: str = 'default') -> bool:
        """
        Thêm giao dịch vào sheet
        
        Args:
            transaction: Dict chứa loai, so_tien, danh_muc, ghi_chu
            user_id: ID của người dùng (mặc định 'default' vì 1 user)
            
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
            self.sheet_transactions.append_row(row)
            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def get_transactions(self, user_id: str = 'default', limit: int = 100) -> List[Dict]:
        """
        Lấy danh sách giao dịch
        
        Args:
            user_id: Lọc theo user (mặc định 'default')
            limit: Số lượng giao dịch cần lấy
            
        Returns:
            List các giao dịch
        """
        try:
            records = self.sheet_transactions.get_all_records()
            
            if user_id:
                records = [r for r in records if r.get('User ID') == user_id]
            
            # Sắp xếp theo ngày giờ (mới nhất trước)
            records.sort(key=lambda x: x.get('Ngày giờ', ''), reverse=True)
            
            return records[:limit]
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    def get_statistics(self, user_id: str = 'default', month: Optional[int] = None, year: Optional[int] = None) -> Dict:
        """
        Tính toán thống kê
        
        Args:
            user_id: ID người dùng
            month: Tháng (None = tất cả)
            year: Năm (None = tất cả)
            
        Returns:
            Dict chứa thống kê
        """
        try:
            transactions = self.get_transactions(user_id, limit=10000)
            
            # Lọc theo tháng/năm nếu có
            if month or year:
                filtered = []
                for t in transactions:
                    date_str = t.get('Ngày giờ', '')
                    if date_str:
                        try:
                            date_obj = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
                            if month and date_obj.month != month:
                                continue
                            if year and date_obj.year != year:
                                continue
                            filtered.append(t)
                        except:
                            continue
                transactions = filtered
            
            # Tính toán
            total_thu = sum(float(t.get('Số tiền', 0)) for t in transactions if t.get('Loại') == 'Thu')
            total_chi = sum(float(t.get('Số tiền', 0)) for t in transactions if t.get('Loại') == 'Chi')
            so_luong = len(transactions)
            
            # Thống kê theo danh mục
            danh_muc_stats = {}
            for t in transactions:
                danh_muc = t.get('Danh mục', 'Khác')
                loai = t.get('Loại', '')
                so_tien = float(t.get('Số tiền', 0))
                
                if danh_muc not in danh_muc_stats:
                    danh_muc_stats[danh_muc] = {'Thu': 0, 'Chi': 0, 'SoLuong': 0}
                
                danh_muc_stats[danh_muc][loai] += so_tien
                danh_muc_stats[danh_muc]['SoLuong'] += 1
            
            return {
                'total_thu': total_thu,
                'total_chi': total_chi,
                'so_luong': so_luong,
                'danh_muc_stats': danh_muc_stats,
                'transactions': transactions[:10]  # 10 giao dịch gần nhất
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                'total_thu': 0,
                'total_chi': 0,
                'so_luong': 0,
                'danh_muc_stats': {},
                'transactions': []
            }

