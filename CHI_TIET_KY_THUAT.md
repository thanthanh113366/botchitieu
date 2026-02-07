# Chi Tiết Kỹ Thuật - Bot Ghi Chép Thu Chi

## 🔍 Làm Rõ Các Điểm Mù Mờ

### 1. Xử Lý Ngôn Ngữ Tự Nhiên (NLP)

#### Pattern Matching với Regex

**Các pattern phổ biến:**
```python
# Ví dụ các câu người dùng có thể nhập:
"Chi 50k ăn trưa"
"Thu 5 triệu lương"
"Hôm nay chi 200k mua quần áo"
"Chi tiền ăn sáng 30 nghìn"
```

**Cách xử lý:**
1. **Nhận diện loại giao dịch:**
   - Từ khóa "Chi", "chi", "CHI" → Loại: Chi
   - Từ khóa "Thu", "thu", "THU" → Loại: Thu

2. **Trích xuất số tiền:**
   - "50k" → 50000
   - "5 triệu" → 5000000
   - "30 nghìn" → 30000
   - "1.5 triệu" → 1500000
   - "50000" → 50000

3. **Nhận diện danh mục:**
   - Từ khóa: "ăn", "ăn uống", "ăn trưa", "ăn sáng" → Danh mục: "Ăn uống"
   - Từ khóa: "lương", "tiền lương" → Danh mục: "Lương"
   - Từ khóa: "mua sắm", "quần áo" → Danh mục: "Mua sắm"

4. **Trích xuất ghi chú:**
   - Phần còn lại sau khi trích xuất số tiền và danh mục

#### Sử Dụng AI/LLM (Optional)

Nếu muốn xử lý các câu phức tạp hơn:
- "Hôm qua tôi đã chi 100k để mua đồ ăn cho bữa tối"
- "Nhận được tiền lương tháng này là 10 triệu đồng"

**Các lựa chọn:**
- **OpenAI GPT-3.5/4:** Chính xác, có chi phí (~$0.002/request)
- **Google Gemini:** Miễn phí với quota nhất định
- **Model Việt Nam:** PhoBERT, v.v. (cần setup phức tạp hơn)

**Prompt mẫu cho AI:**
```
Bạn là một hệ thống xử lý giao dịch tài chính. 
Hãy trích xuất thông tin từ câu sau và trả về JSON:
- loai: "Thu" hoặc "Chi"
- so_tien: số tiền (chỉ số, không có đơn vị)
- danh_muc: danh mục giao dịch
- ghi_chu: ghi chú (nếu có)

Câu: "{user_message}"
```

### 2. Google Sheets Integration

#### Setup Google Service Account

**Bước 1:** Tạo Google Cloud Project
1. Vào https://console.cloud.google.com
2. Tạo project mới
3. Enable "Google Sheets API"

**Bước 2:** Tạo Service Account
1. Vào "IAM & Admin" > "Service Accounts"
2. Tạo service account mới
3. Download JSON key file

**Bước 3:** Share Google Sheet
1. Mở Google Sheet
2. Click "Share"
3. Thêm email của Service Account (có trong JSON key)
4. Cấp quyền "Editor"

#### Cấu Trúc Sheet Đề Xuất

**Sheet 1: Giao dịch**
```
| A: Ngày giờ        | B: Loại | C: Số tiền | D: Danh mục | E: Ghi chú | F: User ID |
|--------------------|---------|------------|-------------|------------|------------|
| 2024-01-15 10:30:00| Chi     | 50000      | Ăn uống     | Ăn trưa    | user123    |
| 2024-01-15 14:00:00| Thu     | 5000000    | Lương       | Lương T1   | user123    |
```

**Sheet 2: Danh mục (nếu cần)**
```
| A: Tên danh mục | B: Loại | C: Mô tả |
|-----------------|---------|----------|
| Ăn uống         | Chi     |          |
| Lương           | Thu     |          |
| Mua sắm         | Chi     |          |
```

### 3. Zalo Bot Integration

#### Webhook Flow

```
1. User gửi tin nhắn trên Zalo
   ↓
2. Zalo gửi POST request đến webhook URL của bạn
   ↓
3. Server xác thực request (verify signature)
   ↓
4. Xử lý tin nhắn (NLP)
   ↓
5. Ghi vào Google Sheets
   ↓
6. Gửi phản hồi về Zalo
```

#### Zalo Bot API Endpoints

**Nhận webhook:**
- Method: POST
- URL: `https://your-server.com/webhook/zalo`
- Headers: Xác thực với secret key

**Gửi tin nhắn:**
- Method: POST
- URL: `https://openapi.zalo.me/v2.0/oa/message`
- Headers: `access_token` (từ API key)

#### Xác Thực Webhook

Zalo sẽ gửi kèm signature trong header để xác thực:
```python
# Pseudo code
signature = request.headers.get('X-Zalo-Signature')
expected_signature = hmac_sha256(secret_key, request_body)
if signature != expected_signature:
    return 401  # Unauthorized
```

### 4. Error Handling

#### Các Trường Hợp Lỗi

1. **Không hiểu được tin nhắn:**
   - Phản hồi: "Xin lỗi, tôi không hiểu. Vui lòng nhập theo format: 'Chi 50k ăn trưa' hoặc 'Thu 5 triệu lương'"

2. **Thiếu thông tin:**
   - Phản hồi: "Thiếu thông tin. Vui lòng nhập đầy đủ: loại (Thu/Chi), số tiền, và mô tả"

3. **Lỗi kết nối Google Sheets:**
   - Log lỗi
   - Phản hồi: "Có lỗi xảy ra, vui lòng thử lại sau"

4. **Lỗi kết nối Zalo API:**
   - Retry mechanism
   - Log lỗi

### 5. Security

#### Bảo Mật API Keys

- **KHÔNG** commit API keys vào git
- Sử dụng `.env` file và `.gitignore`
- Sử dụng environment variables trên production

#### Validate Input

- Kiểm tra format tin nhắn
- Sanitize input để tránh injection
- Giới hạn độ dài tin nhắn

### 6. Performance & Scalability

#### Caching

- Cache danh sách danh mục (nếu có)
- Cache Google Sheets connection

#### Rate Limiting

- Giới hạn số request từ mỗi user
- Tránh spam

#### Async Processing

- Xử lý webhook async (nếu cần)
- Queue cho các request nặng

## 📊 Flow Diagram

```
User (Zalo) → Zalo Bot → Webhook → Server
                                      ↓
                              NLP Processor
                                      ↓
                              Google Sheets API
                                      ↓
                              Response → Zalo Bot → User
```

## 🔧 Dependencies

### Python
```txt
flask==2.3.0          # Web framework
gspread==5.12.0       # Google Sheets API
google-auth==2.23.0   # Google authentication
python-dotenv==1.0.0  # Environment variables
requests==2.31.0      # HTTP requests
openai==1.3.0         # (Optional) OpenAI API
```

### Node.js
```json
{
  "express": "^4.18.0",
  "googleapis": "^126.0.0",
  "dotenv": "^16.3.0",
  "axios": "^1.6.0"
}
```

## 🧪 Testing Strategy

### Unit Tests
- Test NLP processor với các câu mẫu
- Test Google Sheets service (mock)
- Test Zalo Bot service (mock)

### Integration Tests
- Test end-to-end flow
- Test với Google Sheets thật (test sheet)
- Test với Zalo Bot (test account)

### Manual Testing
- Test với các format tin nhắn khác nhau
- Test error cases
- Test với nhiều user

