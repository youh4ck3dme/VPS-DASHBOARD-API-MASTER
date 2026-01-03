#!/bin/bash
# Zálohovací skript pre MySQL databázu
# Použitie: Pridaj do crontab: 0 3 * * * /var/www/api_dashboard/backup_db.sh

# Konfigurácia
DB_USER="root"
DB_PASS="tvoje_heslo"  # ZMEŇ TOTO!
DB_NAME="api_dashboard"
BACKUP_DIR="/var/www/api_dashboard/backups"
DATE=$(date +\%Y-\%m-\%d_\%H-\%M-\%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"
LOG_FILE="/var/www/api_dashboard/logs/backup.log"

# Vytvor backup adresár ak neexistuje
mkdir -p "$BACKUP_DIR"

# Vytvor zálohu
echo "[$(date)] Začínam zálohovanie databázy..." >> "$LOG_FILE"

mysqldump -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$BACKUP_FILE" 2>> "$LOG_FILE"

if [ $? -eq 0 ]; then
    # Komprimuj zálohu
    gzip "$BACKUP_FILE"
    echo "[$(date)] Záloha vytvorená úspešne: $BACKUP_FILE.gz" >> "$LOG_FILE"

    # Vymaž staré zálohy (staršie ako 30 dní)
    find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +30 -delete
    echo "[$(date)] Staré zálohy vymazané" >> "$LOG_FILE"
else
    echo "[$(date)] CHYBA: Zálohovanie zlyhalo!" >> "$LOG_FILE"
    exit 1
fi

echo "[$(date)] Zálohovanie dokončené" >> "$LOG_FILE"
