import os
from dotenv import load_dotenv

load_dotenv()  # Načítanie premenných z `.env`

# Získaj absolútnu cestu k projektu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'tvoje_tajne_heslo_123')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # UPLOAD_FOLDER - dynamicky nastavený podľa prostredia
    # Pre produkciu: /var/www/api_dashboard/scripts
    # Pre lokálne: scripts/ v projekte
    _default_upload = os.path.join(BASE_DIR, 'scripts')
    _prod_upload = '/var/www/api_dashboard/scripts'
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 
                              _prod_upload if os.path.exists(_prod_upload) else _default_upload)
    
    # Vytvor adresár ak neexistuje
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    SUMUP_API_KEY = os.getenv('SUMUP_API_KEY')
    COINGATE_API_KEY = os.getenv('COINGATE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Flask konfigurácia
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 6002))
    
    # Proxy konfigurácia pre CarScraper
    PROXY_LIST = os.getenv('PROXY_LIST', '')  # Čiarkou oddelený zoznam proxy
    PROXY_FILE = os.getenv('PROXY_FILE', 'proxies.txt')  # Súbor s proxy (jeden na riadok)
    USE_PROXY = os.getenv('USE_PROXY', 'true').lower() == 'true'  # Zapnúť/vypnúť proxy
