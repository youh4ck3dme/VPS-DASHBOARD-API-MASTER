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

# Importy
import json
try:
    from utils.proxy_manager import safe_request
    from utils.car_parser import parse_car_title, parse_region, is_blacklisted
    PROXY_AVAILABLE = True
except ImportError:
    PROXY_AVAILABLE = False
    def parse_car_title(t): return None, None
    def parse_region(l): return l
    def is_blacklisted(t): return False

def scrape_autobazar(search_query=None, min_price=None, max_price=5000) -> List[Dict]:
    """
    Scrapuje inzeráty z Autobazar.eu - Kategória LACNÉ AUTÁ (JSON API)
    
    Returns:
        List[Dict]: Zoznam inzerátov
    """
    # Force limit 5000 (Cheap Cars section)
    if max_price is None or max_price > 5000:
        max_price = 5000
    
    # URL s filtrom rok-od=2012 a cenou do 5000
    url = f"https://www.autobazar.eu/kategoria/lacne-auta/?cena-do={max_price}&rok-od=2012&order=od-najnovsich"
    
    print(f"🔄 [AUTOBAZAR] Sťahujem LACNÉ AUTÁ (JSON) z: {url}")
    
    if PROXY_AVAILABLE:
        response = safe_request(url, max_retries=3, delay=1.0)
    else:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        }
        try:
            time.sleep(random.uniform(1.0, 2.0))
            response = requests.get(url, headers=headers, timeout=15)
        except Exception as e:
            print(f"❌ [AUTOBAZAR] Chyba: {e}")
            return []
            
    if not response or not response.text:
        return []
        
    listings = []
    
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.select_one("#__NEXT_DATA__")
        
        if not script:
            print("❌ [AUTOBAZAR] __NEXT_DATA__ nenašiel sa (možno zmena HTML)")
            return []
            
        json_data = json.loads(script.text)
        
        # Navigácia v JSON štruktúre
        # props -> pageProps -> trpcState -> queries -> [0] -> state -> data -> data -> [items]
        try:
            queries = json_data.get("props", {}).get("pageProps", {}).get("trpcState", {}).get("queries", [])
            if not queries:
                 print("⚠️ [AUTOBAZAR] Prázdne trpc queries")
                 return []
            
            # Nájdi query, ktorá má dáta
            items = []
            for q in queries:
                data_block = q.get("state", {}).get("data", {})
                if data_block and "data" in data_block and isinstance(data_block["data"], list):
                    items = data_block["data"]
                    break
            
            print(f"🔎 [AUTOBAZAR] Našiel som {len(items)} inzerátov v JSON")
            
            for item in items[:24]: # Väčší buffer pre filtrovanie, vrátime 12
                try:
                    title = item.get("title") or f"{item.get('brandValue', '')} {item.get('modelValue', '')}"
                    user_name = item.get("user", {}).get("displayName", "")
                    
                    # Blacklist filter (AAA Auto)
                    if is_blacklisted(title) or is_blacklisted(user_name):
                        continue
                        
                    price = item.get("price") or item.get("finalPrice", 0)
                    
                    # Konštrukcia linku
                    # Skúsime formát /detail/{sefName}/{id}
                    sef_name = item.get("sefName")
                    item_id = item.get("id")
                    if sef_name and item_id:
                        link = f"https://www.autobazar.eu/detail/{sef_name}/{item_id}/"
                    else:
                        link = "" # Skip ak nevieme link
                        
                    # Popis / Výbava
                    desc = item.get("carEquipmentValue", "")
                    
                    # Lokácia
                    loc_data = item.get("location", {})
                    location_text = loc_data.get("name", "Neznáme")
                    
                    # Región (pre mapu) - skús parents
                    region_text = location_text
                    if "parentNames" in loc_data:
                        parents = loc_data["parentNames"]
                        # Zvyčajne "Nitriansky kraj", "Slovensko"
                        for p in parents:
                            if "kraj" in p:
                                region_text = p
                                break
                    
                    # Obrázok
                    image_url = ""
                    images = item.get("images", [])
                    if images and len(images) > 0:
                        previews = images[0].get("previewUrls", {})
                        image_url = previews.get("record_premium") or previews.get("record_preview") or previews.get("orig")
                    elif item.get("image"):
                         previews = item.get("image", {}).get("previewUrls", {})
                         image_url = previews.get("record_premium")
                    
                    # Normalize image URL
                    if image_url and not image_url.startswith("http"):
                        image_url = "https:" + image_url
                        
                    # Parse utils
                    brand, model = parse_car_title(title)
                    region = parse_region(region_text)

                    if price > 0 and link:
                        # Map to JSON Schema
                        full_specs = {
                            "basic_info": {
                                "brand": item.get("brandValue"),
                                "model": item.get("modelValue"),
                                "year": item.get("yearValue"),
                                "km": item.get("km"),
                                "fuel_type": item.get("fuelValue"),
                                "transmission": item.get("transmissionValue"),
                                "power_kw": item.get("powerValue"),
                                "engine_size_ccm": item.get("volumeValue")
                            },
                            "technical_details": {
                                "drive_type": item.get("driveValue"),
                                "body_style": item.get("categoryValue"),
                                "color": item.get("colorValue")
                            },
                            "equipment": {
                                "other_features": desc.split(",") if desc else []
                            }
                        }
                        
                        listings.append({
                            "title": title,
                            "price": int(price),
                            "description": desc,
                            "location": location_text,
                            "brand": brand,
                            "model": model,
                            "region": region,
                            "link": link,
                            "source": "Autobazar.eu",
                            "image_url": image_url,
                            "fuel_type": item.get("fuelValue"),
                            "transmission": item.get("transmissionValue"),
                            "full_specs": full_specs
                        })
                        
                    if len(listings) >= 12:
                        break
                except Exception as e:
                    print(f"⚠️ Chyba item parse: {e}")
                    continue
                    
        except AttributeError as e:
            print(f"❌ [AUTOBAZAR] Chyba štruktúry JSON: {e}")
            return []

    except Exception as e:
        print(f"❌ [AUTOBAZAR] Global error: {e}")
        return []
    
    print(f"✅ [AUTOBAZAR] Úspešne získaných {len(listings)} inzerátov")
    return listings[:12]

