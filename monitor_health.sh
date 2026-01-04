#!/bin/bash
# ============================================
# HEALTH MONITORING SCRIPT
# Monitoring zdravia aplikácie a služieb
# ============================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_NAME="vps-dashboard-api"
APP_DIR="/var/www/${APP_NAME}"
HEALTH_URL="${HEALTH_URL:-http://localhost:6002/health}"
ALERT_EMAIL="${ALERT_EMAIL:-}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🏥 Health Monitoring${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Funkcia pre odoslanie alertu
send_alert() {
    local message="$1"
    echo -e "${RED}🚨 ALERT: $message${NC}"
    
    if [ -n "$ALERT_EMAIL" ] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "[${APP_NAME}] Health Alert" "$ALERT_EMAIL" || true
    fi
}

# Kontrola aplikácie
check_app() {
    echo -e "${YELLOW}🔍 Kontrola aplikácie...${NC}"
    
    if systemctl is-active --quiet "${APP_NAME}"; then
        echo -e "${GREEN}✅ ${APP_NAME} beží${NC}"
    else
        send_alert "${APP_NAME} nebeží!"
        return 1
    fi
    
    # Health check endpoint
    if command -v curl &> /dev/null; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" || echo "000")
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}✅ Health check: OK (HTTP $HTTP_CODE)${NC}"
        else
            send_alert "Health check zlyhal (HTTP $HTTP_CODE)"
            return 1
        fi
    fi
}

# Kontrola Nginx
check_nginx() {
    echo -e "${YELLOW}🌐 Kontrola Nginx...${NC}"
    
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✅ Nginx beží${NC}"
    else
        send_alert "Nginx nebeží!"
        return 1
    fi
}

# Kontrola databázy
check_database() {
    echo -e "${YELLOW}🗄️  Kontrola databázy...${NC}"
    
    # Načítanie .env
    if [ -f "${APP_DIR}/.env" ]; then
        DB_URL=$(grep "^DATABASE_URL=" "${APP_DIR}/.env" | cut -d '=' -f2- | tr -d '"' || echo "")
        
        if [[ "$DB_URL" == sqlite* ]]; then
            DB_FILE=$(echo "$DB_URL" | sed 's/sqlite:\/\/\///')
            if [ -f "$DB_FILE" ]; then
                echo -e "${GREEN}✅ SQLite databáza existuje${NC}"
            else
                send_alert "SQLite databáza neexistuje: $DB_FILE"
                return 1
            fi
        elif [[ "$DB_URL" == mysql* ]]; then
            if command -v mysql &> /dev/null; then
                # Extrahovanie údajov z connection stringu
                MYSQL_USER=$(echo "$DB_URL" | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
                MYSQL_PASS=$(echo "$DB_URL" | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
                MYSQL_HOST=$(echo "$DB_URL" | sed -n 's/.*@\([^\/]*\)\/.*/\1/p')
                MYSQL_DB=$(echo "$DB_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
                
                if mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASS" -e "SELECT 1" "$MYSQL_DB" &>/dev/null; then
                    echo -e "${GREEN}✅ MySQL databáza je dostupná${NC}"
                else
                    send_alert "MySQL databáza nie je dostupná"
                    return 1
                fi
            fi
        fi
    fi
}

# Kontrola Redis
check_redis() {
    echo -e "${YELLOW}💾 Kontrola Redis...${NC}"
    
    if systemctl is-active --quiet redis-server || systemctl is-active --quiet redis; then
        if command -v redis-cli &> /dev/null; then
            if redis-cli ping &>/dev/null; then
                echo -e "${GREEN}✅ Redis beží${NC}"
            else
                send_alert "Redis neodpovedá"
                return 1
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Redis nie je nainštalovaný alebo nebeží (voliteľné)${NC}"
    fi
}

# Kontrola disk space
check_disk() {
    echo -e "${YELLOW}💿 Kontrola disk space...${NC}"
    
    DISK_USAGE=$(df -h "${APP_DIR}" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 90 ]; then
        send_alert "Disk space je kritický: ${DISK_USAGE}%"
        return 1
    elif [ "$DISK_USAGE" -gt 80 ]; then
        echo -e "${YELLOW}⚠️  Disk space: ${DISK_USAGE}%${NC}"
    else
        echo -e "${GREEN}✅ Disk space: ${DISK_USAGE}%${NC}"
    fi
}

# Kontrola logov
check_logs() {
    echo -e "${YELLOW}📋 Kontrola logov...${NC}"
    
    ERROR_COUNT=$(grep -i "error\|critical\|fatal" "${APP_DIR}/logs/app.log" 2>/dev/null | tail -20 | wc -l || echo "0")
    if [ "$ERROR_COUNT" -gt 10 ]; then
        echo -e "${YELLOW}⚠️  Nájdených $ERROR_COUNT chýb v posledných logoch${NC}"
    else
        echo -e "${GREEN}✅ Logy vyzerajú v poriadku${NC}"
    fi
}

# Hlavná kontrola
main() {
    local exit_code=0
    
    check_app || exit_code=1
    check_nginx || exit_code=1
    check_database || exit_code=1
    check_redis || true  # Redis je voliteľný
    check_disk || exit_code=1
    check_logs || true
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}✅ Všetky kontroly prešli!${NC}"
        echo -e "${GREEN}========================================${NC}"
    else
        echo -e "${RED}========================================${NC}"
        echo -e "${RED}❌ Niektoré kontroly zlyhali!${NC}"
        echo -e "${RED}========================================${NC}"
    fi
    
    return $exit_code
}

# Spustenie
main

