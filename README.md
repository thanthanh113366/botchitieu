# Bot Ghi Chép Thu Chi - Zalo Bot + Google Sheets

Ứng dụng ghi chép thu chi thông qua Zalo Bot với khả năng xử lý ngôn ngữ tự nhiên, dữ liệu được lưu trữ trên Google Sheets.

## 📚 Tài Liệu

- **[KE_HOACH_TRIEN_KHAI.md](./KE_HOACH_TRIEN_KHAI.md)** - Kế hoạch triển khai chi tiết
- **[CHI_TIET_KY_THUAT.md](./CHI_TIET_KY_THUAT.md)** - Chi tiết kỹ thuật và làm rõ các điểm mù mờ
- **[EXAMPLE_CODE.md](./EXAMPLE_CODE.md)** - Ví dụ code minh họa

## 🎯 Tính Năng

- ✅ Nhận tin nhắn từ Zalo Bot
- ✅ Xử lý ngôn ngữ tự nhiên (NLP) để trích xuất thông tin giao dịch
- ✅ Tự động ghi dữ liệu vào Google Sheets
- ✅ Phản hồi người dùng qua Zalo Bot

## 🏗️ Kiến Trúc

```
User (Zalo) → Zalo Bot → Webhook → Backend Server → Google Sheets
                                      ↓
                                 NLP Processor
```

## 🚀 Quick Start

### Yêu Cầu

- Python 3.8+
- Zalo Bot API Key (đã có)
- Google Cloud Project với Google Sheets API enabled
- Google Service Account JSON key

### Cài Đặt Local

1. **Clone repository và setup môi trường với Conda:**
```bash
# Option 1: Tạo từ file environment.yml (khuyến nghị)
conda env create -f environment.yml
conda activate botchitieu

# Option 2: Tạo thủ công
conda create -n botchitieu python=3.9 -y
conda activate botchitieu
pip install -r requirements.txt
```

2. **Cấu hình environment variables:**
```bash
cp .env.example .env
# Chỉnh sửa .env với các API keys của bạn
```

3. **Setup Google Sheets:**
   - Xem hướng dẫn chi tiết trong [HUONG_DAN_SETUP.md](./HUONG_DAN_SETUP.md)
   - Tạo Google Cloud Project
   - Enable Google Sheets API
   - Tạo Service Account và download JSON key
   - Share Google Sheet với Service Account email

4. **Chạy server:**
```bash
python app.py
```

5. **Setup webhook với Zalo Bot:**
   - Sử dụng ngrok để expose local server: `ngrok http 5000`
   - Cấu hình webhook URL trong Zalo Bot dashboard: `https://your-ngrok-url.ngrok.io/webhook`

### Deploy lên Vercel

Xem hướng dẫn chi tiết trong [SETUP_VERCEL.md](./SETUP_VERCEL.md)

**Tóm tắt:**
1. Cài Vercel CLI: `npm i -g vercel`
2. Login: `vercel login`
3. Setup environment variables trên Vercel Dashboard
4. Deploy: `vercel --prod`
5. Cấu hình webhook URL: `https://your-project.vercel.app/api/webhook`

## 📝 Format Tin Nhắn

Người dùng có thể nhập tin nhắn theo các format sau:

- `Chi 50k ăn trưa`
- `Thu 5 triệu lương`
- `Hôm nay chi 200k mua quần áo`
- `Chi tiền ăn sáng 30 nghìn`
- `Thu tiền lương 10 triệu`

## 🔧 Cấu Hình

### Environment Variables

```env
# Zalo Bot
ZALO_ACCESS_TOKEN=your_access_token
ZALO_SECRET_KEY=your_secret_key
ZALO_OA_ID=your_oa_id

# Google Sheets
GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json
GOOGLE_SHEET_ID=your_sheet_id
```

### Google Sheets Structure

Sheet cần có các cột sau (có thể tự động tạo):
- Ngày giờ
- Loại (Thu/Chi)
- Số tiền
- Danh mục
- Ghi chú
- User ID

## 📊 Cấu Trúc Project

```
BotChiTiu/
├── app.py                  # Main application
├── services/
│   ├── nlp_processor.py    # NLP processing
│   ├── google_sheets.py    # Google Sheets service
│   └── zalo_bot.py         # Zalo Bot service
├── handlers/
│   └── webhook_handler.py  # Webhook handler
├── config/
│   └── settings.py         # Configuration
├── credentials/            # Google credentials (gitignored)
├── .env                    # Environment variables (gitignored)
└── requirements.txt        # Dependencies
```

## 🧪 Testing

```bash
# Test NLP processor
python -m pytest tests/test_nlp.py

# Test Google Sheets service
python -m pytest tests/test_sheets.py

# Test webhook (cần Zalo Bot setup)
python -m pytest tests/test_webhook.py
```

## 📦 Deployment

### Local Development với Ngrok

```bash
# Terminal 1: Chạy server
python app.py

# Terminal 2: Expose với ngrok
ngrok http 5000
# Copy URL và cấu hình trong Zalo Bot dashboard
```

### Production

Có thể deploy lên:
- Heroku
- Railway
- DigitalOcean
- AWS
- VPS

## ❓ Câu Hỏi Thường Gặp

**Q: Làm sao để lấy Google Sheet ID?**
A: Sheet ID nằm trong URL của Google Sheet:
`https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`

**Q: Làm sao để lấy Zalo Bot Secret Key?**
A: Vào Zalo Developer Console, chọn ứng dụng của bạn, vào phần "Webhook" để xem Secret Key.

**Q: Bot không hiểu tin nhắn của tôi?**
A: Kiểm tra format tin nhắn. Bot hiểu các format như "Chi 50k ăn trưa" hoặc "Thu 5 triệu lương".

**Q: Làm sao để thêm danh mục mới?**
A: Chỉnh sửa file `services/nlp_processor.py`, thêm từ khóa vào dictionary `CATEGORIES`.

## 🔐 Security

- ⚠️ **KHÔNG** commit file `.env` hoặc `credentials/` vào git
- Sử dụng environment variables trên production
- Verify signature từ Zalo để đảm bảo request hợp lệ

## 📄 License

MIT

## 🤝 Đóng Góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

## 📞 Liên Hệ

Nếu có câu hỏi hoặc vấn đề, vui lòng tạo issue trên repository.

