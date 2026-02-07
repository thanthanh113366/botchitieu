# Kế Hoạch Triển Khai Ứng Dụng Ghi Chép Thu Chi với Zalo Bot

## 📋 Tổng Quan Dự Án

Ứng dụng cho phép người dùng ghi chép thu chi thông qua Zalo Bot bằng ngôn ngữ tự nhiên, dữ liệu được lưu trữ trên Google Sheets.

## 🎯 Các Điểm Cần Làm Rõ

### 1. **Cấu Trúc Dữ Liệu Google Sheets**

**Câu hỏi cần trả lời:**
- Bạn muốn lưu những thông tin gì cho mỗi giao dịch?
- Có cần phân loại danh mục không? (ăn uống, mua sắm, lương, v.v.)
- Có cần ghi chú/ghi chú không?

**Đề xuất cấu trúc:**
```
| Ngày giờ | Loại | Số tiền | Danh mục | Ghi chú | Người gửi |
|----------|------|---------|----------|---------|-----------|
| 2024-01-15 10:30 | Chi | 50000 | Ăn uống | Ăn trưa | User123 |
| 2024-01-15 14:00 | Thu | 5000000 | Lương | Lương tháng 1 | User123 |
```

### 2. **Format Ngôn Ngữ Tự Nhiên**

**Ví dụ các câu lệnh người dùng có thể nhập:**
- "Chi 50k ăn trưa"
- "Thu 5 triệu lương tháng 1"
- "Hôm nay chi 200k mua quần áo"
- "Chi tiền ăn sáng 30 nghìn"
- "Thu tiền lương 10 triệu"

**Cần xử lý:**
- Nhận diện loại giao dịch (Thu/Chi)
- Trích xuất số tiền (50k = 50000, 5 triệu = 5000000)
- Nhận diện danh mục (ăn uống, lương, mua sắm, v.v.)
- Trích xuất ghi chú

### 3. **Công Nghệ Xử Lý NLP**

**Các lựa chọn:**
- **Option 1:** Sử dụng thư viện NLP đơn giản (regex + keyword matching)
  - Ưu điểm: Nhẹ, nhanh, không cần internet
  - Nhược điểm: Độ chính xác thấp, khó mở rộng
  
- **Option 2:** Sử dụng AI/LLM (OpenAI GPT, Google Gemini, hoặc model Việt Nam)
  - Ưu điểm: Độ chính xác cao, xử lý linh hoạt
  - Nhược điểm: Cần API key, có chi phí, cần internet
  
- **Option 3:** Hybrid (regex cho pattern đơn giản + AI cho câu phức tạp)
  - Ưu điểm: Cân bằng giữa chi phí và độ chính xác
  - Nhược điểm: Phức tạp hơn

**Đề xuất:** Bắt đầu với Option 3 (Hybrid) - dùng regex cho các pattern phổ biến, dùng AI cho các câu phức tạp.

### 4. **Kiến Trúc Hệ Thống**

```
┌─────────────┐
│  Zalo Bot   │
│  (User)     │
└──────┬──────┘
       │ Webhook
       ▼
┌─────────────────────┐
│  Backend Server     │
│  (Python/Node.js)   │
│  - Nhận webhook     │
│  - Xử lý NLP        │
│  - Ghi vào Sheets   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Google Sheets API  │
│  (Database)         │
└─────────────────────┘
```

**Các thành phần:**
1. **Zalo Bot Webhook Handler:** Nhận tin nhắn từ Zalo
2. **NLP Processor:** Xử lý ngôn ngữ tự nhiên
3. **Google Sheets Service:** Ghi dữ liệu vào Sheets
4. **Response Handler:** Trả lời người dùng

### 5. **Công Nghệ Stack Đề Xuất**

**Backend:**
- **Python** (đề xuất) - dễ xử lý NLP, có nhiều thư viện
  - Flask/FastAPI cho webhook server
  - `gspread` hoặc `google-api-python-client` cho Google Sheets
  - `re` (regex) cho pattern matching
  - `openai` hoặc `google-generativeai` cho AI (nếu dùng)
  
- **Node.js** (alternative)
  - Express.js cho webhook server
  - `googleapis` cho Google Sheets
  - `natural` hoặc `compromise` cho NLP cơ bản

**Deployment:**
- **Local development:** Ngrok để expose local server
- **Production:** 
  - Heroku
  - Railway
  - VPS (DigitalOcean, AWS, v.v.)
  - Serverless (Vercel, AWS Lambda)

### 6. **Tích Hợp Zalo Bot**

**Cần có:**
- ✅ Zalo Bot API Key (đã có)
- ⚠️ Zalo Bot Webhook URL (cần setup)
- ⚠️ Zalo Bot Secret Key (cần kiểm tra)

**Quy trình:**
1. Tạo webhook endpoint để nhận tin nhắn từ Zalo
2. Xác thực request từ Zalo (verify signature)
3. Xử lý tin nhắn
4. Gửi phản hồi về Zalo

### 7. **Tích Hợp Google Sheets**

**Cần có:**
- ⚠️ Google Service Account (hoặc OAuth)
- ⚠️ Google Sheets ID
- ⚠️ Service Account JSON key file

**Quy trình:**
1. Tạo Google Cloud Project
2. Enable Google Sheets API
3. Tạo Service Account và download JSON key
4. Share Google Sheet với Service Account email
5. Sử dụng API để đọc/ghi dữ liệu

## 📝 Kế Hoạch Triển Khai Chi Tiết

### Phase 1: Setup & Configuration (1-2 ngày)

#### 1.1. Setup Google Sheets
- [ ] Tạo Google Cloud Project
- [ ] Enable Google Sheets API
- [ ] Tạo Service Account
- [ ] Download Service Account JSON key
- [ ] Tạo Google Sheet với cấu trúc cột
- [ ] Share Sheet với Service Account email

#### 1.2. Setup Zalo Bot
- [ ] Kiểm tra Zalo Bot API Key
- [ ] Lấy Zalo Bot Secret Key (nếu có)
- [ ] Xác định webhook URL (sẽ setup sau khi có server)

#### 1.3. Setup Development Environment
- [ ] Tạo virtual environment (Python) hoặc npm project (Node.js)
- [ ] Cài đặt dependencies
- [ ] Tạo file `.env` cho các API keys

### Phase 2: Core Development (3-5 ngày)

#### 2.1. Google Sheets Service
- [ ] Tạo class/service để kết nối Google Sheets
- [ ] Implement hàm đọc dữ liệu
- [ ] Implement hàm ghi dữ liệu
- [ ] Test kết nối và ghi dữ liệu

#### 2.2. NLP Processor
- [ ] Tạo module xử lý ngôn ngữ tự nhiên
- [ ] Implement regex patterns cho các format phổ biến
- [ ] Implement hàm trích xuất số tiền (k, nghìn, triệu, v.v.)
- [ ] Implement hàm nhận diện loại giao dịch (Thu/Chi)
- [ ] Implement hàm nhận diện danh mục
- [ ] (Optional) Tích hợp AI cho câu phức tạp

#### 2.3. Zalo Bot Webhook Handler
- [ ] Tạo webhook endpoint
- [ ] Implement xác thực request từ Zalo
- [ ] Implement xử lý tin nhắn đến
- [ ] Implement gửi phản hồi về Zalo
- [ ] Test với Zalo Bot

### Phase 3: Integration & Testing (2-3 ngày)

#### 3.1. Tích Hợp Các Module
- [ ] Kết nối webhook handler với NLP processor
- [ ] Kết nối NLP processor với Google Sheets service
- [ ] Implement flow hoàn chỉnh: Nhận tin nhắn → Xử lý → Ghi Sheets → Phản hồi

#### 3.2. Testing
- [ ] Test các format tin nhắn khác nhau
- [ ] Test xử lý lỗi
- [ ] Test với nhiều người dùng (nếu cần)
- [ ] Test performance

### Phase 4: Deployment (1-2 ngày)

#### 4.1. Local Testing với Ngrok
- [ ] Setup ngrok để expose local server
- [ ] Cấu hình Zalo Bot webhook URL
- [ ] Test end-to-end

#### 4.2. Production Deployment
- [ ] Chọn hosting platform
- [ ] Deploy application
- [ ] Cấu hình environment variables
- [ ] Update Zalo Bot webhook URL
- [ ] Test production

### Phase 5: Enhancement (Ongoing)

- [ ] Thêm tính năng xem lịch sử giao dịch
- [ ] Thêm tính năng thống kê (tổng thu, tổng chi, v.v.)
- [ ] Thêm tính năng sửa/xóa giao dịch
- [ ] Cải thiện độ chính xác NLP
- [ ] Thêm validation và error handling tốt hơn

## 🔧 Cấu Trúc Project Đề Xuất

```
BotChiTiu/
├── .env                    # Environment variables (API keys)
├── .gitignore
├── requirements.txt        # Python dependencies
├── README.md
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration settings
├── services/
│   ├── __init__.py
│   ├── google_sheets.py    # Google Sheets service
│   ├── zalo_bot.py         # Zalo Bot service
│   └── nlp_processor.py    # NLP processing
├── handlers/
│   ├── __init__.py
│   └── webhook_handler.py  # Webhook handler
├── utils/
│   ├── __init__.py
│   └── helpers.py          # Helper functions
├── app.py                  # Main application (Flask/FastAPI)
└── credentials/
    └── service_account.json # Google Service Account key (gitignored)
```

## ❓ Câu Hỏi Cần Trả Lời

1. **Bạn muốn xử lý ngôn ngữ tự nhiên bằng cách nào?**
   - Regex đơn giản (nhanh, miễn phí)
   - AI/LLM (chính xác hơn, có chi phí)
   - Hybrid (cân bằng)

2. **Bạn muốn lưu những thông tin gì trong Google Sheets?**
   - Các cột cụ thể?
   - Có cần phân loại danh mục không?

3. **Bạn muốn deploy ở đâu?**
   - Local với ngrok (development)
   - Cloud platform (production)

4. **Bạn có muốn thêm tính năng gì khác không?**
   - Xem lịch sử
   - Thống kê
   - Sửa/xóa giao dịch

5. **Bạn có Zalo Bot Secret Key không?** (cần cho xác thực webhook)

## 🚀 Bước Tiếp Theo

Sau khi bạn trả lời các câu hỏi trên, tôi sẽ:
1. Tạo cấu trúc project
2. Implement các module cơ bản
3. Setup Google Sheets integration
4. Setup Zalo Bot webhook
5. Implement NLP processor
6. Tích hợp tất cả lại với nhau

