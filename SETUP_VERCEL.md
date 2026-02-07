# Hướng Dẫn Deploy lên Vercel

## ⚠️ Lưu Ý Quan Trọng về Google Credentials

Vercel serverless functions không thể lưu file trực tiếp. Có 3 cách để xử lý Google Service Account JSON:

### Option 1: Base64 trong Environment Variable (Đơn giản nhất)

1. **Encode file JSON thành base64:**
```bash
# Windows (PowerShell)
[Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials/service_account.json"))

# Mac/Linux
base64 -i credentials/service_account.json
```

2. **Thêm vào Vercel Environment Variables:**
   - Vào Vercel Dashboard > Project > Settings > Environment Variables
   - Thêm: `GOOGLE_CREDENTIALS_BASE64` = (paste base64 string)

3. **Sửa code để decode:**
   - Cần sửa `services/google_sheets.py` để decode base64 và tạo file tạm

### Option 2: Sử dụng Vercel Blob Storage

1. Upload file JSON lên Vercel Blob
2. Lấy URL và lưu vào environment variable
3. Download file trong code khi cần

### Option 3: Google Application Default Credentials (Khuyến nghị cho production)

1. Setup service account trên Google Cloud
2. Sử dụng environment variable `GOOGLE_APPLICATION_CREDENTIALS_JSON` (JSON content)
3. Parse JSON trong code

## 📋 Các Bước Deploy

### 1. Cài đặt Vercel CLI

```bash
npm i -g vercel
```

### 2. Login

```bash
vercel login
```

### 3. Setup Environment Variables

Tạo file `.env.local` (không commit) hoặc set trên Vercel Dashboard:

```env
ZALO_ACCESS_TOKEN=your_token
ZALO_SECRET_KEY=your_secret
ZALO_OA_ID=your_oa_id
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_CREDENTIALS_BASE64=your_base64_encoded_json
```

### 4. Deploy

```bash
# Deploy lần đầu (preview)
vercel

# Deploy production
vercel --prod
```

### 5. Lấy Webhook URL

Sau khi deploy, bạn sẽ có URL dạng:
```
https://your-project.vercel.app/api/webhook
```

Copy URL này và cấu hình trong Zalo Bot dashboard.

## 🔧 Sửa Code để Support Base64 Credentials

Cần sửa `services/google_sheets.py` để hỗ trợ decode base64:

```python
import base64
import tempfile
import os

# Trong __init__:
if os.getenv('GOOGLE_CREDENTIALS_BASE64'):
    # Decode base64
    creds_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
    creds_json = base64.b64decode(creds_base64).decode('utf-8')
    
    # Tạo file tạm
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    temp_file.write(creds_json)
    temp_file.close()
    
    credentials_path = temp_file.name
else:
    credentials_path = GOOGLE_CREDENTIALS_PATH
```

## 🧪 Test Local trước khi Deploy

```bash
# Chạy local với Vercel dev
vercel dev
```

Server sẽ chạy tại `http://localhost:3000`

## 📝 Checklist trước khi Deploy

- [ ] Đã setup Google Sheets và có Sheet ID
- [ ] Đã tạo Service Account và có JSON key
- [ ] Đã encode JSON thành base64
- [ ] Đã thêm tất cả environment variables vào Vercel
- [ ] Đã test local với `vercel dev`
- [ ] Đã cấu hình webhook URL trong Zalo Bot dashboard

