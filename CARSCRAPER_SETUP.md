# 🚗 CarScraper Pro - Kompletný Setup Guide

## 📋 Prehľad

CarScraper Pro je kompletná aplikácia pre automatické vyhľadávanie a analýzu áut na trhu pomocou AI.

## 🏗️ Architektúra

```
┌─────────────────┐
│  React Frontend │  (Port 3000 - dev, /carscraper - prod)
└────────┬────────┘
         │ API Calls
         ▼
┌─────────────────┐
│  Flask Backend  │  (Port 6002)
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│ SQLite │ │ Scraping │
│   DB   │ │  Scripts │
└────────┘ └──────────┘
```

## 🚀 Rýchly štart

### 1. Backend Setup (Flask)

```bash
# Aktivuj virtual environment
source venv/bin/activate

# Inštaluj závislosti (ak ešte nie sú)
pip install -r requirements.txt

# Vytvor databázu
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Spusti server
python app.py
```

Backend beží na `http://localhost:6002`

### 2. Frontend Setup (React)

```bash
cd frontend

# Inštaluj Node.js závislosti
npm install

# Spusti development server
npm run dev
```

Frontend beží na `http://localhost:3000`

### 3. Vytvorenie CarScraper Pro projektu

```bash
# Spusti scraping skript (automaticky vytvorí projekt)
python scripts/car_scraper.py
```

## 📡 API Endpointy

### Získanie deals

```bash
GET /api/carscraper/deals
GET /api/carscraper/deals?verdict=KÚPIŤ
GET /api/carscraper/deals?limit=10&offset=0
```

**Odpoveď:**
```json
{
  "deals": [
    {
      "id": 1,
      "title": "Škoda Octavia III 2.0 TDI",
      "price": 9500,
      "market_value": 12800,
      "profit": 3300,
      "verdict": "KÚPIŤ",
      "risk_level": "Nízke",
      "reason": "Cena je o 25% nižšia...",
      "source": "Bazoš.sk",
      "link": "https://...",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 50,
  "limit": 50,
  "offset": 0
}
```

### Získanie štatistík

```bash
GET /api/carscraper/stats
```

**Odpoveď:**
```json
{
  "total_deals": 3274,
  "good_deals": 132,
  "total_profit": 450000,
  "success_rate": 4.03
}
```

### Detail deal

```bash
GET /api/carscraper/deals/1
```

## 🔄 Automatizácia

### Cron job pre denné scraping

```bash
# Pridaj do crontab
crontab -e

# Denné scraping o 6:00
0 6 * * * cd /path/to/project && venv/bin/python scripts/car_scraper.py >> logs/carscraper.log 2>&1
```

### Systemd service (voliteľné)

Vytvor `/etc/systemd/system/carscraper.service`:

```ini
[Unit]
Description=CarScraper Pro Scraping Service
After=network.target

[Service]
Type=oneshot
User=www-data
WorkingDirectory=/var/www/api_dashboard
EnvironmentFile=/var/www/api_dashboard/.env
ExecStart=/var/www/api_dashboard/venv/bin/python /var/www/api_dashboard/scripts/car_scraper.py

[Install]
WantedBy=multi-user.target
```

## 🧪 Testovanie

### Test API endpointov

```bash
# Prihlás sa cez web rozhranie, potom:
curl -b cookies.txt http://localhost:6002/api/carscraper/stats
```

### Test scraping skriptu

```bash
python scripts/car_scraper.py
```

### Test frontendu

```bash
cd frontend
npm run dev
# Otvor http://localhost:3000
```

## 📊 Databázový model

```sql
CREATE TABLE car_deals (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    title VARCHAR(200),
    price DECIMAL(10,2),
    market_value DECIMAL(10,2),
    profit DECIMAL(10,2),
    verdict VARCHAR(20),
    risk_level VARCHAR(20),
    reason TEXT,
    source VARCHAR(100),
    link VARCHAR(500),
    description TEXT,
    image_url VARCHAR(500),
    ai_analysis TEXT,
    is_viewed BOOLEAN,
    created_at DATETIME
);
```

## 🔐 Autentifikácia

Všetky API endpointy vyžadujú prihlásenie:

1. Prihlás sa cez web rozhranie (`/login`)
2. Session cookie sa automaticky použije pre API volania
3. Frontend používa `credentials: 'include'` pre cookies

## 🎨 Frontend Features

- ✅ **Dark Mode** - Automatická detekcia OS preferencie
- ✅ **Real-time Updates** - Auto-refresh každých 30s
- ✅ **Filtering** - Filtrovanie podľa verdictu
- ✅ **Responsive** - Mobile-first design
- ✅ **Animations** - Smooth transitions
- ✅ **Loading States** - Skeleton loaders

## 🐛 Riešenie problémov

### Backend nefunguje

```bash
# Skontroluj logy
tail -f logs/app.log

# Skontroluj databázu
python -c "from app import app, db; app.app_context().push(); print(db.engine.table_names())"
```

### Frontend nefunguje

```bash
# Skontroluj konzolu prehliadača (F12)
# Skontroluj network tab pre API chyby
# Skontroluj CORS headers
```

### Scraping zlyhá

```bash
# Skontroluj internetové pripojenie
# Skontroluj, či Bazoš.sk je dostupný
# Skontroluj User-Agent headers
```

## 📈 Monitoring

### Health Check

```bash
curl http://localhost:6002/health
```

### API Stats

```bash
curl -b cookies.txt http://localhost:6002/api/carscraper/stats
```

## 🚀 Deployment

### 1. Build frontendu

```bash
cd frontend
npm run build
```

### 2. Spusti Flask s Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:6002 app:app
```

### 3. Nginx konfigurácia

```nginx
location /carscraper {
    alias /var/www/api_dashboard/static/carscraper;
    try_files $uri $uri/ /carscraper/index.html;
}

location /api {
    proxy_pass http://127.0.0.1:6002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## 📚 Ďalšie dokumenty

- `API_SERVICES_GUIDE.md` - Kde kúpiť API služby
- `MONETIZATION_IDEAS.md` - Ako zarábať
- `CarScraper_Pro_blueprint.md` - Architektúra
- `README.md` - Hlavná dokumentácia

---

**Projekt je pripravený na produkciu!** 🎉

