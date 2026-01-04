#!/bin/bash
# ============================================
# FIREWALL SETUP SCRIPT (UFW)
# Automatická konfigurácia firewallu pre VPS Dashboard API
# ============================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🔥 Firewall Setup (UFW)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Kontrola oprávnení
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Tento script musí byť spustený ako root${NC}"
    exit 1
fi

# Kontrola, či UFW je nainštalovaný
if ! command -v ufw &> /dev/null; then
    echo -e "${YELLOW}📦 Inštalácia UFW...${NC}"
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y ufw
    elif command -v yum &> /dev/null; then
        yum install -y ufw
    else
        echo -e "${RED}❌ Neznámy package manager${NC}"
        exit 1
    fi
fi

# Reset UFW (ak je potrebné)
if ufw status | grep -q "Status: active"; then
    echo -e "${YELLOW}⚠️  UFW je už aktívny. Chceš ho resetovať? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "${YELLOW}🔄 Resetovanie UFW...${NC}"
        ufw --force reset
    else
        echo -e "${YELLOW}📋 Používam existujúcu konfiguráciu${NC}"
    fi
fi

# Nastavenie default policies
echo -e "${YELLOW}⚙️  Nastavenie default policies...${NC}"
ufw default deny incoming
ufw default allow outgoing

# Povolenie SSH (DÔLEŽITÉ - inak sa odpojíš!)
echo -e "${YELLOW}🔐 Povolenie SSH...${NC}"
SSH_PORT="${SSH_PORT:-22}"
ufw allow "${SSH_PORT}/tcp" comment 'SSH'

# Povolenie HTTP a HTTPS
echo -e "${YELLOW}🌐 Povolenie HTTP a HTTPS...${NC}"
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Povolenie aplikácie (ak beží na inom porte)
APP_PORT="${APP_PORT:-6002}"
if [ "$APP_PORT" != "80" ] && [ "$APP_PORT" != "443" ]; then
    echo -e "${YELLOW}🔌 Povolenie aplikácie na porte $APP_PORT...${NC}"
    ufw allow "${APP_PORT}/tcp" comment 'VPS Dashboard API'
fi

# Povolenie Redis (len lokálne)
echo -e "${YELLOW}💾 Konfigurácia Redis...${NC}"
ufw deny 6379/tcp comment 'Redis - local only'

# Povolenie MySQL (len lokálne)
echo -e "${YELLOW}🗄️  Konfigurácia MySQL...${NC}"
ufw deny 3306/tcp comment 'MySQL - local only'

# Rate limiting pre SSH
echo -e "${YELLOW}🛡️  Nastavenie rate limiting pre SSH...${NC}"
ufw limit "${SSH_PORT}/tcp" comment 'SSH rate limit'

# Aktivácia UFW
echo -e "${YELLOW}▶️  Aktivácia UFW...${NC}"
ufw --force enable

# Zobrazenie statusu
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Firewall Setup dokončený!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}📋 Aktuálny stav:${NC}"
ufw status verbose
echo ""
echo -e "${YELLOW}💡 Tipy:${NC}"
echo -e "   - Zobraziť status: ufw status verbose"
echo -e "   - Pridať pravidlo: ufw allow <port>/tcp"
echo -e "   - Odstrániť pravidlo: ufw delete allow <port>/tcp"
echo -e "   - Deaktivovať: ufw disable"
echo ""

