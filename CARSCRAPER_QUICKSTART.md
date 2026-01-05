# 🚀 CarScraper Pro - Rýchly štart

## ✅ Čo je hotové

1. ✅ **Backend API** - Flask endpointy pre deals a štatistiky
2. ✅ **Databázový model** - CarDeal tabuľka
3. ✅ **Scraping skript** - `scripts/car_scraper.py`
4. ✅ **React Frontend** - Moderný UI s dark mode
5. ✅ **Integrácia** - Frontend ↔ Backend

## 🎯 Spustenie v 3 krokoch

### Krok 1: Spusti Flask backend

```bash
# Aktivuj venv
source venv/bin/activate

# Spusti server
python app.py
```

Backend beží na `http://localhost:6002`

### Krok 2: Vytvor CarScraper Pro projekt a naplň dáta

```bash
# V inom termináli (s aktivovaným venv)
python scripts/car_scraper.py
```

Toto:
- Vytvorí projekt "CarScraper Pro" (ak neexistuje)
- Scrapuje inzeráty z Bazoš.sk
- Analyzuje ich a uloží do databázy

### Krok 3: Spusti React frontend

```bash
cd frontend
npm install  # Len prvýkrát
npm run dev
```

Frontend beží na `http://localhost:3000`

## 📱 Použitie

1. **Otvori frontend**: `http://localhost:3000`
2. **Prihlás sa** cez Flask dashboard: `http://localhost:6002/login`
   - Username: `admin`
   - Password: `admin123`
3. **Vráť sa na frontend** - deals sa automaticky načítajú

## 🔄 Automatické obnovovanie

Frontend automaticky obnovuje dáta každých **30 sekúnd**.

## 🎨 Funkcie frontendu

- ✅ Dark mode (automatická detekcia)
- ✅ Real-time updates
- ✅ Filtering (Všetky / Len Kúpiť)
- ✅ Responsive design
- ✅ Smooth animations

## 🐛 Riešenie problémov

### "CarScraper Pro projekt nebol nájdený"

```bash
# Spusti scraping skript - automaticky vytvorí projekt
python scripts/car_scraper.py
```

### Frontend nevidí dáta

1. Skontroluj, či si prihlásený v Flask dashboarde
2. Skontroluj konzolu prehliadača (F12) pre chyby
3. Skontroluj Network tab - či API volania prechádzajú

### API vracia 404

```bash
# Skontroluj, či projekt existuje
python -c "from app import app, db, Project; app.app_context().push(); print(Project.query.filter_by(name='CarScraper Pro').first())"
```

## 📊 Testovanie API

```bash
# Po prihlásení cez web:
curl -b cookies.txt http://localhost:6002/api/carscraper/stats
curl -b cookies.txt http://localhost:6002/api/carscraper/deals
```

## 🚀 Produkcia

### Build frontendu

```bash
cd frontend
npm run build
```

Build sa vytvorí v `static/carscraper/` a je dostupný na `/carscraper`

### Spustenie s Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:6002 app:app
```

---

**Všetko je pripravené a funkčné!** 🎉

