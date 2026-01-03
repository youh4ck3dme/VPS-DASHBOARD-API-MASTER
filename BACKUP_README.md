# Zálohovací skript - Dokumentácia

## Prehľad

`backup_db.sh` je univerzálny zálohovací skript, ktorý podporuje **SQLite** aj **MySQL/MariaDB** databázy. Automaticky detekuje typ databázy z `DATABASE_URL` a vytvorí komprimovanú zálohu.

## Funkcie

✅ **Automatická detekcia typu databázy** (SQLite/MySQL)  
✅ **Podpora environment variables** (načítanie z `.env`)  
✅ **Automatická kompresia** (gzip)  
✅ **Automatické mazanie starých záloh** (konfigurovateľné)  
✅ **Detailné logovanie**  
✅ **Robustný error handling**  

## Konfigurácia

### Environment Variables

Skript používa tieto environment variables (s predvolenými hodnotami):

```bash
# Typ databázy (automaticky detekovaný z DATABASE_URL)
DATABASE_URL="sqlite:///app.db"  # alebo mysql://user:pass@host:port/dbname

# Adresár pre zálohy
BACKUP_DIR="./backups"  # Predvolené: ./backups

# Log súbor
BACKUP_LOG_FILE="./logs/backup.log"  # Predvolené: ./logs/backup.log

# Počet dní na uchovanie záloh
BACKUP_RETENTION_DAYS=30  # Predvolené: 30 dní

# MySQL špecifické (ak nie sú v DATABASE_URL)
MYSQL_USER="root"
MYSQL_PASSWORD="tvoje_heslo"
MYSQL_HOST="localhost"
MYSQL_PORT="3306"
MYSQL_DATABASE="api_dashboard"

# SQLite špecifické (ak nie je v DATABASE_URL)
SQLITE_DB_FILE="./app.db"
```

### Príklady DATABASE_URL

**SQLite:**
```bash
DATABASE_URL="sqlite:///app.db"                    # Relatívna cesta
DATABASE_URL="sqlite:////var/www/app.db"           # Absolútna cesta
```

**MySQL:**
```bash
DATABASE_URL="mysql://root:heslo@localhost:3306/api_dashboard"
DATABASE_URL="mysql://user@localhost/api_dashboard"  # Bez hesla (použije MYSQL_PASSWORD)
```

## Použitie

### Manuálne spustenie

```bash
# Základné použitie (použije .env alebo predvolené hodnoty)
./backup_db.sh

# S environment variables
DATABASE_URL="mysql://root:heslo@localhost/api_dashboard" ./backup_db.sh
```

### Automatické zálohovanie (Cron)

Pridaj do crontab pre denné zálohovanie o 3:00:

```bash
# Otvor crontab
crontab -e

# Pridaj riadok (uprav cestu podľa svojho projektu)
0 3 * * * /var/www/api_dashboard/backup_db.sh >> /var/www/api_dashboard/logs/backup_cron.log 2>&1
```

### Systemd Timer (alternatíva k cron)

Vytvor `backup-db.service`:
```ini
[Unit]
Description=Database Backup Service
After=network.target

[Service]
Type=oneshot
User=www-data
WorkingDirectory=/var/www/api_dashboard
EnvironmentFile=/var/www/api_dashboard/.env
ExecStart=/var/www/api_dashboard/backup_db.sh
```

A `backup-db.timer`:
```ini
[Unit]
Description=Daily Database Backup Timer

[Timer]
OnCalendar=daily
OnCalendar=03:00
Persistent=true

[Install]
WantedBy=timers.target
```

Aktivuj:
```bash
sudo systemctl enable backup-db.timer
sudo systemctl start backup-db.timer
```

## Formát záloh

### SQLite
- **Názov:** `db_backup_YYYY-MM-DD_HH-MM-SS_sqlite.db.gz`
- **Formát:** Komprimovaný SQLite súbor

### MySQL
- **Názov:** `db_backup_YYYY-MM-DD_HH-MM-SS_mysql.sql.gz`
- **Formát:** Komprimovaný SQL dump

## Obnovenie zálohy

### SQLite

```bash
# Rozbal zálohu
gunzip backups/db_backup_2025-01-15_03-00-00_sqlite.db.gz

# Obnov databázu
cp backups/db_backup_2025-01-15_03-00-00_sqlite.db app.db
```

### MySQL

```bash
# Rozbal zálohu
gunzip backups/db_backup_2025-01-15_03-00-00_mysql.sql.gz

# Obnov databázu
mysql -u root -p api_dashboard < backups/db_backup_2025-01-15_03-00-00_mysql.sql
```

## Logovanie

Všetky operácie sa logujú do `logs/backup.log`:

```
[2025-01-15 03:00:00] === Začínam zálohovanie databázy ===
[2025-01-15 03:00:00] DATABASE_URL: sqlite:///app.db
[2025-01-15 03:00:00] BACKUP_DIR: ./backups
[2025-01-15 03:00:00] RETENTION_DAYS: 30
[2025-01-15 03:00:00] Detekovaný typ databázy: sqlite
[2025-01-15 03:00:00] Začínam zálohovanie SQLite databázy...
[2025-01-15 03:00:01] SQLite záloha vytvorená úspešne: backups/db_backup_2025-01-15_03-00-00_sqlite.db.gz
[2025-01-15 03:00:01] Staré SQLite zálohy (staršie ako 30 dní) vymazané
[2025-01-15 03:00:01] === Zálohovanie dokončené úspešne ===
```

## Riešenie problémov

### Chyba: "Nepodporovaný typ databázy"
- Skontroluj `DATABASE_URL` - musí začínať `sqlite:///` alebo `mysql://`

### Chyba: "SQLite databáza neexistuje"
- Skontroluj, či existuje súbor databázy
- Skontroluj cestu v `DATABASE_URL`

### Chyba: "MySQL zálohovanie zlyhalo"
- Skontroluj MySQL prihlasovacie údaje
- Skontroluj, či je MySQL server spustený
- Skontroluj oprávnenia používateľa

### Chyba: "Kompresia zlyhala"
- Skontroluj, či je nainštalovaný `gzip`
- Skontroluj oprávnenia na zápis do `BACKUP_DIR`

## Bezpečnosť

⚠️ **Dôležité:**
- Nikdy neukladaj heslá priamo v skripte
- Používaj `.env` súbor s oprávneniami `600` (`chmod 600 .env`)
- Zálohy obsahujú citlivé dáta - zabezpeč ich správne
- Zváž šifrovanie záloh pre produkciu

## Príklady použitia

### Lokálne testovanie (SQLite)

```bash
cd /path/to/project
DATABASE_URL="sqlite:///app.db" ./backup_db.sh
```

### Produkcia (MySQL)

```bash
cd /var/www/api_dashboard
source .env  # Načítaj environment variables
./backup_db.sh
```

### Vlastný adresár pre zálohy

```bash
BACKUP_DIR="/mnt/backups/database" ./backup_db.sh
```

### Kratšia retencia (7 dní)

```bash
BACKUP_RETENTION_DAYS=7 ./backup_db.sh
```

## Integrácia s CI/CD

Môžeš integrovať do CI/CD pipeline:

```yaml
# .github/workflows/backup.yml
name: Database Backup
on:
  schedule:
    - cron: '0 3 * * *'  # Denné o 3:00
jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run backup
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: ./backup_db.sh
      - name: Upload backup
        uses: actions/upload-artifact@v2
        with:
          name: database-backup
          path: backups/
```

## Podpora

Pre otázky alebo problémy, pozri:
- `README.md` - Hlavná dokumentácia projektu
- `QUICKSTART.md` - Rýchly štart
- `IMPROVEMENTS.md` - Návrhy na vylepšenie

