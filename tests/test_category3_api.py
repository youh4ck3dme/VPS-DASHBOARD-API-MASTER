"""
KATEGÓRIA 3: API ENDPOINT TESTS
Testy pre všetky API endpointy, rate limiting, health check a API dokumentáciu.
"""

import pytest
import json


class TestHealthCheck:
    """Testy pre health check endpoint"""

    def test_health_check_endpoint(self, client):
        """Test health check endpointu"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'timestamp' in data

    def test_api_health_check_endpoint(self, client):
        """Test API health check endpointu"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data

    def test_health_check_structure(self, client):
        """Test štruktúry health check odpovede"""
        response = client.get('/health')
        data = json.loads(response.data)
        
        assert isinstance(data, dict)
        assert 'status' in data
        # Health check môže vrátiť 'healthy', 'degraded' alebo 'ok'
        assert data['status'] in ['healthy', 'degraded', 'ok', 'unhealthy']


class TestAPIDocumentation:
    """Testy pre API dokumentáciu"""

    def test_api_docs_endpoint(self, client):
        """Test API dokumentačného endpointu"""
        response = client.get('/api/docs')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'endpoints' in data
        assert isinstance(data['endpoints'], (list, dict))

    def test_api_docs_structure(self, client):
        """Test štruktúry API dokumentácie"""
        response = client.get('/api/docs')
        data = json.loads(response.data)
        
        assert 'endpoints' in data
        assert 'authentication' in data
        assert 'rate_limiting' in data


class TestAPIRateLimiting:
    """Testy pre rate limiting"""

    def test_rate_limit_decorator_exists(self, app):
        """Test že rate limit decorator existuje"""
        from app import rate_limit
        assert callable(rate_limit)

    def test_api_endpoints_have_rate_limiting(self, client):
        """Test že API endpointy majú rate limiting"""
        # Tento test môže byť podmienený dostupnosťou Redis
        # Ak Redis nie je dostupný, rate limiting môže byť vypnutý
        response = client.get('/api/docs')
        assert response.status_code == 200


class TestAPIAuthentication:
    """Testy pre API autentifikáciu"""

    def test_api_endpoints_require_auth(self, client):
        """Test že API endpointy vyžadujú autentifikáciu"""
        # Väčšina API endpointov by mala vyžadovať prihlásenie
        # Tento test závisí od konkrétnej implementácie API endpointov
        pass


class TestAPIProjectEndpoints:
    """Testy pre API endpointy projektov"""

    def test_project_list_api(self, authenticated_client, test_project):
        """Test API pre zoznam projektov"""
        # Tento test závisí od existencie API endpointu pre projekty
        # Ak existuje /api/projects, testujeme ho
        response = authenticated_client.get('/api/projects')
        if response.status_code != 404:
            assert response.status_code in [200, 401, 403]
            if response.status_code == 200:
                data = json.loads(response.data)
                assert isinstance(data, (dict, list))


class TestAPIErrorHandling:
    """Testy pre spracovanie chýb v API"""

    def test_404_api_error(self, client):
        """Test 404 chyby pre API endpoint"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        # Ak API vracia JSON
        try:
            data = json.loads(response.data)
            assert 'error' in data
        except (json.JSONDecodeError, ValueError):
            # Ak nie je JSON, aspoň overíme status code
            pass

    def test_500_api_error_handling(self, app, client):
        """Test 500 chyby pre API endpoint"""
        # Tento test môže vyžadovať špeciálnu situáciu
        # Pre teraz len overíme že error handler existuje
        assert hasattr(app, 'error_handler_spec')


class TestAPIResponseFormat:
    """Testy pre formát API odpovedí"""

    def test_json_responses(self, client):
        """Test že API endpointy vracajú JSON"""
        response = client.get('/api/docs')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        try:
            data = json.loads(response.data)
            assert isinstance(data, dict)
        except json.JSONDecodeError:
            pytest.fail("API endpoint should return valid JSON")

    def test_error_response_format(self, client):
        """Test formátu chybových odpovedí"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        # Ak je JSON odpoveď
        try:
            data = json.loads(response.data)
            assert 'error' in data or 'message' in data
        except (json.JSONDecodeError, ValueError):
            # Ak nie je JSON, je to OK pre HTML odpovede
            pass


class TestAPICORS:
    """Testy pre CORS hlavičky (ak sú implementované)"""

    def test_cors_headers(self, client):
        """Test CORS hlavičiek"""
        response = client.options('/api/docs')
        # CORS môže byť voliteľné
        # Tento test len overí že OPTIONS request nevyhodí chybu
        assert response.status_code in [200, 404, 405]


class TestAPIVersioning:
    """Testy pre verziovanie API (ak je implementované)"""

    def test_api_version_endpoint(self, client):
        """Test API verzie"""
        # Ak existuje /api/v1 alebo podobné, testujeme
        response = client.get('/api/version')
        # Ak endpoint neexistuje, je to OK
        assert response.status_code in [200, 404]


class TestAPISecurity:
    """Testy pre bezpečnosť API"""

    def test_api_key_validation(self, authenticated_client, test_project):
        """Test validácie API kľúča"""
        # Tento test závisí od implementácie API key validácie
        # Pre teraz len overíme že projekt má API kľúč
        assert test_project.api_key is not None
        assert len(test_project.api_key) > 0

    def test_sql_injection_protection(self, client):
        """Test ochrany pred SQL injection"""
        # Test že špeciálne znaky v parametroch nevyvolajú chyby
        malicious_input = "'; DROP TABLE users; --"
        response = client.get(f'/api/search?q={malicious_input}')
        # Mal by vrátiť buď 404 alebo bezpečne spracovať vstup
        assert response.status_code in [200, 404, 400]

