"""
End-to-End (E2E) testy simulujúce reálnu cestu používateľa aplikáciou.
Tieto testy overujú integráciu medzi API, databázou a očakávaným správaním frontendu.
"""

import pytest
import json
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestUserJourneyE2E:
    """Simulácia cesty používateľa od registrácie/prihlásenia až po zobrazenie dát"""

    def test_full_user_path_to_car_deals(self, client, app):
        """
        Simuluje: 
        1. Prístup na landing page
        2. Prihlásenie
        3. Prístup k dashboardu
        4. Načítanie car scraper štatistík
        5. Načítanie zoznamu deals
        """
        # 1. Landing Page
        landing_res = client.get('/landing')
        assert landing_res.status_code == 200
        assert b"CarScraper Pro" in landing_res.data

        # 2. Login (Simulujeme session prihlásenie cez test_user fixture pattern)
        # Použijeme conftest fixture 'test_user' priamo v app kontexte
        with app.app_context():
            from app import db, User, Project, CarDeal
            db.create_all()  # Ensure tables exist
            
            # Vyčisti staré testovacie dáta pre istotu
            CarDeal.query.delete()
            Project.query.delete()
            User.query.filter_by(username='e2e_user').delete()
            db.session.commit()

            test_user = User(username='e2e_user', email='e2e@test.com')
            test_user.set_password('secure_pass_123')
            db.session.add(test_user)
            db.session.commit()
            user_id = test_user.id

        # Prihlásime klienta manuálne pre túto session
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user_id)
            sess['_fresh'] = True

        # 3. Dashboard Access
        dashboard_res = client.get('/')
        assert dashboard_res.status_code in [200, 302]

        # 4. API Stats (Mali by byť prázdne/nula pre nového užívateľa)
        stats_res = client.get('/api/carscraper/stats')
        # Poznámka: Dashboard automaticky vytvára projekt pre nového usera v app.py index route
        # Ak v teste ideme priamo na api, musíme sa uistiť že projekt existuje
        with app.app_context():
            from app import Project, db
            proj = Project.query.filter_by(user_id=user_id, name='CarScraper Pro').first()
            if not proj:
                proj = Project(name='CarScraper Pro', user_id=user_id, is_active=True, api_key='e2e_test_key')
                db.session.add(proj)
                db.session.commit()
            project_id = proj.id

        stats_res = client.get('/api/carscraper/stats')
        assert stats_res.status_code == 200
        stats_data = stats_res.get_json()
        assert 'total_deals' in stats_data
        assert stats_data['total_deals'] == 0

        # 5. Simulujeme scraping - pridanie deals do DB
        with app.app_context():
            from app import CarDeal, db
            deal = CarDeal(
                project_id=project_id,
                title='Audi A4 E2E Test',
                price=Decimal('12000'),
                verdict='KÚPIŤ',
                link='https://e2e.test/audi',
                source='Bazoš.sk'
            )
            db.session.add(deal)
            db.session.commit()

        # 6. Re-check Deals List
        deals_res = client.get('/api/carscraper/deals')
        assert deals_res.status_code == 200
        deals_data = deals_res.get_json()
        assert len(deals_data['deals']) == 1
        assert deals_data['deals'][0]['title'] == 'Audi A4 E2E Test'

    def test_api_security_e2e(self, client, app):
         """Overenie, že používateľ nevidí dáta iného používateľa"""
         with app.app_context():
            from app import db, User, Project, CarDeal
            
            # User 1
            u1 = User(username='user1', email='u1@test.com')
            u1.set_password('pass')
            db.session.add(u1)
            
            # User 2
            u2 = User(username='user2', email='u2@test.com')
            u2.set_password('pass')
            db.session.add(u2)
            db.session.commit()

            # Project for User 1
            p1 = Project(name='CarScraper Pro', user_id=u1.id, api_key='u1_key')
            db.session.add(p1)
            db.session.commit()

            # Deal for User 1
            d1 = CarDeal(project_id=p1.id, title='U1 Private Car', link='u1.link', source='b')
            db.session.add(d1)
            db.session.commit()
            
            u1_id = u1.id
            u2_id = u2.id

         # Login as User 2
         with client.session_transaction() as sess:
            sess['_user_id'] = str(u2_id)
            sess['_fresh'] = True

         # User 2 tries to see deals
         res = client.get('/api/carscraper/deals')
         # Buď dostane prázdny list alebo 404 (ak nemá vlastný projekt)
         if res.status_code == 200:
             data = res.get_json()
             for deal in data.get('deals', []):
                 assert deal['title'] != 'U1 Private Car'
         else:
             assert res.status_code == 404
