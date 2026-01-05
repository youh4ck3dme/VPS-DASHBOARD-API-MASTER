#!/bin/bash
# ============================================
# PRODUKČNÝ START SCRIPT
# VPS Dashboard API
# ============================================

set -euo pipefail

# Konfigurácia
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${APP_DIR}/venv"
PORT="${PORT:-6002}"

# Farba pre výstup
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🚀 VPS Dashboard API - Production Start${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Kontrola .env súboru
if [ ! -f "${APP_DIR}/.env" ]; then
    echo -e "${YELLOW}⚠️  .env súbor neexistuje!${NC}"
    echo "Vytváram z .env.production.example..."
    if [ -f "${APP_DIR}/.env.production.example" ]; then
        cp "${APP_DIR}/.env.production.example" "${APP_DIR}/.env"
        echo -e "${YELLOW}⚠️  DÔLEŽITÉ: Uprav .env súbor s produkčnými hodnotami!${NC}"
    else
        echo "❌ Chýba .env.production.example súbor"
        exit 1
    fi
fi

# Aktivácia virtual environment
if [ ! -d "${VENV_DIR}" ]; then
    echo "Vytváram virtual environment..."
    python3 -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

# Inštalácia závislostí (ak je potrebné)
if [ ! -f "${VENV_DIR}/.installed" ]; then
    echo "Inštalujem závislosti..."
    pip install --upgrade pip
    pip install -r "${APP_DIR}/requirements.txt"
    touch "${VENV_DIR}/.installed"
fi

# Kontrola Gunicorn
if command -v gunicorn &> /dev/null || [ -f "${VENV_DIR}/bin/gunicorn" ]; then
    echo -e "${GREEN}✅ Spúšťam s Gunicorn (produkcia)${NC}"
    exec "${VENV_DIR}/bin/gunicorn" -c "${APP_DIR}/gunicorn_config.py" app:app
else
    echo -e "${YELLOW}⚠️  Gunicorn nie je nainštalovaný, používam Flask dev server${NC}"
    echo -e "${YELLOW}⚠️  Pre produkciu odporúčame nainštalovať Gunicorn: pip install gunicorn${NC}"
    export FLASK_ENV=production
    export FLASK_DEBUG=False
    exec "${VENV_DIR}/bin/python" "${APP_DIR}/app.py"
fi

