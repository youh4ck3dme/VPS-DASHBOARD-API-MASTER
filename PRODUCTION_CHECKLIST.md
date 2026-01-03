# ✅ Produkčný Checklist

Kompletný checklist pre produkčné nasadenie VPS Dashboard API.

---

## 🔧 Pred Nasadením

### Konfigurácia
- [ ] `.env` súbor vytvorený z `.env.production.example`
- [ ] `SECRET_KEY` nastavený (min. 32 náhodných znakov)
- [ ] `FLASK_ENV=production`
- [ ] `FLASK_DEBUG=False`
- [ ] `DATABASE_URL` správne nastavený
- [ ] `REDIS_URL` správne nastavený
- [ ] Všetky API kľúče nastavené (Stripe, OpenAI, Google)

### Bezpečnosť
- [ ] `.env` má oprávnenia 600
- [ ] `WTF_CSRF_ENABLED=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `SESSION_COOKIE_HTTPONLY=True`
- [ ] Firewall nakonfigurovaný (UFW/Firewalld)
- [ ] SSH kľúče namiesto hesiel
- [ ] Fail2Ban nainštalovaný a aktívny

### Databáza
- [ ] Databáza vytvorená
- [ ] Databázový používateľ vytvorený s minimálnymi oprávneniami
- [ ] Databázové heslo je silné
- [ ] Tabuľky vytvorené (`db.create_all()`)
- [ ] Backup stratégia nastavená

### Systém
- [ ] Systém aktualizovaný (`apt-get update && apt-get upgrade`)
- [ ] Python 3.9+ nainštalovaný
- [ ] MySQL/PostgreSQL nainštalovaný a beží
- [ ] Redis nainštalovaný a beží
- [ ] Nginx nainštalovaný a nakonfigurovaný

---

## 🚀 Nasadenie

### Deployment
- [ ] Kód naklonovaný do `/var/www/vps-dashboard-api`
- [ ] Virtual environment vytvorený
- [ ] Závislosti nainštalované (`pip install -r requirements.txt`)
- [ ] Systemd service vytvorený a aktivovaný
- [ ] Nginx konfigurácia vytvorená
- [ ] Aplikácia beží (`systemctl status vps-dashboard-api`)

### SSL/TLS
- [ ] SSL certifikát nainštalovaný (Let's Encrypt)
- [ ] HTTPS redirect nakonfigurovaný
- [ ] Certifikát sa automaticky obnovuje

### Monitoring
- [ ] Logy kontrolované (`logs/app.log`)
- [ ] Health check funguje (`/health`, `/api/health`)
- [ ] Systemd logy kontrolované (`journalctl -u vps-dashboard-api`)
- [ ] Nginx logy kontrolované

---

## 👤 Používatelia

### Admin
- [ ] Admin používateľ vytvorený
- [ ] Admin heslo zmenené (silné heslo)
- [ ] Admin môže sa prihlásiť
- [ ] Admin má všetky oprávnenia

### Test Používateľ
- [ ] Test používateľ vytvorený
- [ ] Test používateľ môže vytvoriť projekt
- [ ] Test používateľ môže používať API

---

## 🔄 Backup a Údržba

### Backup
- [ ] Backup script testovaný (`backup_db.sh`)
- [ ] Cron job nastavený pre automatické backupy
- [ ] Backup adresár má dostatok miesta
- [ ] Backup retention nastavený (30 dní)
- [ ] Testovanie obnovenia z backupu

### Údržba
- [ ] Log rotation nakonfigurovaný
- [ ] Disk space monitoring nastavený
- [ ] Pravidelné aktualizácie naplánované

---

## 📊 Funkcionalita

### API
- [ ] API endpointy fungujú (`/api/projects`, `/api/health`)
- [ ] API rate limiting funguje
- [ ] API autentifikácia funguje
- [ ] API dokumentácia dostupná (`/api/docs`)

### Web Interface
- [ ] Dashboard sa načíta
- [ ] Prihlásenie funguje
- [ ] Vytvorenie projektu funguje
- [ ] Všetky CRUD operácie fungujú

### CarScraper Pro
- [ ] CarScraper Pro projekt sa automaticky vytvorí
- [ ] Scraping funguje (manuálne aj automaticky)
- [ ] Proxy systém funguje
- [ ] Multi-source scraping funguje

---

## 🧪 Testovanie

### Funkčné Testy
- [ ] Všetky testy prešli (`pytest tests/`)
- [ ] Health check testy prešli
- [ ] API testy prešli
- [ ] Integračné testy prešli

### Bezpečnostné Testy
- [ ] CSRF ochrana funguje
- [ ] SQL injection ochrana funguje
- [ ] XSS ochrana funguje
- [ ] Rate limiting funguje

---

## 📈 Optimalizácia

### Výkon
- [ ] Gunicorn nainštalovaný a používaný
- [ ] Worker procesy optimalizované
- [ ] Redis cache funguje
- [ ] Nginx caching nakonfigurovaný (ak je potrebné)

### Monitoring
- [ ] Response times prijateľné (< 500ms)
- [ ] Memory usage prijateľné
- [ ] CPU usage prijateľné
- [ ] Disk I/O prijateľné

---

## 🔐 Finálna Bezpečnostná Kontrola

- [ ] Všetky default heslá zmenené
- [ ] Všetky default API kľúče zmenené
- [ ] Žiadne debug informácie v produkcii
- [ ] Error handling správne nastavený
- [ ] Logy neobsahujú citlivé informácie
- [ ] SSL/TLS správne nakonfigurovaný
- [ ] Security headers nastavené

---

## 📝 Dokumentácia

- [ ] `PRODUCTION_DEPLOYMENT.md` prečítaný
- [ ] `README.md` aktualizovaný
- [ ] API dokumentácia dostupná
- [ ] Kontaktné informácie aktualizované

---

## ✅ Finálne Overenie

- [ ] Aplikácia beží stabilne 24/7
- [ ] Všetky služby bežia (`systemctl status`)
- [ ] Žiadne kritické chyby v logoch
- [ ] Backup systém funguje
- [ ] Monitoring funguje
- [ ] Dokumentácia kompletná

---

**🎉 Projekt je pripravený na produkciu!**

---

## 🆘 V prípade problémov

1. Skontroluj logy: `tail -f logs/app.log`
2. Skontroluj systemd: `journalctl -u vps-dashboard-api -n 50`
3. Skontroluj Nginx: `tail -f /var/log/nginx/vps-dashboard-api-error.log`
4. Skontroluj databázu: `mysql -u username -p -e "SHOW PROCESSLIST;"`
5. Skontroluj Redis: `redis-cli ping`

