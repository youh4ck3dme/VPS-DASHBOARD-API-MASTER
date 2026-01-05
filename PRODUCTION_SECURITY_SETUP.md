# 🔒 Produkčné Bezpečnostné Nastavenia

Kompletný návod na nastavenie všetkých produkčných bezpečnostných opatrení pre VPS Dashboard API.

---

## 📋 Prehľad

Tento dokument popisuje, ako nastaviť všetky produkčné bezpečnostné opatrenia:

1. ✅ **SSL Certifikát** (Let's Encrypt)
2. ✅ **Firewall** (UFW)
3. ✅ **Fail2Ban** (Ochrana proti bruteforce)
4. ✅ **Log Rotation** (Automatická rotácia logov)
5. ✅ **Health Monitoring** (Automatické kontroly)
6. ✅ **Backup Automatizácia** (Denné backupy)

---

## 🚀 Rýchly Start

### Kompletná Inštalácia (Odporúčané)

```bash
# 1. Najprv spusti základný deployment
sudo ./deploy.sh

# 2. Potom spusti kompletnú produkčnú konfiguráciu
sudo ./setup_production.sh
```

Toto automaticky nastaví všetky bezpečnostné opatrenia!

---

## 1️⃣ SSL Certifikát (Let's Encrypt)

### Automatická Inštalácia

```bash
sudo ./setup_ssl.sh example.com
```

### Čo script robí:
- ✅ Inštaluje certbot (ak nie je nainštalovaný)
- ✅ Kontroluje DNS záznamy
- ✅ Inštaluje SSL certifikát
- ✅ Konfiguruje automatické obnovovanie
- ✅ Nastaví HTTPS redirect

### Manuálna Inštalácia

```bash
# Inštalácia certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Inštalácia certifikátu
sudo certbot --nginx -d example.com

# Test obnovenia
sudo certbot renew --dry-run
```

### Automatické Obnovovanie

Certbot automaticky nastaví cron job pre obnovovanie certifikátov. Môžeš ho skontrolovať:

```bash
crontab -l | grep certbot
```

---

## 2️⃣ Firewall (UFW)

### Automatická Konfigurácia

```bash
sudo ./setup_firewall.sh
```

### Čo script robí:
- ✅ Inštaluje UFW (ak nie je nainštalovaný)
- ✅ Nastaví default policies (deny incoming, allow outgoing)
- ✅ Povolí SSH (port 22)
- ✅ Povolí HTTP (port 80) a HTTPS (port 443)
- ✅ Povolí aplikáciu (port 6002)
- ✅ Zablokuje Redis a MySQL (len lokálne)
- ✅ Nastaví rate limiting pre SSH

### Manuálna Konfigurácia

```bash
# Inštalácia UFW
sudo apt-get install -y ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Povolenie služieb
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw allow 6002/tcp comment 'VPS Dashboard API'

# Rate limiting pre SSH
sudo ufw limit 22/tcp

# Aktivácia
sudo ufw enable
```

### Kontrola Statusu

```bash
# Zobrazenie statusu
sudo ufw status verbose

# Zobrazenie pravidiel
sudo ufw status numbered
```

---

## 3️⃣ Fail2Ban

### Automatická Konfigurácia

```bash
sudo ./setup_fail2ban.sh
```

### Čo script robí:
- ✅ Inštaluje Fail2Ban (ak nie je nainštalovaný)
- ✅ Konfiguruje SSH jail
- ✅ Konfiguruje VPS Dashboard API jail
- ✅ Vytvorí filter pre neúspešné prihlásenia
- ✅ Nastaví email notifikácie (ak je ADMIN_EMAIL nastavený)

### Manuálna Konfigurácia

```bash
# Inštalácia Fail2Ban
sudo apt-get install -y fail2ban

# Konfigurácia
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Editovanie konfigurácie
sudo nano /etc/fail2ban/jail.local

# Restart
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban
```

### Konfigurácia pre VPS Dashboard API

Fail2Ban monitoruje logy aplikácie a banuje IP adresy po 5 neúspešných pokusoch.

**Filter:** `/etc/fail2ban/filter.d/vps-dashboard-api.conf`
**Jail:** `/etc/fail2ban/jail.d/vps-dashboard-api.local`

### Kontrola Statusu

```bash
# Zobrazenie statusu
sudo fail2ban-client status

# Zobrazenie konkrétneho jailu
sudo fail2ban-client status vps-dashboard-api

# Zobrazenie banned IP
sudo fail2ban-client status vps-dashboard-api | grep "Banned IP"

# Odbanovanie IP
sudo fail2ban-client set vps-dashboard-api unbanip <IP>
```

---

## 4️⃣ Log Rotation

### Automatická Konfigurácia

```bash
sudo ./setup_logrotate.sh
```

### Čo script robí:
- ✅ Vytvorí logrotate konfiguráciu
- ✅ Nastaví dennú rotáciu
- ✅ Nastaví retenciu 30 dní
- ✅ Povolí kompresiu
- ✅ Nastaví správne oprávnenia

### Manuálna Konfigurácia

```bash
# Vytvorenie logrotate konfigurácie
sudo nano /etc/logrotate.d/vps-dashboard-api
```

**Príklad konfigurácie:**
```
/var/www/vps-dashboard-api/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload vps-dashboard-api > /dev/null 2>&1 || true
    endscript
}
```

### Testovanie

```bash
# Test konfigurácie
sudo logrotate -d /etc/logrotate.d/vps-dashboard-api

# Manuálne spustenie
sudo logrotate -f /etc/logrotate.d/vps-dashboard-api
```

---

## 5️⃣ Health Monitoring

### Automatická Konfigurácia

```bash
# Script automaticky nastaví cron job pri setup_production.sh
# Alebo manuálne:
chmod +x monitor_health.sh
(crontab -l 2>/dev/null; echo "*/5 * * * * /var/www/vps-dashboard-api/monitor_health.sh >> /var/www/vps-dashboard-api/logs/monitor.log 2>&1") | crontab -
```

### Čo monitoring kontroluje:
- ✅ Status aplikácie (systemd service)
- ✅ Health check endpoint (HTTP 200)
- ✅ Status Nginx
- ✅ Dostupnosť databázy
- ✅ Dostupnosť Redis (ak je nainštalovaný)
- ✅ Disk space
- ✅ Chyby v logoch

### Manuálne Spustenie

```bash
./monitor_health.sh
```

### Email Notifikácie

Nastav `ALERT_EMAIL` v environment variables:

```bash
export ALERT_EMAIL="admin@example.com"
./monitor_health.sh
```

Alebo v cron jobu:

```bash
*/5 * * * * ALERT_EMAIL=admin@example.com /var/www/vps-dashboard-api/monitor_health.sh >> /var/www/vps-dashboard-api/logs/monitor.log 2>&1
```

---

## 6️⃣ Backup Automatizácia

### Automatická Konfigurácia

Backup script (`backup_db.sh`) už existuje a je automaticky nastavený pri `setup_production.sh`.

### Manuálna Konfigurácia

```bash
# Pridanie cron jobu pre denné backupy (3:00)
(crontab -l 2>/dev/null; echo "0 3 * * * /var/www/vps-dashboard-api/backup_db.sh >> /var/www/vps-dashboard-api/logs/backup.log 2>&1") | crontab -
```

### Konfigurácia

Backup script používa environment variables z `.env` súboru:

```bash
DATABASE_URL=mysql://user:pass@localhost/dbname
BACKUP_DIR=/var/www/vps-dashboard-api/backups
BACKUP_RETENTION_DAYS=30
```

### Manuálne Spustenie

```bash
./backup_db.sh
```

---

## 🧪 Testovanie

### Test Všetkých Nastavení

```bash
# Spusti testy
python3 -m pytest tests/test_production_setup.py -v
```

### Manuálne Testy

```bash
# Test SSL
curl -I https://example.com

# Test Firewall
sudo ufw status verbose

# Test Fail2Ban
sudo fail2ban-client status

# Test Log Rotation
sudo logrotate -d /etc/logrotate.d/vps-dashboard-api

# Test Monitoring
./monitor_health.sh

# Test Backup
./backup_db.sh
```

---

## 📋 Checklist

Po nastavení všetkých produkčných opatrení, skontroluj:

- [ ] SSL certifikát je nainštalovaný a funguje
- [ ] Firewall je aktívny a správne nakonfigurovaný
- [ ] Fail2Ban beží a monitoruje logy
- [ ] Log rotation je nastavená a funguje
- [ ] Health monitoring beží každých 5 minút
- [ ] Backupy sa vytvárajú denne
- [ ] Všetky cron joby sú nastavené
- [ ] Email notifikácie fungujú (ak sú nastavené)

---

## 🆘 Troubleshooting

### SSL Certifikát

```bash
# Kontrola certifikátu
sudo certbot certificates

# Obnovenie certifikátu
sudo certbot renew

# Kontrola logov
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

### Firewall

```bash
# Kontrola statusu
sudo ufw status verbose

# Pridanie pravidla
sudo ufw allow 80/tcp

# Odstránenie pravidla
sudo ufw delete allow 80/tcp

# Reset firewallu
sudo ufw --force reset
```

### Fail2Ban

```bash
# Kontrola statusu
sudo fail2ban-client status

# Kontrola logov
sudo tail -f /var/log/fail2ban.log

# Test regex
sudo fail2ban-regex /var/www/vps-dashboard-api/logs/app.log /etc/fail2ban/filter.d/vps-dashboard-api.conf
```

### Log Rotation

```bash
# Kontrola statusu
cat /var/lib/logrotate/status

# Manuálne spustenie
sudo logrotate -f /etc/logrotate.d/vps-dashboard-api

# Kontrola logov
sudo tail -f /var/log/logrotate.log
```

### Monitoring

```bash
# Kontrola cron jobu
crontab -l

# Kontrola logov
tail -f /var/www/vps-dashboard-api/logs/monitor.log

# Manuálne spustenie
./monitor_health.sh
```

---

## 📚 Ďalšie Informácie

- **PRODUCTION_DEPLOYMENT.md** - Kompletný návod na nasadenie
- **PRODUCTION_CHECKLIST.md** - Detailný checklist
- **README_PRODUCTION.md** - Rýchly start pre produkciu

---

**🎉 Všetky produkčné bezpečnostné opatrenia sú teraz implementované a otestované!**

