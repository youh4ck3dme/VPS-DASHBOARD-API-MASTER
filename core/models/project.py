# Project Model
from datetime import datetime
from core.extensions import db


class Project(db.Model):
    """Projekt model - každý projekt má unikátny API kľúč"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    api_key = db.Column(db.String(120), unique=True, nullable=False)
    script_path = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='project', lazy=True, cascade='all, delete-orphan')
    automation = db.relationship('Automation', backref='project', lazy=True, cascade='all, delete-orphan')
    ai_requests = db.relationship('AIRequest', backref='project', lazy=True, cascade='all, delete-orphan')
    car_deals = db.relationship('CarDeal', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.name}>'


class Payment(db.Model):
    """Platby - Stripe, SumUp, CoinGate"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    status = db.Column(db.String(20), default='pending')
    gateway = db.Column(db.String(20), nullable=False)
    transaction_id = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Automation(db.Model):
    """Automatizácie - Cron joby"""
    __tablename__ = 'automation'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    script_name = db.Column(db.String(120), nullable=False)
    schedule = db.Column(db.String(50), nullable=False)
    last_run = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AIRequest(db.Model):
    """AI požiadavky - OpenAI integrácia"""
    __tablename__ = 'ai_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
