#!/usr/bin/env python3
"""
Príklad automatizačného skriptu
Tento skript môžeš použiť ako šablónu pre svoje vlastné skripty.
"""

import logging
import sys
from datetime import datetime

# Nastavenie logovania
logging.basicConfig(
    filename='/var/www/api_dashboard/logs/example_script.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Hlavná funkcia skriptu"""
    try:
        logging.info("Začínam skript example_script.py")
        print(f"Skript beží: {datetime.now()}")

        # Tu môžeš pridať svoju logiku
        # Napríklad:
        # - Spracovanie dát
        # - Volanie API
        # - Generovanie reportov
        # - atď.

        logging.info("Skript dokončený úspešne")
        return 0

    except Exception as e:
        logging.error(f"Chyba v skripte: {str(e)}")
        print(f"Chyba: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
