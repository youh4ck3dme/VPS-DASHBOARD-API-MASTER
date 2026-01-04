#!/bin/bash
# ============================================
# PRODUKČNÝ DEPLOYMENT SCRIPT
# VPS Dashboard API
# ============================================

set -euo pipefail

# Farba pre výstup
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Konfigurácia
APP_NAME="vps-dashboard-api"
APP_DIR="/var/www/${APP_NAME}"
VENV_DIR="${APP_DIR}/venv"
USER="www-data"
SERVICE_NAME="${APP_NAME}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🚀 VPS Dashboard API - Production Deploy${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 1. Kontrola oprávnení
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Tento script musí byť spustený ako root${NC}"
    exit 1
fi

# 2. Vytvorenie adresárov
echo -e "${YELLOW}📁 Vytváranie adresárov...${NC}"
mkdir -p "${APP_DIR}"
mkdir -p "${APP_DIR}/logs"
mkdir -p "${APP_DIR}/uploads"
mkdir -p "${APP_DIR}/backups"
chown -R ${USER}:${USER} "${APP_DIR}"

# 3. Inštalácia systémových závislostí
echo -e "${YELLOW}📦 Inštalácia systémových závislostí...${NC}"
if command -v apt-get &> /dev/null; then
    apt-get update
    apt-get install -y python3 python3-pip python3-venv python3-dev \
        mysql-client libmysqlclient-dev \
        redis-server \
        nginx \
        supervisor \
        git \
        curl \
        build-essential
elif command -v yum &> /dev/null; then
    yum install -y python3 python3-pip python3-devel \
        mysql-devel \
        redis \
        nginx \
        supervisor \
        git \
        curl \
        gcc
fi

# 4. Vytvorenie virtual environment
echo -e "${YELLOW}🐍 Vytváranie virtual environment...${NC}"
if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
fi

# 5. Aktivácia venv a inštalácia závislostí
echo -e "${YELLOW}📚 Inštalácia Python závislostí...${NC}"
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip
pip install -r "${APP_DIR}/requirements.txt"

# 6. Konfigurácia .env súboru
echo -e "${YELLOW}⚙️  Konfigurácia .env súboru...${NC}"
if [ ! -f "${APP_DIR}/.env" ]; then
    if [ -f "${APP_DIR}/.env.production.example" ]; then
        cp "${APP_DIR}/.env.production.example" "${APP_DIR}/.env"
        echo -e "${RED}⚠️  DÔLEŽITÉ: Uprav ${APP_DIR}/.env súbor s produkčnými hodnotami!${NC}"
    else
        echo -e "${RED}❌ Chýba .env.production.example súbor${NC}"
        exit 1
    fi
fi

# 7. Vytvorenie databázy
echo -e "${YELLOW}🗄️  Inicializácia databázy...${NC}"
cd "${APP_DIR}"
source "${VENV_DIR}/bin/activate"
python -c "from app import app, db; app.app_context().push(); db.create_all()" || true

# 8. Vytvorenie systemd service
echo -e "${YELLOW}🔧 Vytváranie systemd service...${NC}"
cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=VPS Dashboard API
After=network.target mysql.service redis.service

[Service]
Type=simple
User=${USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
ExecStart=${VENV_DIR}/bin/python ${APP_DIR}/app.py
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=${APP_DIR}/logs ${APP_DIR}/uploads ${APP_DIR}/backups

# Logging
StandardOutput=append:${APP_DIR}/logs/service.log
StandardError=append:${APP_DIR}/logs/service.error.log

[Install]
WantedBy=multi-user.target
EOF

# 9. Vytvorenie Nginx konfigurácie
echo -e "${YELLOW}🌐 Vytváranie Nginx konfigurácie...${NC}"
cat > "/etc/nginx/sites-available/${APP_NAME}" <<EOF
server {
    listen 80;
    server_name _;

    # Redirect to HTTPS (ak máš SSL certifikát)
    # return 301 https://\$server_name\$request_uri;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:6002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support (ak je potrebné)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files
    location /static {
        alias ${APP_DIR}/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Logs
    access_log /var/log/nginx/${APP_NAME}-access.log;
    error_log /var/log/nginx/${APP_NAME}-error.log;
}
EOF

# Aktivácia Nginx site
if [ -d "/etc/nginx/sites-enabled" ]; then
    ln -sf "/etc/nginx/sites-available/${APP_NAME}" "/etc/nginx/sites-enabled/${APP_NAME}"
fi

# 10. Nastavenie oprávnení
echo -e "${YELLOW}🔒 Nastavenie oprávnení...${NC}"
chown -R ${USER}:${USER} "${APP_DIR}"
chmod 600 "${APP_DIR}/.env"
chmod -R 755 "${APP_DIR}"

# 11. Spustenie služieb
echo -e "${YELLOW}▶️  Spúšťanie služieb...${NC}"
systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"
systemctl restart nginx

# 12. Kontrola stavu
echo -e "${YELLOW}🔍 Kontrola stavu služieb...${NC}"
sleep 3
if systemctl is-active --quiet "${SERVICE_NAME}"; then
    echo -e "${GREEN}✅ ${SERVICE_NAME} beží${NC}"
else
    echo -e "${RED}❌ ${SERVICE_NAME} nebeží - skontroluj logy: journalctl -u ${SERVICE_NAME}${NC}"
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx beží${NC}"
else
    echo -e "${RED}❌ Nginx nebeží${NC}"
fi

# 13. Finálne informácie
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment dokončený!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "📋 Ďalšie kroky:"
echo -e "   1. Uprav ${APP_DIR}/.env s produkčnými hodnotami"
echo -e "   2. Skontroluj databázu: ${APP_DIR}/.env"
echo -e "   3. Skontroluj logy: tail -f ${APP_DIR}/logs/app.log"
echo -e "   4. Skontroluj service: systemctl status ${SERVICE_NAME}"
echo -e "   5. Nastav SSL certifikát (Let's Encrypt): certbot --nginx -d yourdomain.com"
echo ""
echo -e "🔗 URL: http://$(hostname -I | awk '{print $1}')"
echo ""

