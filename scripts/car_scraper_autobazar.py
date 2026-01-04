#!/usr/bin/env python3
"""
CarScraper - Autobazar.eu zdroj (DRUHÝ/ZÁLOŽNÝ)
Nezávislý scraping systém pre Autobazar.eu
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from typing import List, Dict, Optional

# Pridaj parent adresár do path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import proxy manager
try:
    from utils.proxy_manager import safe_request
    PROXY_AVAILABLE = True
except ImportError:
    PROXY_AVAILABLE = False

def safe_extract_price(text):
    """Bezpečne vytiahne cenu z textu"""
    if isinstance(text, (int, float)):
        return int(text)
    numbers = re.findall(r'\d+', str(text).replace(' ', '').replace(',', '').replace('.', ''))
    if numbers:
        return int(numbers[0])
    return 0

def scrape_autobazar(search_query="octavia", min_price=1000, max_price=30000) -> List[Dict]:
    """
    Scrapuje inzeráty z Autobazar.eu (DRUHÝ ZDROJ - FALLBACK)
    
    Returns:
        List[Dict]: Zoznam inzerátov s kľúčmi: title, price, description, link, source
    """
    # Autobazar.eu má iný formát URL
    url = f"https://www.autobazar.eu/skoda/octavia/?cena-od={min_price}&cena-do={max_price}"
    
    print(f"🔄 [AUTOBAZAR] Sťahujem inzeráty z: {url}")
    
    # Použi safe_request s proxy ak je dostupné
    if PROXY_AVAILABLE:
        response = safe_request(url, max_retries=3, delay=2.0)
        if not response:
            print("❌ [AUTOBAZAR] Chyba pri sťahovaní (všetky proxy zlyhali)")
            return []
    else:
        # Fallback na priamy request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "sk-SK,sk;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        try:
            time.sleep(random.uniform(1.5, 3.5))
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ [AUTOBAZAR] Chyba pri sťahovaní: {e}")
            return []
    
    if not response:
        return []
    
    # Skontroluj, či sme dostali validný HTML
    response_text = response.text.lower() if hasattr(response, 'text') else ''
    if 'blocked' in response_text or 'access denied' in response_text or 'captcha' in response_text:
        print("⚠️ [AUTOBAZAR] Pravdepodobne blokovaný alebo CAPTCHA")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    listings = []
    
    # Autobazar.eu má inú HTML štruktúru - skús rôzne selektory
    items = soup.select("div.listing-item, div.car-item, article.listing, div.offer-item")
    
    # Ak nič nenašiel, skús alternatívne selektory
    if not items:
        items = soup.select("div[class*='car'], div[class*='offer'], div[class*='listing']")
    
    print(f"🔎 [AUTOBAZAR] Našiel som {len(items)} inzerátov")
    
    for item in items:
        try:
            # Rôzne možnosti pre názov
            title_tag = (item.select_one("h2 a, h3 a, .title a, .name a, a.title") or 
                        item.select_one("h2, h3, .title, .name"))
            
            if not title_tag:
                continue
            
            title = title_tag.text.strip()
            
            # Link
            link_tag = item.select_one("a")
            if link_tag and link_tag.get('href'):
                href = link_tag.get('href')
                if isinstance(href, list):
                    href = href[0] if href else ''
                if href.startswith('/'):
                    link = "https://www.autobazar.eu" + href
                elif href.startswith('http'):
                    link = href
                else:
                    link = "https://www.autobazar.eu/" + href
            else:
                continue
            
            # Popis
            desc_tag = (item.select_one(".description, .desc, .text, p") or 
                       item.select_one("div[class*='desc'], div[class*='text']"))
            description = desc_tag.text.strip() if desc_tag else "Bez popisu"
            
            # Cena - rôzne možnosti
            price_tag = (item.select_one(".price, .cena, .cost, b.price, span.price") or
                        item.select_one("div[class*='price'], span[class*='price']"))
            price_text = price_tag.text.strip() if price_tag else "0"
            price = safe_extract_price(price_text)
            
            if price > 500 and title:
                listings.append({
                    "title": title,
                    "price": price,
                    "description": description[:200],  # Obmedz na 200 znakov
                    "link": link,
                    "source": "Autobazar.eu"
                })
        except Exception as e:
            print(f"⚠️ [AUTOBAZAR] Chyba pri parsovaní inzerátu: {e}")
            continue
    
    print(f"✅ [AUTOBAZAR] Úspešne získaných {len(listings)} inzerátov")
    return listings[:15]  # Vráť prvých 15

