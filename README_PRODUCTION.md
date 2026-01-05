# 🚀 VPS Dashboard API - Produkčné Nasadenie

## Rýchly Start

```bash
# 1. Klonuj repozitár
git clone https://github.com/yourusername/VPS-DASHBOARD-API-MASTER.git
cd VPS-DASHBOARD-API-MASTER

# 2. Spusti deployment script
chmod +x deploy.sh
sudo ./deploy.sh

# 3. Konfiguruj .env
sudo nano /var/www/vps-dashboard-api/.env

# 4. Inicializuj databázu
cd /var/www/vps-dashboard-api
source venv/bin/activate
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## 📚 Dokumentácia

- **Kompletný návod**: [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
- **Checklist**: [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
- **API Dokumentácia**: `/api/docs` (po nasadení)

## 🔧 Základné Príkazy

```bash
# Restart aplikácie
sudo systemctl restart vps-dashboard-api

# Zobrazenie logov
tail -f /var/www/vps-dashboard-api/logs/app.log

# Kontrola stavu
sudo systemctl status vps-dashboard-api

# Health check
curl http://localhost:6002/health
```

## 🔐 Bezpečnosť

- ✅ SSL/TLS certifikát (Let's Encrypt)
- ✅ Firewall (UFW)
- ✅ Fail2Ban
- ✅ CSRF ochrana
- ✅ Rate limiting
- ✅ Secure cookies

## 📊 Monitoring

- Logy: `/var/www/vps-dashboard-api/logs/`
- Systemd: `journalctl -u vps-dashboard-api`
- Nginx: `/var/log/nginx/`

## 💾 Backup

```bash
# Manuálny backup
./backup_db.sh

# Automatický backup (cron)
0 2 * * * /var/www/vps-dashboard-api/backup_db.sh
```

## 🆘 Podpora

Pre problémy pozri [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md#-troubleshooting)

