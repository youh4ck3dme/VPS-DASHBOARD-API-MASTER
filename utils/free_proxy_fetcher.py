#!/usr/bin/env python3
"""
Free Proxy Fetcher - Automaticky získava a testuje bezplatné proxy
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class FreeProxyFetcher:
    """Získava a testuje bezplatné proxy z rôznych zdrojov"""
    
    def __init__(self):
        self.working_proxies: List[Dict[str, str]] = []
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
    
    def fetch_proxyscrape(self) -> List[str]:
        """Získava proxy z ProxyScrape API (zadarmo)"""
        proxies = []
        try:
            # HTTP proxy
            url = "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                proxies.extend([f"http://{line.strip()}" for line in lines if line.strip()])
                logger.info(f'ProxyScrape: Načítaných {len(proxies)} proxy')
        except Exception as e:
            logger.warning(f'ProxyScrape chyba: {e}')
        return proxies
    
    def fetch_proxylist(self) -> List[str]:
        """Získava proxy z ProxyList.download (zadarmo)"""
        proxies = []
        try:
            url = "https://www.proxy-list.download/api/v1/get?type=http"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                for line in lines[1:]:  # Preskoč header
                    parts = line.strip().split(':')
                    if len(parts) == 2:
                        proxies.append(f"http://{parts[0]}:{parts[1]}")
                logger.info(f'ProxyList: Načítaných {len(proxies)} proxy')
        except Exception as e:
            logger.warning(f'ProxyList chyba: {e}')
        return proxies
    
    def fetch_free_proxy_list(self) -> List[str]:
        """Získava proxy z free-proxy-list.net (scraping)"""
        proxies = []
        try:
            url = "https://free-proxy-list.net/"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table', {'id': 'proxylisttable'})
                if table:
                    rows = table.find_all('tr')[1:21]  # Prvých 20
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            ip = cols[0].text.strip()
                            port = cols[1].text.strip()
                            if ip and port:
                                proxies.append(f"http://{ip}:{port}")
                logger.info(f'FreeProxyList: Načítaných {len(proxies)} proxy')
        except Exception as e:
            logger.warning(f'FreeProxyList chyba: {e}')
        return proxies
    
    def test_proxy(self, proxy_url: str, timeout: int = 5) -> bool:
        """Otestuje, či proxy funguje"""
        try:
            proxies = {'http': proxy_url, 'https': proxy_url}
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            if response.status_code == 200:
                return True
        except Exception:
            pass
        return False
    
    def test_proxy_batch(self, proxy_list: List[str], max_workers: int = 10) -> List[Dict[str, str]]:
        """Testuje viacero proxy paralelne"""
        working = []
        
        def test_single(proxy: str) -> Optional[Dict[str, str]]:
            if self.test_proxy(proxy):
                return {'http': proxy, 'https': proxy}
            return None
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(test_single, proxy): proxy for proxy in proxy_list[:50]}  # Max 50 naraz
            
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=6)
                    if result:
                        working.append(result)
                        if len(working) >= 10:  # Stačí 10 funkčných
                            break
                except Exception:
                    pass
        
        return working
    
    def fetch_all_free_proxies(self) -> List[Dict[str, str]]:
        """Získava proxy zo všetkých zdrojov a otestuje ich"""
        logger.info('🔄 Získavam bezplatné proxy...')
        
        all_proxies = []
        
        # Získaj proxy zo všetkých zdrojov
        all_proxies.extend(self.fetch_proxyscrape())
        time.sleep(1)  # Rate limiting
        all_proxies.extend(self.fetch_proxylist())
        time.sleep(1)
        all_proxies.extend(self.fetch_free_proxy_list())
        
        # Odstráň duplikáty
        unique_proxies = list(set(all_proxies))
        logger.info(f'📊 Celkom získaných proxy: {len(unique_proxies)}')
        
        if not unique_proxies:
            logger.warning('⚠️ Žiadne proxy neboli získané')
            return []
        
        # Otestuj proxy
        logger.info('🧪 Testujem proxy...')
        working = self.test_proxy_batch(unique_proxies)
        
        logger.info(f'✅ Nájdených {len(working)} funkčných proxy')
        return working

