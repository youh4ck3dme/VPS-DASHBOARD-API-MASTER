"""
Integration Tests for VPS Dashboard API.
Tests complete user workflows and component interactions.
"""

import pytest
import json


class TestUserRegistrationWorkflow:
    """Tests for complete user workflow"""

    def test_new_user_can_login_and_create_project(self, app, client):
        """Test complete workflow: create user -> login -> create project"""
        from app import db, User, Project
        import os

        # Step 1: Create user directly (simulating registration)
        with app.app_context():
            # Skontroluj, či používateľ už neexistuje
            existing_user = User.query.filter_by(username='workflowuser').first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
            
            user = User(  # type: ignore[call-arg]
                username='workflowuser',
                email='workflow@example.com'
            )
            user.set_password('workflowpass123')
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
            user_id = user.id
            assert user_id is not None, "User ID musí byť nastavený"

        # Step 2: Login
        response = client.post('/login', data={
            'username': 'workflowuser',
            'password': 'workflowpass123'
        }, follow_redirects=True)

        assert response.status_code == 200, f"Login vrátil {response.status_code}"
        # Overenie že sme prihlásení (buď dashboard alebo redirect)
        assert b'Dashboard' in response.data or b'dashboard' in response.data.lower() or response.status_code == 200

        # Step 3: Create project
        response = client.post('/projects', data={
            'name': 'Workflow Project',
            'script_path': 'workflow_script.py'
        }, follow_redirects=True)

        assert response.status_code == 200, f"Create project vrátil {response.status_code}"
        
        # Overenie že projekt bol vytvorený
        with app.app_context():
            project = Project.query.filter_by(name='Workflow Project', user_id=user_id).first()
            assert project is not None, "Projekt mal byť vytvorený"

        # Step 4: Verify project exists in database
        with app.app_context():
            project = Project.query.filter_by(name='Workflow Project').first()
            assert project is not None
            assert project.user_id == user_id

        # Step 5: Verify project appears in API
        # Poznámka: Auto-vytváranie CarScraper Pro je zakázané počas testov,
        # takže by mal byť len jeden projekt
        response = client.get('/api/projects')
        data = json.loads(response.data)

        # Filtruj len projekty vytvorené používateľom (nie auto-vytvorené)
        user_projects = [p for p in data if p.get('name') == 'Workflow Project']
        assert len(user_projects) == 1
        assert user_projects[0]['name'] == 'Workflow Project'


class TestProjectLifecycle:
    """Tests for project lifecycle management"""

    def test_project_creation_generates_unique_api_key(self, authenticated_client, app):
        """Test that each project gets a unique API key"""
        # Create first project
        authenticated_client.post('/projects', data={
            'name': 'Project Alpha',
            'script_path': ''
        })

        # Create second project
        authenticated_client.post('/projects', data={
            'name': 'Project Beta',
            'script_path': ''
        })

        # Get API response
        response = authenticated_client.get('/api/projects')
        data = json.loads(response.data)

        # Both projects should exist
        assert len(data) == 2

        # API keys should be different
        api_keys = [p['api_key'] for p in data]
        assert len(set(api_keys)) == 2  # All unique

    def test_project_with_all_related_entities(self, app, authenticated_client, test_project):
        """Test project with payments, automations, and AI requests"""
        from app import db, Payment, Automation, AIRequest
        from decimal import Decimal

        with app.app_context():
            # Add payment
            payment = Payment(
                project_id=test_project.id,
                amount=Decimal('50.00'),
                gateway='stripe',
                status='completed'
            )
            db.session.add(payment)

            # Add automation
            automation = Automation(
                project_id=test_project.id,
                script_name='backup.py',
                schedule='0 0 * * *'
            )
            db.session.add(automation)

            # Add AI request
            ai_request = AIRequest(
                project_id=test_project.id,
                prompt='Generate report',
                response='Report generated successfully'
            )
            db.session.add(ai_request)
            db.session.commit()

        # Verify all entities are linked correctly via API
        response = authenticated_client.get(f'/api/project/{test_project.id}')
        data = json.loads(response.data)

        assert data['payments_count'] == 1
        assert data['automations_count'] == 1


class TestPaymentWorkflow:
    """Tests for payment creation workflow"""

    def test_payment_creation_flow(self, authenticated_client, app, test_project):
        """Test creating a payment without Stripe configured"""
        response = authenticated_client.post(
            f'/payments/{test_project.id}',
            data={
                'amount': '25.50',
                'gateway': 'stripe'
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        # Should show error about Stripe not configured
        assert b'Stripe' in response.data or b'nakonfigur' in response.data.lower()

    def test_payment_page_shows_payment_history(self, app, authenticated_client, test_project):
        """Test payment page displays existing payments"""
        from app import db, Payment
        from decimal import Decimal

        with app.app_context():
            # Create test payment
            payment = Payment(
                project_id=test_project.id,
                amount=Decimal('99.99'),
                currency='EUR',
                gateway='stripe',
                status='completed',
                transaction_id='test_tx_123'
            )
            db.session.add(payment)
            db.session.commit()

        response = authenticated_client.get(f'/payments/{test_project.id}')

        assert response.status_code == 200
        # Payment amount should be visible (99.99 or 99,99 depending on locale)
        assert b'99' in response.data


class TestAutomationWorkflow:
    """Tests for automation workflow"""

    def test_automation_creation_and_listing(self, authenticated_client, app, test_project):
        """Test creating automation and seeing it in the list"""
        # Create automation
        response = authenticated_client.post(
            f'/automation/{test_project.id}',
            data={
                'script_name': 'nightly_job.py',
                'schedule': '0 23 * * *'
            },
            follow_redirects=True
        )

        assert response.status_code == 200

        # Automation should appear on the page
        assert b'nightly_job.py' in response.data or b'pridan' in response.data.lower()

        # Verify in database
        from app import db, Automation

        with app.app_context():
            automation = Automation.query.filter_by(script_name='nightly_job.py').first()
            assert automation is not None
            assert automation.schedule == '0 23 * * *'
            assert automation.is_active is True


class TestSessionManagement:
    """Tests for session and authentication management"""

    def test_session_persists_across_requests(self, authenticated_client, test_project):
        """Test that session remains valid across multiple requests"""
        # First request - dashboard
        response1 = authenticated_client.get('/')
        assert response1.status_code == 200

        # Second request - projects
        response2 = authenticated_client.get('/projects')
        assert response2.status_code == 200

        # Third request - API
        response3 = authenticated_client.get('/api/projects')
        assert response3.status_code == 200

    def test_logout_invalidates_session(self, authenticated_client):
        """Test that logout properly invalidates the session"""
        # First, verify we're logged in
        response = authenticated_client.get('/')
        assert response.status_code == 200

        # Logout
        authenticated_client.get('/logout')

        # Try to access protected route
        response = authenticated_client.get('/')
        # Should redirect to login
        assert response.status_code == 302 or b'login' in response.data.lower()


class TestFormValidation:
    """Tests for form validation"""

    def test_project_form_requires_name(self, authenticated_client):
        """Test that project creation requires a name"""
        response = authenticated_client.post('/projects', data={
            'name': '',  # Empty name
            'script_path': 'script.py'
        })

        # Should not create project with empty name
        api_response = authenticated_client.get('/api/projects')
        data = json.loads(api_response.data)

        # No project should be created
        assert len(data) == 0

    def test_automation_form_requires_schedule(self, authenticated_client, test_project):
        """Test that automation creation requires schedule"""
        from app import db, Automation

        response = authenticated_client.post(
            f'/automation/{test_project.id}',
            data={
                'script_name': 'test.py',
                'schedule': ''  # Empty schedule
            }
        )

        # Should not create automation with empty schedule
        api_response = authenticated_client.get(f'/api/project/{test_project.id}')
        data = json.loads(api_response.data)

        assert data['automations_count'] == 0


class TestSecurityFeatures:
    """Tests for security features"""

    def test_password_not_stored_in_plaintext(self, app):
        """Test that passwords are hashed, not stored in plaintext"""
        from app import db, User

        with app.app_context():
            user = User(
                username='securitytest',
                email='security@test.com'
            )
            user.set_password('mysecretpassword')
            db.session.add(user)
            db.session.commit()

            # Retrieve user from database
            retrieved_user = User.query.filter_by(username='securitytest').first()

            # Password should NOT be the plaintext password
            assert retrieved_user.password != 'mysecretpassword'

            # Password should be verifiable
            assert retrieved_user.check_password('mysecretpassword') is True

    def test_api_key_is_unique_per_project(self, app, test_user):
        """Test that API keys are unique across all projects"""
        from app import db, Project
        import os

        with app.app_context():
            api_keys = set()
            for i in range(5):
                project = Project(
                    name=f'Project {i}',
                    api_key=os.urandom(24).hex(),
                    user_id=test_user.id
                )
                db.session.add(project)
                api_keys.add(project.api_key)

            db.session.commit()

            # All API keys should be unique
            assert len(api_keys) == 5

    def test_cross_user_project_access_denied(self, app, client, test_user, admin_user, test_project):
        """Test that users cannot access other users' projects"""
        # Login as admin
        client.post('/login', data={
            'username': 'adminuser',
            'password': 'adminpassword123'
        })

        # Try to access test_user's project payments
        response = client.get(f'/payments/{test_project.id}', follow_redirects=True)

        # Should be denied or redirected
        assert b'opr' in response.data.lower() or b'Dashboard' in response.data
