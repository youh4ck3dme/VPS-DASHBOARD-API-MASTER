# CarDeal Model - CarScraper Pro
from datetime import datetime
from core.extensions import db


class CarDeal(db.Model):
    """Model pre nájdené ponuky áut z autobazárov"""
    __tablename__ = 'car_deals'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Základné info z inzerátu
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    km = db.Column(db.Integer)  # Najazdené kilometre
    year = db.Column(db.Integer)  # Rok výroby
    location = db.Column(db.String(100))
    
    # Štruktúrované dáta
    brand = db.Column(db.String(50))      # Skoda, VW, BMW...
    model = db.Column(db.String(50))      # Octavia, Golf...
    generation = db.Column(db.String(50)) # III, IV...
    region = db.Column(db.String(50))     # Bratislavský, Košický...
    fuel_type = db.Column(db.String(20))  # Diesel, Benzín...
    transmission = db.Column(db.String(20)) # Manuál, Automat...
    
    # AI scoring
    market_value = db.Column(db.Numeric(10, 2))  # Odhadovaná trhová cena
    profit = db.Column(db.Numeric(10, 2))  # Potenciálny profit
    score = db.Column(db.Numeric(5, 2))  # Z-score (-3 až +3)
    verdict = db.Column(db.String(20))  # SUPER_DEAL, GOOD_DEAL, OK, SKIP
    risk_level = db.Column(db.String(20))  # Nízke, Stredné, Vysoké
    reason = db.Column(db.Text)
    
    # Zdroj a link
    source = db.Column(db.String(100))  # bazos.sk, autobazar.eu, atď.
    link = db.Column(db.String(500))
    
    # Detaily
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    ai_analysis = db.Column(db.Text)  # JSON s AI analýzou
    
    # Stav
    is_viewed = db.Column(db.Boolean, default=False)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Serializácia pre API"""
        return {
            'id': self.id,
            'title': self.title,
            'price': float(self.price) if self.price else None,
            'km': self.km,
            'year': self.year,
            'location': self.location,
            'market_value': float(self.market_value) if self.market_value else None,
            'profit': float(self.profit) if self.profit else None,
            'score': float(self.score) if self.score else None,
            'verdict': self.verdict,
            'risk_level': self.risk_level,
            'source': self.source,
            'link': self.link,
            'image_url': self.image_url,
            'brand': self.brand,
            'model': self.model,
            'generation': self.generation,
            'region': self.region,
            'fuel_type': self.fuel_type,
            'transmission': self.transmission,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<CarDeal {self.title} @ {self.price}€>'


class ScrapeJob(db.Model):
    """Scraping job - sledovanie stavu scrape úloh"""
    __tablename__ = 'scrape_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Parametre vyhľadávania
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    max_price = db.Column(db.Integer)
    max_km = db.Column(db.Integer)
    min_year = db.Column(db.Integer)
    
    # Stav
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    results_count = db.Column(db.Integer, default=0)
    error_log = db.Column(db.Text)
    
    # Timestamp
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='scrape_jobs')
    
    def __repr__(self):
        return f'<ScrapeJob {self.brand} {self.model} - {self.status}>'
