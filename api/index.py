"""
Vercel entry point - Import app từ root
Vercel sẽ tự động detect FastAPI từ biến app
"""
import sys
import os

# Thêm root path để import
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Import app từ app.py
# Wrap trong try-except để handle lỗi import
try:
    # Import từ app.py
    import app as app_module
    
    # Lấy app object
    app = getattr(app_module, 'app', None)
    
    # Đảm bảo app không None và là FastAPI instance
    if app is None:
        raise ValueError("app is None in app.py")
    
    # Kiểm tra app có phải FastAPI không
    from fastapi import FastAPI
    if not isinstance(app, FastAPI):
        raise ValueError(f"app is not FastAPI instance, got {type(app)}")
        
except Exception as e:
    # Nếu import lỗi, log và tạo app fallback
    import traceback
    error_msg = f"Error importing app from app.py: {e}\n{traceback.format_exc()}"
    print(error_msg)
    
    # Tạo app fallback
    from fastapi import FastAPI
    app = FastAPI(title="Bot Chi Tieu", description="Zalo Bot for expense tracking")
    
    @app.get("/")
    async def root():
        return {
            "status": "error",
            "message": "Could not import main app",
            "error": str(e)
        }
    
    @app.get("/health")
    async def health():
        return {"status": "error", "message": "Import failed"}

# Vercel sẽ tự động detect biến app

