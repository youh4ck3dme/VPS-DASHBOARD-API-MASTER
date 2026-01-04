#!/usr/bin/env python3
"""
CarScraper - Auto.sme.sk zdroj (TRETÍ/ZÁLOŽNÝ)
Nezávislý scraping systém pre Auto.sme.sk
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

def scrape_autosme(search_query="octavia", min_price=1000, max_price=30000) -> List[Dict]:
    """
    Scrapuje inzeráty z Auto.sme.sk (TRETÍ ZDROJ - FALLBACK)
    
    Returns:
        List[Dict]: Zoznam inzerátov s kľúčmi: title, price, description, link, source
    """
    # Auto.sme.sk URL formát
    url = f"https://auto.sme.sk/inzerat/auta/skoda/octavia?cena-od={min_price}&cena-do={max_price}"
    
    print(f"🔄 [AUTO.SME] Sťahujem inzeráty z: {url}")
    
    # Použi safe_request s proxy ak je dostupné
    if PROXY_AVAILABLE:
        response = safe_request(url, max_retries=3, delay=2.0)
        if not response:
            print("❌ [AUTO.SME] Chyba pri sťahovaní (všetky proxy zlyhali)")
            return []
    else:
        # Fallback na priamy request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "sk-SK,sk;q=0.9"
        }
        try:
            time.sleep(random.uniform(2.0, 4.0))
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ [AUTO.SME] Chyba pri sťahovaní: {e}")
            return []
    
    if not response:
        return []
    
    # Skontroluj, či sme dostali validný HTML
    response_text = response.text.lower() if hasattr(response, 'text') else ''
    if 'blocked' in response_text or 'access denied' in response_text or 'captcha' in response_text:
        print("⚠️ [AUTO.SME] Pravdepodobne blokovaný alebo CAPTCHA")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    listings = []
    
    # Auto.sme.sk selektory
    items = soup.select("article.ad, div.advertisement, .ad-item, .listing-item")
    
    # Alternatívne selektory
    if not items:
        items = soup.select("div[class*='ad'], div[class*='listing'], article[class*='ad']")
    
    print(f"🔎 [AUTO.SME] Našiel som {len(items)} inzerátov")
    
    for item in items:
        try:
            # Názov
            title_tag = (item.select_one("h2 a, h3 a, .title a, .ad-title a") or 
                        item.select_one("h2, h3, .title, .ad-title"))
            
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
                    link = "https://auto.sme.sk" + href
                elif href.startswith('http'):
                    link = href
                else:
                    link = "https://auto.sme.sk/" + href
            else:
                continue
            
            # Popis
            desc_tag = (item.select_one(".description, .desc, .text, .ad-description") or 
                       item.select_one("p, div[class*='desc']"))
            description = desc_tag.text.strip() if desc_tag else "Bez popisu"
            
            # Cena
            price_tag = (item.select_one(".price, .cena, .cost, .ad-price") or
                        item.select_one("span[class*='price'], div[class*='price']"))
            price_text = price_tag.text.strip() if price_tag else "0"
            price = safe_extract_price(price_text)
            
            if price > 500 and title:
                listings.append({
                    "title": title,
                    "price": price,
                    "description": description[:200],
                    "link": link,
                    "source": "Auto.sme.sk"
                })
        except Exception as e:
            print(f"⚠️ [AUTO.SME] Chyba pri parsovaní inzerátu: {e}")
            continue
    
    print(f"✅ [AUTO.SME] Úspešne získaných {len(listings)} inzerátov")
    return listings[:15]  # Vráť prvých 15

