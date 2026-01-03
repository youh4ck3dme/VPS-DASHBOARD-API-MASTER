# Changelog

Všetky významné zmeny v tomto projekte budú zdokumentované v tomto súbore.

## [1.1.0] - 2025-01-15

### Pridané
- ✅ Health check endpoint (`/health`, `/api/health`)
- ✅ API dokumentácia endpoint (`/api/docs`)
- ✅ Rate limiting pre API endpointy (60 req/min)
- ✅ Rozšírené logovanie s file handlerom
- ✅ Dynamická konfigurácia UPLOAD_FOLDER
- ✅ `.env` a `.env.example` súbory
- ✅ `pyrightconfig.json` pre type checking
- ✅ Port forwarding konfigurácia pre Cursor/VSCode
- ✅ Utility skript `run.sh` pre jednoduché spustenie
- ✅ Lepšie error handling s loggingom

### Zmenené
- 🔧 Opravený nekonzistentný port v `app.py`
- 🔧 UPLOAD_FOLDER teraz automaticky detekuje prostredie
- 🔧 Konfigurácia teraz podporuje PORT, FLASK_ENV, FLASK_DEBUG z .env
- 🔧 Pridané `pymysql` a `httpx` do requirements.txt

### Opravené
- 🐛 Chyby s importmi v basedpyright (vypnuté reportMissingImports)
- 🐛 Port forwarding nastavenia
- 🐛 Logging konfigurácia

## [1.0.0] - 2025-01-15

### Pridané
- ✅ Základná Flask aplikácia
- ✅ Autentifikácia s Flask-Login
- ✅ Správa projektov
- ✅ Stripe platby
- ✅ AI generovanie (OpenAI)
- ✅ Automatizácie (Cron)
- ✅ Redis caching
- ✅ MySQL/SQLite podpora

