#!/usr/bin/env python3
"""
Cron kontrolný skript
Tento skript kontroluje naplánované automatizácie a spúšťa ich podľa rozvrhu.
Pridaj do crontab: * * * * * /var/www/api_dashboard/venv/bin/python3 /var/www/api_dashboard/cron_check.py
"""

import sys
import os
from datetime import datetime
import subprocess
import logging

# Pridaj parent directory do path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Automation, Project

# Nastavenie logovania
logging.basicConfig(
    filename='/var/www/api_dashboard/logs/cron_check.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def should_run(schedule, last_run):
    """
    Zistí, či by mal skript bežať podľa cron rozvrhu

    Args:
        schedule (str): Cron rozvrh (napr. "0 3 * * *")
        last_run (datetime): Čas posledného spustenia

    Returns:
        bool: True ak má skript bežať
    """
    try:
        from croniter import croniter
        from datetime import datetime

        cron = croniter(schedule, last_run or datetime(2000, 1, 1))
        next_run = cron.get_next(datetime)

        return datetime.now() >= next_run

    except ImportError:
        # Ak croniter nie je nainštalovaný, jednoduché fallback riešenie
        # Spusti skript ak nebol spustený viac ako hodinu
        if last_run is None:
            return True

        hours_since_last = (datetime.now() - last_run).total_seconds() / 3600
        return hours_since_last >= 1

    except Exception as e:
        logging.error(f"Chyba pri kontrole rozvrhu: {str(e)}")
        return False

def run_pending_automations():
    """Spustí naplánované automatizácie"""
    with app.app_context():
        try:
            automations = Automation.query.filter_by(is_active=True).all()
            logging.info(f"Kontrolujem {len(automations)} automatizácií")

            for auto in automations:
                if should_run(auto.schedule, auto.last_run):
                    project = Project.query.get(auto.project_id)

                    if not project:
                        logging.warning(f"Projekt {auto.project_id} nebol nájdený")
                        continue

                    script_path = os.path.join('/var/www/api_dashboard/scripts', auto.script_name)

                    if os.path.exists(script_path):
                        try:
                            logging.info(f"Spúšťam skript: {auto.script_name}")
                            subprocess.Popen(['python3', script_path])

                            auto.last_run = datetime.now()
                            db.session.commit()

                            logging.info(f"Skript {auto.script_name} spustený úspešne")

                        except Exception as e:
                            logging.error(f"Chyba pri spustení skriptu {auto.script_name}: {str(e)}")
                    else:
                        logging.warning(f"Skript {script_path} nebol nájdený")

        except Exception as e:
            logging.error(f"Chyba pri spracovaní automatizácií: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    run_pending_automations()
