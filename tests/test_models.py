"""
Model Integrity Tests for VPS Dashboard API.
Tests database models, relationships, constraints, and CRUD operations.
"""

import pytest
from datetime import datetime


class TestUserModel:
    """Tests for User model"""

    def test_create_user(self, app):
        """Test creating a new user"""
        from app import db, User

        with app.app_context():
            user = User(
                username='newuser',
                email='newuser@example.com'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.username == 'newuser'
            assert user.email == 'newuser@example.com'
            assert user.is_admin is False
            assert user.created_at is not None

    def test_password_hashing(self, app):
        """Test password is hashed and can be verified"""
        from app import User

        with app.app_context():
            user = User(username='hashtest', email='hash@test.com')
            user.set_password('mysecretpassword')

            # Password should NOT be stored in plain text
            assert user.password != 'mysecretpassword'

            # Password verification should work
            assert user.check_password('mysecretpassword') is True
            assert user.check_password('wrongpassword') is False

    def test_unique_username_constraint(self, app, test_user):
        """Test that duplicate usernames raise an error"""
        from app import db, User
        from sqlalchemy.exc import IntegrityError

        with app.app_context():
            duplicate_user = User(
                username='testuser',  # Same as test_user
                email='another@example.com'
            )
            duplicate_user.set_password('password')
            db.session.add(duplicate_user)

            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_unique_email_constraint(self, app, test_user):
        """Test that duplicate emails raise an error"""
        from app import db, User
        from sqlalchemy.exc import IntegrityError

        with app.app_context():
            duplicate_user = User(
                username='differentuser',
                email='test@example.com'  # Same as test_user
            )
            duplicate_user.set_password('password')
            db.session.add(duplicate_user)

            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()


class TestProjectModel:
    """Tests for Project model"""

    def test_create_project(self, app, test_user):
        """Test creating a new project"""
        from app import db, Project
        import os

        with app.app_context():
            project = Project(
                name='My Project',
                api_key=os.urandom(24).hex(),
                script_path='my_script.py',
                user_id=test_user.id
            )
            db.session.add(project)
            db.session.commit()

            assert project.id is not None
            assert project.name == 'My Project'
            assert len(project.api_key) == 48  # 24 bytes = 48 hex chars
            assert project.is_active is True
            assert project.created_at is not None

    def test_unique_api_key_constraint(self, app, test_user):
        """Test that duplicate API keys raise an error"""
        from app import db, Project
        from sqlalchemy.exc import IntegrityError

        with app.app_context():
            api_key = 'unique_api_key_123456789012345678901234'

            project1 = Project(
                name='Project 1',
                api_key=api_key,
                user_id=test_user.id
            )
            db.session.add(project1)
            db.session.commit()

            project2 = Project(
                name='Project 2',
                api_key=api_key,  # Same API key
                user_id=test_user.id
            )
            db.session.add(project2)

            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_project_user_relationship(self, app, test_user, test_project):
        """Test project belongs to user relationship"""
        from app import db, Project

        with app.app_context():
            project = db.session.get(Project, test_project.id)
            assert project.author.id == test_user.id
            assert project.user_id == test_user.id


class TestPaymentModel:
    """Tests for Payment model"""

    def test_create_payment(self, app, test_project):
        """Test creating a new payment"""
        from app import db, Payment
        from decimal import Decimal

        with app.app_context():
            payment = Payment(
                project_id=test_project.id,
                amount=Decimal('29.99'),
                currency='EUR',
                gateway='stripe',
                transaction_id='tx_123456789'
            )
            db.session.add(payment)
            db.session.commit()

            assert payment.id is not None
            assert float(payment.amount) == 29.99
            assert payment.currency == 'EUR'
            assert payment.status == 'pending'  # Default
            assert payment.gateway == 'stripe'

    def test_payment_project_relationship(self, app, test_project):
        """Test payment belongs to project relationship"""
        from app import db, Payment, Project
        from decimal import Decimal

        with app.app_context():
            payment = Payment(
                project_id=test_project.id,
                amount=Decimal('10.00'),
                gateway='stripe'
            )
            db.session.add(payment)
            db.session.commit()

            project = db.session.get(Project, test_project.id)
            assert len(project.payments) == 1
            assert project.payments[0].id == payment.id


class TestAutomationModel:
    """Tests for Automation model"""

    def test_create_automation(self, app, test_project):
        """Test creating a new automation"""
        from app import db, Automation

        with app.app_context():
            automation = Automation(
                project_id=test_project.id,
                script_name='daily_task.py',
                schedule='0 3 * * *'
            )
            db.session.add(automation)
            db.session.commit()

            assert automation.id is not None
            assert automation.script_name == 'daily_task.py'
            assert automation.schedule == '0 3 * * *'
            assert automation.is_active is True
            assert automation.last_run is None


class TestAIRequestModel:
    """Tests for AIRequest model"""

    def test_create_ai_request(self, app, test_project):
        """Test creating a new AI request"""
        from app import db, AIRequest

        with app.app_context():
            ai_request = AIRequest(
                project_id=test_project.id,
                prompt='Generate a product description',
                response='Here is a great product description...'
            )
            db.session.add(ai_request)
            db.session.commit()

            assert ai_request.id is not None
            assert ai_request.prompt == 'Generate a product description'
            assert ai_request.response == 'Here is a great product description...'
            assert ai_request.created_at is not None


class TestCascadeDelete:
    """Tests for cascade delete behavior"""

    def test_delete_user_deletes_projects(self, app, test_user, test_project):
        """Test deleting user also deletes their projects"""
        from app import db, User, Project

        with app.app_context():
            user_id = test_user.id
            project_id = test_project.id

            # Verify project exists
            assert db.session.get(Project, project_id) is not None

            # Delete user
            user = db.session.get(User, user_id)
            db.session.delete(user)
            db.session.commit()

            # Project should be deleted (cascade)
            assert db.session.get(Project, project_id) is None

    def test_delete_project_deletes_related(self, app, test_project):
        """Test deleting project also deletes payments, automations, and AI requests"""
        from app import db, Project, Payment, Automation, AIRequest
        from decimal import Decimal

        with app.app_context():
            project_id = test_project.id

            # Create related records
            payment = Payment(project_id=project_id, amount=Decimal('10.00'), gateway='stripe')
            automation = Automation(project_id=project_id, script_name='test.py', schedule='0 * * * *')
            ai_request = AIRequest(project_id=project_id, prompt='Test', response='Response')

            db.session.add_all([payment, automation, ai_request])
            db.session.commit()

            payment_id = payment.id
            automation_id = automation.id
            ai_request_id = ai_request.id

            # Delete project
            project = db.session.get(Project, project_id)
            db.session.delete(project)
            db.session.commit()

            # Related records should be deleted
            assert db.session.get(Payment, payment_id) is None
            assert db.session.get(Automation, automation_id) is None
            assert db.session.get(AIRequest, ai_request_id) is None
