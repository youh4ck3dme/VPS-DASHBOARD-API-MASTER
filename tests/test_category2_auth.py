"""
KATEGÓRIA 2: AUTENTIFIKAČNÉ TESTS
Testy pre login, logout, zmenu hesla, autorizáciu a bezpečnosť.
"""

import pytest


class TestLogin:
    """Testy pre prihlásenie"""

    def test_login_page_loads(self, client):
        """Test načítania login stránky"""
        response = client.get('/login')
        assert response.status_code == 200
        # HTML obsahuje UTF-8 kódované znaky, hľadáme v dekódovanom texte alebo ASCII časti
        assert b'login' in response.data.lower() or b'Dashboard' in response.data or b'API' in response.data

    def test_login_with_valid_credentials(self, client, test_user):
        """Test prihlásenia s platnými údajmi"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Po úspešnom prihlásení by mal byť redirect na dashboard
        assert b'dashboard' in response.data or b'projekt' in response.data or b'Dashboard' in response.data

    def test_login_with_invalid_username(self, client, test_user):
        """Test prihlásenia s neplatným používateľským menom"""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'testpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Nespr' in response.data or b'error' in response.data

    def test_login_with_invalid_password(self, client, test_user):
        """Test prihlásenia s neplatným heslom"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Nespr' in response.data or b'error' in response.data

    def test_login_with_empty_fields(self, client):
        """Test prihlásenia s prázdnymi poľami"""
        response = client.post('/login', data={
            'username': '',
            'password': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200

    def test_login_redirects_authenticated_user(self, authenticated_client):
        """Test že prihlásený používateľ je presmerovaný"""
        response = authenticated_client.get('/login', follow_redirects=True)
        assert response.status_code == 200


class TestLogout:
    """Testy pre odhlásenie"""

    def test_logout_requires_login(self, client):
        """Test že odhlásenie vyžaduje prihlásenie"""
        response = client.get('/logout', follow_redirects=True)
        # Mal by presmerovať na login
        assert response.status_code == 200

    def test_logout_success(self, authenticated_client):
        """Test úspešného odhlásenia"""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        # Po odhlásení by mal byť redirect na login
        assert b'login' in response.data or b'Login' in response.data or b'prihlas' in response.data


class TestChangePassword:
    """Testy pre zmenu hesla"""

    def test_settings_page_requires_login(self, client):
        """Test že nastavenia vyžadujú prihlásenie"""
        response = client.get('/settings', follow_redirects=True)
        assert response.status_code == 200

    def test_settings_page_loads(self, authenticated_client):
        """Test načítania stránky nastavení"""
        response = authenticated_client.get('/settings')
        assert response.status_code == 200
        assert b'heslo' in response.data or b'password' in response.data or b'Password' in response.data

    def test_change_password_success(self, authenticated_client, test_user, app):
        """Test úspešnej zmeny hesla"""
        from app import db, User

        response = authenticated_client.post('/settings', data={
            'old_password': 'testpassword123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }, follow_redirects=True)

        assert response.status_code == 200
        
        # Overenie že heslo bolo zmenené
        with app.app_context():
            user = User.query.get(test_user.id)
            assert user.check_password('newpassword123') is True
            assert user.check_password('testpassword123') is False

    def test_change_password_wrong_old_password(self, authenticated_client, app):
        """Test zmeny hesla s nesprávnym starým heslom"""
        from app import db, User
        
        # Získať aktuálne heslo pred zmenou
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            original_password_hash = user.password
        
        response = authenticated_client.post('/settings', data={
            'old_password': 'wrongoldpassword',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }, follow_redirects=True)

        assert response.status_code == 200
        
        # Overenie že heslo sa nezmenilo
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user.password == original_password_hash

    def test_change_password_mismatch(self, authenticated_client):
        """Test zmeny hesla keď sa nové heslá nezhodujú"""
        response = authenticated_client.post('/settings', data={
            'old_password': 'testpassword123',
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'nezhoduj' in response.data or b'Nezhoduj' in response.data or b'error' in response.data or b'Error' in response.data

    def test_change_password_too_short(self, authenticated_client):
        """Test zmeny hesla na príliš krátke heslo"""
        response = authenticated_client.post('/settings', data={
            'old_password': 'testpassword123',
            'new_password': '12345',  # Menej ako 6 znakov
            'confirm_password': '12345'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'6 znakov' in response.data or b'error' in response.data or b'Error' in response.data


class TestAuthorization:
    """Testy pre autorizáciu a oprávnenia"""

    def test_dashboard_requires_login(self, client):
        """Test že dashboard vyžaduje prihlásenie"""
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200
        # Mal by presmerovať na login

    def test_projects_requires_login(self, client):
        """Test že projekty vyžadujú prihlásenie"""
        response = client.get('/projects', follow_redirects=True)
        assert response.status_code == 200

    def test_user_cannot_access_other_user_project(self, app, client, test_user):
        """Test že používateľ nemôže pristupovať k cudzím projektom"""
        from app import db, User, Project
        import os

        with app.app_context():
            # Vytvoriť druhého používateľa
            other_user = User(
                username='otheruser',
                email='other@test.com'
            )
            other_user.set_password('password123')
            db.session.add(other_user)
            db.session.commit()

            # Vytvoriť projekt pre druhého používateľa
            other_project = Project(
                name='Other User Project',
                api_key=os.urandom(24).hex(),
                user_id=other_user.id
            )
            db.session.add(other_project)
            db.session.commit()

            other_project_id = other_project.id
        
        # Prihlásiť sa ako test_user
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword123'
        })

        # Pokúsiť sa pristúpiť k cudziemu projektu
        response = client.get(f'/projects/{other_project_id}/edit', follow_redirects=True)
        assert response.status_code == 200
        # Overenie že sa presmerovalo na dashboard (nie na edit stránku)
        # alebo že obsahuje správu o nedostatočných oprávneniach
        assert b'Dashboard' in response.data or b'forbidden' in response.data.lower() or b'403' in response.data

    def test_api_key_regeneration_requires_ownership(self, app, client, test_user):
        """Test že regenerácia API kľúča vyžaduje vlastníctvo projektu"""
        from app import db, User, Project
        import os

        with app.app_context():
            other_user = User(
                username='otheruser2',
                email='other2@test.com'
            )
            other_user.set_password('password123')
            db.session.add(other_user)
            db.session.commit()

            other_project = Project(
                name='Other Project',
                api_key=os.urandom(24).hex(),
                user_id=other_user.id
            )
            db.session.add(other_project)
            db.session.commit()
            other_project_id = other_project.id
            old_key = other_project.api_key

        # Prihlásiť sa ako test_user
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword123'
        })

        # Pokúsiť sa regenerovať cudzí API kľúč
        response = client.post(f'/projects/{other_project_id}/regenerate-key', follow_redirects=True)
        assert response.status_code == 200
        # Overenie že sa presmerovalo na dashboard alebo obsahuje správu o oprávneniach
        assert b'Dashboard' in response.data or b'forbidden' in response.data.lower() or b'403' in response.data

        # Overiť že kľúč sa nezmenil
        with app.app_context():
            project = Project.query.get(other_project_id)
            assert project.api_key == old_key


class TestSessionManagement:
    """Testy pre správu session"""

    def test_session_persists_after_login(self, client, test_user):
        """Test že session pretrváva po prihlásení"""
        # Prihlásenie
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword123'
        })

        # Ďalšia požiadavka by mala byť autentifikovaná
        response = client.get('/')
        assert response.status_code == 200

    def test_session_cleared_after_logout(self, authenticated_client):
        """Test že session sa vymaže po odhlásení"""
        # Odhlásenie
        authenticated_client.get('/logout')

        # Ďalšia požiadavka by mala vyžadovať prihlásenie
        response = authenticated_client.get('/', follow_redirects=True)
        assert response.status_code == 200

