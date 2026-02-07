import re
from typing import Dict, Optional, List

class NLPProcessor:
    """Xử lý ngôn ngữ tự nhiên để trích xuất thông tin giao dịch bằng regex"""
    
    # Từ khóa cho loại giao dịch
    THU_KEYWORDS = ['thu', 'nhận', 'nhận được', 'lương', 'tiền lương', 'được', 'có']
    CHI_KEYWORDS = ['chi', 'chi tiêu', 'mua', 'trả', 'thanh toán', 'tốn', 'hết']
    
    def __init__(self, categories: List[str] = None):
        """
        Khởi tạo processor
        
        Args:
            categories: Danh sách danh mục từ Google Sheets (nếu có)
        """
        self.categories = categories or []
    
    def process(self, message: str) -> Dict[str, any]:
        """
        Xử lý tin nhắn và trích xuất thông tin
        
        Args:
            message: Tin nhắn từ người dùng
            
        Returns:
            Dict chứa: loai, so_tien, danh_muc, ghi_chu, is_valid
        """
        message_original = message
        message = message.lower().strip()
        
        # Trích xuất loại giao dịch
        loai = self._extract_loai(message)
        
        # Trích xuất số tiền
        so_tien = self._extract_so_tien(message)
        
        # Trích xuất danh mục (sẽ match với danh sách từ sheet)
        danh_muc = self._extract_danh_muc(message)
        
        # Trích xuất ghi chú
        ghi_chu = self._extract_ghi_chu(message, so_tien, danh_muc)
        
        # Validate
        is_valid = loai is not None and so_tien is not None and danh_muc is not None
        
        return {
            'loai': loai,
            'so_tien': so_tien,
            'danh_muc': danh_muc,
            'ghi_chu': ghi_chu,
            'is_valid': is_valid,
            'raw_message': message_original
        }
    
    def _extract_loai(self, message: str) -> Optional[str]:
        """Trích xuất loại giao dịch (Thu/Chi)"""
        # Kiểm tra từ khóa Thu trước (ưu tiên)
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
        # Pattern 1: "50k", "100k", "1k", "1.5k"
        pattern1 = r'(\d+(?:\.\d+)?)\s*k\b'
        match = re.search(pattern1, message, re.IGNORECASE)
        if match:
            return float(match.group(1)) * 1000
        
        # Pattern 2: "5 triệu", "1.5 triệu", "5tr"
        pattern2 = r'(\d+(?:\.\d+)?)\s*tr[iiệ]u\b'
        match = re.search(pattern2, message, re.IGNORECASE)
        if match:
            return float(match.group(1)) * 1000000
        
        # Pattern 3: "5tr" (viết tắt)
        pattern3 = r'(\d+(?:\.\d+)?)\s*tr\b'
        match = re.search(pattern3, message, re.IGNORECASE)
        if match:
            return float(match.group(1)) * 1000000
        
        # Pattern 4: "30 nghìn", "100 nghìn", "30nghin"
        pattern4 = r'(\d+(?:\.\d+)?)\s*ngh[ìi]n\b'
        match = re.search(pattern4, message, re.IGNORECASE)
        if match:
            return float(match.group(1)) * 1000
        
        # Pattern 5: Số thuần túy "50000", "1000000" (ít nhất 4 chữ số)
        pattern5 = r'\b(\d{4,})\b'
        match = re.search(pattern5, message)
        if match:
            return float(match.group(1))
        
        return None
    
    def _extract_danh_muc(self, message: str) -> Optional[str]:
        """
        Trích xuất danh mục từ tin nhắn
        Match với danh sách categories từ Google Sheets
        """
        if not self.categories:
            return None
        
        message_lower = message.lower()
        
        # Tìm category match (tìm từ dài nhất trước)
        sorted_categories = sorted(self.categories, key=len, reverse=True)
        
        for category in sorted_categories:
            category_lower = category.lower()
            # Kiểm tra exact match hoặc partial match
            if category_lower in message_lower:
                return category  # Trả về tên gốc (có thể có chữ hoa)
        
        return None
    
    def _extract_ghi_chu(self, message: str, so_tien: Optional[float], danh_muc: Optional[str]) -> str:
        """Trích xuất ghi chú từ tin nhắn"""
        ghi_chu = message
        
        # Loại bỏ số tiền
        if so_tien:
            # Loại bỏ pattern số tiền
            ghi_chu = re.sub(r'(\d+(?:\.\d+)?)\s*(k|tr[iiệ]u|tr|ngh[ìi]n)\b', '', ghi_chu, flags=re.IGNORECASE)
            ghi_chu = re.sub(r'\b\d{4,}\b', '', ghi_chu)
        
        # Loại bỏ từ khóa loại
        for keyword in self.THU_KEYWORDS + self.CHI_KEYWORDS:
            ghi_chu = re.sub(r'\b' + re.escape(keyword) + r'\b', '', ghi_chu, flags=re.IGNORECASE)
        
        # Loại bỏ danh mục
        if danh_muc:
            ghi_chu = re.sub(re.escape(danh_muc.lower()), '', ghi_chu, flags=re.IGNORECASE)
        
        # Loại bỏ các từ thừa và khoảng trắng
        ghi_chu = re.sub(r'\s+', ' ', ghi_chu).strip()
        ghi_chu = re.sub(r'^(cho|để|với|về|hôm|nay|qua)\s+', '', ghi_chu, flags=re.IGNORECASE)
        
        return ghi_chu if ghi_chu else ''

