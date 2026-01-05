#!/bin/bash
# ============================================
# LOG ROTATION SETUP SCRIPT
# Automatická konfigurácia log rotation pre VPS Dashboard API
# ============================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_NAME="vps-dashboard-api"
APP_DIR="/var/www/${APP_NAME}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}📋 Log Rotation Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Kontrola oprávnení
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Tento script musí byť spustený ako root${NC}"
    exit 1
fi

# Vytvorenie logrotate konfigurácie
echo -e "${YELLOW}⚙️  Vytváranie logrotate konfigurácie...${NC}"

cat > "/etc/logrotate.d/${APP_NAME}" <<EOF
${APP_DIR}/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload ${APP_NAME} > /dev/null 2>&1 || true
    endscript
}

${APP_DIR}/logs/*.error.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload ${APP_NAME} > /dev/null 2>&1 || true
    endscript
}
EOF

# Test logrotate konfigurácie
echo -e "${YELLOW}🧪 Test logrotate konfigurácie...${NC}"
if logrotate -d "/etc/logrotate.d/${APP_NAME}" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Logrotate konfigurácia je platná${NC}"
else
    echo -e "${RED}❌ Chyba v logrotate konfigurácii${NC}"
    logrotate -d "/etc/logrotate.d/${APP_NAME}"
    exit 1
fi

# Vytvorenie adresára pre logy (ak neexistuje)
mkdir -p "${APP_DIR}/logs"
chown -R www-data:www-data "${APP_DIR}/logs"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Log Rotation Setup dokončený!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}📋 Konfigurácia:${NC}"
echo -e "   - Rotácia: Denná"
echo -e "   - Retencia: 30 dní"
echo -e "   - Kompresia: Áno (s oneskorením)"
echo -e "   - Súbor: /etc/logrotate.d/${APP_NAME}"
echo ""
echo -e "${YELLOW}💡 Tipy:${NC}"
echo -e "   - Manuálne spustenie: logrotate -f /etc/logrotate.d/${APP_NAME}"
echo -e "   - Test: logrotate -d /etc/logrotate.d/${APP_NAME}"
echo -e "   - Status: cat /var/lib/logrotate/status"
echo ""

