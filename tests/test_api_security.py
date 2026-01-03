"""
API Security Tests for VPS Dashboard API.
Tests API rate limiting, input validation, and error handling.
"""

import pytest
import json


class TestAPIInputValidation:
    """Tests for API input validation"""

    def test_api_project_id_must_be_integer(self, authenticated_client):
        """Test that project ID must be an integer"""
        invalid_ids = [
            "abc",
            "1.5",
            "null",
            "undefined",
            "{}",
            "[]",
            "true",
            "NaN"
        ]

        for invalid_id in invalid_ids:
            response = authenticated_client.get(f'/api/project/{invalid_id}')
            # Should return 404 (Flask default for invalid int)
            assert response.status_code == 404

    def test_api_negative_project_id(self, authenticated_client):
        """Test handling of negative project ID"""
        response = authenticated_client.get('/api/project/-1')
        assert response.status_code == 404

    def test_api_zero_project_id(self, authenticated_client):
        """Test handling of zero project ID"""
        response = authenticated_client.get('/api/project/0')
        assert response.status_code == 404

    def test_api_very_large_project_id(self, authenticated_client):
        """Test handling of very large project ID"""
        # Very large IDs that overflow int will return 404
        response = authenticated_client.get('/api/project/9999999999')
        assert response.status_code == 404


class TestAPIAuthenticationRequired:
    """Tests for API authentication requirements"""

    def test_api_projects_requires_auth(self, client):
        """Test that /api/projects requires authentication"""
        response = client.get('/api/projects')
        # Should redirect to login
        assert response.status_code == 302
        assert 'login' in response.headers.get('Location', '')

    def test_api_project_detail_requires_auth(self, client):
        """Test that /api/project/<id> requires authentication"""
        response = client.get('/api/project/1')
        assert response.status_code == 302

    def test_api_unauthorized_json_response(self, authenticated_client, app, admin_user):
        """Test that unauthorized access returns JSON error"""
        from app import db, Project
        import os

        with app.app_context():
            admin_project = Project(
                name='Admin Project',
                api_key=os.urandom(24).hex(),
                user_id=admin_user.id
            )
            db.session.add(admin_project)
            db.session.commit()
            project_id = admin_project.id

        response = authenticated_client.get(f'/api/project/{project_id}')

        assert response.status_code == 403
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        assert 'error' in data


class TestAPIResponseFormat:
    """Tests for API response format consistency"""

    def test_api_projects_response_format(self, authenticated_client, test_project):
        """Test /api/projects response format"""
        response = authenticated_client.get('/api/projects')
        data = json.loads(response.data)

        assert isinstance(data, list)
        for project in data:
            assert 'id' in project
            assert 'name' in project
            assert 'api_key' in project
            assert 'is_active' in project
            assert 'created_at' in project

    def test_api_project_detail_response_format(self, authenticated_client, test_project):
        """Test /api/project/<id> response format"""
        response = authenticated_client.get(f'/api/project/{test_project.id}')
        data = json.loads(response.data)

        assert 'id' in data
        assert 'name' in data
        assert 'api_key' in data
        assert 'is_active' in data
        assert 'script_path' in data
        assert 'created_at' in data
        assert 'payments_count' in data
        assert 'automations_count' in data

    def test_api_404_response_format(self, authenticated_client):
        """Test that 404 returns proper response"""
        response = authenticated_client.get('/api/project/99999')

        # Should be 404
        assert response.status_code == 404


class TestAPIRateLimitingBehavior:
    """Tests for API behavior under load (simulated)"""

    def test_many_rapid_requests(self, authenticated_client):
        """Test handling of many rapid API requests"""
        # Make 50 rapid requests
        for i in range(50):
            response = authenticated_client.get('/api/projects')
            # All should succeed (no rate limiting currently implemented)
            assert response.status_code == 200

    def test_concurrent_requests_consistency(self, authenticated_client, test_project):
        """Test that concurrent requests return consistent data"""
        responses = []
        for i in range(10):
            response = authenticated_client.get(f'/api/project/{test_project.id}')
            responses.append(json.loads(response.data))

        # All responses should be identical
        for i in range(1, len(responses)):
            assert responses[i]['id'] == responses[0]['id']
            assert responses[i]['name'] == responses[0]['name']
            assert responses[i]['api_key'] == responses[0]['api_key']


class TestAPIErrorHandling:
    """Tests for API error handling"""

    def test_api_malformed_url(self, authenticated_client):
        """Test handling of malformed API URL"""
        response = authenticated_client.get('/api/projects/')
        # Should handle gracefully
        assert response.status_code in [200, 308, 404]

    def test_api_method_not_allowed(self, authenticated_client):
        """Test that unsupported methods return 405"""
        response = authenticated_client.post('/api/projects', data={})
        # POST not implemented for /api/projects
        assert response.status_code == 405

    def test_api_delete_method_not_allowed(self, authenticated_client, test_project):
        """Test that DELETE is not allowed on API"""
        response = authenticated_client.delete(f'/api/project/{test_project.id}')
        assert response.status_code == 405

    def test_api_put_method_not_allowed(self, authenticated_client, test_project):
        """Test that PUT is not allowed on API"""
        response = authenticated_client.put(f'/api/project/{test_project.id}', data={})
        assert response.status_code == 405


class TestAPISensitiveDataExposure:
    """Tests for sensitive data exposure in API"""

    def test_api_does_not_expose_user_password(self, authenticated_client, test_project):
        """Test that API does not expose user passwords"""
        response = authenticated_client.get(f'/api/project/{test_project.id}')
        data = json.loads(response.data)

        # Should not contain password field
        assert 'password' not in str(data).lower()

    def test_api_does_not_expose_user_id_of_others(self, authenticated_client, app, admin_user):
        """Test that API does not expose other users' data"""
        from app import db, Project
        import os

        with app.app_context():
            # Create project for admin user
            admin_project = Project(
                name='Admin Secret Project',
                api_key=os.urandom(24).hex(),
                user_id=admin_user.id
            )
            db.session.add(admin_project)
            db.session.commit()

        # Authenticated as regular user, try to list projects
        response = authenticated_client.get('/api/projects')
        data = json.loads(response.data)

        # Should not see admin's project
        project_names = [p['name'] for p in data]
        assert 'Admin Secret Project' not in project_names

    def test_api_key_format_is_secure(self, authenticated_client, test_project):
        """Test that API keys are properly formatted"""
        response = authenticated_client.get('/api/projects')
        data = json.loads(response.data)

        for project in data:
            api_key = project['api_key']
            # Should be 48 hex characters (24 bytes)
            assert len(api_key) == 48
            assert all(c in '0123456789abcdef' for c in api_key.lower())
            # Should not be a predictable value
            assert api_key != '0' * 48
            assert api_key != 'a' * 48


class TestAPIJSONSafety:
    """Tests for JSON handling safety"""

    def test_api_handles_special_json_characters(self, authenticated_client, app):
        """Test that API handles special JSON characters in data"""
        from app import db, Project
        import os

        with app.app_context():
            # Create project with special characters
            project = Project(
                name='Test "quotes" and \\backslash',
                api_key=os.urandom(24).hex(),
                script_path='path\nwith\nnewlines',
                user_id=1  # Assumes test_user has ID 1
            )
            db.session.add(project)
            db.session.commit()

        response = authenticated_client.get('/api/projects')

        # Should not crash - valid JSON
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        # Should be valid JSON
        try:
            data = json.loads(response.data)
            assert isinstance(data, list)
        except json.JSONDecodeError:
            pytest.fail("API returned invalid JSON")

    def test_api_escapes_html_in_json(self, authenticated_client, app):
        """Test that HTML is properly handled in JSON responses"""
        from app import db, Project
        import os

        with app.app_context():
            project = Project(
                name='<script>alert(1)</script>',
                api_key=os.urandom(24).hex(),
                user_id=1
            )
            db.session.add(project)
            db.session.commit()

        response = authenticated_client.get('/api/projects')
        data = json.loads(response.data)

        # The name should be preserved in JSON (client-side escaping responsibility)
        # But it should still be valid JSON
        assert response.status_code == 200
