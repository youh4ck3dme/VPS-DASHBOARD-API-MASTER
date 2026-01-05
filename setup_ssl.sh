#!/bin/bash
# ============================================
# SSL CERTIFICATE SETUP SCRIPT
# Automatická inštalácia Let's Encrypt SSL certifikátu
# ============================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_NAME="vps-dashboard-api"
NGINX_CONFIG="/etc/nginx/sites-available/${APP_NAME}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🔒 SSL Certificate Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Kontrola oprávnení
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Tento script musí byť spustený ako root${NC}"
    exit 1
fi

# Kontrola domény
if [ -z "${1:-}" ]; then
    echo -e "${YELLOW}📝 Použitie: $0 <domain.com>${NC}"
    echo -e "${YELLOW}   Príklad: $0 example.com${NC}"
    exit 1
fi

DOMAIN="$1"

# Kontrola, či certbot je nainštalovaný
if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}📦 Inštalácia certbot...${NC}"
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
    elif command -v yum &> /dev/null; then
        yum install -y certbot python3-certbot-nginx
    else
        echo -e "${RED}❌ Neznámy package manager${NC}"
        exit 1
    fi
fi

# Kontrola, či Nginx beží
if ! systemctl is-active --quiet nginx; then
    echo -e "${YELLOW}🌐 Spúšťanie Nginx...${NC}"
    systemctl start nginx
    systemctl enable nginx
fi

# Aktualizácia Nginx konfigurácie pre doménu
echo -e "${YELLOW}⚙️  Aktualizácia Nginx konfigurácie...${NC}"
if [ -f "$NGINX_CONFIG" ]; then
    # Backup pôvodnej konfigurácie
    cp "$NGINX_CONFIG" "${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Aktualizuj server_name
    sed -i "s/server_name _;/server_name ${DOMAIN};/" "$NGINX_CONFIG"
    
    # Pridaj SSL redirect (dočasne zakomentovaný, certbot ho pridá)
    # sed -i '/listen 80;/a\    return 301 https://$server_name$request_uri;' "$NGINX_CONFIG"
    
    systemctl reload nginx
else
    echo -e "${RED}❌ Nginx konfigurácia neexistuje: $NGINX_CONFIG${NC}"
    echo -e "${YELLOW}💡 Spusti najprv deploy.sh${NC}"
    exit 1
fi

# Kontrola DNS
echo -e "${YELLOW}🔍 Kontrola DNS...${NC}"
if ! dig +short "$DOMAIN" | grep -q .; then
    echo -e "${RED}❌ DNS záznam pre $DOMAIN neexistuje alebo nie je dostupný${NC}"
    echo -e "${YELLOW}💡 Uisti sa, že DNS A záznam smeruje na tento server${NC}"
    exit 1
fi

# Inštalácia SSL certifikátu
echo -e "${YELLOW}🔒 Inštalácia SSL certifikátu...${NC}"
echo -e "${YELLOW}   Doména: $DOMAIN${NC}"
echo ""

certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "admin@${DOMAIN}" --redirect

# Kontrola certifikátu
if [ -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
    echo -e "${GREEN}✅ SSL certifikát úspešne nainštalovaný!${NC}"
    
    # Test obnovenia certifikátu
    echo -e "${YELLOW}🧪 Test obnovenia certifikátu...${NC}"
    certbot renew --dry-run
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Automatické obnovovanie certifikátu je nastavené${NC}"
    else
        echo -e "${YELLOW}⚠️  Automatické obnovovanie certifikátu môže vyžadovať manuálnu konfiguráciu${NC}"
    fi
    
    # Pridanie cron jobu pre automatické obnovovanie (ak neexistuje)
    if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
        echo -e "${YELLOW}📅 Pridávanie cron jobu pre automatické obnovovanie...${NC}"
        (crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -
        echo -e "${GREEN}✅ Cron job pridaný${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ SSL Setup dokončený!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "🔗 URL: https://${DOMAIN}"
    echo -e "📋 Certifikát: /etc/letsencrypt/live/${DOMAIN}/"
    echo -e "🔄 Automatické obnovovanie: Každý deň o 3:00"
    echo ""
else
    echo -e "${RED}❌ SSL certifikát sa nepodarilo nainštalovať${NC}"
    exit 1
fi

