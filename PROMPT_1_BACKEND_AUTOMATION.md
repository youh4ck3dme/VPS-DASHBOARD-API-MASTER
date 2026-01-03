# 🚀 PROMPT 1: Backend Automatizácia a Integrácia

## Úloha
Vylepši Flask backend pre CarScraper Pro tak, aby bol plne automatizovaný a integrovaný do dashboardu.

## Čo treba implementovať:

### 1. AUTOMATICKÉ VYTVORENIE PROJEKTU
**Problém**: CarScraper Pro projekt sa nevytvára automaticky pri prihlásení.

**Riešenie**:
- V `dashboard()` route (app.py, riadok ~193) pridaj automatické vytvorenie projektu
- Skontroluj, či používateľ už má projekt "CarScraper Pro"
- Ak nie, automaticky ho vytvor s:
  - `name='CarScraper Pro'`
  - `api_key=os.urandom(24).hex()`
  - `user_id=current_user.id`
  - `is_active=True`
- Zobraz flash message: "CarScraper Pro projekt bol automaticky vytvorený!"
- Ulož do databázy

### 2. INTEGRÁCIA DO DASHBOARDU
**Problém**: CarScraper nie je viditeľný v hlavnom dashboarde.

**Riešenie**:
- V `dashboard()` route pridaj:
  - Získanie CarScraper projektu
  - Získanie top 5 deals (najnovšie, verdict='KÚPIŤ')
  - Získanie štatistík CarScraper (total_deals, good_deals, total_profit)
- V `dashboard.html` template pridaj:
  - Widget s top 5 deals (karta s názvom "🚗 CarScraper Pro - Top Deals")
  - Zobraz: title, price, market_value, profit, verdict, link
  - Pridaj button "Zobraziť všetky deals" → `/carscraper`
  - Pridaj štatistiky CarScraper do stats sekcie
- V `base.html` template pridaj:
  - Link v navigácii: "CarScraper Pro" → `/carscraper`
  - Ikona: `fas fa-car`

### 3. AUTOMATICKÉ SCRAPING
**Problém**: Scraping musíš manuálne spúšťať.

**Riešenie**:
- Vytvor nový route `/api/carscraper/scrape` (POST, @login_required)
- Tento route spustí scraping v background:
  - Import `scripts.car_scraper` modul
  - Zavolaj `scrape_bazos()` a `save_deals_to_db()`
  - Vráť JSON: `{"status": "success", "deals_found": X, "deals_saved": Y}`
- Vytvor Flask route `/carscraper/run-scraping` (GET, @login_required)
  - Zobrazí stránku s button "Spustiť Scraping"
  - Po kliknutí zavolá `/api/carscraper/scrape` cez AJAX
  - Zobrazí progress a výsledok
- Pridaj automatické spustenie scraping každých 6 hodín:
  - Použi `APScheduler` alebo jednoduchý background thread
  - Skontroluj, či existuje CarScraper projekt
  - Spusti scraping len ak je projekt aktívny

### 4. VYLEPŠENIE SCRAPING SKRIPTU
**Problém**: Skript vytvára projekt len pre admin používateľa.

**Riešenie**:
- Uprav `scripts/car_scraper.py`:
  - Funkcia `main()` má prijať `user_id` parameter
  - Namiesto hardcoded admin, použij `user_id`
  - Ak `user_id` nie je zadaný, použij aktuálne prihláseného používateľa
- Uprav `save_deals_to_db()` aby neukladala duplikáty (už je, ale overiť)

## Technické požiadavky:

1. **Bezpečnosť**:
   - Všetky routes musia mať `@login_required`
   - Scraping môže spustiť len vlastník projektu
   - Validácia user_id pred vytvorením projektu

2. **Error Handling**:
   - Try-except bloky pre všetky databázové operácie
   - Logovanie chýb do `logs/app.log`
   - User-friendly error messages

3. **Performance**:
   - Lazy loading pre deals (len top 5 v dashboarde)
   - Caching štatistík (Redis ak je dostupný)
   - Background scraping aby neblokoval request

4. **Kódová štruktúra**:
   - Pridaj komentáre v slovenčine
   - Použi existujúce naming conventions
   - Dodržaj PEP 8

## Očakávaný výsledok:

Po implementácii:
- ✅ Pri prihlásení sa automaticky vytvorí CarScraper Pro projekt
- ✅ V dashboarde je viditeľný widget s top deals
- ✅ V navigácii je link na CarScraper Pro
- ✅ Môžeš manuálne spustiť scraping cez web rozhranie
- ✅ Scraping sa automaticky spúšťa každých 6 hodín
- ✅ Všetko funguje bez manuálnych krokov

## Súbory na úpravu:

1. `app.py` - dashboard route, nové routes
2. `templates/dashboard.html` - widget s deals
3. `templates/base.html` - navigácia
4. `scripts/car_scraper.py` - vylepšenie pre user_id
5. `requirements.txt` - pridať APScheduler ak použiješ

## Testovanie:

Po implementácii otestuj:
1. Prihlás sa → projekt sa vytvorí automaticky
2. Dashboard zobrazuje top deals
3. Klikni na "Spustiť Scraping" → funguje
4. Počkaj 6 hodín → automatické scraping funguje

---

**Dôležité**: Implementuj všetko čo je v tomto prompte. Kód musí byť produkčne pripravený, s error handlingom a logovaním.

