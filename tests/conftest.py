import pytest
import os
import sys
from sqlalchemy.pool import NullPool

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORTANT: Set environment variables BEFORE importing app
# Use a file in /tmp to ensure write permissions and thread sharing
db_path = '/tmp/vps_test.db'

# Clean start
if os.path.exists(db_path):
    os.remove(db_path)

os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing'


class TestConfig:
    """Test configuration - uses SQLite file database for test isolation"""
    SECRET_KEY = 'test-secret-key-for-testing'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'poolclass': NullPool}
    UPLOAD_FOLDER = '/tmp/test_scripts'
    STRIPE_SECRET_KEY = None
    STRIPE_PUBLIC_KEY = None
    SUMUP_API_KEY = None
    COINGATE_API_KEY = None
    OPENAI_API_KEY = None
    REDIS_URL = 'redis://localhost:6379/1'
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    TESTING = True


@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test."""
    from app import app as flask_app, db

    flask_app.config.from_object(TestConfig)

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()
        # Dispose engine to release lock
        db.engine.dispose()

    # Clean up the DB file after tests
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass


@pytest.fixture(scope='function')
def client(app):
    """Test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Database session for direct database operations."""
    from app import db
    yield db.session


@pytest.fixture(scope='function')
def test_user(app):
    """Create a test user (returns user ID for use in tests)."""
    from app import db, User

    user = User(
        username='testuser',
        email='test@example.com'
    )
    user.set_password('testpassword123')
    db.session.add(user)
    db.session.commit()

    # Return the user object (can be used directly since we're in app context)
    yield user


@pytest.fixture(scope='function')
def authenticated_client(app, test_user, client):
    """Test client that is already logged in as test_user."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['_fresh'] = True

    yield client


@pytest.fixture(scope='function')
def test_project(app, test_user):
    """Create a test project."""
    from app import db, Project
    import os as _os

    project = Project(
        name='Test Project',
        api_key=_os.urandom(24).hex(),
        script_path='test_script.py',
        is_active=True,
        user_id=test_user.id
    )
    db.session.add(project)
    db.session.commit()

    yield project


@pytest.fixture(scope='function')
def admin_user(app):
    """Create an admin test user."""
    from app import db, User

    user = User(
        username='adminuser',
        email='admin@example.com',
        is_admin=True
    )
    user.set_password('adminpassword123')
    db.session.add(user)
    db.session.commit()

    yield user
