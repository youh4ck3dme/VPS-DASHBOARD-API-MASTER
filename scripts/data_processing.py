#!/usr/bin/env python3
"""
Príklad skriptu na spracovanie dát
Tento skript demonštruje prácu s dátami, ktoré môžu byť použité v automatizáciách.
"""

import logging
import json
import sys
from datetime import datetime

# Nastavenie logovania
logging.basicConfig(
    filename='/var/www/api_dashboard/logs/data_processing.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def process_data(input_file=None):
    """
    Spracuje dáta zo súboru alebo iného zdroja

    Args:
        input_file (str): Cesta k vstupnému súboru
    """
    try:
        logging.info("Začínam spracovanie dát")

        # Príklad spracovania dát
        data = {
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "records_processed": 0,
            "errors": []
        }

        # Tu môžeš pridať logiku na:
        # - Čítanie dát z databázy
        # - Spracovanie CSV súborov
        # - Transformáciu dát
        # - Validáciu
        # atď.

        logging.info(f"Spracované {data['records_processed']} záznamov")

        # Uloženie výsledkov
        output_file = f"/var/www/api_dashboard/logs/processing_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logging.info(f"Výsledky uložené do {output_file}")
        return True

    except Exception as e:
        logging.error(f"Chyba pri spracovaní dát: {str(e)}")
        return False

def main():
    """Hlavná funkcia"""
    success = process_data()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
