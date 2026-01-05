#!/usr/bin/env python3
"""
Proxy Refresher - Background thread na automatické obnovovanie free proxy
"""

import time
import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)

class ProxyRefresher:
    """Automaticky obnovuje proxy pool každých X minút"""
    
    def __init__(self, refresh_interval_minutes: int = 30):
        self.refresh_interval = refresh_interval_minutes * 60  # Konvertuj na sekundy
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.proxy_manager = None
    
    def start(self, proxy_manager):
        """Spustí background thread na obnovovanie proxy"""
        if self.running:
            logger.warning('Proxy refresher už beží')
            return
        
        self.proxy_manager = proxy_manager
        self.running = True
        self.thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self.thread.start()
        logger.info(f'✅ Proxy refresher spustený (obnovovanie každých {self.refresh_interval // 60} minút)')
    
    def stop(self):
        """Zastaví background thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info('Proxy refresher zastavený')
    
    def _refresh_loop(self):
        """Hlavný loop pre obnovovanie proxy"""
        while self.running:
            try:
                time.sleep(self.refresh_interval)
                
                if not self.running:
                    break
                
                logger.info('🔄 Automatické obnovovanie proxy pool...')
                if self.proxy_manager:
                    success = self.proxy_manager.refresh_proxy_pool()
                    if success:
                        logger.info('✅ Proxy pool úspešne obnovený')
                    else:
                        logger.warning('⚠️ Nepodarilo sa obnoviť proxy pool')
            except Exception as e:
                logger.error(f'Chyba v proxy refresher loop: {e}', exc_info=True)

# Globálna inštancia
_refresher: Optional[ProxyRefresher] = None

def start_proxy_refresher(proxy_manager, interval_minutes: int = 30):
    """Spustí globálny proxy refresher"""
    global _refresher
    if _refresher is None:
        _refresher = ProxyRefresher(refresh_interval_minutes=interval_minutes)
        _refresher.start(proxy_manager)
    return _refresher

