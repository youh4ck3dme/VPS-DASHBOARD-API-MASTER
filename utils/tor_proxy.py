#!/usr/bin/env python3
"""
Tor Proxy Support - Bezplatné proxy cez Tor network
"""

import subprocess
import logging
import requests
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class TorProxy:
    """Správa Tor proxy (zadarmo, ale pomalé)"""
    
    def __init__(self):
        self.tor_port = 9050
        self.tor_control_port = 9051
        self.is_available = self.check_tor_installed()
    
    def check_tor_installed(self) -> bool:
        """Skontroluj, či je Tor nainštalovaný"""
        try:
            result = subprocess.run(['which', 'tor'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def install_tor_instructions(self) -> str:
        """Vráť inštrukcie na inštaláciu Tor"""
        return """
📦 Inštalácia Tor (zadarmo):

macOS:
  brew install tor

Linux (Ubuntu/Debian):
  sudo apt-get update
  sudo apt-get install tor

Linux (CentOS/RHEL):
  sudo yum install tor

Windows:
  Stiahni z: https://www.torproject.org/download/

Po inštalácii spusti:
  tor

Tor proxy bude dostupné na: socks5://127.0.0.1:9050
"""
    
    def get_tor_proxy(self) -> Optional[Dict[str, str]]:
        """Vráť Tor proxy konfiguráciu"""
        if not self.is_available:
            return None
        
        # Skús SOCKS5, ak nefunguje použij HTTP proxy (ak je nainštalovaný)
        return {
            'http': f'socks5h://127.0.0.1:{self.tor_port}',
            'https': f'socks5h://127.0.0.1:{self.tor_port}'
        }
    
    def test_tor(self) -> bool:
        """Otestuj, či Tor funguje"""
        proxy = self.get_tor_proxy()
        if not proxy:
            return False
        
        try:
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxy,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def renew_tor_circuit(self) -> bool:
        """Obnov Tor circuit (zmení IP adresu)"""
        if not self.is_available:
            return False
        
        try:
            import socket
            s = socket.socket()
            s.connect(('127.0.0.1', self.tor_control_port))
            s.send(b'AUTHENTICATE\r\n')
            response = s.recv(1024)
            if b'250' in response:
                s.send(b'SIGNAL NEWNYM\r\n')
                s.recv(1024)
                s.close()
                logger.info('✅ Tor circuit obnovený (nová IP)')
                return True
        except Exception as e:
            logger.warning(f'Tor circuit renewal failed: {e}')
        
        return False

