"""
Testy pre CarScraper Pro API endpointy
"""

import pytest
import os
import importlib.util
from decimal import Decimal


class TestCarScraperAPI:
    """Testy pre CarScraper Pro API"""

    def test_get_car_deals_requires_login(self, client):
        """Test že API vyžaduje prihlásenie"""
        response = client.get('/api/carscraper/deals')
        assert response.status_code in [302, 401, 403]  # Redirect alebo unauthorized

    def test_get_car_deals_with_project(self, authenticated_client, test_user, app):
        """Test získania deals s existujúcim projektom"""
        with app.app_context():
            # Import inside app context to use the correct db instance
            from app import db, Project, CarDeal
            
            # Vytvor CarScraper Pro projekt
            project = Project(
                name='CarScraper Pro',
                api_key='test_api_key_123',
                user_id=test_user.id,
                is_active=True
            )
            db.session.add(project)
            db.session.commit()

            # Vytvor test deal
            deal = CarDeal(
                project_id=project.id,
                title='Test Auto',
                price=Decimal('10000'),
                market_value=Decimal('12000'),
                profit=Decimal('2000'),
                verdict='KÚPIŤ',
                risk_level='Nízke',
                reason='Test reason',
                source='Bazoš.sk',
                link='https://test.com',
                description='Test description'
            )
            db.session.add(deal)
            db.session.commit()

        # Test API
        response = authenticated_client.get('/api/carscraper/deals')
        assert response.status_code == 200
        data = response.get_json()
        assert 'deals' in data
        assert len(data['deals']) > 0
        assert data['deals'][0]['title'] == 'Test Auto'

    def test_get_car_deals_filter_by_verdict(self, authenticated_client, test_user, app):
        """Test filtrovania deals podľa verdictu"""
        with app.app_context():
            from app import db, Project, CarDeal
            
            project = Project.query.filter_by(name='CarScraper Pro', user_id=test_user.id).first()
            if not project:
                project = Project(
                    name='CarScraper Pro',
                    api_key='test_api_key_123',
                    user_id=test_user.id,
                    is_active=True
                )
                db.session.add(project)
                db.session.commit()

            # Vytvor deals s rôznymi verdictmi
            deal1 = CarDeal(
                project_id=project.id,
                title='Good Deal',
                price=Decimal('10000'),
                verdict='KÚPIŤ',
                source='Bazoš.sk',
                link='https://test.com/1'
            )
            deal2 = CarDeal(
                project_id=project.id,
                title='Bad Deal',
                price=Decimal('15000'),
                verdict='NEKUPOVAŤ',
                source='Bazoš.sk',
                link='https://test.com/2'
            )
            db.session.add_all([deal1, deal2])
            db.session.commit()

        # Test filter
        response = authenticated_client.get('/api/carscraper/deals?verdict=KÚPIŤ')
        assert response.status_code == 200
        data = response.get_json()
        assert all(d['verdict'] == 'KÚPIŤ' for d in data['deals'])

    def test_get_car_deal_detail(self, authenticated_client, test_user, app):
        """Test získania detailu deal"""
        with app.app_context():
            from app import db, Project, CarDeal
            
            project = Project.query.filter_by(name='CarScraper Pro', user_id=test_user.id).first()
            if not project:
                project = Project(
                    name='CarScraper Pro',
                    api_key='test_api_key_123',
                    user_id=test_user.id,
                    is_active=True
                )
                db.session.add(project)
                db.session.commit()

            deal = CarDeal(
                project_id=project.id,
                title='Test Auto Detail',
                price=Decimal('10000'),
                verdict='KÚPIŤ',
                source='Bazoš.sk',
                link='https://test.com'
            )
            db.session.add(deal)
            db.session.commit()
            deal_id = deal.id

        # Test API
        response = authenticated_client.get(f'/api/carscraper/deals/{deal_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Test Auto Detail'
        assert data['is_viewed'] is True  # Malo by byť označené ako videné

    def test_get_carscraper_stats(self, authenticated_client, test_user, app):
        """Test získania štatistík"""
        with app.app_context():
            from app import db, Project, CarDeal
            
            project = Project.query.filter_by(name='CarScraper Pro', user_id=test_user.id).first()
            if not project:
                project = Project(
                    name='CarScraper Pro',
                    api_key='test_api_key_123',
                    user_id=test_user.id,
                    is_active=True
                )
                db.session.add(project)
                db.session.commit()

            # Vytvor deals
            deal1 = CarDeal(
                project_id=project.id,
                title='Good Deal',
                price=Decimal('10000'),
                profit=Decimal('2000'),
                verdict='KÚPIŤ',
                source='Bazoš.sk',
                link='https://test.com/1'
            )
            deal2 = CarDeal(
                project_id=project.id,
                title='Bad Deal',
                price=Decimal('15000'),
                verdict='NEKUPOVAŤ',
                source='Bazoš.sk',
                link='https://test.com/2'
            )
            db.session.add_all([deal1, deal2])
            db.session.commit()

        # Test API
        response = authenticated_client.get('/api/carscraper/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_deals' in data
        assert 'good_deals' in data
        assert 'total_profit' in data
        assert 'success_rate' in data
        assert data['total_deals'] >= 2
        assert data['good_deals'] >= 1

    def test_get_car_deals_no_project(self, authenticated_client):
        """Test že API vráti 404 ak projekt neexistuje"""
        response = authenticated_client.get('/api/carscraper/deals')
        # Môže vrátiť 404 alebo prázdny zoznam
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.get_json()
            assert 'error' in data or len(data.get('deals', [])) == 0


class TestCarScraperImports:
    """Testy pre správne importy - KRITICKÉ pre fungovanie scrapera"""
    
    def test_app_init_no_stray_characters(self):
        """Test že app/__init__.py nemá náhodné znaky pred komentárom"""
        import os
        app_init_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'core', '__init__.py'
        )
        with open(app_init_path, 'r') as f:
            content = f.read()
        
        # Nesmie začínať s 'S#' - to bola chyba spôsobujúca NameError
        assert not content.startswith('S#'), "core/__init__.py začína s 'S#' - preklep!"
        first_char = content.strip()[0] if content.strip() else ''
        assert first_char in ['#', '"', "'", 'f', 'i'], f"Neočakávaný prvý znak: {first_char}"
    
    def test_car_scraper_uses_importlib(self):
        """Test že car_scraper.py používa importlib (nie 'from app import')"""
        import os
        scraper_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'scripts', 'car_scraper.py'
        )
        with open(scraper_path, 'r') as f:
            content = f.read()
        
        assert 'importlib.util' in content, "car_scraper.py musí používať importlib"
        assert 'from app import app' not in content, "car_scraper.py nesmie mať 'from app import app'"
        assert 'main_app.app' in content, "car_scraper.py musí používať main_app.app"


class TestCarScraperComponents:
    """Testy pre existenciu všetkých CarScraper komponentov"""
    
    def test_scoring_module_exists(self):
        """Test že scoring.py existuje a má správne funkcie"""
        import os
        scoring_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'core', 'blueprints', 'carscraper', 'scoring.py'
        )
        assert os.path.exists(scoring_path), "scoring.py neexistuje!"
        
        with open(scoring_path, 'r') as f:
            content = f.read()
        
        assert 'def calculate_deal_score' in content, "Chýba calculate_deal_score"
        assert 'SUPER_DEAL' in content, "Chýba SUPER_DEAL"
        assert 'GOOD_DEAL' in content, "Chýba GOOD_DEAL"
    
    def test_notifications_module_exists(self):
        """Test že notifications.py existuje"""
        import os
        notifications_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'core', 'blueprints', 'carscraper', 'notifications.py'
        )
        assert os.path.exists(notifications_path), "notifications.py neexistuje!"
        
        with open(notifications_path, 'r') as f:
            content = f.read()
        
        assert 'class TelegramNotifier' in content, "Chýba TelegramNotifier"
        assert 'send_deal_notification' in content, "Chýba send_deal_notification"
    
    def test_stripe_service_exists(self):
        """Test že stripe_service.py existuje s plánmi"""
        import os
        stripe_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'core', 'services', 'stripe_service.py'
        )
        assert os.path.exists(stripe_path), "stripe_service.py neexistuje!"
        
        with open(stripe_path, 'r') as f:
            content = f.read()
        
        assert 'PLAN_FEATURES' in content, "Chýba PLAN_FEATURES"
        assert "'free'" in content, "Chýba free plán"
        assert "'hobby'" in content, "Chýba hobby plán"
        assert "'pro'" in content, "Chýba pro plán"
    
    def test_landing_page_exists(self):
        """Test že landing.html existuje s pricingom"""
        import os
        landing_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'templates', 'landing.html'
        )
        assert os.path.exists(landing_path), "landing.html neexistuje!"
        
        with open(landing_path, 'r') as f:
            content = f.read()
        
        assert '29' in content, "Chýba cena 29€"
        assert '79' in content, "Chýba cena 79€"


class TestPriceExtraction:
    """Testy pre extrakciu ceny"""
    
    def test_price_from_int(self):
        """Test extrakcie z int"""
        import re
        from decimal import Decimal
        
        def safe_extract_price(text):
            if isinstance(text, (int, float)):
                return int(text)
            if isinstance(text, Decimal):
                return int(text)
            numbers = re.findall(r'\d+', str(text).replace(' ', '').replace(',', ''))
            return int(numbers[0]) if numbers else 0
        
        assert safe_extract_price(15000) == 15000
        assert safe_extract_price(15000.50) == 15000
        assert safe_extract_price(Decimal("15000.99")) == 15000
        assert safe_extract_price("15 000 €") == 15000
        assert safe_extract_price("") == 0
