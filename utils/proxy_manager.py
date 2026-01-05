#!/usr/bin/env python3
"""
Proxy Manager pre CarScraper Pro
Zabezpečuje rotáciu IP adries, User-Agent a ochranu proti blokovaniu
"""

import os
import random
import time
import logging
from typing import Optional, Dict, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Import free proxy fetcher a Tor support
try:
    from utils.free_proxy_fetcher import FreeProxyFetcher
    from utils.tor_proxy import TorProxy
    FREE_PROXY_AVAILABLE = True
except ImportError:
    FREE_PROXY_AVAILABLE = False
    logger.warning('Free proxy fetcher nie je dostupný')

class ProxyManager:
    """Správa proxy serverov a rotácie IP adries - ZADARMO a AUTOMATICKY"""
    
    def __init__(self, auto_fetch_free_proxies: bool = True):
        self.proxies: List[Dict[str, str]] = []
        self.current_proxy_index = 0
        self.failed_proxies: set = set()
        self.tor_proxy: Optional[Dict[str, str]] = None
        self.auto_fetch = auto_fetch_free_proxies
        self.user_agents: List[str] = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
        ]
        self.load_proxies()
        
        # Inicializuj Tor ak je dostupný
        if FREE_PROXY_AVAILABLE:
            try:
                tor = TorProxy()
                if tor.is_available:
                    self.tor_proxy = tor.get_tor_proxy()
                    logger.info('✅ Tor proxy dostupné (zadarmo)')
            except Exception as e:
                logger.debug(f'Tor nie je dostupný: {e}')
    
    def load_proxies(self):
        """Načíta proxy z environment variables, súboru alebo automaticky získava zadarmo"""
        # 1. Z .env alebo environment variables (priorita)
        proxy_list = os.getenv('PROXY_LIST', '')
        
        if proxy_list:
            # Formát: http://user:pass@ip:port alebo http://ip:port (oddelené čiarkou)
            for proxy_str in proxy_list.split(','):
                proxy_str = proxy_str.strip()
                if proxy_str:
                    self.proxies.append({'http': proxy_str, 'https': proxy_str})
        
        # 2. Ak nie sú proxy v env, skús načítať z súboru
        if not self.proxies:
            proxy_file = os.getenv('PROXY_FILE', 'proxies.txt')
            if os.path.exists(proxy_file):
                try:
                    with open(proxy_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                self.proxies.append({'http': line, 'https': line})
                except Exception as e:
                    logger.warning(f'Nepodarilo sa načítať proxy zo súboru: {e}')
        
        # 3. AK NIE SÚ ŽIADNE PROXY - AUTOMATICKY ZÍSKAJ ZADARMO
        if not self.proxies and self.auto_fetch and FREE_PROXY_AVAILABLE:
            logger.info('🔄 Žiadne proxy nastavené - získavam bezplatné proxy automaticky...')
            try:
                fetcher = FreeProxyFetcher()
                free_proxies = fetcher.fetch_all_free_proxies()
                if free_proxies:
                    self.proxies.extend(free_proxies)
                    logger.info(f'✅ Automaticky získaných {len(free_proxies)} bezplatných proxy')
                else:
                    logger.warning('⚠️ Nepodarilo sa získať bezplatné proxy')
            except Exception as e:
                logger.warning(f'Chyba pri získavaní bezplatných proxy: {e}')
        
        # 4. Ak stále nie sú proxy, použij Tor (ak je dostupný)
        if not self.proxies and self.tor_proxy:
            logger.info('📡 Používam Tor proxy (zadarmo, ale pomalé)')
            self.proxies.append(self.tor_proxy)
        
        logger.info(f'📊 Celkom načítaných {len(self.proxies)} proxy serverov')
    
    def get_random_user_agent(self) -> str:
        """Vráti náhodný User-Agent"""
        return random.choice(self.user_agents)
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Vráti ďalší proxy v rotácii"""
        if not self.proxies:
            # Ak nie sú proxy, skús získať nové automaticky
            if self.auto_fetch and FREE_PROXY_AVAILABLE:
                logger.info('🔄 Obnovujem proxy pool...')
                try:
                    fetcher = FreeProxyFetcher()
                    new_proxies = fetcher.fetch_all_free_proxies()
                    if new_proxies:
                        self.proxies.extend(new_proxies)
                        self.failed_proxies.clear()
                        logger.info(f'✅ Obnovených {len(new_proxies)} proxy')
                    elif self.tor_proxy:
                        logger.info('📡 Používam Tor proxy (fallback)')
                        self.proxies.append(self.tor_proxy)
                except Exception as e:
                    logger.warning(f'Chyba pri obnovovaní proxy: {e}')
            return None
        
        # Filtruj nefunkčné proxy
        available_proxies = [p for i, p in enumerate(self.proxies) if i not in self.failed_proxies]
        
        if not available_proxies:
            # Ak sú všetky nefunkčné, resetni a skús získať nové
            logger.warning('⚠️ Všetky proxy zlyhali, obnovujem pool...')
            self.failed_proxies.clear()
            
            # Skús získať nové free proxy
            if self.auto_fetch and FREE_PROXY_AVAILABLE:
                try:
                    fetcher = FreeProxyFetcher()
                    new_proxies = fetcher.fetch_all_free_proxies()
                    if new_proxies:
                        self.proxies = new_proxies
                        available_proxies = self.proxies
                        logger.info(f'✅ Obnovených {len(new_proxies)} proxy')
                    elif self.tor_proxy:
                        self.proxies = [self.tor_proxy]
                        available_proxies = self.proxies
                        logger.info('📡 Používam Tor proxy (fallback)')
                except Exception:
                    pass
            
            # Ak stále nie sú, použij všetky (aj nefunkčné)
            if not available_proxies:
                available_proxies = self.proxies
        
        # Rotácia
        proxy = available_proxies[self.current_proxy_index % len(available_proxies)]
        self.current_proxy_index += 1
        
        return proxy
    
    def refresh_proxy_pool(self):
        """Manuálne obnoví proxy pool (získaj nové free proxy)"""
        if FREE_PROXY_AVAILABLE:
            logger.info('🔄 Manuálne obnovujem proxy pool...')
            try:
                fetcher = FreeProxyFetcher()
                new_proxies = fetcher.fetch_all_free_proxies()
                if new_proxies:
                    self.proxies = new_proxies
                    self.failed_proxies.clear()
                    self.current_proxy_index = 0
                    logger.info(f'✅ Proxy pool obnovený: {len(new_proxies)} proxy')
                    return True
            except Exception as e:
                logger.error(f'Chyba pri obnovovaní proxy pool: {e}')
        return False
    
    def mark_proxy_failed(self, proxy: Dict[str, str]):
        """Označí proxy ako nefunkčný"""
        try:
            # Konvertuj proxy na dict ak je to MutableMapping
            proxy_dict = dict(proxy) if hasattr(proxy, 'items') else proxy
            # Nájdi index proxy v zozname
            for i, p in enumerate(self.proxies):
                if p == proxy_dict or (p.get('http') == proxy_dict.get('http') and p.get('https') == proxy_dict.get('https')):
                    self.failed_proxies.add(i)
                    logger.warning(f'Proxy {i} označený ako nefunkčný')
                    return
        except (ValueError, AttributeError, TypeError):
            pass
    
    def test_proxy(self, proxy: Dict[str, str], timeout: int = 5) -> bool:
        """Otestuje, či proxy funguje"""
        try:
            response = requests.get(
                'https://httpbin.org/ip',
                proxies=proxy,
                timeout=timeout,
                headers={'User-Agent': self.get_random_user_agent()}
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def create_session(self, use_proxy: bool = True) -> requests.Session:
        """Vytvorí requests session s proxy a retry logikou"""
        session = requests.Session()
        
        # Retry stratégia
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Proxy
        if use_proxy and self.proxies:
            proxy = self.get_next_proxy()
            if proxy:
                session.proxies = proxy
                logger.debug(f'Používam proxy: {proxy}')
        
        # User-Agent
        session.headers.update({
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'sk-SK,sk;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        return session

# Globálna inštancia
_proxy_manager: Optional[ProxyManager] = None

def get_proxy_manager() -> ProxyManager:
    """Získaj globálnu inštanciu ProxyManager"""
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = ProxyManager()
    return _proxy_manager

def safe_request(url: str, max_retries: int = 3, delay: float = 2.0, **kwargs) -> Optional[requests.Response]:
    """
    Bezpečný HTTP request s proxy rotáciou a retry logikou
    
    Args:
        url: URL na request
        max_retries: Maximálny počet pokusov
        delay: Delay medzi pokusmi (sekundy)
        **kwargs: Ďalšie argumenty pre requests.get()
    
    Returns:
        Response objekt alebo None ak zlyhalo
    """
    proxy_manager = get_proxy_manager()
    use_proxy = os.getenv('USE_PROXY', 'true').lower() == 'true'
    
    for attempt in range(max_retries):
        try:
            session = proxy_manager.create_session(use_proxy=use_proxy)
            
            # Náhodný delay (0.5-1.0 sekundy) pre 1-2 requesty za sekundu
            time.sleep(random.uniform(0.5, 1.0))
            
            response = session.get(url, timeout=15, **kwargs)
            
            # Skontroluj, či nie sme blokovaní
            if response.status_code == 403 or response.status_code == 429:
                logger.warning(f'Blokovaný request (status {response.status_code}), rotujem proxy...')
                if use_proxy and session.proxies:
                    proxy_dict = dict(session.proxies)  # type: ignore[arg-type]
                    proxy_manager.mark_proxy_failed(proxy_dict)
                time.sleep(delay * (attempt + 1))
                continue
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.ProxyError as e:
            logger.warning(f'Proxy chyba (pokus {attempt + 1}/{max_retries}): {e}')
            if use_proxy and 'session' in locals() and session.proxies:
                proxy_dict = dict(session.proxies)  # type: ignore[arg-type]
                proxy_manager.mark_proxy_failed(proxy_dict)
            time.sleep(delay * (attempt + 1))
            
        except requests.exceptions.RequestException as e:
            logger.warning(f'Request chyba (pokus {attempt + 1}/{max_retries}): {e}')
            time.sleep(delay * (attempt + 1))
    
    logger.error(f'Všetky pokusy zlyhali pre URL: {url}')
    return None

