#!/usr/bin/env python3
"""
CarScraper - Bazoš.sk zdroj (PRVÝ/ZÁKLADNÝ)
Nezávislý scraping systém pre Bazoš.sk
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
    from utils.car_parser import parse_car_title, parse_region, is_blacklisted
    PROXY_AVAILABLE = True
except ImportError:
    PROXY_AVAILABLE = False
    # Mock parser ak import zlyhá
    def parse_car_title(t): return None, None
    def parse_region(l): return l
    def is_blacklisted(t): return False

def safe_extract_price(text):
    """Bezpečne vytiahne cenu z textu"""
    if isinstance(text, (int, float)):
        return int(text)
    numbers = re.findall(r'\d+', str(text).replace(' ', '').replace(',', ''))
    if numbers:
        return int(numbers[0])
    return 0

def scrape_bazos(search_query="octavia", min_price=1000, max_price=30000) -> List[Dict]:
    """
    Scrapuje inzeráty z Bazoš.sk (PRVÝ ZDROJ)
    
    Returns:
        List[Dict]: Zoznam inzerátov s kľúčmi: title, price, description, link, source
    """
    url = f"https://auto.bazos.sk/skoda/?hledat={search_query}&rubriky=auto&hlokalita=&humkreis=25&cenaod={min_price}&cenado={max_price}&order=1"
    
    print(f"🔄 [BAZOŠ] Sťahujem inzeráty z: {url}")
    
    # Použi safe_request s proxy ak je dostupné
    if PROXY_AVAILABLE:
        response = safe_request(url, max_retries=3, delay=2.0)
        if not response:
            print("❌ [BAZOŠ] Chyba pri sťahovaní (všetky proxy zlyhali)")
            return []
    else:
        # Fallback na priamy request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            time.sleep(random.uniform(0.5, 1.0))
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ [BAZOŠ] Chyba pri sťahovaní: {e}")
            return []
    
    if not response:
        return []
    
    # Skontroluj, či sme dostali validný HTML
    response_text = response.text.lower() if hasattr(response, 'text') else ''
    if 'blocked' in response_text or 'access denied' in response_text:
        print("⚠️ [BAZOŠ] Pravdepodobne blokovaný")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    listings = []
    
    items = soup.select("div.inzeraty")
    print(f"🔎 [BAZOŠ] Našiel som {len(items)} inzerátov")
    
    for item in items:
        try:
            title_tag = item.select_one("h2.nadpis a")
            if not title_tag:
                continue
            
            title = title_tag.text.strip()
            href = title_tag.get('href', '')
            if isinstance(href, list):
                href = href[0] if href else ''
            elif not isinstance(href, str):
                href = str(href) if href else ''
            link = "https://auto.bazos.sk" + href
            
            desc_tag = item.select_one("div.popis")
            description = desc_tag.text.strip() if desc_tag else "Bez popisu"
            
            # Blacklist filter (AAA Auto)
            if is_blacklisted(title) or is_blacklisted(description):
                continue
            
            # Location
            loc_tag = item.select_one("div.inzeratylok")
            location_text = loc_tag.text.strip() if loc_tag else "Neznáme"
            
            # Parse struct data
            brand, model = parse_car_title(title)
            region = parse_region(location_text)

            price_tag = item.select_one("div.inzeratycena b")
            price_text = price_tag.text.strip() if price_tag else "0"
            price = safe_extract_price(price_text)
            
            if price > 500:
                # Extrakcia obrázku
                img_tag = item.select_one("img")
                image_url = ""
                if img_tag:
                    image_url = img_tag.get("src", "")
                    # Bazoš má malé náhľady, skús získať väčšiu verziu
                    if image_url and "/mini/" in image_url:
                        image_url = image_url.replace("/mini/", "/img/")
                
                listings.append({
                    "title": title,
                    "price": price,
                    "description": description,
                    "location": location_text,
                    "brand": brand,
                    "model": model,
                    "region": region,
                    "link": link,
                    "source": "Bazoš.sk",
                    "image_url": image_url,
                    "full_specs": {
                        "basic_info": {
                            "brand": brand,
                            "model": model,
                            "price": price
                        }
                    }
                })
        except Exception as e:
            print(f"⚠️ [BAZOŠ] Chyba pri parsovaní inzerátu: {e}")
            continue
    
    print(f"✅ [BAZOŠ] Úspešne získaných {len(listings)} inzerátov")
    return listings[:15]  # Vráť prvých 15
