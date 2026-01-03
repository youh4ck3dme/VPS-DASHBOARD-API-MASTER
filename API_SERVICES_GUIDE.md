# 🛒 Kde nakúpiť API pre VPS Dashboard

## 📋 Prehľad potrebných služieb

Tento dokument obsahuje **kompletný zoznam všetkých API služieb**, ktoré projekt potrebuje, kde ich kúpiť a koľko stoja.

---

## 🔴 KRITICKÉ API (Projekt ich potrebuje na základnú funkčnosť)

### 1. **OpenAI API** - AI Generovanie obsahu
**Čo to je**: API pre generovanie textu pomocou GPT-3.5/GPT-4  
**Kde kúpiť**: https://platform.openai.com/  
**Cena**: Pay-as-you-go (platiť podľa použitia)
- GPT-3.5 Turbo: $0.002 za 1000 tokenov (vstup)
- GPT-4: $0.03 za 1000 tokenov (vstup)
- **Odhadovaná cena**: 10-50 USD/mesiac (podľa používania)

**Ako získať**:
1. Choď na https://platform.openai.com/signup
2. Zaregistruj sa (potrebuješ email + telefónne číslo)
3. Prejdi na https://platform.openai.com/api-keys
4. Klikni "Create new secret key"
5. Skopíruj API kľúč (zobrazí sa len raz!)
6. Pridaj do `.env`:
   ```bash
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
   ```

**Prvé použitie zadarmo**: $5 kredit na prvých 3 mesiace

---

### 2. **Stripe API** - Platobná brána (karty)
**Čo to je**: Najpoužívanejšia platobná brána na svete  
**Kde kúpiť**: https://stripe.com/  
**Cena**: 2.9% + 0.30 EUR za transakciu (žiadny fixný mesačný poplatok)
- **Príklad**: Pri platbe 100 EUR zaplatíš 3.20 EUR Stripe

**Ako získať**:
1. Choď na https://dashboard.stripe.com/register
2. Zaregistruj sa (email + firma/jednotlivec)
3. Prejdi na **Developers → API keys**
4. Skopíruj:
   - **Publishable key** (začína `pk_test_...` alebo `pk_live_...`)
   - **Secret key** (začína `sk_test_...` alebo `sk_live_...`)
5. Pridaj do `.env`:
   ```bash
   STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxx
   STRIPE_PUBLIC_KEY=pk_test_xxxxxxxxxxxxxxxxxxxx
   ```

**Test režim**: Zadarmo neobmedzene (na testovanie)  
**Live režim**: Aktivuj po overení firmy/jednotlivca (Stripe pošle dokumenty)

**⚠️ Pre Slovensko**: Potrebuješ IČO alebo live ako jednotlivec

---

### 3. **Redis Cloud** - Caching a Rate Limiting
**Čo to je**: In-memory databáza pre rýchle caching  
**Kde kúpiť**: https://redis.com/try-free/  
**Cena**: Free tier: 30 MB RAM zadarmo (stačí pre tento projekt)
- Platený od $7/mesiac (250 MB RAM)

**Ako získať**:
1. Choď na https://redis.com/try-free/
2. Zaregistruj sa (Google/GitHub/Email)
3. Vytvor novú databázu:
   - Klikni **"New Database"**
   - Vyber **Free** plán
   - Vyber región (Europe - Amsterdam alebo Frankfurt)
   - Skopíruj **Redis Endpoint** (vyzerá ako `redis://default:pass@endpoint:port`)
4. Pridaj do `.env`:
   ```bash
   REDIS_URL=redis://default:tvoje_heslo@redis-12345.c123.eu-central-1.ec2.cloud.redislabs.com:12345
   ```

**Alternatíva (vlastný VPS)**:
```bash
# Nainštaluj Redis na svoj VPS
sudo apt install redis-server -y
sudo systemctl start redis
sudo systemctl enable redis

# V .env použi:
REDIS_URL=redis://localhost:6379/0
```

---

## 🟡 VOLITEĽNÉ API (Pre rozšírené funkcie)

### 4. **SumUp API** - Platby terminálom
**Čo to je**: Platobná brána pre terminálové platby  
**Kde kúpiť**: https://sumup.com/  
**Cena**: 
- Terminál: Od 29 EUR (jednorazovo)
- Transakcie: 1.95% za transakciu (bez fixného poplatku)

**Ako získať**:
1. Choď na https://me.sumup.com/signup
2. Zaregistruj sa ako obchodník
3. Objednaj SumUp terminál (príde poštou)
4. Po aktivácii choď na **Settings → API Credentials**
5. Vygeneruj API kľúč
6. Pridaj do `.env`:
   ```bash
   SUMUP_API_KEY=sup_sk_xxxxxxxxxxxxxxxxx
   ```

**Poznámka**: SumUp je vhodný, ak prijímaš platby osobne (obchod, služby)

---

### 5. **CoinGate API** - Kryptomeny (Bitcoin, Ethereum)
**Čo to je**: Platobná brána pre kryptomeny  
**Kde kúpiť**: https://coingate.com/  
**Cena**: 
- Business plán: 1% za transakciu
- Merchant plán: 0.5% za transakciu (od $499/mesiac)

**Ako získať**:
1. Choď na https://coingate.com/signup
2. Zaregistruj sa ako Merchant
3. Prejdi KYC verifikáciou (pošlú ti email)
4. Po schválení choď na **Account → API**
5. Vytvor nový **API Token**
6. Pridaj do `.env`:
   ```bash
   COINGATE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Poznámka**: CoinGate je vhodný, ak chceš prijímať Bitcoin, Ethereum, USDT

---

## 🟢 API PRE MONETIZÁCIU (Podľa nápadov z MONETIZATION_IDEAS.md)

### 6. **CoinGecko API** - Ceny kryptomien (pre NÁPAD 1)
**Čo to je**: Real-time ceny kryptomien  
**Kde kúpiť**: https://www.coingecko.com/en/api  
**Cena**: 
- **Free**: 10-50 volaní/minútu (stačí na začiatok)
- **Analyst**: $129/mesiac (500 volaní/minútu)
- **Pro**: $499/mesiac (neobmedzené)

**Ako získať**:
1. Choď na https://www.coingecko.com/en/api
2. Zaregistruj sa (email)
3. Prejdi na **Dashboard → API Keys**
4. Skopíruj API kľúč
5. Použi v `scripts/crypto_prices.py`:
   ```python
   import requests
   url = f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
   headers = {"x-cg-demo-api-key": "tvoj_api_key"}
   response = requests.get(url, headers=headers)
   ```

---

### 7. **ExchangeRate API** - Kurzové lístky (pre NÁPAD 1)
**Čo to je**: Real-time kurzové lístky (EUR/USD, atď.)  
**Kde kúpiť**: https://www.exchangerate-api.com/  
**Cena**: 
- **Free**: 1500 požiadaviek/mesiac
- **Basic**: $9/mesiac (100,000 požiadaviek)

**Ako získať**:
1. Choď na https://www.exchangerate-api.com/
2. Klikni **"Get Free Key"**
3. Zaregistruj sa (email)
4. Skopíruj API kľúč
5. Použi v `scripts/forex_rates.py`:
   ```python
   import requests
   url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/EUR"
   response = requests.get(url)
   ```

---

### 8. **Alpha Vantage API** - Ceny akcií (pre NÁPAD 1)
**Čo to je**: Real-time ceny akcií a komodít  
**Kde kúpiť**: https://www.alphavantage.co/  
**Cena**: 
- **Free**: 25 volaní/deň (stačí na testovanie)
- **Premium**: Od $49/mesiac (75 volaní/minútu)

**Ako získať**:
1. Choď na https://www.alphavantage.co/support/#api-key
2. Zadaj email a meno
3. Dostaneš API kľúč okamžite na email
4. Použi v `scripts/stock_prices.py`:
   ```python
   import requests
   url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey={api_key}"
   response = requests.get(url)
   ```

---

### 9. **OpenWeatherMap API** - Počasie (pre NÁPAD 1)
**Čo to je**: Real-time počasie  
**Kde kúpiť**: https://openweathermap.org/api  
**Cena**: 
- **Free**: 1000 volaní/deň (60 volaní/minútu)
- **Startup**: $40/mesiac (100,000 volaní/mesiac)

**Ako získať**:
1. Choď na https://home.openweathermap.org/users/sign_up
2. Zaregistruj sa (email)
3. Prejdi na **API keys**
4. Skopíruj API kľúč
5. Použi v `scripts/weather_data.py`:
   ```python
   import requests
   url = f"https://api.openweathermap.org/data/2.5/weather?q=Bratislava&appid={api_key}"
   response = requests.get(url)
   ```

---

### 10. **ScraperAPI** - Proxy pre Web Scraping (pre NÁPAD 2)
**Čo to je**: Rotujúce proxy pre scraping (obchádza blokovanie IP)  
**Kde kúpiť**: https://www.scraperapi.com/  
**Cena**: 
- **Hobby**: $49/mesiac (100,000 API volaní)
- **Startup**: $149/mesiac (1,000,000 API volaní)

**Ako získať**:
1. Choď na https://www.scraperapi.com/signup
2. Zaregistruj sa (email)
3. Dostaneš 5000 volaní zadarmo
4. Prejdi na **Dashboard → API Key**
5. Použi v `scripts/price_monitor.py`:
   ```python
   import requests
   url = "http://api.scraperapi.com"
   params = {
       "api_key": "tvoj_api_key",
       "url": "https://www.bazos.sk/..."
   }
   response = requests.get(url, params=params)
   ```

**Alternatíva (lacnejšia)**: Bright Data, Oxylabs

---

## 📦 Náklady - Súhrn

### Minimálna konfigurácia (len základné funkcie):
```
OpenAI API (Free trial):        $5 kredit (prvé 3 mesiace)
Stripe (test mode):             $0 (test režim)
Redis Cloud (Free):             $0 (30 MB RAM)
────────────────────────────────────────────────
SPOLU:                          $0-5 (prvé 3 mesiace)
```

### Štandardná konfigurácia (pre produkciu):
```
OpenAI API:                     $20/mesiac
Stripe:                         2.9% za transakciu
Redis Cloud (Free):             $0
────────────────────────────────────────────────
SPOLU:                          $20/mesiac + transakcie
```

### Plná konfigurácia (všetky funkcie + monetizácia):
```
OpenAI API:                     $20-50/mesiac
Stripe:                         2.9% za transakciu
Redis Cloud:                    $0 (Free)
SumUp:                          1.95% za transakciu
CoinGate:                       1% za transakciu
CoinGecko API:                  $129/mesiac
ExchangeRate API:               $9/mesiac
Alpha Vantage:                  $49/mesiac
OpenWeatherMap:                 $0 (Free)
ScraperAPI:                     $49/mesiac
────────────────────────────────────────────────
SPOLU:                          $256-286/mesiac + transakcie
```

---

## ⚡ Odporúčaná postupnosť nákupu

### Týždeň 1 (Zadarmo):
1. ✅ OpenAI API (Free trial - $5 kredit)
2. ✅ Stripe (Test mode)
3. ✅ Redis Cloud (Free tier)

**Investícia**: $0  
**Funkčnosť**: 80% (základné funkcie fungujú)

---

### Týždeň 2-4 (Platená verzia):
4. ✅ OpenAI API (platená verzia - $20/mesiac)
5. ✅ Stripe (Live mode - aktivuj platby)

**Investícia**: $20/mesiac  
**Funkčnosť**: 100% (plná produkčná verzia)

---

### Mesiac 2+ (Monetizácia):
6. ✅ CoinGecko API ($129/mesiac) - pre NÁPAD 1
7. ✅ ExchangeRate API ($9/mesiac) - pre NÁPAD 1
8. ✅ ScraperAPI ($49/mesiac) - pre NÁPAD 2

**Investícia**: $187-207/mesiac  
**Potenciálny príjem**: $1500+/mesiac (podľa MONETIZATION_IDEAS.md)  
**Zisk**: $1300+/mesiac

---

## 🔒 Bezpečnosť API kľúčov

**Nikdy neukáž API kľúče na GitHub!**

1. **Vždy použi `.env` súbor**:
   ```bash
   # .env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxx
   STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxx
   REDIS_URL=redis://default:pass@endpoint:port
   ```

2. **Pridaj `.env` do `.gitignore`**:
   ```bash
   echo ".env" >> .gitignore
   ```

3. **Vytvor `.env.example` (bez skutočných kľúčov)**:
   ```bash
   cp .env .env.example
   # Potom vymaž hodnoty v .env.example (nechaj len názvy premenných)
   ```

---

## 🎯 Zhrnutie pre 100% kondíciu

Pre **100% funkčnosť projektu v produkcii** potrebuješ:

### Kritické (musíš mať):
1. ✅ **OpenAI API** - $20/mesiac
2. ✅ **Stripe API** - 2.9% za transakciu
3. ✅ **Redis Cloud** - $0 (Free tier stačí)

**Celkom**: $20/mesiac + transakčné poplatky

### Voliteľné (ak chceš zarábať $1500/mesiac):
4. ✅ **CoinGecko API** - $129/mesiac (pre NÁPAD 1)
5. ✅ **ExchangeRate API** - $9/mesiac (pre NÁPAD 1)
6. ✅ **ScraperAPI** - $49/mesiac (pre NÁPAD 2)

**Celkom**: $207/mesiac

**ROI**: Pri zisku $1500/mesiac máš **$1293 čistého zisku** (87% marža)

---

## 📞 Podpora

Ak máš problém s registráciou alebo konfiguráciou API:
1. Pozri dokumentáciu v `README.md`
2. Skontroluj `.env.example` pre správny formát
3. Otestuj API kľúče cez `curl`:
   ```bash
   # Test OpenAI
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   
   # Test Redis
   redis-cli -u "$REDIS_URL" ping
   ```

---

**Projekt je pripravený zarábať!** 🚀💰

