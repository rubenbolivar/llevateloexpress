#!/bin/bash
# SCRIPT DE BACKUP UNIFICADO - LLEVATELOEXPRESS
set -e

PROJECT_DIR=/var/www/llevateloexpress
BACKUP_ROOT=$PROJECT_DIR/backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y%m%d)

DB_NAME=llevateloexpress_utf8
DB_USER=llevateloexpress_user
DB_PASSWORD=llevateloexpress_pass
MAX_DAILY_BACKUPS=7

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +%H:%M:%S)] $1${NC}"; }
info() { echo -e "${BLUE}[$(date +%H:%M:%S)] $1${NC}"; }

echo ""
echo "=== BACKUP UNIFICADO - LLEVATELOEXPRESS ==="
echo "Timestamp: $TIMESTAMP"
echo ""

mkdir -p "$BACKUP_ROOT"/{daily,weekly,monthly}

log "Backup de base de datos..."
DB_BACKUP="$BACKUP_ROOT/daily/db_${DATE}_${TIMESTAMP}.sql"
export PGPASSWORD="$DB_PASSWORD"
pg_dump -h localhost -U "$DB_USER" "$DB_NAME" > "$DB_BACKUP"
gzip "$DB_BACKUP"
unset PGPASSWORD
log "Base de datos OK: $(du -h ${DB_BACKUP}.gz | cut -f1)"

log "Backup de código..."
CODE_BACKUP="$BACKUP_ROOT/daily/code_${DATE}_${TIMESTAMP}.tar.gz"
cd "$PROJECT_DIR"
tar -czf "$CODE_BACKUP" \
    --exclude='backups' \
    --exclude='backend_env' \
    --exclude='__pycache__' \
    --exclude='*/__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='staticfiles' \
    --exclude='*.tar.gz' \
    --exclude='*.bundle' \
    .
log "Código OK: $(du -h $CODE_BACKUP | cut -f1)"

log "Creando backup combinado..."
COMBINED="$BACKUP_ROOT/daily/llevateloexpress_completo_${DATE}_${TIMESTAMP}.tar.gz"
cd "$BACKUP_ROOT/daily"
tar -czf "$COMBINED" \
    "db_${DATE}_${TIMESTAMP}.sql.gz" \
    "code_${DATE}_${TIMESTAMP}.tar.gz"
rm -f "db_${DATE}_${TIMESTAMP}.sql.gz" "code_${DATE}_${TIMESTAMP}.tar.gz"
log "Backup combinado OK: $(du -h $COMBINED | cut -f1)"

log "Rotación de backups (mantener últimos $MAX_DAILY_BACKUPS)..."
cd "$BACKUP_ROOT/daily"
ls -t llevateloexpress_completo_*.tar.gz 2>/dev/null | tail -n +$((MAX_DAILY_BACKUPS + 1)) | xargs -r rm -f
REMAINING=$(ls -1 llevateloexpress_completo_*.tar.gz 2>/dev/null | wc -l)
info "Backups diarios: $REMAINING archivos"

if [ "$(date +%u)" -eq 7 ]; then
    log "Backup semanal (domingo)..."
    cp "$COMBINED" "$BACKUP_ROOT/weekly/weekly_$(date +%Y_W%V).tar.gz"
    cd "$BACKUP_ROOT/weekly"
    ls -t weekly_*.tar.gz 2>/dev/null | tail -n +5 | xargs -r rm -f
fi

if [ "$(date +%d)" -eq "01" ]; then
    log "Backup mensual (día 1)..."
    cp "$COMBINED" "$BACKUP_ROOT/monthly/monthly_$(date +%Y_%m).tar.gz"
    cd "$BACKUP_ROOT/monthly"
    ls -t monthly_*.tar.gz 2>/dev/null | tail -n +4 | xargs -r rm -f
fi

LOG_FILE="/var/log/llevateloexpress/backup.log"
mkdir -p "$(dirname $LOG_FILE)"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup OK: $COMBINED" >> "$LOG_FILE"

echo ""
log "✅ Backup completado exitosamente"
info "📁 Archivo: $COMBINED"
info "📊 Tamaño: $(du -h $COMBINED | cut -f1)"
echo ""

exit 0
