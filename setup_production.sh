#!/bin/bash
# ============================================
# COMPLETE PRODUCTION SETUP SCRIPT
# Kompletná produkčná konfigurácia všetkých bezpečnostných opatrení
# ============================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

APP_NAME="vps-dashboard-api"
APP_DIR="/var/www/${APP_NAME}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 Complete Production Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Tento script nastaví:${NC}"
echo -e "   ✅ Firewall (UFW)"
echo -e "   ✅ Fail2Ban"
echo -e "   ✅ Log Rotation"
echo -e "   ✅ Health Monitoring"
echo -e "   ⚠️  SSL Certificate (ak zadáš doménu)"
echo ""

# Kontrola oprávnení
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Tento script musí byť spustený ako root${NC}"
    exit 1
fi

# Kontrola, či deploy.sh už bol spustený
if [ ! -f "/etc/systemd/system/${APP_NAME}.service" ]; then
    echo -e "${RED}❌ Najprv spusti deploy.sh!${NC}"
    exit 1
fi

# 1. Firewall
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}1️⃣  Firewall Setup${NC}"
echo -e "${GREEN}========================================${NC}"
if [ -f "${APP_DIR}/setup_firewall.sh" ]; then
    bash "${APP_DIR}/setup_firewall.sh"
else
    echo -e "${RED}❌ setup_firewall.sh neexistuje${NC}"
    exit 1
fi

# 2. Fail2Ban
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}2️⃣  Fail2Ban Setup${NC}"
echo -e "${GREEN}========================================${NC}"
if [ -f "${APP_DIR}/setup_fail2ban.sh" ]; then
    bash "${APP_DIR}/setup_fail2ban.sh"
else
    echo -e "${RED}❌ setup_fail2ban.sh neexistuje${NC}"
    exit 1
fi

# 3. Log Rotation
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}3️⃣  Log Rotation Setup${NC}"
echo -e "${GREEN}========================================${NC}"
if [ -f "${APP_DIR}/setup_logrotate.sh" ]; then
    bash "${APP_DIR}/setup_logrotate.sh"
else
    echo -e "${RED}❌ setup_logrotate.sh neexistuje${NC}"
    exit 1
fi

# 4. Health Monitoring
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}4️⃣  Health Monitoring Setup${NC}"
echo -e "${GREEN}========================================${NC}"
if [ -f "${APP_DIR}/monitor_health.sh" ]; then
    chmod +x "${APP_DIR}/monitor_health.sh"
    
    # Pridanie cron jobu
    if ! crontab -l 2>/dev/null | grep -q "monitor_health.sh"; then
        (crontab -l 2>/dev/null; echo "*/5 * * * * ${APP_DIR}/monitor_health.sh >> ${APP_DIR}/logs/monitor.log 2>&1") | crontab -
        echo -e "${GREEN}✅ Monitoring cron job pridaný (každých 5 minút)${NC}"
    else
        echo -e "${YELLOW}⚠️  Monitoring cron job už existuje${NC}"
    fi
    
    # Testovanie monitoringu
    echo -e "${YELLOW}🧪 Testovanie monitoringu...${NC}"
    bash "${APP_DIR}/monitor_health.sh"
else
    echo -e "${RED}❌ monitor_health.sh neexistuje${NC}"
    exit 1
fi

# 5. SSL Certificate (voliteľné)
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}5️⃣  SSL Certificate Setup (Voliteľné)${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}Chceš nastaviť SSL certifikát? (y/N)${NC}"
read -r setup_ssl
if [[ "$setup_ssl" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}Zadaj doménu (napr. example.com):${NC}"
    read -r domain
    if [ -n "$domain" ]; then
        if [ -f "${APP_DIR}/setup_ssl.sh" ]; then
            bash "${APP_DIR}/setup_ssl.sh" "$domain"
        else
            echo -e "${RED}❌ setup_ssl.sh neexistuje${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⏭️  SSL certifikát preskočený${NC}"
    echo -e "${YELLOW}   Môžeš ho nainštalovať neskôr: ${APP_DIR}/setup_ssl.sh <domain.com>${NC}"
fi

# 6. Backup automatizácia
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}6️⃣  Backup Automatizácia${NC}"
echo -e "${GREEN}========================================${NC}"
if [ -f "${APP_DIR}/backup_db.sh" ]; then
    chmod +x "${APP_DIR}/backup_db.sh"
    
    # Pridanie cron jobu pre denné backupy (3:00)
    if ! crontab -l 2>/dev/null | grep -q "backup_db.sh"; then
        (crontab -l 2>/dev/null; echo "0 3 * * * ${APP_DIR}/backup_db.sh >> ${APP_DIR}/logs/backup.log 2>&1") | crontab -
        echo -e "${GREEN}✅ Backup cron job pridaný (denne o 3:00)${NC}"
    else
        echo -e "${YELLOW}⚠️  Backup cron job už existuje${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  backup_db.sh neexistuje${NC}"
fi

# Finálny súhrn
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}✅ Production Setup dokončený!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}📋 Nastavené služby:${NC}"
echo -e "   ✅ Firewall (UFW)"
echo -e "   ✅ Fail2Ban"
echo -e "   ✅ Log Rotation"
echo -e "   ✅ Health Monitoring (každých 5 minút)"
echo -e "   ✅ Backup automatizácia (denne o 3:00)"
if [[ "$setup_ssl" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "   ✅ SSL Certificate"
fi
echo ""
echo -e "${YELLOW}📋 Užitočné príkazy:${NC}"
echo -e "   - Status firewall: ufw status verbose"
echo -e "   - Status Fail2Ban: fail2ban-client status"
echo -e "   - Health check: ${APP_DIR}/monitor_health.sh"
echo -e "   - Zobraziť cron jobs: crontab -l"
echo ""
echo -e "${GREEN}🎉 Všetko je pripravené na produkciu!${NC}"
echo ""

