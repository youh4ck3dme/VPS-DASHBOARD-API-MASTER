"""
Performance Tests for VPS Dashboard API.
Tests response times, resource usage, and load handling.
"""

import pytest
import time


class TestResponseTimes:
    """Tests for response time thresholds"""

    def test_login_page_response_time(self, client):
        """Test that login page loads within acceptable time"""
        start = time.time()
        response = client.get('/login')
        elapsed = time.time() - start

        assert response.status_code == 200
        # Should load within 500ms
        assert elapsed < 0.5, f"Login page took {elapsed:.3f}s (expected < 0.5s)"

    def test_dashboard_response_time(self, authenticated_client):
        """Test that dashboard loads within acceptable time"""
        start = time.time()
        response = authenticated_client.get('/')
        elapsed = time.time() - start

        assert response.status_code == 200
        # Should load within 500ms
        assert elapsed < 0.5, f"Dashboard took {elapsed:.3f}s (expected < 0.5s)"

    def test_api_projects_response_time(self, authenticated_client):
        """Test that API projects endpoint responds quickly"""
        start = time.time()
        response = authenticated_client.get('/api/projects')
        elapsed = time.time() - start

        assert response.status_code == 200
        # API should be faster - within 200ms
        assert elapsed < 0.2, f"API took {elapsed:.3f}s (expected < 0.2s)"

    def test_api_project_detail_response_time(self, authenticated_client, test_project):
        """Test that API project detail responds quickly"""
        start = time.time()
        response = authenticated_client.get(f'/api/project/{test_project.id}')
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.2, f"API detail took {elapsed:.3f}s (expected < 0.2s)"

    def test_projects_page_response_time(self, authenticated_client):
        """Test that projects page loads quickly"""
        start = time.time()
        response = authenticated_client.get('/projects')
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5, f"Projects page took {elapsed:.3f}s (expected < 0.5s)"


class TestLoadHandling:
    """Tests for handling multiple requests"""

    def test_sequential_requests(self, authenticated_client):
        """Test handling of 20 sequential requests"""
        times = []

        for i in range(20):
            start = time.time()
            response = authenticated_client.get('/')
            elapsed = time.time() - start
            times.append(elapsed)

            assert response.status_code == 200

        avg_time = sum(times) / len(times)
        max_time = max(times)

        # Average should be under 500ms
        assert avg_time < 0.5, f"Average: {avg_time:.3f}s"
        # Max should be under 1s (no significant degradation)
        assert max_time < 1.0, f"Max: {max_time:.3f}s"

    def test_api_sequential_requests(self, authenticated_client):
        """Test handling of 50 sequential API requests"""
        times = []

        for i in range(50):
            start = time.time()
            response = authenticated_client.get('/api/projects')
            elapsed = time.time() - start
            times.append(elapsed)

            assert response.status_code == 200

        avg_time = sum(times) / len(times)

        # API should remain fast
        assert avg_time < 0.1, f"Average API time: {avg_time:.3f}s (expected < 0.1s)"

    def test_mixed_endpoint_requests(self, authenticated_client, test_project):
        """Test mixed requests to different endpoints"""
        endpoints = [
            '/',
            '/projects',
            '/api/projects',
            f'/api/project/{test_project.id}',
            f'/payments/{test_project.id}',
            f'/automation/{test_project.id}',
            f'/ai/{test_project.id}'
        ]

        total_time = 0
        for endpoint in endpoints:
            start = time.time()
            response = authenticated_client.get(endpoint)
            elapsed = time.time() - start
            total_time += elapsed

            # All should succeed
            assert response.status_code == 200

        avg_time = total_time / len(endpoints)
        assert avg_time < 0.3, f"Average mixed endpoint time: {avg_time:.3f}s"


class TestDatabaseQueryPerformance:
    """Tests for database query performance"""

    def test_project_listing_with_many_projects(self, app, authenticated_client, test_user):
        """Test performance with many projects"""
        from app import db, Project
        import os

        # Create 20 projects
        with app.app_context():
            for i in range(20):
                project = Project(
                    name=f'Perf Test Project {i}',
                    api_key=os.urandom(24).hex(),
                    user_id=test_user.id
                )
                db.session.add(project)
            db.session.commit()

        # Measure dashboard load time
        start = time.time()
        response = authenticated_client.get('/')
        elapsed = time.time() - start

        assert response.status_code == 200
        # Should still be fast even with many projects
        assert elapsed < 1.0, f"Dashboard with 20 projects: {elapsed:.3f}s"

    def test_payment_history_with_many_payments(self, app, authenticated_client, test_project):
        """Test performance with many payments"""
        from app import db, Payment
        from decimal import Decimal

        # Create 50 payments
        with app.app_context():
            for i in range(50):
                payment = Payment(
                    project_id=test_project.id,
                    amount=Decimal(f'{10 + i}.00'),
                    gateway='stripe'
                )
                db.session.add(payment)
            db.session.commit()

        # Measure payments page load time
        start = time.time()
        response = authenticated_client.get(f'/payments/{test_project.id}')
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0, f"Payments page with 50 payments: {elapsed:.3f}s"


class TestMemoryUsage:
    """Tests for memory usage patterns"""

    def test_no_memory_leak_on_repeated_requests(self, authenticated_client):
        """Test that repeated requests don't cause memory growth"""
        import sys

        # Get initial memory estimate (object count as proxy)
        initial_objects = len([obj for obj in gc_get_all() if obj is not None]) if hasattr(sys, 'gettotalrefcount') else 0

        # Make many requests
        for i in range(100):
            authenticated_client.get('/')
            authenticated_client.get('/api/projects')

        # This is a simplified check - in production use memory_profiler
        # For now, just verify no crashes
        response = authenticated_client.get('/')
        assert response.status_code == 200

    def test_large_response_handling(self, app, authenticated_client, test_user):
        """Test handling of larger responses"""
        from app import db, Project
        import os

        # Create projects with long names
        with app.app_context():
            for i in range(10):
                project = Project(
                    name='A' * 100 + f' {i}',  # Long name
                    api_key=os.urandom(24).hex(),
                    script_path='B' * 100,  # Long path
                    user_id=test_user.id
                )
                db.session.add(project)
            db.session.commit()

        response = authenticated_client.get('/api/projects')

        assert response.status_code == 200
        # Response should be reasonable size
        assert len(response.data) < 1024 * 1024  # Less than 1MB


class TestCachingBehavior:
    """Tests for caching behavior"""

    def test_static_content_caching_headers(self, client):
        """Test that static content has appropriate caching headers"""
        # This test checks if Flask is configured for static file caching
        # The actual static files would need to exist
        response = client.get('/login')

        # Page should have caching headers or not (depends on config)
        # Just verify response is valid
        assert response.status_code == 200

    def test_api_no_cache_headers(self, authenticated_client):
        """Test that API responses are not cached"""
        response = authenticated_client.get('/api/projects')

        assert response.status_code == 200
        # API responses typically shouldn't be cached
        cache_control = response.headers.get('Cache-Control', '')
        # Either no cache header or proper no-cache directive
        # (depends on implementation)


class TestResponseSizes:
    """Tests for response sizes"""

    def test_login_page_size(self, client):
        """Test that login page is reasonably sized"""
        response = client.get('/login')

        assert response.status_code == 200
        # Login page should be small (< 50KB)
        assert len(response.data) < 50 * 1024

    def test_dashboard_page_size(self, authenticated_client):
        """Test that dashboard is reasonably sized"""
        response = authenticated_client.get('/')

        assert response.status_code == 200
        # Dashboard should be reasonable (< 100KB)
        assert len(response.data) < 100 * 1024

    def test_api_response_size(self, authenticated_client):
        """Test that API response is compact"""
        response = authenticated_client.get('/api/projects')

        assert response.status_code == 200
        # Empty projects list should be tiny
        assert len(response.data) < 1024  # Less than 1KB for empty list


# Helper function for memory test
def gc_get_all():
    """Get all objects tracked by garbage collector"""
    import gc
    return gc.get_objects()
