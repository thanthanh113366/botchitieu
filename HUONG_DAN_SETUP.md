# Hướng Dẫn Setup Bot Ghi Chép Thu Chi

## 📋 Bước 1: Setup Google Sheets

### 1.1. Tạo Google Cloud Project

1. Vào https://console.cloud.google.com
2. Tạo project mới (hoặc chọn project có sẵn)
3. Đặt tên project (ví dụ: "Bot Chi Tieu")

### 1.2. Enable Google Sheets API

1. Vào **APIs & Services** > **Library**
2. Tìm "Google Sheets API"
3. Click **Enable**

### 1.3. Tạo Service Account

1. Vào **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Điền thông tin:
   - **Service account name**: `bot-chi-tieu`
   - **Service account ID**: tự động tạo
4. Click **Create and Continue**
5. Bỏ qua phần **Grant this service account access to project** (không cần)
6. Click **Done**

### 1.4. Tạo và Download JSON Key

1. Click vào service account vừa tạo
2. Vào tab **Keys**
3. Click **Add Key** > **Create new key**
4. Chọn **JSON**
5. Click **Create** - File JSON sẽ tự động download
6. **Lưu file này** vào thư mục `credentials/` với tên `service_account.json`

### 1.5. Tạo Google Sheet

1. Vào https://sheets.google.com
2. Tạo Sheet mới
3. Đặt tên (ví dụ: "Bot Chi Tieu")
4. **Lấy Sheet ID từ URL:**
   ```
   https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
   ```
   Copy phần `SHEET_ID`

### 1.6. Share Sheet với Service Account

1. Trong Google Sheet, click **Share** (góc trên bên phải)
2. Lấy email của Service Account từ file JSON (trường `client_email`)
3. Paste email vào ô **Add people and groups**
4. Chọn quyền **Editor**
5. Click **Send** (không cần gửi email thật, chỉ cần share)

## 📋 Bước 2: Setup Zalo Bot

### 2.1. Lấy API Keys

1. Vào Zalo Developer Console: https://developers.zalo.me/
2. Chọn ứng dụng của bạn
3. Vào **Cấu hình** > **Thông tin ứng dụng**
4. Copy các thông tin:
   - **Access Token** (hoặc tạo mới)
   - **Secret Key** (trong phần Webhook)
   - **OA ID**

### 2.2. Cấu hình Webhook

1. Vào **Cấu hình** > **Webhook**
2. Nhập Webhook URL:
   - **Local test**: Sử dụng ngrok (xem bước 3)
   - **Production**: URL từ Vercel (sau khi deploy)
3. Lưu **Secret Key** để verify requests

## 📋 Bước 3: Setup Local Development

### 3.1. Cài đặt Dependencies với Conda

```bash
# Tạo conda environment
conda create -n botchitieu python=3.9 -y

# Activate environment
conda activate botchitieu

# Cài đặt packages
pip install -r requirements.txt
```

**Lưu ý:** Nếu bạn dùng venv thay vì conda:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3.2. Cấu hình Environment Variables

1. Copy file `.env.example` thành `.env`:
```bash
cp .env.example .env
```

2. Chỉnh sửa file `.env`:
```env
ZALO_ACCESS_TOKEN=your_actual_token
ZALO_SECRET_KEY=your_actual_secret
ZALO_OA_ID=your_actual_oa_id
GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json
GOOGLE_SHEET_ID=your_actual_sheet_id
```

3. Đảm bảo file `credentials/service_account.json` đã có

### 3.3. Chạy Local Server

```bash
python app.py
```

Server sẽ chạy tại `http://localhost:5000`

### 3.4. Test với Ngrok

1. Cài đặt ngrok: https://ngrok.com/download
2. Chạy ngrok:
```bash
ngrok http 5000
```
3. Copy URL (ví dụ: `https://abc123.ngrok.io`)
4. Cấu hình webhook trong Zalo Bot dashboard:
   - Webhook URL: `https://abc123.ngrok.io/webhook`

## 📋 Bước 4: Deploy lên Vercel

### 4.1. Cài đặt Vercel CLI

```bash
npm i -g vercel
```

### 4.2. Login Vercel

```bash
vercel login
```

### 4.3. Deploy

```bash
# Deploy lần đầu
vercel

# Deploy production
vercel --prod
```

### 4.4. Cấu hình Environment Variables trên Vercel

1. Vào Vercel Dashboard: https://vercel.com/dashboard
2. Chọn project
3. Vào **Settings** > **Environment Variables**
4. Thêm các biến:
   - `ZALO_ACCESS_TOKEN`
   - `ZALO_SECRET_KEY`
   - `ZALO_OA_ID`
   - `GOOGLE_SHEET_ID`
   - `GOOGLE_CREDENTIALS_PATH` (hoặc upload file JSON)

### 4.5. Upload Google Credentials

**Option 1: Base64 trong Environment Variable**
```bash
# Encode file JSON thành base64
base64 -i credentials/service_account.json

# Thêm vào Vercel env: GOOGLE_CREDENTIALS_BASE64
# Trong code, decode và tạo file tạm
```

**Option 2: Sử dụng Vercel Blob hoặc Secret Manager**
- Upload file JSON lên Vercel Blob
- Hoặc sử dụng Google Secret Manager

**Option 3: Sử dụng Google Application Default Credentials**
- Setup trên Vercel với service account

### 4.6. Cập nhật Webhook URL

1. Lấy URL từ Vercel (sẽ có dạng: `https://your-project.vercel.app/api/webhook`)
2. Cập nhật trong Zalo Bot dashboard

## 📋 Bước 5: Test

### 5.1. Test Ghi Chép

Gửi tin nhắn trên Zalo:
- `Chi 50k ăn trưa`
- `Thu 5 triệu lương`
- `Chi 200k mua quần áo`

### 5.2. Test Thống Kê

Gửi tin nhắn:
- `thống kê`
- `thống kê tháng 1`
- `thống kê năm 2024`

### 5.3. Kiểm tra Google Sheets

Mở Google Sheet và kiểm tra:
- Sheet "Giao dịch" có dữ liệu mới
- Sheet "Danh mục" có danh sách danh mục

## 🔧 Troubleshooting

### Lỗi: "Credentials file not found"
- Kiểm tra đường dẫn trong `.env`
- Đảm bảo file `service_account.json` tồn tại

### Lỗi: "Invalid signature"
- Kiểm tra `ZALO_SECRET_KEY` trong `.env`
- Đảm bảo secret key đúng với Zalo Bot dashboard

### Lỗi: "Sheet not found"
- Kiểm tra `GOOGLE_SHEET_ID` trong `.env`
- Đảm bảo đã share sheet với service account email

### Lỗi: "Permission denied"
- Kiểm tra quyền của service account (phải là Editor)
- Kiểm tra Google Sheets API đã được enable

## 📝 Lưu Ý

- **KHÔNG** commit file `.env` hoặc `credentials/` vào git
- File `.gitignore` đã được cấu hình để bỏ qua các file nhạy cảm
- Trên Vercel, cần setup environment variables và credentials riêng
- Webhook URL trên Vercel sẽ là: `https://your-project.vercel.app/api/webhook`

