# User Model
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from core.extensions import db, logger


class User(UserMixin, db.Model):
    """Používateľský model s autentifikáciou a subscription podporou"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # CarScraper Pro subscription
    subscription_plan = db.Column(db.String(20), default='free')  # free, hobby, pro
    subscription_id = db.Column(db.String(100))  # Stripe subscription ID
    telegram_chat_id = db.Column(db.String(50))  # Pre notifikácie
    
    # Relationships
    projects = db.relationship('Project', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hashuje heslo pomocou werkzeug (pbkdf2 pre Python 3.9 kompatibilitu)"""
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Overí heslo"""
        try:
            return check_password_hash(self.password, password)
        except AttributeError as e:
            if 'scrypt' in str(e).lower():
                logger.warning(f'Scrypt hash detected for user {self.id}, cannot verify.')
                return False
            raise
        except Exception as e:
            logger.error(f'Error checking password for user {self.id}: {str(e)}')
            raise
    
    @property
    def scrape_limit(self):
        """Vráti denný limit scrapes podľa plánu"""
        limits = {
            'free': 5,
            'hobby': 20,
            'pro': 100
        }
        return limits.get(self.subscription_plan, 5)
    
    def __repr__(self):
        return f'<User {self.username}>'
