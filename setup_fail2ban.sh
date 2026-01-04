#!/bin/bash
# ============================================
# FAIL2BAN SETUP SCRIPT
# Automatická konfigurácia Fail2Ban pre ochranu proti bruteforce útokom
# ============================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_NAME="vps-dashboard-api"
LOG_FILE="/var/www/${APP_NAME}/logs/app.log"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🛡️  Fail2Ban Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Kontrola oprávnení
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Tento script musí byť spustený ako root${NC}"
    exit 1
fi

# Kontrola, či Fail2Ban je nainštalovaný
if ! command -v fail2ban-server &> /dev/null; then
    echo -e "${YELLOW}📦 Inštalácia Fail2Ban...${NC}"
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y fail2ban
    elif command -v yum &> /dev/null; then
        yum install -y fail2ban
    else
        echo -e "${RED}❌ Neznámy package manager${NC}"
        exit 1
    fi
fi

# Vytvorenie jail.local konfigurácie
echo -e "${YELLOW}⚙️  Vytváranie Fail2Ban konfigurácie...${NC}"

# SSH jail
cat > /etc/fail2ban/jail.d/ssh.local <<EOF
[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s
maxretry = 5
bantime = 3600
findtime = 600
EOF

# VPS Dashboard API jail
cat > /etc/fail2ban/jail.d/vps-dashboard-api.local <<EOF
[vps-dashboard-api]
enabled = true
port = http,https
filter = vps-dashboard-api
logpath = ${LOG_FILE}
maxretry = 5
bantime = 3600
findtime = 600
action = iptables-multiport[name=vps-dashboard-api, port="http,https", protocol=tcp]
EOF

# Vytvorenie filtra pre VPS Dashboard API
cat > /etc/fail2ban/filter.d/vps-dashboard-api.conf <<EOF
[Definition]
# Filtrovanie neúspešných prihlásení
failregex = ^.*Failed login attempt for user: <HOST>.*$
            ^.*Invalid login attempt from <HOST>.*$
            ^.*Rate limit exceeded for <HOST>.*$

# Ignorovať úspešné prihlásenia
ignoreregex =
EOF

# Vytvorenie akcie pre email notifikácie (voliteľné)
if [ -n "${ADMIN_EMAIL:-}" ]; then
    echo -e "${YELLOW}📧 Konfigurácia email notifikácií...${NC}"
    cat >> /etc/fail2ban/jail.d/vps-dashboard-api.local <<EOF

# Email notifikácie
action = iptables-multiport[name=vps-dashboard-api, port="http,https", protocol=tcp]
         sendmail-whois[name=vps-dashboard-api, dest=${ADMIN_EMAIL}, sender=fail2ban@$(hostname)]
EOF
fi

# Restart Fail2Ban
echo -e "${YELLOW}🔄 Reštartovanie Fail2Ban...${NC}"
systemctl restart fail2ban
systemctl enable fail2ban

# Kontrola statusu
sleep 2
if systemctl is-active --quiet fail2ban; then
    echo -e "${GREEN}✅ Fail2Ban beží${NC}"
else
    echo -e "${RED}❌ Fail2Ban nebeží - skontroluj logy: journalctl -u fail2ban${NC}"
    exit 1
fi

# Zobrazenie statusu
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Fail2Ban Setup dokončený!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}📋 Aktuálny stav:${NC}"
fail2ban-client status
echo ""
echo -e "${YELLOW}📋 Status jailov:${NC}"
fail2ban-client status sshd 2>/dev/null || true
fail2ban-client status vps-dashboard-api 2>/dev/null || true
echo ""
echo -e "${YELLOW}💡 Tipy:${NC}"
echo -e "   - Zobraziť status: fail2ban-client status"
echo -e "   - Zobraziť banned IP: fail2ban-client status vps-dashboard-api"
echo -e "   - Odbanovať IP: fail2ban-client set vps-dashboard-api unbanip <IP>"
echo -e "   - Test regex: fail2ban-regex ${LOG_FILE} /etc/fail2ban/filter.d/vps-dashboard-api.conf"
echo ""

