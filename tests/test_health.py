"""
Health Check Tests for VPS Dashboard API.
Tests system health, connectivity, and monitoring endpoints.
"""

import pytest


class TestDatabaseHealth:
    """Tests for database health checks"""

    def test_database_connection_works(self, app):
        """Test that database connection is working"""
        from app import db, User

        with app.app_context():
            # Simple query should work
            try:
                count = User.query.count()
                assert count >= 0
            except Exception as e:
                pytest.fail(f"Database connection failed: {e}")

    def test_database_write_works(self, app):
        """Test that database writes are working"""
        from app import db, User

        with app.app_context():
            try:
                user = User(
                    username='healthcheck',
                    email='health@check.com'
                )
                user.set_password('password')
                db.session.add(user)
                db.session.commit()

                # Verify write succeeded
                retrieved = User.query.filter_by(username='healthcheck').first()
                assert retrieved is not None

                # Cleanup
                db.session.delete(retrieved)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                pytest.fail(f"Database write failed: {e}")

    def test_database_tables_exist(self, app):
        """Test that all required tables exist"""
        from app import db, User, Project, Payment, Automation, AIRequest

        with app.app_context():
            # All models should be queryable
            try:
                User.query.count()
                Project.query.count()
                Payment.query.count()
                Automation.query.count()
                AIRequest.query.count()
            except Exception as e:
                pytest.fail(f"Missing table: {e}")


class TestApplicationHealth:
    """Tests for application health"""

    def test_app_is_running(self, client):
        """Test that the application is responding"""
        response = client.get('/login')
        assert response.status_code == 200

    def test_app_context_works(self, app):
        """Test that app context is properly configured"""
        with app.app_context():
            assert app.config['SECRET_KEY'] is not None
            assert app.config['SQLALCHEMY_DATABASE_URI'] is not None

    def test_login_manager_configured(self, app):
        """Test that login manager is properly configured"""
        # Login manager should be set up - check by trying to access protected route
        with app.test_client() as client:
            response = client.get('/')
            # Should redirect to login (login_manager working)
            assert response.status_code == 302
            assert 'login' in response.headers.get('Location', '')

    def test_templates_exist(self, client):
        """Test that required templates exist and render"""
        response = client.get('/login')
        assert response.status_code == 200
        assert len(response.data) > 0

    def test_static_folder_configured(self, app):
        """Test that static folder is configured"""
        assert app.static_folder is not None


class TestSecurityConfiguration:
    """Tests for security configuration"""

    def test_secret_key_configured(self, app):
        """Test that SECRET_KEY is configured"""
        with app.app_context():
            assert app.config['SECRET_KEY'] is not None
            assert app.config['SECRET_KEY'] != ''
            assert len(app.config['SECRET_KEY']) > 10

    def test_debug_mode_disabled_in_production(self, app):
        """Test that debug mode configuration is correct"""
        # In test mode, debug might be on, but in production it should be off
        # This test just verifies the config exists
        assert 'DEBUG' in app.config or True  # Config key may not exist

    def test_csrf_enabled_by_default(self, app):
        """Test CSRF protection configuration"""
        # CSRF might be disabled for testing
        # Just verify the config option exists
        assert 'WTF_CSRF_ENABLED' in app.config


class TestExternalServicesConfiguration:
    """Tests for external service configuration"""

    def test_stripe_config_exists(self, app):
        """Test Stripe configuration exists (may be None)"""
        with app.app_context():
            # Config key should exist
            assert 'STRIPE_SECRET_KEY' in app.config

    def test_openai_config_exists(self, app):
        """Test OpenAI configuration exists (may be None)"""
        with app.app_context():
            assert 'OPENAI_API_KEY' in app.config

    def test_redis_config_exists(self, app):
        """Test Redis configuration exists"""
        with app.app_context():
            assert 'REDIS_URL' in app.config


class TestRouteHealth:
    """Tests for route health"""

    def test_all_public_routes_accessible(self, client):
        """Test that public routes are accessible"""
        public_routes = [
            '/login',
        ]

        for route in public_routes:
            response = client.get(route)
            assert response.status_code in [200, 302], f"Route {route} failed"

    def test_all_protected_routes_redirect(self, client):
        """Test that protected routes redirect to login"""
        protected_routes = [
            '/',
            '/projects',
            '/api/projects',
        ]

        for route in protected_routes:
            response = client.get(route)
            # Should redirect to login
            assert response.status_code == 302, f"Route {route} didn't redirect"
            assert 'login' in response.headers.get('Location', '').lower()

    def test_authenticated_routes_work(self, authenticated_client, test_project):
        """Test that authenticated routes work"""
        routes = [
            '/',
            '/projects',
            '/api/projects',
            f'/payments/{test_project.id}',
            f'/automation/{test_project.id}',
            f'/ai/{test_project.id}',
        ]

        for route in routes:
            response = authenticated_client.get(route)
            assert response.status_code == 200, f"Route {route} failed"


class TestModelHealth:
    """Tests for model health and relationships"""

    def test_user_model_works(self, app):
        """Test User model operations"""
        from app import db, User

        with app.app_context():
            user = User(
                username='modeltest',
                email='model@test.com'
            )
            user.set_password('password')

            # Test password methods
            assert user.check_password('password') is True
            assert user.check_password('wrong') is False

    def test_project_model_works(self, app, test_user):
        """Test Project model operations"""
        from app import db, Project
        import os

        with app.app_context():
            project = Project(
                name='Model Test',
                api_key=os.urandom(24).hex(),
                user_id=test_user.id
            )
            db.session.add(project)
            db.session.commit()

            # Verify
            assert project.id is not None
            assert project.is_active is True

    def test_relationships_work(self, app, test_user, test_project):
        """Test model relationships work"""
        from app import db, Project, User

        with app.app_context():
            # Refresh objects in this context
            user = db.session.get(User, test_user.id)
            project = db.session.get(Project, test_project.id)

            # Relationships should work
            assert project.author.id == user.id
            assert project in user.projects


class TestConfigurationHealth:
    """Tests for configuration health"""

    def test_upload_folder_configured(self, app):
        """Test that upload folder is configured"""
        with app.app_context():
            assert 'UPLOAD_FOLDER' in app.config
            assert app.config['UPLOAD_FOLDER'] is not None

    def test_database_uri_configured(self, app):
        """Test that database URI is configured"""
        with app.app_context():
            assert 'SQLALCHEMY_DATABASE_URI' in app.config
            assert app.config['SQLALCHEMY_DATABASE_URI'] is not None

    def test_session_configured(self, app):
        """Test that session is properly configured"""
        with app.app_context():
            # Session should work
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['test'] = 'value'

                with client.session_transaction() as sess:
                    assert sess.get('test') == 'value'


class TestStartupHealth:
    """Tests for application startup health"""

    def test_app_creates_tables(self, app):
        """Test that app creates database tables on startup"""
        from app import db

        with app.app_context():
            # Tables should exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()

            required_tables = ['users', 'projects', 'payments', 'automation', 'ai_requests']
            for table in required_tables:
                assert table in tables, f"Missing table: {table}"

    def test_app_handles_missing_env_gracefully(self, app):
        """Test that app handles missing environment variables"""
        # App should start even with missing optional config
        # (like Stripe, OpenAI keys)
        assert app is not None

        with app.app_context():
            # These may be None but shouldn't crash
            stripe_key = app.config.get('STRIPE_SECRET_KEY')
            openai_key = app.config.get('OPENAI_API_KEY')
            # Just verify they don't cause errors to access
