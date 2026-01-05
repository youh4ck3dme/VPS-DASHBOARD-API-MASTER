import sys
import os
import requests
import json
from sqlalchemy import text
from app import app, db
from core.models.car_deal import CarDeal
import psutil
import platform

print("🚀 CarScraper Pro - Gigantic Final Test Suite")
print("============================================")

def check_system():
    print(f"🖥️  System: {platform.system()} {platform.release()}")
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    print(f"📊 CPU: {cpu_usage}%, RAM: {ram_usage}%, Disk: {disk_usage}%")
    if disk_usage > 90:
        print("⚠️  WARNING: Disk space critical!")
    else:
        print("✅ System resources OK")

def check_service():
    # Check if gunicorn is running
    gunicorn_running = False
    for process in psutil.process_iter(['name', 'cmdline']):
        if 'gunicorn' in process.info['name'] or (process.info['cmdline'] and 'gunicorn' in process.info['cmdline'][0]):
            gunicorn_running = True
            break
    
    if gunicorn_running:
        print("✅ Service 'gunicorn' is RUNNING")
    else:
        print("❌ Service 'gunicorn' is NOT running!")

def check_database():
    try:
        with app.app_context():
            # Check connection
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Check counts
            deal_count = CarDeal.query.count()
            print(f"📈 Total Car Deals in DB: {deal_count}")
            
            # Check latest deal
            latest = CarDeal.query.order_by(CarDeal.created_at.desc()).first()
            if latest:
                print(f"🆕 Latest Deal: {latest.title} ({latest.price}€) from {latest.source}")
                if hasattr(latest, 'full_specs') and latest.full_specs:
                    print("   ✅ Full Specs JSON present")
                else:
                    print("   ⚠️  Full Specs JSON missing on latest deal")
            else:
                print("⚠️  Database is empty")

    except Exception as e:
        print(f"❌ Database Error: {e}")

def check_scraping_config():
    from config import Config
    print(f"⚙️  Scraper Enabled: {Config.SCRAPER_ENABLED}")
    
def check_network():
    try:
        r = requests.get('https://www.google.com', timeout=5)
        if r.status_code == 200:
             print("✅ Internet connectivity OK")
        else:
             print(f"⚠️  Internet connectivity status: {r.status_code}")
    except Exception as e:
        print(f"❌ Internet connectivity ERROR: {e}")

def check_ssl_local():
    # Check if local endpoint responds
    try:
        r = requests.get('http://127.0.0.1:5000/landing')
        if r.status_code == 200:
            print("✅ Internal API endpoint OK (http://127.0.0.1:5000/landing)")
        else:
            print(f"❌ Internal API endpoint status: {r.status_code}")
    except Exception as e:
         print(f"❌ Internal API Error: {e}")

if __name__ == "__main__":
    print("\n--- System Checks ---")
    check_system()
    check_service()
    check_network()
    
    print("\n--- App Checks ---")
    check_scraping_config()
    check_database()
    check_ssl_local()
    
    print("\n============================================")
    print("🏁 Test Suite Completed")
