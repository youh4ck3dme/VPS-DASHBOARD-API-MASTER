# Dokumentácia projektu: CarScraper Pro

## Prehľad systému

CarScraper Pro je pokročilý systém na monitorovanie trhu s jazdenými vozidlami na Slovensku. Systém automaticky sťahuje inzeráty z najpopulárnejších portálov, analyzuje ich a zobrazuje v prehľadnom dashboarde.

## Architektúra

- **Backend**: Flask (Python) s SQLAlchemy a SQLite.
- **Frontend**: React.js s moderným dizajnom (Glassmorphism, Dark Mode).
- **Scraping**: Vlastné skripty s podporou proxy rotácie a parsovania JSON dát.

## Kľúčové Funkcie

### 1. Inteligentný Scraping

- **Zdroje**: Bazoš.sk, Autobazar.eu.
- **Autobazar.eu (JSON)**: Používa extrakciu dát priamo z `__NEXT_DATA__` pre maximálnu spoľahlivosť.
- **Proxy Management**: Automatické získavanie a rotácia bezplatných proxy serverov.

### 2. Filtre a Pravidlá

- **AAA Auto Exclusion**: Systém automaticky filtruje a neukladá inzeráty od spoločnosti AAA Auto.
- **Onboarding (Package Start)**: Pri inicializácii systém stiahne maximálne **10 najlepších inzerátov pre každú z 15 top značiek**, čím zabezpečí okamžitú diverzitu v dashboarde.
- **Pravidelná Rotácia**: Background scraper beží každých **60 sekúnd** a v každom cykle spracuje inú značku zo zoznamu Top 15, čím udržiava dáta čerstvé bez preťaženia zdrojov.
- **Lacné Autá**: Špeciálna sekcia pre autá do 5000 € s ročníkom 2012 a novším.

### 3. Interaktívna Mapa

- Integrovaná SVG mapa Slovenska rozdelená na 8 krajov.
- Umožňuje geografické filtrovanie príležitostí jedným klikom.

## Technické Detaily

### Scraping Pravidlá (Pravidlá hry)

- Inzeráty od AAA Auto sú blokované globálne cez `is_blacklisted()` v `utils/car_parser.py`.
- Pri Autobazar.eu sa sťahuje vždy 12 najnovších kúskov spĺňajúcich kritériá.

### Spustenie Scrapera

```bash
python3 scripts/car_scraper.py
```

### Konfigurácia

Všetky hlavné nastavenia sa nachádzajú v `config.py`, kde je možné vypnúť/zapnúť background scraper alebo nastaviť porty.

---

#### Vytvorené pre VPS-DASHBOARD-API-MASTER
