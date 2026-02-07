"""
Vercel entry point - Import app từ root
Vercel sẽ tự động detect FastAPI từ biến app
"""
import sys
import os

# Thêm root path để import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app từ app.py
from app import app

# Vercel sẽ tự động detect biến app

