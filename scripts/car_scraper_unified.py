#!/usr/bin/env python3
"""
CarScraper Unified - Zjednotený systém s viacerými zdrojmi a fallback logikou
Kombinuje všetky zdroje a zabezpečuje redundanciu
"""

import sys
import os
import time
import logging
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeout

# Pridaj parent adresár do path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import jednotlivých scraperov
try:
    from scripts.car_scraper_bazos import scrape_bazos
    BAZOS_AVAILABLE = True
except ImportError:
    BAZOS_AVAILABLE = False
    print("⚠️ Bazoš scraper nie je dostupný")

try:
    from scripts.car_scraper_autobazar import scrape_autobazar
    AUTOBAZAR_AVAILABLE = True
except ImportError:
    AUTOBAZAR_AVAILABLE = False
    print("⚠️ Autobazar scraper nie je dostupný")

try:
    from scripts.car_scraper_autosme import scrape_autosme
    AUTOSME_AVAILABLE = True
except ImportError:
    AUTOSME_AVAILABLE = False
    print("⚠️ Auto.sme scraper nie je dostupný")

logger = logging.getLogger(__name__)

class UnifiedCarScraper:
    """
    Zjednotený scraper s viacerými zdrojmi a inteligentným fallback systémom
    """
    
    def __init__(self):
        self.sources = []
        
        # Zoznam dostupných zdrojov v poradí priority
        if BAZOS_AVAILABLE:
            self.sources.append({
                'name': 'Bazoš.sk',
                'function': scrape_bazos,
                'priority': 1,  # Najvyššia priorita
                'timeout': 20,
                'enabled': True
            })
        
        if AUTOBAZAR_AVAILABLE:
            self.sources.append({
                'name': 'Autobazar.eu',
                'function': scrape_autobazar,
                'priority': 2,
                'timeout': 20,
                'enabled': True  # Enabled for Cheap Cars (<5000 EUR)
            })
        
        if AUTOSME_AVAILABLE:
            self.sources.append({
                'name': 'Auto.sme.sk',
                'function': scrape_autosme,
                'priority': 3,
                'timeout': 20,
                'enabled': False  # DISABLED: URL returns 404 (site structure changed 2026-01)
            })
        
        # Zoradiť podľa priority
        self.sources.sort(key=lambda x: x['priority'])
        
        logger.info(f'✅ Unified scraper inicializovaný s {len(self.sources)} zdrojmi')
    
    def scrape_single_source(self, source: Dict, search_query: str = "octavia", 
                             min_price: int = 1000, max_price: int = 30000) -> Tuple[str, List[Dict], bool]:
        """
        Scrapuje jeden zdroj
        
        Returns:
            Tuple[str, List[Dict], bool]: (source_name, listings, success)
        """
        if not source['enabled']:
            return (source['name'], [], False)
        
        try:
            print(f"🔄 [{source['name']}] Spúšťam scraping...")
            start_time = time.time()
            
            # Spusti scraping s timeoutom
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    source['function'], 
                    search_query, 
                    min_price, 
                    max_price
                )
                try:
                    listings = future.result(timeout=source['timeout'])
                    elapsed = time.time() - start_time
                    
                    if listings and len(listings) > 0:
                        print(f"✅ [{source['name']}] Úspešne získaných {len(listings)} inzerátov za {elapsed:.2f}s")
                        return (source['name'], listings, True)
                    else:
                        print(f"⚠️ [{source['name']}] Žiadne inzeráty (alebo prázdny výsledok)")
                        return (source['name'], [], False)
                except FutureTimeout:
                    print(f"⏱️ [{source['name']}] Timeout po {source['timeout']}s")
                    return (source['name'], [], False)
                except Exception as e:
                    print(f"❌ [{source['name']}] Chyba: {e}")
                    return (source['name'], [], False)
        
        except Exception as e:
            logger.error(f"Chyba pri scraping {source['name']}: {e}", exc_info=True)
            return (source['name'], [], False)
    
    def scrape_all_parallel(self, search_query: str = "octavia", 
                           min_price: int = 1000, max_price: int = 30000,
                           min_sources: int = 1) -> Dict[str, any]:
        """
        Scrapuje všetky zdroje paralelne
        
        Args:
            search_query: Vyhľadávací dotaz
            min_price: Minimálna cena
            max_price: Maximálna cena
            min_sources: Minimálny počet úspešných zdrojov (fallback logika)
        
        Returns:
            Dict s výsledkami: {
                'success': bool,
                'total_listings': int,
                'unique_listings': int,
                'sources_used': List[str],
                'sources_failed': List[str],
                'listings': List[Dict],
                'stats': Dict
            }
        """
        print(f"\n{'='*60}")
        print(f"🚗 UNIFIED SCRAPER - Spúšťam všetky zdroje paralelne")
        print(f"{'='*60}\n")
        
        all_listings = []
        sources_used = []
        sources_failed = []
        source_results = {}
        
        # Spusti všetky zdroje paralelne
        with ThreadPoolExecutor(max_workers=len(self.sources)) as executor:
            futures = {
                executor.submit(
                    self.scrape_single_source, 
                    source, 
                    search_query, 
                    min_price, 
                    max_price
                ): source['name'] 
                for source in self.sources
            }
            
            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    name, listings, success = future.result(timeout=30)
                    
                    if success and listings:
                        sources_used.append(name)
                        all_listings.extend(listings)
                        source_results[name] = {
                            'count': len(listings),
                            'success': True
                        }
                        print(f"✅ [{name}] Pridaných {len(listings)} inzerátov")
                    else:
                        sources_failed.append(name)
                        source_results[name] = {
                            'count': 0,
                            'success': False
                        }
                        print(f"❌ [{name}] Zlyhalo")
                
                except Exception as e:
                    source_name = futures[future]
                    sources_failed.append(source_name)
                    source_results[source_name] = {
                        'count': 0,
                        'success': False,
                        'error': str(e)
                    }
                    print(f"❌ [{source_name}] Výnimka: {e}")
        
        # Odstráň duplikáty (podľa linku)
        unique_listings = []
        seen_links = set()
        
        for listing in all_listings:
            link = listing.get('link', '')
            if link and link not in seen_links:
                seen_links.add(link)
                unique_listings.append(listing)
        
        # Over, či máme dostatok úspešných zdrojov
        success = len(sources_used) >= min_sources
        
        stats = {
            'total_raw': len(all_listings),
            'unique': len(unique_listings),
            'duplicates_removed': len(all_listings) - len(unique_listings),
            'sources_success': len(sources_used),
            'sources_failed': len(sources_failed),
            'success_rate': len(sources_used) / len(self.sources) * 100 if self.sources else 0
        }
        
        print(f"\n{'='*60}")
        print(f"📊 VÝSLEDKY:")
        print(f"   Úspešné zdroje: {len(sources_used)}/{len(self.sources)}")
        print(f"   Celkom inzerátov: {len(all_listings)}")
        print(f"   Unikátnych: {len(unique_listings)}")
        print(f"   Duplikátov odstránených: {stats['duplicates_removed']}")
        print(f"{'='*60}\n")
        
        return {
            'success': success,
            'total_listings': len(all_listings),
            'unique_listings': len(unique_listings),
            'sources_used': sources_used,
            'sources_failed': sources_failed,
            'listings': unique_listings,
            'stats': stats,
            'source_results': source_results
        }
    
    def scrape_with_fallback(self, search_query: str = "octavia", 
                             min_price: int = 1000, max_price: int = 30000) -> List[Dict]:
        """
        Scrapuje s fallback logikou - skúša zdroje jeden po druhom
        
        Returns:
            List[Dict]: Zoznam inzerátov
        """
        print(f"\n{'='*60}")
        print(f"🔄 FALLBACK MODE - Skúšam zdroje postupne")
        print(f"{'='*60}\n")
        
        for source in self.sources:
            if not source['enabled']:
                continue
            
            name, listings, success = self.scrape_single_source(
                source, search_query, min_price, max_price
            )
            
            if success and listings:
                print(f"✅ [{name}] Úspešne získaných {len(listings)} inzerátov")
                return listings
            else:
                print(f"⚠️ [{name}] Zlyhalo, skúšam ďalší zdroj...")
                time.sleep(2)  # Krátka pauza medzi zdrojmi
        
        print("❌ Všetky zdroje zlyhali")
        return []

def scrape_all_sources(search_query: str = "octavia", 
                       min_price: int = 1000, 
                       max_price: int = 30000,
                       mode: str = "parallel") -> List[Dict]:
    """
    Hlavná funkcia pre unified scraping
    
    Args:
        search_query: Vyhľadávací dotaz
        min_price: Minimálna cena
        max_price: Maximálna cena
        mode: "parallel" (všetky naraz) alebo "fallback" (jeden po druhom)
    
    Returns:
        List[Dict]: Zoznam unikátnych inzerátov
    """
    scraper = UnifiedCarScraper()
    
    if mode == "parallel":
        result = scraper.scrape_all_parallel(search_query, min_price, max_price)
        return result['listings']
    else:
        return scraper.scrape_with_fallback(search_query, min_price, max_price)

if __name__ == '__main__':
    # Test
    results = scrape_all_sources(mode="parallel")
    print(f"\n✅ Celkom získaných {len(results)} unikátnych inzerátov")

