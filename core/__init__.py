# App Package - Flask Application Factory
import os
import logging
from flask import Flask
from config import Config


def create_app(config_class=Config):
    """
    Flask Application Factory
    
    Vytvorí a nakonfiguruje Flask aplikáciu s blueprintmi.
    """
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    app.config.from_object(config_class)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Logging
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )
    
    # Inicializuj extensions
    from core.extensions import db, login_manager, init_redis
    
    db.init_app(app)
    login_manager.init_app(app)
    init_redis(app)
    
    # User loader
    from core.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registruj blueprinty
    from core.blueprints.carscraper import carscraper_bp
    app.register_blueprint(carscraper_bp)
    
    # Vytvor tabuľky
    with app.app_context():
        db.create_all()
    
    return app
