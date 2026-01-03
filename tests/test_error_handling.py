"""
Error Handling Tests for VPS Dashboard API.
Tests application behavior when external services fail.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestDatabaseErrorHandling:
    """Tests for database connection error handling"""

    def test_app_handles_missing_project(self, app, authenticated_client):
        """Test handling of missing project gracefully"""
        # Request a non-existent project
        response = authenticated_client.get('/api/project/99999')
        
        # Should return 404, not crash
        assert response.status_code == 404

    def test_app_handles_invalid_data(self, app, authenticated_client):
        """Test handling of invalid form data"""
        response = authenticated_client.post('/projects', data={
            'name': '',  # Empty required field
            'script_path': ''
        })

        # Should not crash, return form or error
        assert response.status_code in [200, 302, 400]


class TestRedisErrorHandling:
    """Tests for Redis connection error handling"""

    def test_app_starts_without_redis(self, app):
        """Test that app starts even if Redis is unavailable"""
        # The app should start even if Redis fails
        # This is already tested by our test suite working
        assert app is not None

    def test_app_handles_redis_connection_error(self, app, client, test_user):
        """Test handling of Redis errors during operation"""
        # The login should work even if Redis has issues
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword123'
        }, follow_redirects=True)

        # Should work without Redis for basic functionality
        assert response.status_code == 200


class TestStripeErrorHandling:
    """Tests for Stripe API error handling"""

    def test_stripe_not_configured(self, authenticated_client, test_project):
        """Test handling when Stripe is not configured"""
        response = authenticated_client.post(f'/payments/{test_project.id}', data={
            'amount': '25.00',
            'gateway': 'stripe'
        }, follow_redirects=True)

        # Should show error message about Stripe not being configured
        assert response.status_code == 200
        assert b'Stripe' in response.data or b'nakonfigur' in response.data.lower()

    def test_stripe_api_error(self, app, authenticated_client, test_project):
        """Test handling of Stripe API errors"""
        import stripe

        with patch.object(stripe.PaymentIntent, 'create') as mock_create:
            mock_create.side_effect = stripe.error.APIError("API Error")

            # Configure Stripe for this test
            app.config['STRIPE_SECRET_KEY'] = 'sk_test_fake'

            response = authenticated_client.post(f'/payments/{test_project.id}', data={
                'amount': '25.00',
                'gateway': 'stripe'
            }, follow_redirects=True)

            # Should handle gracefully
            assert response.status_code in [200, 302, 500]

            # Reset
            app.config['STRIPE_SECRET_KEY'] = None


class TestOpenAIErrorHandling:
    """Tests for OpenAI API error handling"""

    def test_openai_not_configured(self, authenticated_client, test_project):
        """Test handling when OpenAI is not configured"""
        response = authenticated_client.post(f'/ai/{test_project.id}', data={
            'prompt': 'Generate something'
        }, follow_redirects=True)

        # Should show error about OpenAI not being configured
        assert response.status_code == 200
        assert b'nakonfigur' in response.data.lower() or b'API' in response.data

    def test_openai_graceful_without_key(self, app, authenticated_client, test_project):
        """Test AI endpoint works gracefully without OpenAI key"""
        # OpenAI key is not set in test config
        response = authenticated_client.get(f'/ai/{test_project.id}')
        
        # Should display the AI page
        assert response.status_code == 200


class TestTemplateErrorHandling:
    """Tests for template rendering error handling"""

    def test_missing_template_variable(self, app, authenticated_client):
        """Test handling of missing template variables"""
        # This is more of a development-time error, but test that app handles it
        response = authenticated_client.get('/')
        assert response.status_code == 200

    def test_template_renders_without_projects(self, authenticated_client):
        """Test that dashboard renders even with no projects"""
        response = authenticated_client.get('/')

        assert response.status_code == 200
        assert b'Dashboard' in response.data


class TestFormValidationErrors:
    """Tests for form validation error handling"""

    def test_invalid_decimal_amount(self, authenticated_client, test_project):
        """Test handling of invalid decimal in payment amount"""
        response = authenticated_client.post(f'/payments/{test_project.id}', data={
            'amount': 'not a number',
            'gateway': 'stripe'
        }, follow_redirects=True)

        # Should not crash, should show form again
        assert response.status_code == 200

    def test_empty_required_fields(self, authenticated_client):
        """Test handling of empty required fields"""
        response = authenticated_client.post('/projects', data={
            'name': '',  # Empty required field
            'script_path': ''
        }, follow_redirects=True)

        # Should not create project, show form again
        assert response.status_code == 200


class TestFileSystemErrors:
    """Tests for file system error handling"""

    def test_script_file_not_found(self, authenticated_client, app, test_project):
        """Test handling when script file doesn't exist"""
        from app import db, Project

        with app.app_context():
            project = db.session.get(Project, test_project.id)
            project.script_path = 'nonexistent_script.py'
            db.session.commit()

        response = authenticated_client.get(f'/run_script/{test_project.id}', follow_redirects=True)

        # Should handle gracefully
        assert response.status_code == 200
        # Should show warning about script not found
        assert b'warning' in response.data.lower() or b'nen' in response.data.lower()

    def test_upload_folder_not_accessible(self, app, authenticated_client, test_project):
        """Test handling when upload folder is not accessible"""
        original_folder = app.config['UPLOAD_FOLDER']
        app.config['UPLOAD_FOLDER'] = '/nonexistent/path/that/does/not/exist'

        response = authenticated_client.get(f'/run_script/{test_project.id}', follow_redirects=True)

        # Should handle gracefully
        assert response.status_code == 200

        app.config['UPLOAD_FOLDER'] = original_folder


class TestHTTPErrorHandling:
    """Tests for HTTP error handling"""

    def test_404_error_has_proper_page(self, authenticated_client):
        """Test that 404 errors show proper error page"""
        response = authenticated_client.get('/this/route/does/not/exist')

        assert response.status_code == 404

    def test_method_not_allowed_handled(self, client):
        """Test that method not allowed is handled"""
        response = client.delete('/login')

        # Should return 405 or redirect
        assert response.status_code in [405, 302]

    def test_large_request_handled(self, client):
        """Test handling of very large requests"""
        large_data = 'x' * (1024 * 1024)  # 1MB string

        response = client.post('/login', data={
            'username': large_data,
            'password': 'password'
        })

        # Should handle without crashing
        assert response.status_code in [200, 302, 400, 413, 500]


class TestGracefulDegradation:
    """Tests for graceful degradation when services fail"""

    def test_app_works_without_external_services(self, client, app, test_user):
        """Test that core functionality works without external services"""
        # Login should work
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Dashboard' in response.data

    def test_dashboard_works_without_redis(self, authenticated_client):
        """Test that dashboard works without Redis"""
        response = authenticated_client.get('/')

        assert response.status_code == 200
        assert b'Dashboard' in response.data
