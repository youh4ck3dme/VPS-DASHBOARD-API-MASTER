# 🔒 Proxy Setup pre CarScraper Pro

## Prečo potrebuješ proxy?

Scraping každých **60 sekúnd** bez proxy = **100% blokovanie IP adresy** Bazoš.sk.

## ✅ Riešenie: Proxy Rotácia

### 1. **Kde kúpiť proxy?**

#### 🏆 Odporúčané (spoľahlivé):
- **Bright Data** (ex-Luminati): https://brightdata.com
  - Cena: od $500/mesiac
  - Kvalita: ⭐⭐⭐⭐⭐
  - Rotácia: Automatická
  - Podpora: 24/7

- **Smartproxy**: https://smartproxy.com
  - Cena: od $75/mesiac
  - Kvalita: ⭐⭐⭐⭐
  - Rotácia: Automatická
  - 10M+ IP adries

- **Oxylabs**: https://oxylabs.io
  - Cena: od $300/mesiac
  - Kvalita: ⭐⭐⭐⭐⭐
  - Rotácia: Automatická
  - Enterprise grade

#### 💰 Budget opcie:
- **Proxy-Cheap**: https://proxy-cheap.com
  - Cena: od $10/mesiac
  - Kvalita: ⭐⭐⭐
  - Rotácia: Manuálna
  - Menej spoľahlivé

- **ProxyRack**: https://www.proxyrack.com
  - Cena: od $50/mesiac
  - Kvalita: ⭐⭐⭐
  - Rotácia: Automatická

### 2. **Ako nastaviť proxy?**

#### Možnosť A: Environment Variables (odporúčané)

Pridaj do `.env`:
```bash
# Zapnúť/vypnúť proxy (true/false)
USE_PROXY=true

# Proxy list (čiarkou oddelené)
PROXY_LIST=http://user:pass@proxy1.com:8080,http://user:pass@proxy2.com:8080,http://user:pass@proxy3.com:8080

# Alebo súbor s proxy (jeden na riadok)
PROXY_FILE=proxies.txt
```

#### Možnosť B: Súbor `proxies.txt`

Vytvor súbor `proxies.txt` v root adresári:
```
http://user:pass@proxy1.com:8080
http://user:pass@proxy2.com:8080
http://user:pass@proxy3.com:8080
```

### 3. **Formát proxy**

```
# HTTP proxy
http://ip:port
http://user:password@ip:port

# HTTPS proxy
https://ip:port
https://user:password@ip:port

# SOCKS proxy (vyžaduje requests[socks])
socks5://ip:port
```

### 4. **Ako to funguje?**

1. **Proxy rotácia**: Každý request použije iný proxy
2. **User-Agent rotácia**: Náhodný User-Agent pre každý request
3. **Retry logika**: Automatický retry pri zlyhaní
4. **Delay**: Náhodný delay 1-3 sekundy medzi requestmi
5. **Error handling**: Automatické označenie nefunkčných proxy

### 5. **Testovanie proxy**

```bash
# Test proxy manuálne
python3 -c "
from utils.proxy_manager import get_proxy_manager
pm = get_proxy_manager()
print(f'Načítaných proxy: {len(pm.proxies)}')
for i, proxy in enumerate(pm.proxies):
    print(f'Proxy {i+1}: {proxy}')
    print(f'  Funkčný: {pm.test_proxy(proxy)}')
"
```

### 6. **Monitoring**

```bash
# Sleduj logy pre proxy chyby
tail -f logs/app.log | grep -i proxy

# Sleduj scraping progress
tail -f logs/app.log | grep -i scraping
```

### 7. **Bezplatné alternatívy (NEDOPORÚČANÉ)**

⚠️ **Varovanie**: Bezplatné proxy sú:
- Pomalé
- Nespôsobili
- Často blokované
- Môžu obsahovať malware

**NEPOUŽÍVAJ** pre produkciu!

### 8. **Odporúčaná konfigurácia**

Pre scraping každých 60 sekúnd:
- **Minimum**: 10-20 rotujúcich proxy
- **Odporúčané**: 50+ proxy
- **Enterprise**: 100+ proxy s automatickou rotáciou

### 9. **Cost analýza**

**Scenár 1: Budget (Proxy-Cheap)**
- 20 proxy: $10-20/mesiac
- Kvalita: ⭐⭐⭐
- Uptime: ~80%

**Scenár 2: Professional (Smartproxy)**
- 50 proxy: $75-150/mesiac
- Kvalita: ⭐⭐⭐⭐
- Uptime: ~95%

**Scenár 3: Enterprise (Bright Data)**
- Neobmedzené proxy: $500+/mesiac
- Kvalita: ⭐⭐⭐⭐⭐
- Uptime: ~99.9%

### 10. **Alternatívne riešenie: VPS s rotujúcimi IP**

Namiesto proxy môžeš:
1. Vytvoriť VPS s rotujúcimi IP adresami
2. Použiť VPN s rotáciou
3. Použiť Tor network (pomalé, ale zadarmo)

---

## 🎯 Quick Start

1. **Kúp proxy** (odporúčam Smartproxy - dobrý pomer cena/kvalita)
2. **Pridaj do `.env`**:
   ```
   USE_PROXY=true
   PROXY_LIST=http://user:pass@proxy1.com:8080,http://user:pass@proxy2.com:8080
   ```
3. **Restartuj server**
4. **Sleduj logy** - malo by fungovať bez blokovania

---

**Dôležité**: Bez proxy bude scraping každých 60 sekúnd **100% blokovaný**. Proxy je **nevyhnutné**!

