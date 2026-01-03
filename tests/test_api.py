"""
API Endpoint Tests for VPS Dashboard API.
Tests JSON API responses, authentication, and data structure.
"""

import pytest
import json


class TestAPIProjects:
    """Tests for /api/projects endpoint"""

    def test_api_projects_requires_login(self, client):
        """Test API projects endpoint requires authentication"""
        response = client.get('/api/projects')

        # Should redirect to login
        assert response.status_code == 302
        assert 'login' in response.headers.get('Location', '')

    def test_api_projects_returns_json(self, authenticated_client):
        """Test API projects returns JSON response"""
        response = authenticated_client.get('/api/projects')

        assert response.status_code == 200
        assert response.content_type == 'application/json'

    def test_api_projects_empty_list(self, authenticated_client):
        """Test API projects returns empty list for new user"""
        response = authenticated_client.get('/api/projects')
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) == 0

    def test_api_projects_returns_user_projects(self, authenticated_client, test_project):
        """Test API projects returns only the user's projects"""
        response = authenticated_client.get('/api/projects')
        data = json.loads(response.data)

        assert len(data) == 1
        assert data[0]['id'] == test_project.id
        assert data[0]['name'] == 'Test Project'
        assert 'api_key' in data[0]
        assert data[0]['is_active'] is True
        assert 'created_at' in data[0]

    def test_api_projects_does_not_show_other_user_projects(self, app, authenticated_client, admin_user):
        """Test API projects does not return other user's projects"""
        from app import db, Project
        import os

        with app.app_context():
            # Create project for admin user (different from authenticated user)
            admin_project = Project(
                name='Admin Only Project',
                api_key=os.urandom(24).hex(),
                user_id=admin_user.id
            )
            db.session.add(admin_project)
            db.session.commit()

        response = authenticated_client.get('/api/projects')
        data = json.loads(response.data)

        # Should not include admin's project
        project_names = [p['name'] for p in data]
        assert 'Admin Only Project' not in project_names


class TestAPIProjectDetail:
    """Tests for /api/project/<id> endpoint"""

    def test_api_project_detail_requires_login(self, client, test_project):
        """Test API project detail endpoint requires authentication"""
        response = client.get(f'/api/project/{test_project.id}')

        assert response.status_code == 302
        assert 'login' in response.headers.get('Location', '')

    def test_api_project_detail_returns_json(self, authenticated_client, test_project):
        """Test API project detail returns JSON response"""
        response = authenticated_client.get(f'/api/project/{test_project.id}')

        assert response.status_code == 200
        assert response.content_type == 'application/json'

    def test_api_project_detail_structure(self, authenticated_client, test_project):
        """Test API project detail returns correct data structure"""
        response = authenticated_client.get(f'/api/project/{test_project.id}')
        data = json.loads(response.data)

        # Check all required fields are present
        assert 'id' in data
        assert 'name' in data
        assert 'api_key' in data
        assert 'is_active' in data
        assert 'script_path' in data
        assert 'created_at' in data
        assert 'payments_count' in data
        assert 'automations_count' in data

        # Check values
        assert data['id'] == test_project.id
        assert data['name'] == 'Test Project'
        assert data['is_active'] is True
        assert data['payments_count'] == 0
        assert data['automations_count'] == 0

    def test_api_project_detail_unauthorized(self, app, authenticated_client, admin_user):
        """Test API project detail returns 403 for other user's project"""
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
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Unauthorized'

    def test_api_project_detail_not_found(self, authenticated_client):
        """Test API project detail returns 404 for non-existent project"""
        response = authenticated_client.get('/api/project/99999')

        assert response.status_code == 404


class TestAPIDataIntegrity:
    """Tests for API data integrity"""

    def test_api_project_counts_payments(self, app, authenticated_client, test_project):
        """Test API project detail correctly counts payments"""
        from app import db, Payment
        from decimal import Decimal

        with app.app_context():
            # Add payments
            for i in range(3):
                payment = Payment(
                    project_id=test_project.id,
                    amount=Decimal('10.00'),
                    gateway='stripe'
                )
                db.session.add(payment)
            db.session.commit()

        response = authenticated_client.get(f'/api/project/{test_project.id}')
        data = json.loads(response.data)

        assert data['payments_count'] == 3

    def test_api_project_counts_automations(self, app, authenticated_client, test_project):
        """Test API project detail correctly counts automations"""
        from app import db, Automation

        with app.app_context():
            # Add automations
            for i in range(2):
                automation = Automation(
                    project_id=test_project.id,
                    script_name=f'script_{i}.py',
                    schedule='0 * * * *'
                )
                db.session.add(automation)
            db.session.commit()

        response = authenticated_client.get(f'/api/project/{test_project.id}')
        data = json.loads(response.data)

        assert data['automations_count'] == 2

    def test_api_key_format(self, authenticated_client, test_project):
        """Test API key is in correct format (48 hex characters)"""
        response = authenticated_client.get('/api/projects')
        data = json.loads(response.data)

        api_key = data[0]['api_key']
        assert len(api_key) == 48  # 24 bytes = 48 hex chars
        assert all(c in '0123456789abcdef' for c in api_key.lower())

    def test_api_datetime_format(self, authenticated_client, test_project):
        """Test created_at is in ISO format"""
        response = authenticated_client.get('/api/projects')
        data = json.loads(response.data)

        created_at = data[0]['created_at']
        # Should be in ISO format (YYYY-MM-DDTHH:MM:SS...)
        assert 'T' in created_at
        assert len(created_at) >= 19  # At least YYYY-MM-DDTHH:MM:SS
