"""
Vercel serverless function wrapper pre Flask aplikáciu
Vercel Python runtime automaticky detekuje Flask aplikáciu ak exportujeme 'app'
"""
import sys
import os

# Pridaj root adresár do Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Nastav environment variables pre Vercel
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')

# Import Flask aplikácie
# Vercel automaticky rozpozná Flask aplikáciu ak exportujeme 'app'
from app import app

# Export pre Vercel
__all__ = ['app']
