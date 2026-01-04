"""
Testy pre CarScraper Pro API endpointy
"""

import pytest
from app import db, Project, CarDeal, User
from decimal import Decimal


class TestCarScraperAPI:
    """Testy pre CarScraper Pro API"""

    def test_get_car_deals_requires_login(self, client):
        """Test že API vyžaduje prihlásenie"""
        response = client.get('/api/carscraper/deals')
        assert response.status_code in [302, 401, 403]  # Redirect alebo unauthorized

    def test_get_car_deals_with_project(self, authenticated_client, test_user, app):
        """Test získania deals s existujúcim projektom"""
        with app.app_context():
            # Vytvor CarScraper Pro projekt
            project = Project(
                name='CarScraper Pro',
                api_key='test_api_key_123',
                user_id=test_user.id,
                is_active=True
            )
            db.session.add(project)
            db.session.commit()

            # Vytvor test deal
            deal = CarDeal(
                project_id=project.id,
                title='Test Auto',
                price=Decimal('10000'),
                market_value=Decimal('12000'),
                profit=Decimal('2000'),
                verdict='KÚPIŤ',
                risk_level='Nízke',
                reason='Test reason',
                source='Bazoš.sk',
                link='https://test.com',
                description='Test description'
            )
            db.session.add(deal)
            db.session.commit()

        # Test API
        response = authenticated_client.get('/api/carscraper/deals')
        assert response.status_code == 200
        data = response.get_json()
        assert 'deals' in data
        assert len(data['deals']) > 0
        assert data['deals'][0]['title'] == 'Test Auto'

    def test_get_car_deals_filter_by_verdict(self, authenticated_client, test_user, app):
        """Test filtrovania deals podľa verdictu"""
        with app.app_context():
            project = Project.query.filter_by(name='CarScraper Pro', user_id=test_user.id).first()
            if not project:
                project = Project(
                    name='CarScraper Pro',
                    api_key='test_api_key_123',
                    user_id=test_user.id,
                    is_active=True
                )
                db.session.add(project)
                db.session.commit()

            # Vytvor deals s rôznymi verdictmi
            deal1 = CarDeal(
                project_id=project.id,
                title='Good Deal',
                price=Decimal('10000'),
                verdict='KÚPIŤ',
                source='Bazoš.sk',
                link='https://test.com/1'
            )
            deal2 = CarDeal(
                project_id=project.id,
                title='Bad Deal',
                price=Decimal('15000'),
                verdict='NEKUPOVAŤ',
                source='Bazoš.sk',
                link='https://test.com/2'
            )
            db.session.add_all([deal1, deal2])
            db.session.commit()

        # Test filter
        response = authenticated_client.get('/api/carscraper/deals?verdict=KÚPIŤ')
        assert response.status_code == 200
        data = response.get_json()
        assert all(d['verdict'] == 'KÚPIŤ' for d in data['deals'])

    def test_get_car_deal_detail(self, authenticated_client, test_user, app):
        """Test získania detailu deal"""
        with app.app_context():
            project = Project.query.filter_by(name='CarScraper Pro', user_id=test_user.id).first()
            if not project:
                project = Project(
                    name='CarScraper Pro',
                    api_key='test_api_key_123',
                    user_id=test_user.id,
                    is_active=True
                )
                db.session.add(project)
                db.session.commit()

            deal = CarDeal(
                project_id=project.id,
                title='Test Auto Detail',
                price=Decimal('10000'),
                verdict='KÚPIŤ',
                source='Bazoš.sk',
                link='https://test.com'
            )
            db.session.add(deal)
            db.session.commit()
            deal_id = deal.id

        # Test API
        response = authenticated_client.get(f'/api/carscraper/deals/{deal_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Test Auto Detail'
        assert data['is_viewed'] is True  # Malo by byť označené ako videné

    def test_get_carscraper_stats(self, authenticated_client, test_user, app):
        """Test získania štatistík"""
        with app.app_context():
            project = Project.query.filter_by(name='CarScraper Pro', user_id=test_user.id).first()
            if not project:
                project = Project(
                    name='CarScraper Pro',
                    api_key='test_api_key_123',
                    user_id=test_user.id,
                    is_active=True
                )
                db.session.add(project)
                db.session.commit()

            # Vytvor deals
            deal1 = CarDeal(
                project_id=project.id,
                title='Good Deal',
                price=Decimal('10000'),
                profit=Decimal('2000'),
                verdict='KÚPIŤ',
                source='Bazoš.sk',
                link='https://test.com/1'
            )
            deal2 = CarDeal(
                project_id=project.id,
                title='Bad Deal',
                price=Decimal('15000'),
                verdict='NEKUPOVAŤ',
                source='Bazoš.sk',
                link='https://test.com/2'
            )
            db.session.add_all([deal1, deal2])
            db.session.commit()

        # Test API
        response = authenticated_client.get('/api/carscraper/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_deals' in data
        assert 'good_deals' in data
        assert 'total_profit' in data
        assert 'success_rate' in data
        assert data['total_deals'] >= 2
        assert data['good_deals'] >= 1

    def test_get_car_deals_no_project(self, authenticated_client):
        """Test že API vráti 404 ak projekt neexistuje"""
        response = authenticated_client.get('/api/carscraper/deals')
        # Môže vrátiť 404 alebo prázdny zoznam
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.get_json()
            assert 'error' in data or len(data.get('deals', [])) == 0

