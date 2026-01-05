# 🆓 ZADARMO Proxy Setup - Kompletný Návod

## ✅ Čo je automaticky nastavené?

**VŠETKO FUNGUJE ZADARMO A AUTOMATICKY!** 🎉

### 1. **Automatické získavanie free proxy**
- ✅ Získava proxy z 3 bezplatných zdrojov:
  - ProxyScrape API (zadarmo)
  - ProxyList.download (zadarmo)
  - Free-Proxy-List.net (scraping, zadarmo)
- ✅ Automaticky testuje a filtruje funkčné proxy
- ✅ Používa len overené, funkčné proxy

### 2. **Tor Network Support**
- ✅ Automaticky používa Tor ak je nainštalovaný
- ✅ Tor = zadarmo, anonymné, ale pomalšie
- ✅ Fallback ak free proxy zlyhajú

### 3. **Automatické obnovovanie**
- ✅ Proxy pool sa obnovuje každých 30 minút
- ✅ Automaticky získava nové free proxy
- ✅ Odstraňuje nefunkčné proxy

### 4. **Inteligentná rotácia**
- ✅ Každý request použije iný proxy
- ✅ Každý request použije iný User-Agent
- ✅ Automatická detekcia blokovania
- ✅ Retry logika s backoff

---

## 🚀 Quick Start (ŽIADNA KONFIGURÁCIA!)

**VŠETKO FUNGUJE AUTOMATICKY!** Stačí spustiť aplikáciu:

```bash
python app.py
```

Systém automaticky:
1. ✅ Získava bezplatné proxy
2. ✅ Testuje ich funkčnosť
3. ✅ Používa ich pre scraping
4. ✅ Obnovuje každých 30 minút

**ŽIADNE NASTAVOVANIE NIE JE POTREBNÉ!** 🎉

---

## 📦 Voliteľné: Inštalácia Tor (pre ešte lepšiu anonymitu)

Tor je **zadarmo** a poskytuje **anonymné proxy**:

### macOS:
```bash
brew install tor
tor
```

### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tor
sudo systemctl start tor
```

### Windows:
1. Stiahni z: https://www.torproject.org/download/
2. Nainštaluj a spusti

**Po inštalácii Tor sa automaticky použije ako fallback!**

---

## 🔧 Pokročilá konfigurácia (voliteľné)

Ak chceš použiť vlastné proxy (napr. platené), pridaj do `.env`:

```bash
# Vlastné proxy (priorita nad free proxy)
PROXY_LIST=http://user:pass@proxy1.com:8080,http://user:pass@proxy2.com:8080

# Alebo súbor
PROXY_FILE=proxies.txt
```

**Poznámka:** Ak nastavíš vlastné proxy, free proxy sa **nepoužijú**.

---

## 📊 Ako to funguje?

### Priorita proxy (od najvyššej):

1. **Vlastné proxy** (z `.env` alebo `proxies.txt`)
2. **Free proxy** (automaticky získané)
3. **Tor proxy** (ak je nainštalovaný)
4. **Priamy request** (bez proxy, menej bezpečné)

### Automatické obnovovanie:

- **Proxy pool refresh:** Každých 30 minút
- **Scraping interval:** Každých 60 sekúnd
- **Proxy rotácia:** Každý request
- **User-Agent rotácia:** Každý request

---

## ⚠️ Dôležité poznámky

### Free proxy sú:
- ✅ **Zadarmo**
- ✅ **Automatické**
- ✅ **Dostatočné pre väčšinu prípadov**

### Ale:
- ⚠️ Môžu byť pomalšie ako platené
- ⚠️ Niektoré môžu zlyhať (systém ich automaticky odstráni)
- ⚠️ Môžu mať obmedzenú rýchlosť

### Odporúčania:

1. **Pre testovanie:** Free proxy sú perfektné ✅
2. **Pre produkciu:** Zváž platené proxy ak potrebuješ:
   - Vysokú rýchlosť
   - 99.9% uptime
   - Neobmedzenú šírku pásma

---

## 🐛 Troubleshooting

### Proxy sa neobnovujú?

Skontroluj logy:
```bash
tail -f logs/app.log | grep proxy
```

### Tor nefunguje?

Skontroluj, či je Tor spustený:
```bash
# macOS/Linux
ps aux | grep tor

# Alebo skús manuálne
tor
```

### Žiadne proxy nefungujú?

Systém automaticky:
1. Skúsi získať nové free proxy
2. Použije Tor ak je dostupný
3. Spadne na priamy request (s varovaním)

---

## 📈 Monitoring

### Sleduj proxy pool:
```bash
# V logoch
tail -f logs/app.log | grep -i "proxy\|scraping"
```

### Test proxy manuálne:
```python
from utils.proxy_manager import get_proxy_manager
pm = get_proxy_manager()
print(f'Proxy v pool: {len(pm.proxies)}')
print(f'Funkčné proxy: {len(pm.proxies) - len(pm.failed_proxies)}')
```

---

## 🎯 Súhrn

✅ **VŠETKO JE ZADARMO A AUTOMATICKÉ!**
✅ **ŽIADNA KONFIGURÁCIA NIE JE POTREBNÁ!**
✅ **Systém automaticky získava, testuje a používa proxy!**
✅ **Tor je voliteľný bonus pre anonymitu!**

**Stačí spustiť aplikáciu a funguje to!** 🚀

