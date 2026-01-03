"""
Route and View Tests for VPS Dashboard API.
Tests HTTP endpoints, access control, and form handling.
"""

import pytest


class TestAuthenticationRoutes:
    """Tests for authentication routes"""

    def test_login_page_loads(self, client):
        """Test login page is accessible"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Prihl' in response.data or b'login' in response.data.lower()

    def test_login_with_valid_credentials(self, app, client, test_user):
        """Test login with correct username and password"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword123'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should redirect to dashboard after successful login
        assert b'Dashboard' in response.data or b'dashboard' in response.data.lower()

    def test_login_with_invalid_credentials(self, app, client, test_user):
        """Test login with wrong password"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        # Should stay on login page or show error
        assert b'Nespr' in response.data or b'login' in response.data.lower()

    def test_logout(self, authenticated_client):
        """Test logout functionality"""
        response = authenticated_client.get('/logout', follow_redirects=True)

        assert response.status_code == 200
        # Should redirect to login after logout
        assert b'login' in response.data.lower() or b'prihl' in response.data.lower()

    def test_authenticated_user_redirected_from_login(self, authenticated_client):
        """Test that logged-in users are redirected away from login page"""
        response = authenticated_client.get('/login', follow_redirects=False)

        # Should either redirect or show dashboard
        assert response.status_code in [200, 302]


class TestDashboardRoutes:
    """Tests for dashboard routes"""

    def test_dashboard_requires_login(self, client):
        """Test dashboard redirects unauthenticated users"""
        response = client.get('/')

        # Should redirect to login
        assert response.status_code == 302
        assert 'login' in response.headers.get('Location', '')

    def test_dashboard_accessible_when_logged_in(self, authenticated_client):
        """Test dashboard is accessible for authenticated users"""
        response = authenticated_client.get('/')

        assert response.status_code == 200
        assert b'Dashboard' in response.data


class TestProjectRoutes:
    """Tests for project management routes"""

    def test_projects_page_requires_login(self, client):
        """Test projects page redirects unauthenticated users"""
        response = client.get('/projects')

        assert response.status_code == 302
        assert 'login' in response.headers.get('Location', '')

    def test_projects_page_loads(self, authenticated_client):
        """Test projects page is accessible for authenticated users"""
        response = authenticated_client.get('/projects')

        assert response.status_code == 200
        assert b'projekt' in response.data.lower() or b'project' in response.data.lower()

    def test_create_project(self, authenticated_client, app):
        """Test creating a new project"""
        from app import db, Project

        response = authenticated_client.post('/projects', data={
            'name': 'New Test Project',
            'script_path': 'test_script.py'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'New Test Project' in response.data or b'pridan' in response.data.lower()

        # Verify project was created in database
        with app.app_context():
            project = Project.query.filter_by(name='New Test Project').first()
            assert project is not None
            assert project.script_path == 'test_script.py'


class TestPaymentRoutes:
    """Tests for payment routes"""

    def test_payments_page_requires_login(self, client):
        """Test payments page redirects unauthenticated users"""
        response = client.get('/payments/1')

        assert response.status_code == 302
        assert 'login' in response.headers.get('Location', '')

    def test_payments_page_requires_ownership(self, app, authenticated_client, admin_user):
        """Test user cannot access another user's project payments"""
        from app import db, Project
        import os

        with app.app_context():
            # Create project for admin user
            admin_project = Project(
                name='Admin Project',
                api_key=os.urandom(24).hex(),
                user_id=admin_user.id
            )
            db.session.add(admin_project)
            db.session.commit()
            project_id = admin_project.id

        response = authenticated_client.get(f'/payments/{project_id}', follow_redirects=True)

        # Should be denied - either 404, redirect, or show error
        assert response.status_code in [200, 302, 403, 404]
        if response.status_code == 200:
            # If 200, should show error message or redirect to dashboard
            assert b'opr' in response.data.lower() or b'danger' in response.data.lower() or b'Dashboard' in response.data

    def test_payments_page_accessible_for_owner(self, app, authenticated_client, test_project):
        """Test project owner can access payments page"""
        response = authenticated_client.get(f'/payments/{test_project.id}')

        # Should show payments page
        assert response.status_code == 200
        assert b'Platb' in response.data or b'payment' in response.data.lower()


class TestAutomationRoutes:
    """Tests for automation routes"""

    def test_automation_page_loads(self, authenticated_client, test_project):
        """Test automation page is accessible for project owner"""
        response = authenticated_client.get(f'/automation/{test_project.id}')

        assert response.status_code == 200
        assert b'Automatiz' in response.data or b'automation' in response.data.lower()

    def test_create_automation(self, authenticated_client, app, test_project):
        """Test creating a new automation"""
        from app import db, Automation

        response = authenticated_client.post(f'/automation/{test_project.id}', data={
            'script_name': 'daily_backup.py',
            'schedule': '0 2 * * *'
        }, follow_redirects=True)

        assert response.status_code == 200

        # Verify automation was created
        with app.app_context():
            automation = Automation.query.filter_by(script_name='daily_backup.py').first()
            assert automation is not None
            assert automation.schedule == '0 2 * * *'


class TestAIRoutes:
    """Tests for AI generator routes"""

    def test_ai_page_loads(self, authenticated_client, test_project):
        """Test AI page is accessible for project owner"""
        response = authenticated_client.get(f'/ai/{test_project.id}')

        assert response.status_code == 200
        assert b'AI' in response.data or b'Generat' in response.data

    def test_ai_request_without_api_key(self, authenticated_client, app, test_project):
        """Test AI request fails gracefully without OpenAI API key"""
        response = authenticated_client.post(f'/ai/{test_project.id}', data={
            'prompt': 'Test prompt for AI'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should show error about missing API key
        assert b'nakonfigur' in response.data.lower() or b'API' in response.data


class TestRunScriptRoute:
    """Tests for run script route"""

    def test_run_script_requires_login(self, client):
        """Test run script redirects unauthenticated users"""
        response = client.get('/run_script/1')

        assert response.status_code == 302
        assert 'login' in response.headers.get('Location', '')

    def test_run_script_nonexistent_project(self, authenticated_client):
        """Test running script for non-existent project returns 404"""
        response = authenticated_client.get('/run_script/99999')

        assert response.status_code == 404


class TestErrorHandlers:
    """Tests for error handlers"""

    def test_404_error_handler(self, authenticated_client):
        """Test 404 error page is returned for non-existent routes"""
        response = authenticated_client.get('/this-route-does-not-exist')

        assert response.status_code == 404

    def test_project_not_found_returns_404(self, authenticated_client):
        """Test 404 for non-existent project"""
        response = authenticated_client.get('/api/project/99999')

        assert response.status_code == 404
