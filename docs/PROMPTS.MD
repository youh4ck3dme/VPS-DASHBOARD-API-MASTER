# CarScraper Pro - Prompty

Toto je presne 7 promptov, ktoré ti pokryjú celý projekt od technológií po monetizáciu. Každý prompt je navrhnutý pre maximálnu akčnosť a konkrétne výstupy.

***

## **Prompt 1: Technická Architektúra MVP**

```text
Si senior Python architekt. Môj projekt je Flask + PostgreSQL + Redis scraping platforma. Potrebujem detailný technický plán pre Phase 0 (2 týždne) a Phase 1 (4 týždne). 

VÝSTUP: 
- Konkrétny zoznam Python súborov a ich obsah (routes, models, scrapers)
- Presné SQL migrácie pre PostgreSQL (projects, cars, jobs tabuľky)
- Redis cache stratégia (ktoré dáta cacheovať, TTL)
- Flask app factory pattern s blueprintmi
- Error handling a retry logika pre scraper (bez proxy)

FORMAT: Markdown s kódom pripraveným na copy-paste. Žiadne všeobecné rady, len konkrétny kód.
```

***

## **Prompt 2: CarScraper Pro - Happy Path Implementácia**

```text
Si full-stack developer. Vytvor kompletný "happy path" pre CarScraper Pro:

1. Flask route `/scrape` ktorý prijme JSON (znacka, model, max_cena, max_km)
2. Bazoš scraper ktorý vráti 20 inzerátov s poliami: title, price, km, year, url, location
3. Data normalizácia (odstrániť "€", "km", konvertovať na int)
4. Uloženie do PostgreSQL
5. Simple Flask admin page `/admin/cars` ktorý zobrazí tabuľku s výsledkami
6. Telegram notifikácia s top 3 "najlepšími" ponukami (podľa cena/km ratio)

VÝSTUP: Kompletný Python kód pre všetky časti, vrátane HTML template pre admin. Použi Flask, SQLAlchemy, python-telegram-bot.
```

***

## **Prompt 3: AI Scoring & Z-Score Model**

```text
Si data scientist. Vytvor jednoduchý scoring model pre jazdené autá:

DÁTA: Každé auto má: price (EUR), km (tisíce), year (2020-2024), engine_power (kW)

ÚLOHA:
1. Vypočítaj Z-Score pre price (nižšia cena = lepšie) a km (nižšie km = lepšie)
2. Váhy: price 60%, km 30%, year 10%
3. Celkové skóre = vážený priemer Z-Scores
4. Pravidlo: Ak skóre > 1.5, označ ako "SUPER DEAL"
5. Gemini Flash prompt: "Analyzuj tento inzerát na auto a identifikuj riziká: {text}". Volaj len na autá so skóre > 1.5

VÝSTUP: Python funkcia `calculate_score(price, km, year, engine_power)` a `get_ai_analysis(inzerat_text)`. Vráť kompletný kód s komentármi.
```

***

## **Prompt 4: Monetizácia & Pricing Strategy**

```text
Si SaaS business stratég. Môj CarScraper Pro má 3 plány:

FREE: 5 scrapes/deň, žiadne notifikácie
HOBBY: 29 EUR/mesiac, 20 scrapes/deň, Telegram notifikácie
PRO: 79 EUR/mesiac, 100 scrapes/deň, API prístup, týždenné reporty

ÚLOHA:
1. Vypočítaj CAC (Customer Acquisition Cost) pre každý kanál (Reddit, Product Hunt, LinkedIn)
2. Navrh 3 marketingové kampane s budgetom 100 EUR/kanál
3. Vytvor Stripe Checkout linky pre HOBBY a PRO plán
4. Napíš email sequence pre onboarding (4 emaily: welcome, setup, first scrape, upgrade)

VÝSTUP: Kompletný business plán s číslami, kampaniami a email textami. Formát: Markdown.
```

***

## **Prompt 5: B2B Scraping Service - Generic Framework**

```text
Si senior developer. Vytvor univerzálny scraping framework pre B2B klientov:

ŠTRUKTÚRA:
- Project: name, url_pattern, schedule (cron), client_id
- Job: project_id, status, results_count, error_log
- Result: job_id, data (JSONB), scraped_at

ÚLOHA:
1. Python class `GenericScraper` ktorá prijíma: start_url, link_selector, data_selectors (dict)
2. Metóda `scrape()` ktorá vráti list slovníkov
3. Flask route `/api/v1/projects` (CRUD)
4. Flask route `/api/v1/projects/<id>/scrape` (spustí job)
5. Flask route `/api/v1/projects/<id>/data` (vráti posledné výsledky)
6. Jednoduchá auth: API key v header `X-API-Key`

VÝSTUP: Kompletný kód s Flask, SQLAlchemy, vrátane CREATE TABLE SQL. Formát: Python súbory s komentármi.
```

***

## **Prompt 6: Marketing & Launch Sequence**

```text
Si growth hacker. Priprav launch plán pre CarScraper Pro na 30 dní:

Cieľ: Získať 10 platiacich klientov (HOBBY plán = 29 EUR/mesiac)

KANÁLY:
- Reddit: r/cars, r/usedcars, r/AutoSlovakia
- Product Hunt
- LinkedIn (Slovak/Czech car enthusiasts)
- Facebook skupiny (jazdené autá)

ÚLOHA:
1. Vytvor content calendar (30 príspevkov, 1 denne)
2. Napíš 5 rôznych Reddit postov (každý iný uhol: AI, úspora peňazí, scam detection)
3. Priprav Product Hunt launch kit (tagline, description, 3 screenshoty, maker comment)
4. Vytvor 3 LinkedIn články s prípadovými štúdiami
5. Priprav 10 odpovedí na najčastejšie námietky (cena, bezpečnosť, legálnosť)

VÝSTUP: Kompletný launch kit s textami, hashtagmi a časovým plánom. Formát: Markdown.
```

***

## **Prompt 7: Legal, Etika & Risk Management**

```text
Si právnik špecializovaný na web scraping a SaaS. Priprav kompletný právny rámec:

ÚLOHY:
1. Terms of Service pre CarScraper Pro (zamerané na scraping Bazoš/Autobazar.eu)
   - Čo je povolené, čo nie
   - Zodpovednosť za dáta
   - Rate limiting a fair use

2. Privacy Policy (GDPR compliance pre EU užívateľov)
   - Aké dáta zbierame (email, API kľúče, search history)
   - Ako ich používame
   - Právo na vymazanie

3. Risk assessment:
   - Právne riziká scraping Bazoš (robots.txt, ToS)
   - Technické riziká (IP ban, CAPTCHA)
   - Finančné riziká (náklady na API, proxy)
   - Mitigácia pre každé riziko

4. Príprava "disclaimer" pre užívateľov:
   "Tento nástroj slúži na research. Overte si všetky informácie priamo u predajcu."

VÝSTUP: Kompletné právne dokumenty v Markdown, pripravené na použitie. Formát: 3 samostatné sekcie.
```

***

### **Ako používať tieto prompty v Antigravity:**

1. **Jeden prompt = jedna session** - nezadávaj všetky naraz
2. **Kontext je kľúčový** - pred každým promptom pripomeň AI, že ide o VPS Dashboard API projekt
3. **Iteruj** - ak výstup nie je dokonalý, doplňujúcimi prompty ("Vylepši túto časť...", "Pridaj error handling pre...")
4. **Ukladaj výstupy** - každý prompt ti vygeneruje konkrétny kód alebo dokument, ktorý si ulož do projektu

**Priorita spustenia:** Prompt 1 → Prompt 2 → Prompt 3 → Prompt 4 → Prompt 6 (paralelne) → Prompt 5 → Prompt 7 (keď máš prvých klientov)

Zdroje
