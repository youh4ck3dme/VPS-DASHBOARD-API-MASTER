"""
Performance testy špecializované na CarScraper Pro funkcie.
Zameriava sa na rýchlosť spracovania veľkého množstva deals a AI analýzu.
"""

import pytest
import time
from decimal import Decimal
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestCarScraperPerformance:
    """Výkonnostné testy pre CarScraper Pro komponenty"""

    def test_deals_listing_performance_large_data(self, app, authenticated_client, test_user):
        """Test rýchlosti načítania API s 100+ inzerátmi"""
        with app.app_context():
            from app import db, Project, CarDeal
            db.create_all()
            
            project = Project.query.filter_by(user_id=test_user.id, name='CarScraper Pro').first()
            if not project:
                project = Project(name='CarScraper Pro', user_id=test_user.id, is_active=True, api_key='perf_key_1')
                db.session.add(project)
                db.session.commit()
            
            # Hromadné pridanie 100 inzerátov
            deals = []
            for i in range(100):
                deals.append(CarDeal(
                    project_id=project.id,
                    title=f'Car {i}',
                    price=Decimal(str(1000 + i)),
                    verdict='KÚPIŤ',
                    link=f'https://test.com/{i}',
                    source='Bazoš.sk'
                ))
            db.session.add_all(deals)
            db.session.commit()

        # Meranie času API requestu
        start = time.time()
        response = authenticated_client.get('/api/carscraper/deals')
        elapsed = time.time() - start
        
        assert response.status_code == 200
        # 100 inzerátov by malo byť pod 300ms
        assert elapsed < 0.3, f"Načítanie 100 inzerátov trvalo {elapsed:.3f}s (limit 0.3s)"

    def test_stats_calculation_performance(self, app, authenticated_client, test_user):
        """Test rýchlosti výpočtu štatistík pri veľkom počte dát"""
        # (Projekt a dáta už existujú z predchádzajúceho testu ak je scope správny, 
        # ale pre istotu vytvoríme nové v rámci funkčného scope)
        with app.app_context():
            from app import db, Project, CarDeal
            project = Project.query.filter_by(user_id=test_user.id, name='CarScraper Pro').first()
            if not project:
                project = Project(name='CarScraper Pro', user_id=test_user.id, is_active=True, api_key='perf_key_2')
                db.session.add(project)
                db.session.commit()

        start = time.time()
        response = authenticated_client.get('/api/carscraper/stats')
        elapsed = time.time() - start
        
        assert response.status_code == 200
        # Štatistiky by mali byť bleskové (pod 100ms)
        assert elapsed < 0.1, f"Výpočet štatistík trval {elapsed:.3f}s (limit 0.1s)"

    def test_ai_analysis_fallback_speed(self):
        """Test rýchlosti fallback AI analýzy (nesmie blokovať execution)"""
        from scripts.car_scraper import analyze_with_ai
        
        car_data = {'price': 15000, 'title': 'BMW 3'}
        
        start = time.time()
        # Spustíme 10 analýz po sebe
        for _ in range(10):
            analyze_with_ai(car_data)
        elapsed = time.time() - start
        
        # Jedna analýza (fallback) by mala byť takmer okamžitá
        avg_time = elapsed / 10
        assert avg_time < 0.05, f"Priemerný čas AI analýzy: {avg_time:.3f}s"

    def test_database_write_performance(self, app, test_user):
        """Test rýchlosti zápisu 50 nových inzerátov do DB"""
        from scripts.car_scraper import save_deals_to_db
        
        with app.app_context():
            from app import db, Project
            project = Project.query.filter_by(user_id=test_user.id, name='CarScraper Pro').first()
            if not project:
                project = Project(name='CarScraper Pro', user_id=test_user.id, is_active=True, api_key='perf_key_3')
                db.session.add(project)
                db.session.commit()
            project_id = project.id

        listings = []
        for i in range(50):
            listings.append({
                'title': f'Perf Test {i}',
                'price': 5000 + i,
                'link': f'https://perf.test/{i}_{time.time()}',
                'source': 'Bazoš.sk',
                'description': 'Speed test'
            })

        start = time.time()
        with app.app_context():
            saved = save_deals_to_db(listings, project_id)
        elapsed = time.time() - start
        
        assert saved == 50
        # Zápis 50 záznamov aj s AI analýzou by mal byť pod 1s
        assert elapsed < 1.0, f"Zápis 50 inzerátov trval {elapsed:.3f}s (limit 1.0s)"
