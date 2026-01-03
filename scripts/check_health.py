#!/usr/bin/env python3
"""
Utility skript pre kontrolu zdravia aplikácie
Použitie: python3 scripts/check_health.py
"""

import sys
import os
import requests
from datetime import datetime

# Pridaj parent directory do path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_health(base_url='http://localhost:6002'):
    """Kontrola health endpointu"""
    try:
        response = requests.get(f'{base_url}/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data.get('status', 'unknown')}")
            print(f"   Timestamp: {data.get('timestamp', 'unknown')}")
            print(f"   Services:")
            for service, status in data.get('services', {}).items():
                status_icon = "✅" if status == "connected" or status == "configured" else "⚠️"
                print(f"     {status_icon} {service}: {status}")
            return True
        else:
            print(f"❌ Health Check failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Nepodarilo sa pripojiť k {base_url}")
        print("   Uistite sa, že server beží!")
        return False
    except Exception as e:
        print(f"❌ Chyba: {str(e)}")
        return False

def check_api_docs(base_url='http://localhost:6002'):
    """Kontrola API dokumentácie"""
    try:
        response = requests.get(f'{base_url}/api/docs', timeout=5)
        if response.status_code == 200:
            print("✅ API Dokumentácia: Dostupné")
            return True
        else:
            print(f"⚠️  API Dokumentácia: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  API Dokumentácia: {str(e)}")
        return False

if __name__ == '__main__':
    print("🔍 Kontrola zdravia VPS Dashboard API...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:6002'
    print(f"🌐 Kontrolujem: {base_url}\n")
    
    health_ok = check_health(base_url)
    print()
    docs_ok = check_api_docs(base_url)
    
    print("-" * 50)
    if health_ok and docs_ok:
        print("✅ Všetky kontroly prešli úspešne!")
        sys.exit(0)
    else:
        print("⚠️  Niektoré kontroly zlyhali")
        sys.exit(1)

