# CarScraper Blueprint Package

from flask import Blueprint

# Vytvor blueprint tu, importuj routes neskôr
carscraper_bp = Blueprint(
    'carscraper', 
    __name__, 
    url_prefix='/carscraper',
    template_folder='templates'
)

# Import routes až po vytvorení blueprint (circular import fix)
from core.blueprints.carscraper import routes
