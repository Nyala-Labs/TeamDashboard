"""
Vercel Serverless Function: proxies all /api/* requests to the FastAPI backend.
Uses Mangum to adapt the Vercel/Lambda request format to ASGI.
"""
import os
import sys

# Add backend to path so we can import app (monorepo: backend is sibling to api)
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(backend_path))

from mangum import Mangum
from app.main import app

handler = Mangum(app)
