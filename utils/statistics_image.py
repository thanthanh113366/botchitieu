# Comment out để giảm dependencies cho Vercel
# Function này tạm thời disabled để giảm size
import io
from typing import Dict
from datetime import datetime

def create_statistics_image(stats: Dict, month: int = None, year: int = None) -> bytes:
    """
    Tạo hình ảnh thống kê từ dữ liệu
    
    Args:
        stats: Dict chứa thống kê từ GoogleSheetsService.get_statistics()
        month: Tháng (None = tất cả)
        year: Năm (None = tất cả)
        
    Returns:
        bytes: Hình ảnh dưới dạng bytes
    """
    # Function disabled để giảm dependencies cho Vercel
    # Cần PIL/Pillow để chạy function này
    raise NotImplementedError(
        "Image generation disabled to reduce Vercel function size. "
        "Install pillow for local use: pip install pillow"
    )
    
    # Code below is disabled
    # from PIL import Image, ImageDraw, ImageFont
    # width = 800
    # height = 1000
    # img = Image.new('RGB', (width, height), color='white')
    # draw = ImageDraw.Draw(img)
    
    # Màu sắc
    color_bg = (240, 240, 240)
    color_header = (70, 130, 180)
    color_text = (50, 50, 50)
    color_thu = (34, 139, 34)  # Xanh lá
    color_chi = (220, 20, 60)  # Đỏ
    
    # Font (sử dụng font mặc định, có thể thay bằng font khác)
    try:
        font_title = ImageFont.truetype("arial.ttf", 32)
        font_header = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        # Fallback nếu không có font
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    y_position = 30
    
    # Tiêu đề
    title = "📊 THỐNG KÊ THU CHI"
    if month and year:
        title += f" - {month}/{year}"
    elif year:
        title += f" - Năm {year}"
    
    draw.text((width//2, y_position), title, fill=color_header, font=font_title, anchor='mt')
    y_position += 60
    
    # Tổng quan
    draw.rectangle([50, y_position, width-50, y_position+120], fill=color_bg, outline=color_header, width=2)
    y_position += 20
    
    total_thu = stats.get('total_thu', 0)
    total_chi = stats.get('total_chi', 0)
    so_luong = stats.get('so_luong', 0)
    chenh_lech = total_thu - total_chi
    
    draw.text((70, y_position), f"Tổng Thu: {total_thu:,.0f} VNĐ", fill=color_thu, font=font_header)
    y_position += 35
    draw.text((70, y_position), f"Tổng Chi: {total_chi:,.0f} VNĐ", fill=color_chi, font=font_header)
    y_position += 35
    draw.text((70, y_position), f"Số giao dịch: {so_luong}", fill=color_text, font=font_header)
    y_position += 35
    draw.text((70, y_position), f"Chênh lệch: {chenh_lech:,.0f} VNĐ", 
              fill=color_thu if chenh_lech >= 0 else color_chi, font=font_header)
    y_position += 50
    
    # Thống kê theo danh mục
    danh_muc_stats = stats.get('danh_muc_stats', {})
    if danh_muc_stats:
        draw.text((width//2, y_position), "Thống kê theo Danh mục", fill=color_header, font=font_header, anchor='mt')
        y_position += 40
        
        # Vẽ bảng
        table_y_start = y_position
        row_height = 40
        col_widths = [200, 150, 150, 150]  # Danh mục, Thu, Chi, Số lượng
        
        # Header
        headers = ['Danh mục', 'Thu', 'Chi', 'Số lượng']
        x_pos = 50
        for i, header in enumerate(headers):
            draw.rectangle([x_pos, y_position, x_pos + col_widths[i], y_position + row_height], 
                          fill=color_header, outline='black', width=1)
            draw.text((x_pos + col_widths[i]//2, y_position + row_height//2), header, 
                     fill='white', font=font_text, anchor='mm')
            x_pos += col_widths[i]
        y_position += row_height
        
        # Rows
        for danh_muc, data in sorted(danh_muc_stats.items(), 
                                    key=lambda x: x[1]['Thu'] + x[1]['Chi'], 
                                    reverse=True):
            x_pos = 50
            row_data = [
                danh_muc[:15],  # Giới hạn độ dài
                f"{data['Thu']:,.0f}" if data['Thu'] > 0 else "-",
                f"{data['Chi']:,.0f}" if data['Chi'] > 0 else "-",
                str(data['SoLuong'])
            ]
            
            for i, cell_data in enumerate(row_data):
                draw.rectangle([x_pos, y_position, x_pos + col_widths[i], y_position + row_height], 
                              fill='white', outline='black', width=1)
                draw.text((x_pos + col_widths[i]//2, y_position + row_height//2), cell_data, 
                         fill=color_text, font=font_small, anchor='mm')
                x_pos += col_widths[i]
            
            y_position += row_height
            
            # Giới hạn số dòng hiển thị
            if y_position > height - 200:
                break
        
        y_position += 30
    
    # Giao dịch gần nhất
    transactions = stats.get('transactions', [])[:5]
    if transactions:
        draw.text((width//2, y_position), "Giao dịch gần nhất", fill=color_header, font=font_header, anchor='mt')
        y_position += 40
        
        for t in transactions:
            loai = t.get('Loại', '')
            so_tien = float(t.get('Số tiền', 0))
            danh_muc = t.get('Danh mục', '')
            ghi_chu = t.get('Ghi chú', '')
            date_str = t.get('Ngày giờ', '')
            
            # Format date
            try:
                if date_str:
                    date_obj = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
                    date_display = date_obj.strftime('%d/%m/%Y')
                else:
                    date_display = ''
            except:
                date_display = date_str.split()[0] if date_str else ''
            
            text = f"{date_display} | {loai} | {so_tien:,.0f} | {danh_muc}"
            if ghi_chu:
                text += f" | {ghi_chu[:20]}"
            
            draw.text((70, y_position), text, fill=color_text, font=font_small)
            y_position += 25
    
    # Footer
    footer_text = f"Tạo lúc: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    draw.text((width//2, height - 30), footer_text, fill=(150, 150, 150), font=font_small, anchor='mt')
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()

