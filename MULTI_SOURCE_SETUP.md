# 🔄 Multi-Source Scraping System - Dokumentácia

## 📋 Prehľad

Systém používa **viacero nezávislých zdrojov** pre získavanie dát s automatickým fallback mechanizmom.

### 🎯 Hlavné vlastnosti:

1. **Redundancia** - Ak jeden zdroj zlyhá, použije sa druhý
2. **Paralelné spracovanie** - Všetky zdroje sa spúšťajú súčasne
3. **Automatický fallback** - Inteligentné prepínanie medzi zdrojmi
4. **Odstránenie duplikátov** - Automatické odfiltrovanie duplikátov
5. **Nezávislé systémy** - Každý zdroj je samostatný modul

---

## 📦 Zdroje dát

### 1. **Bazoš.sk** (PRVÝ ZDROJ - Základný)
- **Súbor:** `scripts/car_scraper_bazos.py`
- **Priorita:** 1 (najvyššia)
- **Status:** ✅ Aktívny
- **Timeout:** 20 sekúnd

### 2. **Autobazar.eu** (DRUHÝ ZDROJ - Záložný)
- **Súbor:** `scripts/car_scraper_autobazar.py`
- **Priorita:** 2
- **Status:** ✅ Aktívny
- **Timeout:** 20 sekúnd

### 3. **Auto.sme.sk** (TRETÍ ZDROJ - Záložný)
- **Súbor:** `scripts/car_scraper_autosme.py`
- **Priorita:** 3
- **Status:** ✅ Aktívny
- **Timeout:** 20 sekúnd

---

## 🔧 Ako to funguje?

### Režim 1: Paralelné spracovanie (Odporúčané)

Všetky zdroje sa spúšťajú **súčasne**:

```python
from scripts.car_scraper_unified import scrape_all_sources

results = scrape_all_sources(
    search_query="octavia",
    min_price=1000,
    max_price=30000,
    mode="parallel"
)
```

**Výhody:**
- ✅ Najrýchlejšie (všetko naraz)
- ✅ Maximálna redundancia
- ✅ Viac dát za kratší čas

### Režim 2: Fallback (Sekvenčné)

Zdroje sa skúšajú **jeden po druhom**:

```python
results = scrape_all_sources(
    search_query="octavia",
    min_price=1000,
    max_price=30000,
    mode="fallback"
)
```

**Výhody:**
- ✅ Menej náročné na zdroje
- ✅ Ak prvý zdroj funguje, ostatné sa nespúšťajú
- ✅ Úspora proxy/bandwidth

---

## 📊 Výstup

Unified scraper vráti:

```python
{
    'success': True,  # Úspešné ak aspoň 1 zdroj fungoval
    'total_listings': 45,  # Celkom inzerátov (pred odstránením duplikátov)
    'unique_listings': 38,  # Po odstránení duplikátov
    'sources_used': ['Bazoš.sk', 'Autobazar.eu'],  # Úspešné zdroje
    'sources_failed': ['Auto.sme.sk'],  # Zlyhané zdroje
    'listings': [...],  # Zoznam unikátnych inzerátov
    'stats': {
        'total_raw': 45,
        'unique': 38,
        'duplicates_removed': 7,
        'sources_success': 2,
        'sources_failed': 1,
        'success_rate': 66.67
    },
    'source_results': {
        'Bazoš.sk': {'count': 25, 'success': True},
        'Autobazar.eu': {'count': 20, 'success': True},
        'Auto.sme.sk': {'count': 0, 'success': False}
    }
}
```

---

## 🔄 Automatická integrácia

Systém je **automaticky integrovaný** do `car_scraper.py`:

```python
# V app.py alebo car_scraper.py
from scripts.car_scraper import scrape_bazos

# Automaticky použije unified scraper s fallback
listings = scrape_bazos()
```

**Žiadne zmeny nie sú potrebné!** Systém automaticky:
1. ✅ Skúša unified scraper
2. ✅ Ak zlyhá, použije fallback
3. ✅ Kombinuje výsledky zo všetkých zdrojov

---

## 🛠️ Konfigurácia

### Povolenie/zakázanie zdrojov

V `scripts/car_scraper_unified.py`:

```python
self.sources.append({
    'name': 'Bazoš.sk',
    'function': scrape_bazos,
    'priority': 1,
    'timeout': 20,
    'enabled': True  # ← Zmeniť na False pre zakázanie
})
```

### Zmena priority

Zmeniť `priority` hodnotu (nižšie = vyššia priorita):

```python
'priority': 1,  # Najvyššia priorita
'priority': 2,  # Stredná
'priority': 3,  # Najnižšia
```

### Timeout

Upraviť timeout pre každý zdroj:

```python
'timeout': 20,  # sekundy
```

---

## 📈 Monitoring

### Logy

Sleduj logy pre každý zdroj:

```bash
tail -f logs/app.log | grep -E "\[BAZOŠ\]|\[AUTOBAZAR\]|\[AUTO.SME\]"
```

### Štatistiky

Výstup obsahuje detailné štatistiky:

```python
stats = result['stats']
print(f"Úspešnosť: {stats['success_rate']:.1f}%")
print(f"Unikátnych: {stats['unique']}")
print(f"Duplikátov: {stats['duplicates_removed']}")
```

---

## 🐛 Troubleshooting

### Všetky zdroje zlyhajú?

1. **Skontroluj proxy:**
   ```bash
   # V logoch
   tail -f logs/app.log | grep proxy
   ```

2. **Skontroluj internetové pripojenie:**
   ```bash
   curl -I https://auto.bazos.sk
   ```

3. **Testuj jednotlivé zdroje:**
   ```python
   from scripts.car_scraper_bazos import scrape_bazos
   results = scrape_bazos()
   ```

### Jeden zdroj zlyhá?

**To je normálne!** Systém automaticky použije ostatné zdroje.

### Duplikáty?

Systém automaticky odstraňuje duplikáty podľa `link` poľa.

---

## 🚀 Pridanie nového zdroja

1. **Vytvor nový súbor:** `scripts/car_scraper_novysource.py`

2. **Implementuj funkciu:**
   ```python
   def scrape_novysource(search_query="octavia", min_price=1000, max_price=30000):
       # Tvoja logika
       return listings  # List[Dict]
   ```

3. **Pridaj do unified scraper:**
   ```python
   from scripts.car_scraper_novysource import scrape_novysource
   
   self.sources.append({
       'name': 'Nový Source',
       'function': scrape_novysource,
       'priority': 4,
       'timeout': 20,
       'enabled': True
   })
   ```

---

## ✅ Výhody tohto systému

1. **Redundancia** - Ak jeden zdroj zlyhá, ostatné fungujú
2. **Rýchlosť** - Paralelné spracovanie
3. **Spoľahlivosť** - Viac zdrojov = viac dát
4. **Flexibilita** - Ľahko pridať nový zdroj
5. **Automatizácia** - Všetko funguje automaticky

---

## 📝 Súhrn

✅ **3 nezávislé zdroje**  
✅ **Automatický fallback**  
✅ **Paralelné spracovanie**  
✅ **Odstránenie duplikátov**  
✅ **100% automatické**  

**Stačí spustiť aplikáciu a funguje to!** 🚀

