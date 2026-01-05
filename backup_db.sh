#!/bin/bash
# Univerzálny zálohovací skript pre SQLite a MySQL databázy
# Použitie: Pridaj do crontab: 0 3 * * * /path/to/backup_db.sh
# Alebo spusti manuálne: ./backup_db.sh

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Načítanie .env súboru ak existuje
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.env" ]; then
    set +e  # Dočasne vypni -e pre source
    set -a
    source "$SCRIPT_DIR/.env" 2>/dev/null || true
    set +a
    set -e  # Zapni -e späť
fi

# Konfigurácia z environment variables (s fallback na predvolené hodnoty)
DB_URL="${DATABASE_URL:-sqlite:///app.db}"
BACKUP_DIR="${BACKUP_DIR:-$SCRIPT_DIR/backups}"
LOG_FILE="${BACKUP_LOG_FILE:-$SCRIPT_DIR/logs/backup.log}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# Validácia RETENTION_DAYS
if ! [[ "$RETENTION_DAYS" =~ ^[0-9]+$ ]] || [ "$RETENTION_DAYS" -lt 0 ]; then
    echo "CHYBA: RETENTION_DAYS musí byť kladné číslo" >&2
    exit 1
fi

# Vytvor potrebné adresáre
mkdir -p "$BACKUP_DIR" || {
    echo "CHYBA: Nepodarilo sa vytvoriť BACKUP_DIR: $BACKUP_DIR" >&2
    exit 1
}

# Vytvor adresár pre log súbor
LOG_DIR="$(dirname "$LOG_FILE")"
if [ "$LOG_DIR" != "." ] && [ "$LOG_DIR" != "$SCRIPT_DIR" ]; then
    mkdir -p "$LOG_DIR" || {
        echo "CHYBA: Nepodarilo sa vytvoriť LOG_DIR: $LOG_DIR" >&2
        exit 1
    }
fi

# Skontroluj, či je BACKUP_DIR zapisovateľný
if [ ! -w "$BACKUP_DIR" ]; then
    echo "CHYBA: BACKUP_DIR nie je zapisovateľný: $BACKUP_DIR" >&2
    exit 1
fi

# Definuj DATE hneď na začiatku (pred použitím v funkciách)
DATE=$(date +%Y-%m-%d_%H-%M-%S)

# Funkcia pre logovanie (bezpečná pre set -e)
log() {
    local message="$1"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S') || timestamp="$(date)"
    echo "[$timestamp] $message" | tee -a "$LOG_FILE" || {
        # Fallback ak tee zlyhá
        echo "[$timestamp] $message" >> "$LOG_FILE" 2>/dev/null || true
    }
}

# Funkcia pre error handling
error_exit() {
    local message="$1"
    log "CHYBA: $message"
    exit 1
}

# Validácia potrebných nástrojov
check_requirements() {
    local missing_tools=()
    
    # Vždy potrebujeme gzip
    if ! command -v gzip >/dev/null 2>&1; then
        missing_tools+=("gzip")
    fi
    
    # Pre MySQL potrebujeme mysqldump
    if [[ "$DB_URL" == mysql* ]] || [[ "$DB_URL" == mariadb* ]]; then
        if ! command -v mysqldump >/dev/null 2>&1; then
            missing_tools+=("mysqldump")
        fi
    fi
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        error_exit "Chýbajú potrebné nástroje: ${missing_tools[*]}"
    fi
}

# Detekcia typu databázy z DATABASE_URL
detect_db_type() {
    if [[ "$DB_URL" == sqlite* ]]; then
        echo "sqlite"
    elif [[ "$DB_URL" == mysql* ]] || [[ "$DB_URL" == mariadb* ]]; then
        echo "mysql"
    else
        error_exit "Nepodporovaný typ databázy: $DB_URL"
    fi
}

# Parsovanie MySQL connection string
parse_mysql_url() {
    # mysql://user:pass@host:port/dbname
    local url="$1"
    if [[ "$url" =~ mysql://([^:]+):([^@]+)@([^:]+):?([0-9]*)/(.+) ]]; then
        DB_USER="${BASH_REMATCH[1]}"
        DB_PASS="${BASH_REMATCH[2]}"
        DB_HOST="${BASH_REMATCH[3]}"
        DB_PORT="${BASH_REMATCH[4]:-3306}"
        DB_NAME="${BASH_REMATCH[5]}"
    elif [[ "$url" =~ mysql://([^@]+)@([^:]+):?([0-9]*)/(.+) ]]; then
        # Bez hesla v URL
        DB_USER="${BASH_REMATCH[1]}"
        DB_PASS="${MYSQL_PASSWORD:-}"
        DB_HOST="${BASH_REMATCH[2]}"
        DB_PORT="${BASH_REMATCH[3]:-3306}"
        DB_NAME="${BASH_REMATCH[4]}"
    else
        # Fallback na environment variables
        DB_USER="${MYSQL_USER:-${DB_USER:-root}}"
        DB_PASS="${MYSQL_PASSWORD:-${DB_PASS:-}}"
        DB_HOST="${MYSQL_HOST:-${DB_HOST:-localhost}}"
        DB_PORT="${MYSQL_PORT:-${DB_PORT:-3306}}"
        DB_NAME="${MYSQL_DATABASE:-${DB_NAME:-api_dashboard}}"
    fi
    
    # Validácia MySQL parametrov
    if [ -z "$DB_USER" ] || [ -z "$DB_HOST" ] || [ -z "$DB_NAME" ]; then
        error_exit "Neplatné MySQL parametre (user, host, database sú povinné)"
    fi
}

# Parsovanie SQLite cesty
parse_sqlite_url() {
    # sqlite:///app.db alebo sqlite:////absolute/path/to/app.db
    local url="$1"
    if [[ "$url" =~ sqlite:///(.+) ]]; then
        local path="${BASH_REMATCH[1]}"
        if [[ "$path" =~ ^/ ]]; then
            # Absolútna cesta
            DB_FILE="$path"
        else
            # Relatívna cesta - relatívne k SCRIPT_DIR
            DB_FILE="$SCRIPT_DIR/$path"
        fi
    else
        DB_FILE="${SQLITE_DB_FILE:-$SCRIPT_DIR/app.db}"
    fi
    
    # Normalizuj cestu (odstráň duplicitné lomítka)
    DB_FILE="$(echo "$DB_FILE" | sed 's|//*|/|g')"
    
    if [ ! -f "$DB_FILE" ]; then
        error_exit "SQLite databáza neexistuje: $DB_FILE"
    fi
    
    if [ ! -r "$DB_FILE" ]; then
        error_exit "SQLite databáza nie je čitateľná: $DB_FILE"
    fi
}

# Zálohovanie MySQL databázy
backup_mysql() {
    log "Začínam zálohovanie MySQL databázy..."
    parse_mysql_url "$DB_URL"
    
    local backup_file="$BACKUP_DIR/db_backup_${DATE}_mysql.sql"
    
    # Bezpečné zálohovanie s MYSQL_PWD (heslo nie je viditeľné v procesoch)
    export MYSQL_PWD="$DB_PASS"
    
    # Vytvor zálohu
    if mysqldump -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" "$DB_NAME" > "$backup_file" 2>> "$LOG_FILE"; then
        unset MYSQL_PWD
    else
        unset MYSQL_PWD
        error_exit "MySQL zálohovanie zlyhalo - skontroluj log: $LOG_FILE"
    fi
    
    # Skontroluj, či záloha nie je prázdna
    if [ ! -s "$backup_file" ]; then
        rm -f "$backup_file"
        error_exit "MySQL záloha je prázdna - zálohovanie zlyhalo"
    fi
    
    # Komprimuj zálohu
    if gzip "$backup_file"; then
        log "MySQL záloha vytvorená úspešne: ${backup_file}.gz ($(du -h "${backup_file}.gz" | cut -f1))"
    else
        error_exit "Kompresia zlyhala"
    fi
    
    # Vymaž staré zálohy
    local deleted_count
    deleted_count=$(find "$BACKUP_DIR" -name "db_backup_*_mysql.sql.gz" -mtime +$RETENTION_DAYS -delete -print 2>/dev/null | wc -l | tr -d ' ')
    if [ "$deleted_count" -gt 0 ]; then
        log "Vymazané staré MySQL zálohy: $deleted_count súborov (staršie ako $RETENTION_DAYS dní)"
    fi
}

# Zálohovanie SQLite databázy
backup_sqlite() {
    log "Začínam zálohovanie SQLite databázy..."
    parse_sqlite_url "$DB_URL"
    
    local backup_file="$BACKUP_DIR/db_backup_${DATE}_sqlite.db"
    
    # Vytvor zálohu (kopírovanie súboru)
    if cp "$DB_FILE" "$backup_file"; then
        log "SQLite databáza skopírovaná: $DB_FILE -> $backup_file"
    else
        error_exit "SQLite zálohovanie zlyhalo - kopírovanie súboru neúspešné"
    fi
    
    # Skontroluj, či záloha nie je prázdna
    if [ ! -s "$backup_file" ]; then
        rm -f "$backup_file"
        error_exit "SQLite záloha je prázdna - zálohovanie zlyhalo"
    fi
    
    # Komprimuj zálohu
    if gzip "$backup_file"; then
        log "SQLite záloha vytvorená úspešne: ${backup_file}.gz ($(du -h "${backup_file}.gz" | cut -f1))"
    else
        rm -f "$backup_file"  # Vymaž nekomprimovanú zálohu ak kompresia zlyhala
        error_exit "Kompresia zlyhala"
    fi
    
    # Vymaž staré zálohy
    local deleted_count
    deleted_count=$(find "$BACKUP_DIR" -name "db_backup_*_sqlite.db.gz" -mtime +$RETENTION_DAYS -delete -print 2>/dev/null | wc -l | tr -d ' ')
    if [ "$deleted_count" -gt 0 ]; then
        log "Vymazané staré SQLite zálohy: $deleted_count súborov (staršie ako $RETENTION_DAYS dní)"
    fi
}

# Hlavný kód
log "=== Začínam zálohovanie databázy ==="
log "DATABASE_URL: ${DB_URL}"
log "BACKUP_DIR: ${BACKUP_DIR}"
log "RETENTION_DAYS: ${RETENTION_DAYS}"

# Skontroluj požiadavky
check_requirements

DB_TYPE=$(detect_db_type)
log "Detekovaný typ databázy: $DB_TYPE"

case "$DB_TYPE" in
    mysql|mariadb)
        backup_mysql
        ;;
    sqlite)
        backup_sqlite
        ;;
    *)
        error_exit "Nepodporovaný typ databázy: $DB_TYPE"
        ;;
esac

log "=== Zálohovanie dokončené úspešne ==="
exit 0
