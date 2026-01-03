#!/bin/bash
# Inštalačný skript pre API Dashboard
# Použitie: sudo bash install.sh

set -e  # Zastav pri chybe

echo "========================================="
echo "API Dashboard - Inštalačný skript"
echo "========================================="
echo ""

# Kontrola, či je spustený ako root
if [ "$EUID" -ne 0 ]; then
    echo "CHYBA: Prosím spusti tento skript ako root (sudo bash install.sh)"
    exit 1
fi

# Farby pre output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funkcie pre farebný výpis
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Aktualizácia systému
info "Aktualizujem systém..."
apt update && apt upgrade -y

# 2. Inštalácia závislostí
info "Inštalujem závislosti..."
apt install -y python3 python3-pip python3-venv nginx mysql-server redis-server git

# 3. Vytvorenie adresára
info "Vytváram adresár /var/www/api_dashboard..."
mkdir -p /var/www/api_dashboard
cd /var/www/api_dashboard

# 4. Kopírovanie súborov (ak sú v inom adresári)
if [ -f "$PWD/app.py" ]; then
    info "Súbory už sú na správnom mieste"
else
    error "Spusti tento skript z adresára projektu!"
    exit 1
fi

# 5. Vytvorenie virtuálneho prostredia
info "Vytváram virtuálne prostredie..."
python3 -m venv venv
source venv/bin/activate

# 6. Inštalácia Python závislostí
info "Inštalujem Python balíčky..."
pip install --upgrade pip
pip install -r requirements.txt

# 7. Vytvorenie .env súboru
if [ ! -f .env ]; then
    info "Vytváram .env súbor..."
    cp .env.example .env
    warn "POZOR: Uprav .env súbor s tvojimi API kľúčmi!"
fi

# 8. Vytvorenie adresárov
info "Vytváram adresáre pre logy a zálohy..."
mkdir -p logs backups static

# 9. Nastavenie MySQL databázy
info "Nastavujem MySQL databázu..."
read -p "Zadaj heslo pre MySQL root používateľa: " MYSQL_PASSWORD

mysql -u root -p"$MYSQL_PASSWORD" <<EOF
CREATE DATABASE IF NOT EXISTS api_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
FLUSH PRIVILEGES;
EOF

info "Načítavam databázové schéma..."
mysql -u root -p"$MYSQL_PASSWORD" api_dashboard < database/init_db.sql

# 10. Nastavenie systemd služby
info "Nastavujem systemd službu..."
cp api_dashboard.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable api_dashboard

# 11. Nastavenie Nginx
info "Nastavujem Nginx..."
read -p "Zadaj tvoju doménu (napr. example.com): " DOMAIN

# Nahradenie domény v nginx.conf
sed -i "s/tvojadomena.top/$DOMAIN/g" nginx.conf
cp nginx.conf /etc/nginx/sites-available/api_dashboard
ln -sf /etc/nginx/sites-available/api_dashboard /etc/nginx/sites-enabled/

# Test Nginx konfigurácie
nginx -t

# 12. Nastavenie cron jobov
info "Nastavujem cron joby..."
chmod +x backup_db.sh

# Pridanie cron jobov
(crontab -l 2>/dev/null; echo "* * * * * /var/www/api_dashboard/venv/bin/python3 /var/www/api_dashboard/cron_check.py") | crontab -
(crontab -l 2>/dev/null; echo "0 3 * * * /var/www/api_dashboard/backup_db.sh") | crontab -

# 13. Nastavenie firewall
info "Nastavujem firewall..."
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

# 14. Spustenie služieb
info "Spúšťam služby..."
systemctl start api_dashboard
systemctl restart nginx

# 15. Nastavenie SSL (voliteľné)
read -p "Chceš nainštalovať SSL certifikát (Let's Encrypt)? (y/n): " SSL_CHOICE
if [ "$SSL_CHOICE" = "y" ] || [ "$SSL_CHOICE" = "Y" ]; then
    info "Inštalujem certbot..."
    apt install -y certbot python3-certbot-nginx
    certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN"
fi

# Hotovo!
echo ""
echo "========================================="
info "Inštalácia dokončená!"
echo "========================================="
echo ""
info "Aplikácia beží na: http://$DOMAIN"
info "Predvolené prihlásenie: admin / admin123"
warn "NEZABUDNI ZMENIŤ HESLO PO PRVOM PRIHLÁSENÍ!"
echo ""
info "Ďalšie kroky:"
echo "  1. Uprav .env súbor: nano /var/www/api_dashboard/.env"
echo "  2. Zmeň heslo v backup_db.sh: nano /var/www/api_dashboard/backup_db.sh"
echo "  3. Reštartuj službu: systemctl restart api_dashboard"
echo ""
info "Kontrola služby: systemctl status api_dashboard"
info "Logy: tail -f /var/www/api_dashboard/logs/gunicorn_error.log"
echo ""
echo "========================================="
