# API Dashboard - VPS Admin Panel

Kompletný VPS API Dashboard s podporou platieb, automatizácií a AI generovania obsahu.

> 📖 **Pozri [USE_CASES.md](USE_CASES.md) pre kompletný prehľad možností využitia tohto projektu**

## 🔐 Prihlasovacie údaje

**Predvolené prihlasovacie údaje pre admin účet:**

- **URL**: `http://localhost:6002/login` (lokálne) alebo `https://tvojadomena.top/login` (produkcia)
- **Užívateľské meno**: `admin`
- **Heslo**: `admin123`

⚠️ **DÔLEŽITÉ**: Zmeň heslo ihneď po prvom prihlásení!

### Rýchle prihlásenie

1. Spusti server: `./run.sh` alebo `python3 app.py`
2. Otvor prehliadač: `http://localhost:6002`
3. Prihlás sa s údajmi vyššie
4. **Ihneď zmeň heslo** v nastaveniach

## Funkcie

- **Správa projektov** - Vytváranie a správa viacerých projektov s unikátnymi API kľúčmi
- **Platobné brány** - Integrácia so Stripe, SumUp a CoinGate
- **Automatizácie** - Naplánované spúšťanie skriptov cez cron
- **AI generovanie** - OpenAI integrácia pre generovanie obsahu
- **Redis caching** - Vyrovnávacia pamäť pre lepší výkon
- **Bezpečnosť** - Hashované heslá, HTTPS podpora, firewall
- **Health Check** - Monitoring endpoint pre kontrolu stavu služieb
- **API Dokumentácia** - Automatická dokumentácia API endpointov
- **Rate Limiting** - Ochrana API proti zneužitiu (60 req/min)
- **Rozšírené logovanie** - File-based logging pre debugging

## Architektúra projektu

```
/var/www/api_dashboard/
├── app.py                    # Hlavný Flask server
├── config.py                 # Konfigurácia
├── requirements.txt          # Python závislosti
├── .env                      # Premenné prostredia (vytvor z .env.example)
├── cron_check.py            # Cron kontrolný skript
├── backup_db.sh             # Zálohovací skript
├── nginx.conf               # Nginx konfigurácia
├── api_dashboard.service    # Systemd služba
├── static/                  # CSS, JS, obrázky
├── templates/               # HTML šablóny
├── database/                # SQL skripty
│   └── init_db.sql         # Inicializácia databázy
├── scripts/                 # Automatizačné skripty
│   ├── example_script.py   # Príklad skriptu
│   ├── ai_generate.py      # AI generovanie
│   └── data_processing.py  # Spracovanie dát
├── logs/                    # Logy
└── backups/                 # Zálohy databázy
```

---

## Inštalácia (krok po kroku)

### 1. Pripojenie na VPS

```bash
ssh root@IP_TVOJEHO_VPS
```

### 2. Inštalácia závislostí

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx mysql-server redis-server git -y
```

### 3. Vytvorenie projektu

```bash
# Vytvor adresár a skopíruj súbory
mkdir -p /var/www/api_dashboard
cd /var/www/api_dashboard

# Ak máš projekt na GitHube, naklonuj ho:
# git clone https://github.com/tvoj-uzivatel/api-dashboard.git .

# Alebo skopíruj súbory manuálne do tohto adresára
```

### 4. Vytvorenie virtuálneho prostredia

```bash
cd /var/www/api_dashboard
python3 -m venv venv
source venv/bin/activate
```

### 5. Inštalácia Python balíčkov

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Konfigurácia .env súboru

```bash
cp .env.example .env
nano .env
```

Uprav nasledujúce hodnoty:

```ini
SECRET_KEY=tvoj_nahodny_tajny_kluc_123456
DATABASE_URL=mysql://root:tvoje_mysql_heslo@localhost/api_dashboard
STRIPE_SECRET_KEY=sk_test_tvoj_stripe_kluc
STRIPE_PUBLIC_KEY=pk_test_tvoj_stripe_kluc
OPENAI_API_KEY=sk-tvoj_openai_kluc
```

### 7. Nastavenie MySQL databázy

```bash
# Prihlás sa do MySQL
sudo mysql -u root -p

# V MySQL konzole spusti:
CREATE DATABASE api_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'api_user'@'localhost' IDENTIFIED BY 'silne_heslo';
GRANT ALL PRIVILEGES ON api_dashboard.* TO 'api_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Načítaj databázové schéma:

```bash
mysql -u root -p api_dashboard < database/init_db.sql
```

### 8. Test aplikácie

```bash
source venv/bin/activate
python3 app.py
```

Otvor prehliadač a prejdi na `http://localhost:6002` (alebo port z .env súboru)

**Predvolené prihlasovacie údaje:**
- **URL**: `http://localhost:6002/login`
- **Užívateľ**: `admin`
- **Heslo**: `admin123`

⚠️ **ZMEŇ HESLO PO PRVOM PRIHLÁSENÍ!**

Ak všetko funguje, ukonči server (Ctrl+C) a pokračuj na konfiguráciu produkčného prostredia.

---

## Produkčná konfigurácia

### 9. Nastavenie Gunicorn služby

```bash
# Skopíruj service súbor
sudo cp api_dashboard.service /etc/systemd/system/

# Načítaj a spusti službu
sudo systemctl daemon-reload
sudo systemctl start api_dashboard
sudo systemctl enable api_dashboard

# Skontroluj stav
sudo systemctl status api_dashboard
```

### 10. Nastavenie Nginx

```bash
# Uprav nginx.conf a zmeň doménu
nano nginx.conf

# Skopíruj konfiguráciu
sudo cp nginx.conf /etc/nginx/sites-available/api_dashboard

# Vytvor symlink
sudo ln -s /etc/nginx/sites-available/api_dashboard /etc/nginx/sites-enabled/

# Otestuj konfiguráciu
sudo nginx -t

# Reštartuj Nginx
sudo systemctl restart nginx
```

### 11. Nastavenie HTTPS (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tvojadomena.top -d www.tvojadomena.top

# Certbot automaticky upraví nginx.conf
```

### 12. Nastavenie Firewall (UFW)

```bash
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS
sudo ufw enable
sudo ufw status
```

### 13. Nastavenie Cron jobov

```bash
# Urob backup skript spustiteľný
chmod +x backup_db.sh

# Uprav heslo v backup_db.sh
nano backup_db.sh

# Pridaj cron joby
crontab -e
```

Pridaj nasledujúce riadky:

```bash
# Kontrola automatizácií každú minútu
* * * * * /var/www/api_dashboard/venv/bin/python3 /var/www/api_dashboard/cron_check.py

# Záloha databázy každý deň o 3:00
0 3 * * * /var/www/api_dashboard/backup_db.sh
```

### 14. Vytvorenie adresárov pre logy

```bash
mkdir -p /var/www/api_dashboard/logs
mkdir -p /var/www/api_dashboard/backups
chmod 755 /var/www/api_dashboard/logs
chmod 755 /var/www/api_dashboard/backups
```

---

## Použitie

### Prihlásenie

1. Otvor `https://tvojadomena.top` alebo `http://localhost:6002` (lokálne)
2. Prejdi na login stránku: `/login`
3. Prihlás sa s predvolenými údajmi:
   - **Užívateľské meno**: `admin`
   - **Heslo**: `admin123`
4. **IHNEĎ ZMEŇ HESLO!** (v nastaveniach účtu)

### Vytvorenie projektu

1. Klikni na **"Projekty"** v menu
2. Vyplň názov projektu a cestu k skriptu (voliteľné)
3. Klikni **"Vytvoriť projekt"**
4. Skopíruj si vygenerovaný API kľúč

### Spustenie skriptu

1. Na dashboarde klikni na **"Spustiť skript"** pri projekte
2. Skript sa spustí na pozadí
3. Sleduj logy v `/var/www/api_dashboard/logs/`

### Platby

1. Klikni na **"Platby"** pri projekte
2. Vyplň sumu a vyber platobnú bránu
3. Dokonči platbu podľa pokynov

### Automatizácie

1. Klikni na **"Automatizácie"** pri projekte
2. Pridaj názov skriptu a cron rozvrh
3. Skript sa bude spúšťať automaticky podľa rozvrhu

### AI Generovanie

1. Klikni na **"AI Generátor"** pri projekte
2. Napíš prompt (napr. "Napíš popis produktu")
3. Klikni **"Generovať"**
4. AI vygeneruje obsah pomocou OpenAI

---

## API Endpoints

### Health Check

```bash
curl -X GET http://localhost:6002/health
# alebo
curl -X GET http://localhost:6002/api/health
```

Vráti JSON so stavom služieb (databáza, Redis, Stripe, OpenAI).

### API Dokumentácia

```bash
curl -X GET http://localhost:6002/api/docs
```

Vráti kompletnú dokumentáciu všetkých API endpointov.

### Získanie zoznamu projektov

```bash
curl -X GET https://tvojadomena.top/api/projects \
  -H "Cookie: session=tvoj_session_cookie"
```

### Získanie detailu projektu

```bash
curl -X GET https://tvojadomena.top/api/project/1 \
  -H "Cookie: session=tvoj_session_cookie"
```

**Poznámka:** Všetky API endpointy majú rate limiting 60 požiadavok za minútu.

---

## Správa a údržba

### Reštart služby

```bash
sudo systemctl restart api_dashboard
```

### Zobrazenie logov

```bash
# Logy aplikácie
tail -f /var/www/api_dashboard/logs/gunicorn_error.log

# Logy Nginx
tail -f /var/log/nginx/api_dashboard_error.log

# Logy cron jobov
tail -f /var/www/api_dashboard/logs/cron_check.log
```

### Manuálna záloha databázy

```bash
/var/www/api_dashboard/backup_db.sh
```

### Obnova zo zálohy

```bash
gunzip /var/www/api_dashboard/backups/db_backup_2025-01-15.sql.gz
mysql -u root -p api_dashboard < /var/www/api_dashboard/backups/db_backup_2025-01-15.sql
```

### Aktualizácia aplikácie

```bash
cd /var/www/api_dashboard
source venv/bin/activate
git pull  # ak používaš git
pip install -r requirements.txt --upgrade
sudo systemctl restart api_dashboard
```

---

## Bezpečnosť

### Odporúčania

1. **Zmeň predvolené heslo** po prvom prihlásení
2. **Používaj silné heslá** pre databázu a aplikáciu
3. **Udržiavaj systém aktuálny**: `sudo apt update && sudo apt upgrade -y`
4. **Pravidelne zálohuj databázu**
5. **Sleduj logy** pre podozrivú aktivitu
6. **Nepoužívaj root** - vytvor dedikovaného používateľa (voliteľné)

### Vytvorenie dedikovaného používateľa (voliteľné)

```bash
sudo adduser apiuser
sudo usermod -aG www-data apiuser
sudo chown -R apiuser:www-data /var/www/api_dashboard

# Uprav api_dashboard.service: User=apiuser, Group=www-data
sudo systemctl daemon-reload
sudo systemctl restart api_dashboard
```

---

## Riešenie problémov

### Aplikácia sa nespustí

```bash
# Skontroluj logy
sudo systemctl status api_dashboard
journalctl -u api_dashboard -n 50

# Skontroluj, či beží MySQL a Redis
sudo systemctl status mysql
sudo systemctl status redis-server
```

### 502 Bad Gateway chyba

```bash
# Skontroluj, či beží Gunicorn
sudo systemctl status api_dashboard

# Reštartuj službu
sudo systemctl restart api_dashboard
```

### Databázové chyby

```bash
# Skontroluj pripojenie
mysql -u root -p -e "SHOW DATABASES;"

# Skontroluj používateľa a oprávnenia
mysql -u root -p -e "SELECT user, host FROM mysql.user;"
```

### Platby nefungujú

1. Skontroluj, či sú API kľúče v `.env` správne
2. Pre Stripe používaj test kľúče pri testovaní
3. Sleduj logy pre chybové hlásenia

---

## Pokročilé nastavenia

### Pridanie monitoringu (Grafana)

```bash
sudo apt install grafana -y
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

Prístup na `http://vps-ip:3000` (admin/admin)

### WebSocket podpora (pre live notifikácie)

```bash
pip install flask-socketio
```

Uprav `app.py` a pridaj SocketIO podporu.

---

## Podpora

Ak máš problémy:

1. Skontroluj logy v `/var/www/api_dashboard/logs/`
2. Prečítaj si sekciu "Riešenie problémov"
3. Skontroluj, či sú všetky služby spustené

---

## Licencia

Tento projekt je poskytovaný "ako je" bez akejkoľvek záruky.

---

## Autor

Vytvorené pre VPS Dashboard projekt, 2025
