#!/usr/bin/env python3
"""
AI generovanie obsahu pomocou OpenAI
Tento skript používa OpenAI API na generovanie textu.
"""

import sys
import os
import logging
from datetime import datetime

# Pridaj parent directory do path pre import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

# Nastavenie logovania
logging.basicConfig(
    filename='/var/www/api_dashboard/logs/ai_generate.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_content(prompt):
    """
    Generuje obsah pomocou OpenAI API

    Args:
        prompt (str): Prompt pre AI generovanie

    Returns:
        str: Vygenerovaný obsah
    """
    try:
        import httpx
        from openai import OpenAI

        if not Config.OPENAI_API_KEY:
            logging.error("OpenAI API kľúč nie je nastavený")
            return None

        # Vytvor httpx klienta s trust_env=False aby sa vyhol proxy problémom
        http_client = httpx.Client(trust_env=False)
        client = OpenAI(api_key=Config.OPENAI_API_KEY, http_client=http_client)

        logging.info(f"Generujem obsah pre prompt: {prompt[:50]}...")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        generated_text = response.choices[0].message.content
        logging.info("Obsah vygenerovaný úspešne")

        return generated_text

    except Exception as e:
        logging.error(f"Chyba pri generovaní: {str(e)}")
        return None

def main():
    """Hlavná funkcia"""
    if len(sys.argv) < 2:
        print("Použitie: python3 ai_generate.py 'Tvoj prompt'")
        return 1

    prompt = ' '.join(sys.argv[1:])
    result = generate_content(prompt)

    if result:
        print("\n=== Vygenerovaný obsah ===")
        print(result)
        print("\n")
        return 0
    else:
        print("Chyba pri generovaní obsahu")
        return 1

if __name__ == "__main__":
    sys.exit(main())
