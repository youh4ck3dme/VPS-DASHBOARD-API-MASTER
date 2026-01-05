"""
Testy pre landing page routes a template rendering
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLandingPageAccess:
    """Testy pre prístup na landing page"""
    
    def test_landing_page_returns_200(self, client):
        """Test že /landing vracia 200 OK"""
        response = client.get('/landing')
        assert response.status_code == 200
    
    def test_landing_page_content_type(self, client):
        """Test že /landing vracia HTML"""
        response = client.get('/landing')
        assert 'text/html' in response.content_type
    
    def test_landing_page_no_auth_required(self, client):
        """Test že /landing nevyžaduje prihlásenie"""
        response = client.get('/landing')
        # Nemá sa presmerovať na login
        assert response.status_code != 302
        assert response.status_code != 401


class TestLandingPageContent:
    """Testy pre obsah landing page"""
    
    def test_landing_page_has_title(self, client):
        """Test že landing page má správny title"""
        response = client.get('/landing')
        assert b'CarScraper Pro' in response.data
    
    def test_landing_page_has_pricing(self, client):
        """Test že landing page má pricing sekciu"""
        response = client.get('/landing')
        html = response.data.decode('utf-8')
        
        assert '29' in html or '29 €' in html  # Hobby plán
        assert '79' in html or '79 €' in html  # Pro plán
    
    def test_landing_page_has_features(self, client):
        """Test že landing page má features sekciu"""
        response = client.get('/landing')
        html = response.data.decode('utf-8')
        
        assert 'features' in html.lower() or 'funkcie' in html.lower()
    
    def test_landing_page_has_login_link(self, client):
        """Test že landing page má link na login"""
        response = client.get('/landing')
        html = response.data.decode('utf-8')
        
        # Link na login musí existovať
        assert 'login' in html.lower() or 'prihlásiť' in html.lower()
    
    def test_landing_page_no_jinja_errors(self, client):
        """Test že landing page nemá Jinja template chyby"""
        response = client.get('/landing')
        html = response.data.decode('utf-8')
        
        # Nemalo by obsahovať nezrendrovené Jinja tagy
        assert '{{ ' not in html
        assert '{% ' not in html


class TestLandingPageSEO:
    """Testy pre SEO elementy na landing page"""
    
    def test_landing_page_has_meta_viewport(self, client):
        """Test že landing page má viewport meta tag"""
        response = client.get('/landing')
        html = response.data.decode('utf-8')
        
        assert 'viewport' in html
    
    def test_landing_page_has_charset(self, client):
        """Test že landing page má charset deklaráciu"""
        response = client.get('/landing')
        html = response.data.decode('utf-8')
        
        assert 'UTF-8' in html or 'utf-8' in html
    
    def test_landing_page_has_title_tag(self, client):
        """Test že landing page má title tag"""
        response = client.get('/landing')
        html = response.data.decode('utf-8')
        
        assert '<title>' in html and '</title>' in html


class TestLandingPagePerformance:
    """Testy pre performance landing page"""
    
    def test_landing_page_response_time(self, client):
        """Test že landing page odpovie do 500ms"""
        import time
        
        start = time.time()
        response = client.get('/landing')
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.5, f"Landing page trvala {elapsed:.2f}s (limit 0.5s)"
    
    def test_landing_page_size_reasonable(self, client):
        """Test že landing page nie je príliš veľká"""
        response = client.get('/landing')
        
        # Max 100KB pre HTML
        assert len(response.data) < 100 * 1024, f"Landing page má {len(response.data)} bytes"


class TestLoginPageRoutes:
    """Testy pre login stránku"""
    
    def test_login_page_accessible(self, client):
        """Test že /login je prístupná"""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_login_page_has_form(self, client):
        """Test že login stránka má formulár"""
        response = client.get('/login')
        html = response.data.decode('utf-8')
        
        assert '<form' in html.lower()
        assert 'password' in html.lower()
    
    def test_login_post_without_credentials(self, client):
        """Test POST na /login bez údajov"""
        response = client.post('/login', data={})
        # Buď chyba alebo redirect späť
        assert response.status_code in [200, 302, 400]


class TestDashboardRedirects:
    """Testy pre redirecty na dashboard"""
    
    def test_dashboard_requires_auth(self, client):
        """Test že / (dashboard) vyžaduje prihlásenie"""
        response = client.get('/')
        
        # Buď redirect na login alebo 401
        assert response.status_code in [302, 401, 403]
    
    def test_authenticated_user_sees_dashboard(self, authenticated_client):
        """Test že prihlásený user vidí dashboard"""
        response = authenticated_client.get('/')
        
        # Buď 200 OK alebo redirect na dashboard
        assert response.status_code in [200, 302]


class TestAPIRoutes:
    """Testy pre API routes"""
    
    def test_api_carscraper_deals_requires_auth(self, client):
        """Test že /api/carscraper/deals vyžaduje auth"""
        response = client.get('/api/carscraper/deals')
        assert response.status_code in [302, 401, 403]
    
    def test_api_carscraper_stats_requires_auth(self, client):
        """Test že /api/carscraper/stats vyžaduje auth"""
        response = client.get('/api/carscraper/stats')
        assert response.status_code in [302, 401, 403]
    
    def test_authenticated_api_access(self, authenticated_client):
        """Test že prihlásený user má prístup k API"""
        response = authenticated_client.get('/api/carscraper/deals')
        # Buď data alebo 404 ak nemá projekt
        assert response.status_code in [200, 404]
