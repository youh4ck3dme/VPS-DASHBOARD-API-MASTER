#!/usr/bin/env python3
"""
CarScraper Pro - Scraping skript pre Bazoš.sk
Tento skript stiahne inzeráty, analyzuje ich pomocou AI a uloží do databázy
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import random
from decimal import Decimal

# Pridaj parent adresár do path pre import app modulov
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, Project, CarDeal

# Import proxy manager
try:
    from utils.proxy_manager import safe_request
    PROXY_AVAILABLE = True
except ImportError:
    PROXY_AVAILABLE = False
    import logging
    logging.warning('Proxy manager nie je dostupný, používam priame requesty')

def safe_extract_price(text):
    """Bezpečne vytiahne cenu z textu"""
    if isinstance(text, (int, float)):
        return int(text)
    if isinstance(text, Decimal):
        return int(text)
    # Nájde prvé číslo v texte
    numbers = re.findall(r'\d+', str(text).replace(' ', '').replace(',', ''))
    if numbers:
        return int(numbers[0])
    return 0

def scrape_bazos(search_query="octavia", min_price=1000, max_price=30000):
    """
    Scrapuje inzeráty - používa unified scraper s viacerými zdrojmi
    Automaticky používa fallback ak unified scraper nie je dostupný
    """
    try:
        from scripts.car_scraper_unified import scrape_all_sources
        results = scrape_all_sources(search_query, min_price, max_price, mode="parallel")
        # Vráť zoznam inzerátov (nie dict)
        if isinstance(results, dict):
            return results.get('listings', [])
        return results if isinstance(results, list) else []
    except ImportError as e:
        print(f"⚠️ Unified scraper nie je dostupný, používam fallback: {e}")
        return scrape_bazos_fallback(search_query, min_price, max_price)
    except Exception as e:
        print(f"⚠️ Chyba v unified scraper, používam fallback: {e}")
        return scrape_bazos_fallback(search_query, min_price, max_price)

def scrape_bazos_fallback(search_query="octavia", min_price=1000, max_price=30000):
    """Scrapuje inzeráty z Bazoš.sk s proxy rotáciou a ochranou proti blokovaniu"""
    url = f"https://auto.bazos.sk/skoda/?hledat={search_query}&rubriky=auto&hlokalita=&humkreis=25&cenaod={min_price}&cenado={max_price}&order=1"
    
    print(f"🔄 Sťahujem inzeráty z: {url}")
    
    # Použi safe_request s proxy ak je dostupné
    if PROXY_AVAILABLE:
        response = safe_request(url, max_retries=3, delay=2.0)
        if not response:
            print("❌ Chyba pri sťahovaní (všetky proxy zlyhali)")
            return []
    else:
        # Fallback na priamy request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            # Náhodný delay pre simuláciu ľudského správania
            time.sleep(random.uniform(1.0, 3.0))
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Chyba pri sťahovaní: {e}")
            return []
    
    if not response:
        return []
    
    # Skontroluj, či sme dostali validný HTML (nie blokovací page)
    response_text = response.text.lower() if hasattr(response, 'text') else ''
    if 'blocked' in response_text or 'access denied' in response_text:
        print("⚠️ Pravdepodobne blokovaný - rotujem proxy...")
        # Proxy sa nedá získať priamo z response, použije sa pri ďalšom requeste
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    listings = []
    
    items = soup.select("div.inzeraty")
    print(f"🔎 Našiel som {len(items)} inzerátov")
    
    for item in items:
        try:
            title_tag = item.select_one("h2.nadpis a")
            if not title_tag:
                continue
            
            title = title_tag.text.strip()
            href = title_tag.get('href', '')
            # Zajisti, že href je string
            if isinstance(href, list):
                href = href[0] if href else ''
            elif not isinstance(href, str):
                href = str(href) if href else ''
            link = "https://auto.bazos.sk" + href
            
            desc_tag = item.select_one("div.popis")
            description = desc_tag.text.strip() if desc_tag else "Bez popisu"
            
            price_tag = item.select_one("div.inzeratycena b")
            price_text = price_tag.text.strip() if price_tag else "0"
            price = safe_extract_price(price_text)
            
            if price > 500:
                listings.append({
                    "title": title,
                    "price": price,
                    "description": description,
                    "link": link,
                    "source": "Bazoš.sk"
                })
        except Exception as e:
            print(f"⚠️ Chyba pri parsovaní inzerátu: {e}")
            continue
    
    return listings[:10]  # Vráť prvých 10 pre testovanie

def analyze_with_ai(car_data, openai_client=None):
    """Analyzuje auto pomocou AI (ak je OpenAI dostupné)"""
    if not openai_client:
        # Fallback analýza bez AI
        market_value = int(car_data['price'] * 1.15)  # Odhad +15%
        profit = market_value - car_data['price']
        
        if profit > 2000:
            verdict = "KÚPIŤ"
            risk_level = "Nízke"
            reason = "Výrazne pod trhovou cenou"
        elif profit > 500:
            verdict = "RIZIKO"
            risk_level = "Stredné"
            reason = "Mierne pod trhovou cenou"
        else:
            verdict = "NEKUPOVAŤ"
            risk_level = "Nízke"
            reason = "Cena je v norme alebo nad trhovou"
        
        return {
            "odhad_ceny_cislo": market_value,
            "verdikt": verdict,
            "risk_level": risk_level,
            "dovod_skratene": reason
        }
    
    # TODO: Implementovať OpenAI analýzu ak je dostupná
    # Použi podobnú logiku ako v Colab template
    return {
        "odhad_ceny_cislo": int(car_data['price'] * 1.15),
        "verdikt": "RIZIKO",
        "risk_level": "Stredné",
        "dovod_skratene": "AI analýza nie je implementovaná"
    }

def save_deals_to_db(listings, project_id):
    """Uloží deals do databázy"""
    saved_count = 0
    
    with app.app_context():
        for listing in listings:
            try:
                # Skontroluj, či už existuje (podľa linku)
                existing = CarDeal.query.filter_by(link=listing['link']).first()
                if existing:
                    continue
                
                # AI analýza
                analysis = analyze_with_ai(listing)
                
                market_value = analysis.get('odhad_ceny_cislo', listing['price'])
                profit = market_value - listing['price']
                
                # type: ignore[call-arg]
                deal = CarDeal(
                    project_id=project_id,  # type: ignore[arg-type]
                    title=listing['title'],  # type: ignore[arg-type]
                    price=Decimal(str(listing['price'])),  # type: ignore[arg-type]
                    market_value=Decimal(str(market_value)),  # type: ignore[arg-type]
                    profit=Decimal(str(profit)),  # type: ignore[arg-type]
                    verdict=analysis.get('verdikt', 'RIZIKO'),  # type: ignore[arg-type]
                    risk_level=analysis.get('risk_level', 'Stredné'),  # type: ignore[arg-type]
                    reason=analysis.get('dovod_skratene', ''),  # type: ignore[arg-type]
                    source=listing.get('source', 'Bazoš.sk'),  # type: ignore[arg-type]
                    link=listing['link'],  # type: ignore[arg-type]
                    description=listing.get('description', ''),  # type: ignore[arg-type]
                    image_url=listing.get('image_url', ''),  # type: ignore[arg-type]
                    ai_analysis=json.dumps(analysis)  # type: ignore[arg-type]
                )
                
                db.session.add(deal)
                saved_count += 1
            except Exception as e:
                print(f"⚠️ Chyba pri ukladaní deal: {e}")
                continue
        
        db.session.commit()
        print(f"✅ Uložených {saved_count} nových deals")
    
    return saved_count

def main(user_id=None):
    """Hlavná funkcia
    
    Args:
        user_id: ID používateľa pre ktorého sa má vytvoriť/nájsť projekt.
                 Ak nie je zadaný, použije sa admin používateľ.
    """
    print("🚗 CarScraper Pro - Spúšťam scraping...")
    
    with app.app_context():
        # Nájdeme alebo vytvoríme CarScraper Pro projekt
        if user_id:
            # Hľadáme projekt pre konkrétneho používateľa
            project = Project.query.filter_by(name='CarScraper Pro', user_id=user_id).first()
        else:
            # Fallback na admin používateľa (pre kompatibilitu)
            project = Project.query.filter_by(name='CarScraper Pro').first()
        
        if not project:
            # Vytvoríme projekt
            from app import User
            if user_id:
                target_user = User.query.get(user_id)
            else:
                target_user = User.query.filter_by(username='admin').first()
            
            if not target_user:
                print("❌ Používateľ neexistuje!")
                return
            
            # type: ignore[call-arg]
            project = Project(
                name='CarScraper Pro',  # type: ignore[arg-type]
                api_key=os.urandom(24).hex(),  # type: ignore[arg-type]
                is_active=True,  # type: ignore[arg-type]
                user_id=target_user.id  # type: ignore[arg-type]
            )
            db.session.add(project)
            db.session.commit()
            print(f"✅ Vytvorený projekt CarScraper Pro (ID: {project.id}) pre používateľa {target_user.username}")
        
        # Scraping
        listings = scrape_bazos()
        
        if not listings:
            print("❌ Žiadne inzeráty na spracovanie")
            return
        
        # Uloženie do DB
        saved = save_deals_to_db(listings, project.id)
        
        print(f"✅ Hotovo! Spracovaných {len(listings)} inzerátov, uložených {saved} nových")

if __name__ == '__main__':
    main()

