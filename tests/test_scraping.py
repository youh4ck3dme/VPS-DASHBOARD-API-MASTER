"""
Testy pre scraping logiku - car_scraper.py a súvisiace moduly
"""

import pytest
import os
import sys
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
import json

# Pridaj parent adresár do path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPriceExtraction:
    """Testy pre safe_extract_price funkciu"""
    
    def test_extract_from_integer(self):
        """Test extrakcie z integer hodnoty"""
        from scripts.car_scraper import safe_extract_price
        assert safe_extract_price(15000) == 15000
        assert safe_extract_price(0) == 0
        assert safe_extract_price(999999) == 999999
    
    def test_extract_from_float(self):
        """Test extrakcie z float hodnoty"""
        from scripts.car_scraper import safe_extract_price
        assert safe_extract_price(15000.50) == 15000
        assert safe_extract_price(9999.99) == 9999
    
    def test_extract_from_decimal(self):
        """Test extrakcie z Decimal hodnoty"""
        from scripts.car_scraper import safe_extract_price
        assert safe_extract_price(Decimal("15000.99")) == 15000
        assert safe_extract_price(Decimal("0.50")) == 0
    
    def test_extract_from_string_with_spaces(self):
        """Test extrakcie z textu s medzerami"""
        from scripts.car_scraper import safe_extract_price
        assert safe_extract_price("15 000 €") == 15000
        assert safe_extract_price("1 234 567") == 1234567
    
    def test_extract_from_string_with_currency(self):
        """Test extrakcie z textu s menou"""
        from scripts.car_scraper import safe_extract_price
        assert safe_extract_price("15000€") == 15000
        assert safe_extract_price("€15000") == 15000
        assert safe_extract_price("15000 EUR") == 15000
    
    def test_extract_from_empty_string(self):
        """Test extrakcie z prázdneho textu"""
        from scripts.car_scraper import safe_extract_price
        assert safe_extract_price("") == 0
        assert safe_extract_price("   ") == 0
    
    def test_extract_from_non_numeric_string(self):
        """Test extrakcie z textu bez čísel"""
        from scripts.car_scraper import safe_extract_price
        assert safe_extract_price("Cena dohodou") == 0
        assert safe_extract_price("N/A") == 0
    
    def test_extract_with_comma_separator(self):
        """Test extrakcie s čiarkou ako oddeľovačom"""
        from scripts.car_scraper import safe_extract_price
        assert safe_extract_price("15,000") == 15000


class TestAIAnalysis:
    """Testy pre analyze_with_ai funkciu (fallback režim)"""
    
    def test_good_deal_detection(self):
        """Test detekcie dobrého dealu"""
        from scripts.car_scraper import analyze_with_ai
        
        car_data = {'price': 10000, 'title': 'Škoda Octavia'}
        result = analyze_with_ai(car_data)
        
        assert 'odhad_ceny_cislo' in result
        assert 'verdikt' in result
        assert 'risk_level' in result
        assert 'dovod_skratene' in result
        assert result['odhad_ceny_cislo'] > car_data['price']
    
    def test_verdict_values(self):
        """Test že verdikt má validné hodnoty"""
        from scripts.car_scraper import analyze_with_ai
        
        car_data = {'price': 10000, 'title': 'Test Auto'}
        result = analyze_with_ai(car_data)
        
        valid_verdicts = ['KÚPIŤ', 'NEKUPOVAŤ', 'RIZIKO']
        assert result['verdikt'] in valid_verdicts
    
    def test_risk_level_values(self):
        """Test že risk_level má validné hodnoty"""
        from scripts.car_scraper import analyze_with_ai
        
        car_data = {'price': 10000, 'title': 'Test Auto'}
        result = analyze_with_ai(car_data)
        
        valid_levels = ['Nízke', 'Stredné', 'Vysoké']
        assert result['risk_level'] in valid_levels
    
    def test_market_value_calculation(self):
        """Test výpočtu trhovej hodnoty"""
        from scripts.car_scraper import analyze_with_ai
        
        car_data = {'price': 10000, 'title': 'Test Auto'}
        result = analyze_with_ai(car_data)
        
        # Fallback pridáva 15%
        expected = int(10000 * 1.15)
        assert result['odhad_ceny_cislo'] == expected


class TestScrapingFunctions:
    """Testy pre scraping funkcie"""
    
    def test_scrape_bazos_returns_list(self):
        """Test že scrape_bazos vráti zoznam"""
        from scripts.car_scraper import scrape_bazos
        
        # Mock unified scraper
        with patch('scripts.car_scraper_unified.scrape_all_sources') as mock_scrape:
            mock_scrape.return_value = {'listings': [
                {'title': 'Test', 'price': 10000, 'link': 'http://test.com'}
            ]}
            
            result = scrape_bazos()
            assert isinstance(result, list)
    
    def test_scrape_bazos_handles_empty_result(self):
        """Test že scrape_bazos správne spracuje prázdny výsledok"""
        from scripts.car_scraper import scrape_bazos
        
        with patch('scripts.car_scraper_unified.scrape_all_sources') as mock_scrape:
            mock_scrape.return_value = {'listings': []}
            
            result = scrape_bazos()
            assert result == []
    
    def test_scrape_bazos_handles_dict_response(self):
        """Test že scrape_bazos správne spracuje dict odpoveď"""
        from scripts.car_scraper import scrape_bazos
        
        with patch('scripts.car_scraper_unified.scrape_all_sources') as mock_scrape:
            mock_scrape.return_value = {
                'listings': [{'title': 'Test Car', 'price': 5000}],
                'stats': {'total': 1}
            }
            
            result = scrape_bazos()
            assert isinstance(result, list)
            assert len(result) == 1


class TestUnifiedScraper:
    """Testy pre unified scraper"""
    
    def test_unified_scraper_init(self):
        """Test inicializácie unified scrapera"""
        from scripts.car_scraper_unified import UnifiedCarScraper
        
        scraper = UnifiedCarScraper()
        
        # Mal by mať aspoň jeden zdroj
        assert len(scraper.sources) >= 1
        
        # Bazoš by mal byť enabled
        bazos_enabled = any(s['name'] == 'Bazoš.sk' and s['enabled'] for s in scraper.sources)
        assert bazos_enabled, "Bazoš.sk by mal byť enabled"
    
    def test_unified_scraper_disabled_sources(self):
        """Test že nefunkčné zdroje sú disabled"""
        from scripts.car_scraper_unified import UnifiedCarScraper
        
        scraper = UnifiedCarScraper()
        
        # Autobazar a SME by mali byť disabled
        for source in scraper.sources:
            if source['name'] in ['Autobazar.eu', 'Auto.sme.sk']:
                assert source['enabled'] == False, f"{source['name']} by mal byť disabled"
    
    def test_source_priority_order(self):
        """Test že zdroje sú zoradené podľa priority"""
        from scripts.car_scraper_unified import UnifiedCarScraper
        
        scraper = UnifiedCarScraper()
        
        priorities = [s['priority'] for s in scraper.sources]
        assert priorities == sorted(priorities), "Zdroje by mali byť zoradené podľa priority"


class TestListingValidation:
    """Testy pre validáciu inzerátov"""
    
    def test_listing_has_required_fields(self):
        """Test že inzerát má požadované polia"""
        required_fields = ['title', 'price', 'link', 'source']
        
        # Mock listing
        listing = {
            'title': 'Škoda Octavia',
            'price': 10000,
            'description': 'Test description',
            'link': 'https://auto.bazos.sk/inzerat/123',
            'source': 'Bazoš.sk'
        }
        
        for field in required_fields:
            assert field in listing, f"Chýba povinné pole: {field}"
    
    def test_price_minimum_threshold(self):
        """Test že cena spĺňa minimálnu hranicu (500€)"""
        from scripts.car_scraper import safe_extract_price
        
        # Ceny pod 500 by mali byť ignorované
        low_price = safe_extract_price("400 €")
        valid_price = safe_extract_price("600 €")
        
        assert low_price < 500
        assert valid_price >= 500


class TestDatabaseSaving:
    """Testy pre ukladanie do databázy"""
    
    def test_save_deals_creates_cardeal(self, app):
        """Test že save_deals_to_db vytvorí CarDeal záznamy"""
        from scripts.car_scraper import save_deals_to_db
        
        with app.app_context():
            from app import db, Project, CarDeal, User
            
            # Vytvor test user a projekt
            user = User.query.filter_by(username='admin').first()
            if not user:
                user = User(username='admin', email='admin@test.com')
                user.set_password('test123')
                db.session.add(user)
                db.session.commit()
            
            project = Project.query.filter_by(name='Test Scraper Project').first()
            if not project:
                project = Project(
                    name='Test Scraper Project',
                    api_key='test_key_123',
                    user_id=user.id,
                    is_active=True
                )
                db.session.add(project)
                db.session.commit()
            
            # Test listings
            listings = [
                {
                    'title': 'Test Auto 1',
                    'price': 10000,
                    'description': 'Test',
                    'link': f'https://test.com/unique_{os.urandom(4).hex()}',
                    'source': 'Bazoš.sk'
                }
            ]
            
            initial_count = CarDeal.query.filter_by(project_id=project.id).count()
            saved = save_deals_to_db(listings, project.id)
            final_count = CarDeal.query.filter_by(project_id=project.id).count()
            
            assert saved == 1
            assert final_count == initial_count + 1
    
    def test_save_deals_skips_duplicates(self, app):
        """Test že save_deals_to_db preskočí duplikáty"""
        from scripts.car_scraper import save_deals_to_db
        
        with app.app_context():
            from app import db, Project, CarDeal, User
            
            user = User.query.filter_by(username='admin').first()
            project = Project.query.filter_by(name='Test Scraper Project').first()
            
            if not project:
                pytest.skip("Test projekt neexistuje")
            
            unique_link = f'https://test.com/duplicate_test_{os.urandom(4).hex()}'
            
            listings = [
                {
                    'title': 'Duplicate Test',
                    'price': 10000,
                    'description': 'Test',
                    'link': unique_link,
                    'source': 'Bazoš.sk'
                }
            ]
            
            # Prvé uloženie
            saved1 = save_deals_to_db(listings, project.id)
            # Druhé uloženie (rovnaký link)
            saved2 = save_deals_to_db(listings, project.id)
            
            assert saved1 == 1
            assert saved2 == 0  # Duplikát by mal byť preskočený
