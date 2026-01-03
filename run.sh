#!/bin/bash
# Utility skript pre spustenie VPS Dashboard API

set -e

# Farba pre výstup
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 VPS Dashboard API - Spúšťanie${NC}"

# Kontrola virtuálneho prostredia
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtuálne prostredie neexistuje. Vytváram...${NC}"
    python3 -m venv venv
fi

# Aktivácia venv
echo -e "${GREEN}📦 Aktivujem virtuálne prostredie...${NC}"
source venv/bin/activate

# Nastavenie PATH pre pip (fallback ak aktivácia nefunguje)
export PATH="$(pwd)/venv/bin:$PATH"

# Kontrola závislostí
if [ ! -f "venv/.installed" ]; then
    echo -e "${YELLOW}📥 Inštalujem závislosti...${NC}"
    # Použij python3 -m pip pre lepšiu kompatibilitu
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    touch venv/.installed
fi

# Kontrola .env súboru
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env súbor neexistuje. Kopírujem z .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Uprav .env súbor pred spustením!${NC}"
    else
        echo -e "${RED}❌ .env.example neexistuje!${NC}"
        exit 1
    fi
fi

# Vytvorenie potrebných adresárov
mkdir -p logs
mkdir -p backups
mkdir -p scripts

# Kontrola databázy
if [ ! -f "app.db" ] && [ ! -f "instance/app.db" ]; then
    echo -e "${YELLOW}💾 Databáza neexistuje. Vytváram...${NC}"
    # Použij python z venv
    "$(pwd)/venv/bin/python" -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Databáza vytvorená')" || python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Databáza vytvorená')"
fi

# Spustenie aplikácie
echo -e "${GREEN}✅ Všetko pripravené!${NC}"
echo -e "${GREEN}🌐 Server sa spúšťa na porte 6002...${NC}"
echo -e "${YELLOW}📝 Pre zastavenie stlač Ctrl+C${NC}"
echo ""

# Použij python z venv
"$(pwd)/venv/bin/python" app.py || python3 app.py

