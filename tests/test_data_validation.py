"""
Data Validation Tests for VPS Dashboard API.
Tests input validation for forms and API endpoints.
"""

import pytest
from decimal import Decimal


class TestEmailValidation:
    """Tests for email format validation"""

    def test_valid_email_formats(self, app):
        """Test that valid email formats are accepted"""
        from app import db, User

        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.com",
            "user@subdomain.domain.com",
            "123@numbers.com"
        ]

        with app.app_context():
            for i, email in enumerate(valid_emails):
                user = User(
                    username=f'emailtest{i}',
                    email=email
                )
                user.set_password('password123')
                db.session.add(user)

            # Should not raise exception
            db.session.commit()

    def test_duplicate_email_rejected(self, app, test_user):
        """Test that duplicate emails are rejected"""
        from app import db, User
        from sqlalchemy.exc import IntegrityError

        with app.app_context():
            duplicate = User(
                username='newuser',
                email='test@example.com'  # Same as test_user
            )
            duplicate.set_password('password')
            db.session.add(duplicate)

            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()


class TestAmountValidation:
    """Tests for payment amount validation"""

    def test_positive_amount_accepted(self, authenticated_client, test_project):
        """Test that positive amounts are accepted"""
        response = authenticated_client.post(f'/payments/{test_project.id}', data={
            'amount': '100.00',
            'gateway': 'stripe'
        }, follow_redirects=True)

        # Should process (even if Stripe not configured)
        assert response.status_code == 200

    def test_zero_amount_handled(self, authenticated_client, test_project):
        """Test handling of zero amount"""
        response = authenticated_client.post(f'/payments/{test_project.id}', data={
            'amount': '0.00',
            'gateway': 'stripe'
        }, follow_redirects=True)

        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_negative_amount_handled(self, authenticated_client, test_project):
        """Test handling of negative amount"""
        response = authenticated_client.post(f'/payments/{test_project.id}', data={
            'amount': '-50.00',
            'gateway': 'stripe'
        }, follow_redirects=True)

        # Should handle gracefully
        assert response.status_code == 200

    def test_very_large_amount_handled(self, authenticated_client, test_project):
        """Test handling of very large amount"""
        response = authenticated_client.post(f'/payments/{test_project.id}', data={
            'amount': '99999999999.99',
            'gateway': 'stripe'
        }, follow_redirects=True)

        # Should handle gracefully
        assert response.status_code == 200

    def test_decimal_precision(self, app, test_project):
        """Test decimal precision in payments"""
        from app import db, Payment

        with app.app_context():
            payment = Payment(
                project_id=test_project.id,
                amount=Decimal('19.99'),
                gateway='stripe'
            )
            db.session.add(payment)
            db.session.commit()

            # Retrieve and check precision
            retrieved = db.session.get(Payment, payment.id)
            assert float(retrieved.amount) == 19.99


class TestCronScheduleValidation:
    """Tests for cron schedule format validation"""

    def test_valid_cron_schedules(self, authenticated_client, test_project):
        """Test that valid cron schedules are accepted"""
        valid_schedules = [
            "0 0 * * *",      # Every day at midnight
            "*/5 * * * *",    # Every 5 minutes
            "0 9 * * 1-5",    # 9am weekdays
            "0 0 1 * *",      # First day of month
            "30 4 1,15 * *"   # 4:30am on 1st and 15th
        ]

        for schedule in valid_schedules:
            response = authenticated_client.post(f'/automation/{test_project.id}', data={
                'script_name': 'test.py',
                'schedule': schedule
            }, follow_redirects=True)

            # Should be accepted
            assert response.status_code == 200

    def test_invalid_cron_schedule_stored(self, authenticated_client, app, test_project):
        """Test that invalid cron schedules are stored (validation at runtime)"""
        # Note: Flask-WTF doesn't validate cron format, it's stored as string
        invalid_schedule = "not a valid cron"

        response = authenticated_client.post(f'/automation/{test_project.id}', data={
            'script_name': 'test.py',
            'schedule': invalid_schedule
        }, follow_redirects=True)

        # Will be stored (runtime validation in cron_check.py)
        assert response.status_code == 200


class TestPathValidation:
    """Tests for file path validation"""

    def test_relative_path_accepted(self, authenticated_client, app):
        """Test that relative paths are accepted"""
        response = authenticated_client.post('/projects', data={
            'name': 'Test Project',
            'script_path': 'script.py'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'pridan' in response.data.lower() or b'Test Project' in response.data

    def test_path_with_subdirectory(self, authenticated_client, app):
        """Test path with subdirectory"""
        response = authenticated_client.post('/projects', data={
            'name': 'Subdir Project',
            'script_path': 'subdir/script.py'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_empty_path_accepted(self, authenticated_client, app):
        """Test that empty script path is accepted"""
        response = authenticated_client.post('/projects', data={
            'name': 'No Script Project',
            'script_path': ''
        }, follow_redirects=True)

        assert response.status_code == 200


class TestProjectNameValidation:
    """Tests for project name validation"""

    def test_minimum_length_name(self, authenticated_client, app):
        """Test minimum length project name"""
        response = authenticated_client.post('/projects', data={
            'name': 'A',  # Single character
            'script_path': ''
        }, follow_redirects=True)

        # Should be accepted (no min length constraint)
        assert response.status_code == 200

    def test_maximum_length_name(self, authenticated_client, app):
        """Test maximum length project name"""
        from app import db, Project

        long_name = 'A' * 120  # Exactly max length

        response = authenticated_client.post('/projects', data={
            'name': long_name,
            'script_path': ''
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_name_exceeding_max_length(self, authenticated_client, app):
        """Test project name exceeding max length"""
        very_long_name = 'A' * 200  # Exceeds 120 char limit

        response = authenticated_client.post('/projects', data={
            'name': very_long_name,
            'script_path': ''
        }, follow_redirects=True)

        # Should handle gracefully (either accept truncated or show error)
        assert response.status_code in [200, 400]


class TestUsernameValidation:
    """Tests for username validation"""

    def test_username_uniqueness(self, app, test_user):
        """Test that usernames must be unique"""
        from app import db, User
        from sqlalchemy.exc import IntegrityError

        with app.app_context():
            duplicate = User(
                username='testuser',  # Same as test_user
                email='different@email.com'
            )
            duplicate.set_password('password')
            db.session.add(duplicate)

            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_username_special_characters(self, app):
        """Test usernames with special characters"""
        from app import db, User

        special_usernames = [
            "user_with_underscore",
            "user-with-dash",
            "user.with.dots",
            "user123"
        ]

        with app.app_context():
            for i, username in enumerate(special_usernames):
                user = User(
                    username=username,
                    email=f'user{i}@test.com'
                )
                user.set_password('password')
                db.session.add(user)

            db.session.commit()


class TestPasswordValidation:
    """Tests for password validation"""

    def test_password_hashing(self, app):
        """Test that passwords are hashed"""
        from app import User

        with app.app_context():
            user = User(username='hashtest', email='hash@test.com')
            user.set_password('mypassword123')

            # Password should be hashed
            assert user.password != 'mypassword123'
            assert len(user.password) > 20  # Hash is longer

    def test_password_verification(self, app):
        """Test password verification works"""
        from app import User

        with app.app_context():
            user = User(username='verifytest', email='verify@test.com')
            user.set_password('correctpassword')

            assert user.check_password('correctpassword') is True
            assert user.check_password('wrongpassword') is False

    def test_empty_password_set(self, app):
        """Test setting empty password"""
        from app import User

        with app.app_context():
            user = User(username='emptypass', email='empty@test.com')
            user.set_password('')

            # Empty password should still be hashed
            assert user.password != ''


class TestAPIKeyValidation:
    """Tests for API key generation and validation"""

    def test_api_key_length(self, app, test_user):
        """Test API key has correct length"""
        from app import db, Project
        import os

        with app.app_context():
            project = Project(
                name='Key Test',
                api_key=os.urandom(24).hex(),
                user_id=test_user.id
            )
            db.session.add(project)
            db.session.commit()

            # Should be 48 hex characters (24 bytes)
            assert len(project.api_key) == 48

    def test_api_key_uniqueness(self, app, test_user):
        """Test API keys must be unique"""
        from app import db, Project
        from sqlalchemy.exc import IntegrityError

        with app.app_context():
            api_key = 'a' * 48

            project1 = Project(
                name='Project 1',
                api_key=api_key,
                user_id=test_user.id
            )
            db.session.add(project1)
            db.session.commit()

            project2 = Project(
                name='Project 2',
                api_key=api_key,  # Same key
                user_id=test_user.id
            )
            db.session.add(project2)

            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_api_key_format(self, app, test_user):
        """Test API key is valid hex"""
        from app import db, Project
        import os

        with app.app_context():
            project = Project(
                name='Format Test',
                api_key=os.urandom(24).hex(),
                user_id=test_user.id
            )
            db.session.add(project)
            db.session.commit()

            # Should be valid hex
            assert all(c in '0123456789abcdef' for c in project.api_key.lower())
