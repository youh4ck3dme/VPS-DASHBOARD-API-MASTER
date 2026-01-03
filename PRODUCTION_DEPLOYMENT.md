# 🚀 Produkčné Nasadenie - VPS Dashboard API

Kompletný návod na produkčné nasadenie VPS Dashboard API.

---

## 📋 Predpoklady

- **VPS Server** (Ubuntu 20.04+ / Debian 11+ / CentOS 8+)
- **Root prístup** alebo sudo oprávnenia
- **Doména** (voliteľné, ale odporúčané)
- **MySQL/PostgreSQL** databáza (alebo SQLite pre malé projekty)
- **Redis** server (pre rate limiting)

---

## 🔧 Rýchle Nasadenie

### 1. Klonovanie Repozitára

```bash
cd /var/www
git clone https://github.com/yourusername/VPS-DASHBOARD-API-MASTER.git vps-dashboard-api
cd vps-dashboard-api
```

### 2. Spustenie Deployment Scriptu

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

### 3. Konfigurácia

Uprav `.env` súbor:

```bash
sudo nano /var/www/vps-dashboard-api/.env
```

**Dôležité hodnoty:**
- `SECRET_KEY` - vygeneruj náhodný string (min. 32 znakov)
- `DATABASE_URL` - MySQL/PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `FLASK_ENV=production`
- `FLASK_DEBUG=False`

### 4. Inicializácia Databázy

```bash
cd /var/www/vps-dashboard-api
source venv/bin/activate
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 5. Vytvorenie Admin Používateľa

```bash
python -c "
from app import app, db, User
with app.app_context():
    admin = User(username='admin', email='admin@example.com', is_admin=True)
    admin.set_password('ZMEŇ_TOTO_HESLO')
    db.session.add(admin)
    db.session.commit()
    print('✅ Admin používateľ vytvorený')
"
```

---

## 🔒 Bezpečnostné Nastavenia

### 1. Firewall (UFW)

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. SSL Certifikát (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 3. Aktualizácia Systému

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

### 4. Fail2Ban (Ochrana proti bruteforce)

```bash
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📊 Monitoring a Logy

### Zobrazenie Logov

```bash
# Aplikácia logy
tail -f /var/www/vps-dashboard-api/logs/app.log

# Systemd service logy
journalctl -u vps-dashboard-api -f

# Nginx logy
tail -f /var/log/nginx/vps-dashboard-api-access.log
tail -f /var/log/nginx/vps-dashboard-api-error.log
```

### Health Check

```bash
curl http://localhost:6002/health
curl http://localhost:6002/api/health
```

---

## 🔄 Aktualizácia Aplikácie

```bash
cd /var/www/vps-dashboard-api
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart vps-dashboard-api
```

---

## 💾 Backup Stratégia

### Automatický Backup (Cron)

```bash
# Pridaj do crontab
sudo crontab -e

# Denný backup o 2:00
0 2 * * * /var/www/vps-dashboard-api/backup_db.sh
```

### Manuálny Backup

```bash
cd /var/www/vps-dashboard-api
./backup_db.sh
```

---

## 🛠️ Údržba

### Restart Služby

```bash
sudo systemctl restart vps-dashboard-api
```

### Kontrola Stavu

```bash
sudo systemctl status vps-dashboard-api
```

### Reštart Nginx

```bash
sudo systemctl restart nginx
```

---

## 📈 Optimalizácia Výkonu

### 1. Gunicorn (Odporúčané pre produkciu)

```bash
pip install gunicorn
```

Vytvor `gunicorn_config.py`:

```python
bind = "127.0.0.1:6002"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
```

Uprav systemd service:

```ini
ExecStart=/var/www/vps-dashboard-api/venv/bin/gunicorn -c gunicorn_config.py app:app
```

### 2. Redis Cache

Uisti sa, že Redis beží:

```bash
sudo systemctl status redis
sudo systemctl enable redis
```

### 3. Nginx Caching

Pridaj do Nginx konfigurácie:

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m;
proxy_cache api_cache;
proxy_cache_valid 200 10m;
```

---

## 🐛 Troubleshooting

### Aplikácia nebeží

```bash
# Skontroluj logy
journalctl -u vps-dashboard-api -n 50

# Skontroluj .env súbor
cat /var/www/vps-dashboard-api/.env

# Skontroluj databázu
mysql -u username -p -e "USE vps_dashboard; SHOW TABLES;"
```

### 502 Bad Gateway

```bash
# Skontroluj, či aplikácia beží
sudo systemctl status vps-dashboard-api

# Skontroluj port
netstat -tlnp | grep 6002
```

### Databázové Chyby

```bash
# Skontroluj connection string v .env
# Testuj pripojenie
mysql -u username -p -h localhost vps_dashboard
```

---

## 🔐 Bezpečnostný Checklist

- [ ] `FLASK_DEBUG=False` v `.env`
- [ ] `SECRET_KEY` je náhodný a silný (min. 32 znakov)
- [ ] `WTF_CSRF_ENABLED=True`
- [ ] SSL certifikát nainštalovaný
- [ ] Firewall nakonfigurovaný
- [ ] Fail2Ban aktívny
- [ ] Databázové heslo je silné
- [ ] `.env` súbor má oprávnenia 600
- [ ] Admin heslo zmenené
- [ ] Pravidelné backupy nastavené
- [ ] Systém aktualizovaný

---

## 📞 Podpora

Pre problémy a otázky:
- GitHub Issues: https://github.com/yourusername/VPS-DASHBOARD-API-MASTER/issues
- Dokumentácia: `/docs` v projekte

---

## ✅ Produkčný Checklist

- [ ] Všetky environment variables nastavené
- [ ] Databáza vytvorená a inicializovaná
- [ ] Admin používateľ vytvorený
- [ ] SSL certifikát nainštalovaný
- [ ] Firewall nakonfigurovaný
- [ ] Backupy nastavené
- [ ] Monitoring nakonfigurovaný
- [ ] Logy kontrolované
- [ ] Health check funguje
- [ ] Aplikácia beží stabilne

---

**🎉 Gratulujeme! Aplikácia je pripravená na produkciu!**

