# 🚀 CarScraper Pro - Vylepšené Prompty V2

> Prispôsobené pre existujúci VPS Dashboard API projekt (Flask + SQLAlchemy + Redis)

---

## 📋 Poradie použitia

```text
1. Prompt 1 → Refaktoring (ak chceš blueprinty)
2. Prompt 2 → Bazoš Scraper (happy path)
3. Prompt 3 → AI Scoring
4. Prompt 4 → Telegram notifikácie
5. Prompt 5 → Monetizácia
6. Prompt 6 → Marketing
7. Prompt 7 → Legal
```

---

## Prompt 1: Refaktoring na Blueprint Architektúru

```text
Si senior Flask architekt. Mám existujúci monolitický app.py (1400 riadkov) s:
- Flask-Login autentifikáciou
- SQLAlchemy modelmi (User, Project, Payment, Automation, AIRequest, CarDeal)
- Redis caching
- Stripe integráciou

ÚLOHA: Refaktoruj na Flask blueprint architektúru

POŽIADAVKY:
1. App factory pattern (create_app funkcia)
2. Blueprinty: auth, dashboard, projects, carscraper, api_v1
3. Zachovať všetky existujúce routes a funkcionalitu
4. Oddelené modely do app/models/*.py
5. Extensions (db, redis, login_manager) do app/extensions.py

VÝSTUP:
- Kompletná adresárová štruktúra
- app/__init__.py s create_app()
- app/extensions.py
- app/blueprints/auth.py (login, logout, settings)
- app/blueprints/carscraper/__init__.py (routes pre /carscraper)
- run.py (entry point)

FORMAT: Python kód pripravený na copy-paste s komentármi.
```

---

## Prompt 2: Bazoš Scraper - Happy Path

```text
Si Python developer špecializovaný na web scraping. Projekt používa Flask + SQLAlchemy.

EXISTUJÚCI MODEL (zachovaj):
```python
class CarDeal(db.Model):
    __tablename__ = 'car_deals'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    market_value = db.Column(db.Numeric(10, 2))
    profit = db.Column(db.Numeric(10, 2))
    verdict = db.Column(db.String(20))
    risk_level = db.Column(db.String(20))
    reason = db.Column(db.Text)
    source = db.Column(db.String(100))
    link = db.Column(db.String(500))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    ai_analysis = db.Column(db.Text)
    is_viewed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

ÚLOHA:

1. Vytvor `BazosCarScraper` class
2. Scrape <https://auto.bazos.sk/> pre zadanú značku/model
3. Extrahuj: title, price, km, year, location, url, image_url
4. Normalizuj dáta (odstráň "€", "km", konvertuj na int/float)
5. Ulož do CarDeal modelu
6. Retry logika: 3 pokusy, exponential backoff, user-agent rotation
7. Flask route POST /api/carscraper/scrape

VSTUP JSON:
{
  "brand": "skoda",
  "model": "octavia",
  "max_price": 15000,
  "max_km": 200000,
  "min_year": 2015
}

VÝSTUP: Kompletný scraper.py + route, vrátane error handling.

---

## Prompt 3: AI Scoring Model

```text

Si data scientist. Vytvor scoring model pre CarScraper Pro.

VSTUPY:

- price: cena v EUR
- km: kilometre
- year: rok výroby (2015-2024)
- engine_power: výkon v kW (voliteľné)

ALGORITMUS:

1. Z-Score pre price: z_price = (price - mean_price) / std_price
2. Z-Score pre km: z_km = (km - mean_km) / std_km
3. Age penalty: (2024 - year) * 0.1
4. Celkové skóre = (z_price *0.6) + (z_km* 0.3) + age_penalty

PRAVIDLÁ:

- score > 1.5 → SUPER_DEAL (zelená)
- score > 0.5 → GOOD_DEAL (modrá)
- score > -0.5 → OK (šedá)
- score <= -0.5 → SKIP (červená)

AI ANALÝZA (len pre SUPER_DEAL):

```python
prompt = f"""
Analyzuj tento inzerát na auto a identifikuj potenciálne riziká:

Značka/Model: {title}
Cena: {price} EUR
Kilometre: {km} km
Rok výroby: {year}
Popis: {description}

Odpovedz v JSON formáte:
{{
  "risks": ["riziko1", "riziko2"],
  "red_flags": ["varovanie1"],
  "recommendation": "KÚPIŤ/OVERIŤ/NEKUPOVAŤ",
  "estimated_market_value": 12000
}}
"""
```

VÝSTUP:

- scoring.py s funkciami calculate_score() a get_ai_analysis()
- Integrácia s existujúcou OpenAI konfiguráciou (app.config['OPENAI_API_KEY'])

---

## Prompt 4: Telegram Notifikácie

```text

Si Python developer. Pridaj Telegram notifikácie do CarScraper Pro.

POŽIADAVKY:

1. Vytvor Telegram bota cez @BotFather
2. Pošli notifikáciu pri SUPER_DEAL (score > 1.5)
3. Formát správy:
   🚗 SUPER DEAL!
   {title}
   💰 {price} EUR (market: {market_value} EUR)
   📍 {location}
   ⭐ Skóre: {score}
   🔗 {url}

4. Denný digest: Top 3 deals o 18:00
5. Uloženie chat_id do User modelu (nové pole: telegram_chat_id)

KONFIGURÁCIA (.env):
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_ADMIN_CHAT_ID=xxx

VÝSTUP:

- notifications.py s TelegramNotifier class
- Flask route /settings/telegram pre prepojenie účtu
- APScheduler alebo cron pre denný digest

```

---

## Prompt 5: Monetizácia - Stripe Subscription

```text

Si SaaS developer. Implementuj subscription plány pre CarScraper Pro.

PLÁNY:

- FREE: 5 scrapes/deň, žiadne notifikácie, žiadne AI
- HOBBY (29 EUR/mes): 20 scrapes/deň, Telegram, základné AI
- PRO (79 EUR/mes): 100 scrapes/deň, priority scraping, full AI, API prístup

EXISTUJÚCA STRIPE INTEGRÁCIA:

- stripe.api_key = app.config['STRIPE_SECRET_KEY']
- Stripe je už v requirements.txt

ÚLOHY:

1. Vytvor Stripe Products a Prices (Products: carscraper_hobby, carscraper_pro)
2. Flask route `/subscribe/<plan>` → Stripe Checkout
3. Webhook /webhook/stripe pre subscription.created/canceled
4. Middleware/decorator @require_plan('hobby') pre rate limiting
5. Nové User pole: subscription_plan (free/hobby/pro), subscription_id

VÝSTUP:

- stripe_service.py s create_checkout(), handle_webhook()
- Dekorátor @require_plan()
- HTML pricing page template

```

---

## Prompt 6: Marketing & Launch

```text

Si growth hacker. Priprav 30-dňový launch plán pre CarScraper Pro.

CIEĽ: 10 platiacich zákazníkov (HOBBY = 29 EUR)

PERSONA:

- Slovenský/Český zákazník
- Hľadá jazdené auto
- Nechce byť podvedený
- Nemá čas prechádzať tisíce inzerátov

KANÁLY (SK/CZ focused):

- Reddit: r/Slovakia, r/czech, r/AutoSlovakia
- Facebook: skupiny "Jazdené autá", "Autobazar"
- YouTube: review video (5 min demo)

CONTENT:

1. 10 Reddit postov (rôzne uhly: AI, úspora času, detekcia scamov)
2. 3 Facebook príspevky s case study
3. Script pre YouTube video
4. Product Hunt launch kit

VÝSTUP: Kompletný content calendar s textami, nie všeobecné rady.

```

---

## Prompt 7: Legal - ToS & Privacy

```text

Si právnik špecializovaný na SaaS a GDPR. Priprav právne dokumenty.

KONTEXT:

- Služba scrapuje verejne dostupné inzeráty z Bazoš.sk, Autobazar.eu
- Zbierame: email, Telegram chat_id, história vyhľadávania
- Platby cez Stripe
- EU používatelia

DOKUMENTY:

1. Terms of Service (SK jazyk)
   - Čo služba robí a nerobí
   - Obmedzenie zodpovednosti
   - Fair use policy (max scrapes/deň)

2. Privacy Policy (GDPR compliant, SK jazyk)
   - Aké dáta zbierame
   - Účel spracovania
   - Právo na vymazanie
   - Cookie policy

3. Disclaimer na dashboard:
   "Dáta pochádzajú z verejných zdrojov. Vždy overte informácie priamo u predajcu."

VÝSTUP: Kompletné dokumenty v Markdown, pripravené na použitie.

```

---

## 💡 Tipy pre použitie

1. **Kontext je kľúčový** - pred každým promptom pripomeň:
   > "Projekt: Flask + SQLAlchemy + Redis, existujúci model CarDeal, config v .env"

2. **Jeden prompt = jedna session** - nezadávaj všetky naraz

3. **Iteruj** - ak výstup nie je dokonalý:
   > "Vylepši error handling pre timeout"
   > "Pridaj logging"

4. **Testuj priebežne** - po každom prompte spusti kód a overte
