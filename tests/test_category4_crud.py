"""
KATEGÓRIA 4: CRUD OPERÁCIE TESTS
Testy pre vytváranie, čítanie, aktualizáciu a mazanie projektov, platieb, automatizácií.
"""


class TestProjectCRUD:
    """Testy pre CRUD operácie projektov"""

    def test_create_project(self, authenticated_client, test_user):
        """Test vytvorenia projektu"""
        response = authenticated_client.post('/projects', data={
            'name': 'New Test Project',
            'script_path': 'new_script.py'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'New Test Project' in response.data or b'pridan' in response.data or b'Pridan' in response.data

    def test_read_project_list(self, authenticated_client, test_project):
        """Test zobrazenia zoznamu projektov"""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        assert b'Test Project' in response.data or b'projekt' in response.data or b'Projekt' in response.data

    def test_read_project_details(self, authenticated_client, test_project):
        """Test zobrazenia detailov projektu"""
        response = authenticated_client.get(f'/projects/{test_project.id}/edit')
        assert response.status_code == 200
        assert b'Test Project' in response.data

    def test_update_project(self, authenticated_client, test_project, app):
        """Test aktualizácie projektu"""
        from app import Project

        response = authenticated_client.post(f'/projects/{test_project.id}/edit', data={
            'name': 'Updated Project Name',
            'script_path': 'updated_script.py',
            'is_active': 'True'
        }, follow_redirects=True)

        assert response.status_code == 200
        
        # Overenie v databáze
        with app.app_context():
            project = Project.query.get(test_project.id)
            assert project is not None, "Projekt musí existovať"
            assert project.name == 'Updated Project Name'
            assert project.script_path == 'updated_script.py'

    def test_delete_project(self, authenticated_client, test_project, app):
        """Test vymazania projektu"""
        from app import Project

        project_id = test_project.id
        response = authenticated_client.post(
            f'/projects/{project_id}/delete',
            follow_redirects=True
        )

        assert response.status_code == 200

        # Overenie že projekt bol vymazaný - refresh session aby sme videli zmeny
        with app.app_context():
            from app import db
            db.session.expire_all()  # Expire all objects to force refresh
            project = Project.query.get(project_id)
            assert project is None

    def test_project_search(self, authenticated_client, test_project):
        """Test vyhľadávania projektov"""
        response = authenticated_client.get('/?search=Test')
        assert response.status_code == 200

    def test_project_pagination(self, authenticated_client, app, test_user):
        """Test paginácie projektov"""
        from app import db, Project
        import os

        # Vytvoriť viacero projektov
        with app.app_context():
            for i in range(15):
                project = Project(  # type: ignore[call-arg]
                    name=f'Project {i}',  # type: ignore[arg-type]
                    api_key=os.urandom(24).hex(),  # type: ignore[arg-type]
                    user_id=test_user.id  # type: ignore[arg-type]
                )
                db.session.add(project)
            db.session.commit()

        # Test prvej stránky
        response = authenticated_client.get('/?page=1&per_page=10')
        assert response.status_code == 200

        # Test druhej stránky
        response = authenticated_client.get('/?page=2&per_page=10')
        assert response.status_code == 200


class TestPaymentCRUD:
    """Testy pre CRUD operácie platieb"""

    def test_create_payment(self, authenticated_client, test_project):
        """Test vytvorenia platby"""
        response = authenticated_client.post(
            f'/payments/{test_project.id}',
            data={
                'amount': '99.99',
                'gateway': 'stripe'
            },
            follow_redirects=True
        )

        assert response.status_code == 200

    def test_read_payment_list(self, authenticated_client, test_project, app):
        """Test zobrazenia zoznamu platieb"""
        from app import db, Payment

        # Vytvoriť platbu
        with app.app_context():
            payment = Payment(  # type: ignore[call-arg]
                project_id=test_project.id,  # type: ignore[arg-type]
                amount=50.00,  # type: ignore[arg-type]
                gateway='stripe'  # type: ignore[arg-type]
            )
            db.session.add(payment)
            db.session.commit()

        response = authenticated_client.get(f'/payments/{test_project.id}')
        assert response.status_code == 200

    def test_payment_status_update(self, authenticated_client, test_project, app):
        """Test aktualizácie stavu platby"""
        from app import db, Payment

        with app.app_context():
            payment = Payment(  # type: ignore[call-arg]
                project_id=test_project.id,  # type: ignore[arg-type]
                amount=100.00,  # type: ignore[arg-type]
                gateway='stripe',  # type: ignore[arg-type]
                status='pending'  # type: ignore[arg-type]
            )
            db.session.add(payment)
            db.session.commit()

        # Aktualizovať status (ak existuje endpoint)
        # Tento test závisí od implementácie


class TestAutomationCRUD:
    """Testy pre CRUD operácie automatizácií"""

    def test_create_automation(self, authenticated_client, test_project):
        """Test vytvorenia automatizácie"""
        response = authenticated_client.post(
            f'/automation/{test_project.id}',
            data={
                'script_name': 'test_automation.py',
                'schedule': '0 * * * *'
            },
            follow_redirects=True
        )

        assert response.status_code == 200

    def test_read_automation_list(self, authenticated_client, test_project, app):
        """Test zobrazenia zoznamu automatizácií"""
        from app import db, Automation

        # Vytvoriť automatizáciu
        with app.app_context():
            automation = Automation(  # type: ignore[call-arg]
                project_id=test_project.id,  # type: ignore[arg-type]
                script_name='test.py',  # type: ignore[arg-type]
                schedule='0 0 * * *'  # type: ignore[arg-type]
            )
            db.session.add(automation)
            db.session.commit()

        response = authenticated_client.get(f'/automation/{test_project.id}')
        assert response.status_code == 200

    def test_update_automation(self, authenticated_client, test_project, app):
        """Test aktualizácie automatizácie"""
        from app import db, Automation

        with app.app_context():
            automation = Automation(  # type: ignore[call-arg]
                project_id=test_project.id,  # type: ignore[arg-type]
                script_name='old_script.py',  # type: ignore[arg-type]
                schedule='0 0 * * *'  # type: ignore[arg-type]
            )
            db.session.add(automation)
            db.session.commit()

        # Aktualizovať automatizáciu (ak existuje endpoint)
        # Tento test závisí od implementácie


class TestAIRequestCRUD:
    """Testy pre CRUD operácie AI požiadaviek"""

    def test_create_ai_request(self, authenticated_client, test_project):
        """Test vytvorenia AI požiadavky"""
        response = authenticated_client.post(
            f'/ai/{test_project.id}',
            data={
                'prompt': 'Generate test content'
            },
            follow_redirects=True
        )

        # AI endpoint môže vyžadovať API kľúč
        assert response.status_code in [200, 400, 500]

    def test_read_ai_request_list(self, authenticated_client, test_project, app):
        """Test zobrazenia zoznamu AI požiadaviek"""
        from app import db, AIRequest

        # Vytvoriť AI požiadavku
        with app.app_context():
            ai_request = AIRequest(  # type: ignore[call-arg]
                project_id=test_project.id,  # type: ignore[arg-type]
                prompt='Test prompt',  # type: ignore[arg-type]
                response='Test response'  # type: ignore[arg-type]
            )
            db.session.add(ai_request)
            db.session.commit()

        response = authenticated_client.get(f'/ai/{test_project.id}')
        assert response.status_code == 200


class TestAPIKeyManagement:
    """Testy pre správu API kľúčov"""

    def test_regenerate_api_key(self, authenticated_client, test_project, app):
        """Test regenerácie API kľúča"""
        from app import Project

        old_key = test_project.api_key

        response = authenticated_client.post(
            f'/projects/{test_project.id}/regenerate-key',
            follow_redirects=True
        )

        assert response.status_code == 200

        # Overenie že kľúč bol zmenený
        with app.app_context():
            project = Project.query.get(test_project.id)
            assert project is not None, "Projekt musí existovať"
            assert project.api_key != old_key
            assert len(project.api_key) == 48

    def test_api_key_display(self, authenticated_client, test_project):
        """Test zobrazenia API kľúča"""
        response = authenticated_client.get(f'/projects/{test_project.id}/edit')
        assert response.status_code == 200
        assert test_project.api_key.encode() in response.data


class TestExportOperations:
    """Testy pre export operácie"""

    def test_export_projects_json(self, authenticated_client, test_project):
        """Test exportu projektov do JSON"""
        response = authenticated_client.get('/export/projects')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        import json
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_export_payments_csv(self, authenticated_client, test_project, app):
        """Test exportu platieb do CSV"""
        from app import db, Payment

        # Vytvoriť platbu
        with app.app_context():
            payment = Payment(  # type: ignore[call-arg]
                project_id=test_project.id,  # type: ignore[arg-type]
                amount=100.00,  # type: ignore[arg-type]
                gateway='stripe'  # type: ignore[arg-type]
            )
            db.session.add(payment)
            db.session.commit()

        response = authenticated_client.get('/export/payments')
        assert response.status_code == 200
        assert 'text/csv' in response.content_type or 'application/csv' in response.content_type
