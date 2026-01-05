# CarScraper Blueprint - Routes
# Wrapper pre existujúce scrapers z scripts/

import sys
import os
from datetime import datetime
from functools import wraps
from flask import request, jsonify, render_template, current_app
from flask_login import login_required, current_user

# Pridaj parent pre import existujúcich scraperov
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from core.extensions import db, redis_client, logger
from core.models import CarDeal, ScrapeJob, Project
from core.blueprints.carscraper import carscraper_bp

# Import existujúceho unified scrapera
try:
    from scripts.car_scraper_unified import UnifiedCarScraper, scrape_all_sources
    SCRAPER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Unified scraper nie je dostupný: {e}")
    SCRAPER_AVAILABLE = False


# --- Rate Limiting Decorator ---
def check_scrape_limit(f):
    """Skontroluje denný limit scrapes podľa subscription plánu"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Vyžaduje prihlásenie'}), 401
        
        # Počet scrapes dnes
        today = datetime.utcnow().date()
        today_scrapes = ScrapeJob.query.filter(
            ScrapeJob.user_id == current_user.id,
            db.func.date(ScrapeJob.created_at) == today
        ).count()
        
        # Limit podľa plánu
        limit = current_user.scrape_limit
        
        if today_scrapes >= limit:
            return jsonify({
                'error': 'Denný limit scrapes dosiahnutý',
                'used': today_scrapes,
                'limit': limit,
                'plan': current_user.subscription_plan,
                'upgrade_url': '/subscribe'
            }), 429
        
        return f(*args, **kwargs)
    return decorated_function


# --- API Routes ---

@carscraper_bp.route('/api/scrape', methods=['POST'])
@login_required
@check_scrape_limit
def api_scrape():
    """
    Spustí scraping všetkých zdrojov
    
    Request JSON:
    {
        "brand": "skoda",
        "model": "octavia",
        "max_price": 15000,
        "max_km": 200000,
        "min_year": 2015,
        "mode": "parallel"  // alebo "fallback"
    }
    """
    if not SCRAPER_AVAILABLE:
        return jsonify({'error': 'Scraper nie je dostupný'}), 503
    
    data = request.get_json() or {}
    
    # Parametre
    search_query = f"{data.get('brand', '')} {data.get('model', '')}".strip() or "octavia"
    min_price = data.get('min_price', 1000)
    max_price = data.get('max_price', 30000)
    mode = data.get('mode', 'parallel')
    
    # Vytvor job záznam
    job = ScrapeJob(
        user_id=current_user.id,
        brand=data.get('brand'),
        model=data.get('model'),
        max_price=max_price,
        max_km=data.get('max_km'),
        min_year=data.get('min_year'),
        status='running',
        started_at=datetime.utcnow()
    )
    db.session.add(job)
    db.session.commit()
    
    try:
        # Spusti unified scraper
        scraper = UnifiedCarScraper()
        
        if mode == 'parallel':
            result = scraper.scrape_all_parallel(
                search_query=search_query,
                min_price=min_price,
                max_price=max_price
            )
        else:
            listings = scraper.scrape_with_fallback(
                search_query=search_query,
                min_price=min_price,
                max_price=max_price
            )
            result = {
                'success': len(listings) > 0,
                'listings': listings,
                'unique_listings': len(listings)
            }
        
        # Nájdi alebo vytvor CarScraper projekt
        project = Project.query.filter_by(
            user_id=current_user.id,
            name='CarScraper Pro'
        ).first()
        
        if not project:
            project = Project(
                name='CarScraper Pro',
                api_key=os.urandom(24).hex(),
                user_id=current_user.id,
                is_active=True
            )
            db.session.add(project)
            db.session.commit()
        
        # Ulož deals do databázy
        saved_count = 0
        for listing in result.get('listings', []):
            # Skip ak už existuje (podľa linku)
            existing = CarDeal.query.filter_by(link=listing.get('link')).first()
            if existing:
                continue
            
            deal = CarDeal(
                project_id=project.id,
                title=listing.get('title', 'Bez názvu'),
                price=listing.get('price', 0),
                km=listing.get('km'),
                year=listing.get('year'),
                location=listing.get('location'),
                source=listing.get('source', 'unknown'),
                link=listing.get('link'),
                image_url=listing.get('image_url'),
                description=listing.get('description')
            )
            db.session.add(deal)
            saved_count += 1
        
        # Update job
        job.status = 'completed'
        job.results_count = saved_count
        job.completed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'job_id': job.id,
            'total_found': result.get('unique_listings', 0),
            'saved': saved_count,
            'sources_used': result.get('sources_used', []),
            'sources_failed': result.get('sources_failed', [])
        })
    
    except Exception as e:
        logger.error(f"Scraping error: {e}", exc_info=True)
        job.status = 'failed'
        job.error_log = str(e)
        job.completed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'error': str(e)}), 500


@carscraper_bp.route('/api/deals', methods=['GET'])
@login_required
def api_deals():
    """Vráti zoznam deals pre aktuálneho používateľa"""
    
    # Nájdi CarScraper projekt
    project = Project.query.filter_by(
        user_id=current_user.id,
        name='CarScraper Pro'
    ).first()
    
    if not project:
        return jsonify({'deals': [], 'total': 0})
    
    # Parametre
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    verdict = request.args.get('verdict')  # SUPER_DEAL, GOOD_DEAL, OK, SKIP
    sort_by = request.args.get('sort', 'created_at')
    
    # Query
    query = CarDeal.query.filter_by(project_id=project.id)
    
    if verdict:
        query = query.filter_by(verdict=verdict)
    
    # Sorting
    if sort_by == 'price':
        query = query.order_by(CarDeal.price.asc())
    elif sort_by == 'score':
        query = query.order_by(CarDeal.score.desc())
    else:
        query = query.order_by(CarDeal.created_at.desc())
    
    # Paginácia
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'deals': [deal.to_dict() for deal in pagination.items],
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })


@carscraper_bp.route('/api/stats', methods=['GET'])
@login_required
def api_stats():
    """Štatistiky CarScraper pre aktuálneho používateľa"""
    
    project = Project.query.filter_by(
        user_id=current_user.id,
        name='CarScraper Pro'
    ).first()
    
    if not project:
        return jsonify({
            'total_deals': 0,
            'super_deals': 0,
            'good_deals': 0,
            'today_scrapes': 0,
            'scrape_limit': current_user.scrape_limit
        })
    
    # Štatistiky
    total_deals = CarDeal.query.filter_by(project_id=project.id).count()
    super_deals = CarDeal.query.filter_by(project_id=project.id, verdict='SUPER_DEAL').count()
    good_deals = CarDeal.query.filter_by(project_id=project.id, verdict='GOOD_DEAL').count()
    
    # Dnešné scrapes
    today = datetime.utcnow().date()
    today_scrapes = ScrapeJob.query.filter(
        ScrapeJob.user_id == current_user.id,
        db.func.date(ScrapeJob.created_at) == today
    ).count()
    
    return jsonify({
        'total_deals': total_deals,
        'super_deals': super_deals,
        'good_deals': good_deals,
        'today_scrapes': today_scrapes,
        'scrape_limit': current_user.scrape_limit,
        'subscription_plan': current_user.subscription_plan
    })


# --- Frontend Route ---

@carscraper_bp.route('/')
@login_required
def index():
    """CarScraper Pro dashboard - React frontend"""
    return render_template('carscraper/index.html')
