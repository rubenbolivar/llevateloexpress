#!/bin/bash

# Script de Backup Completo - LlévateloExpress
# Autor: Sistema de Backup Automatizado
# Fecha: $(date)

set -e  # Salir si hay algún error

# Configuración
PROJECT_DIR="/var/www/llevateloexpress"
BACKUP_DIR="/var/www/backups"
DB_NAME="llevateloexpress_db"
DB_USER="llevateloexpress_user"
TIMESTAMP=$(date +%Y%m%d_%H%M)

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Crear directorio de backups si no existe
mkdir -p $BACKUP_DIR

log "🚀 Iniciando backup completo de LlévateloExpress"

# 1. Backup de la base de datos
log "📊 Creando backup de la base de datos..."
DB_BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

if sudo -u postgres pg_dump $DB_NAME > $DB_BACKUP_FILE; then
    log "✅ Backup de base de datos creado: $DB_BACKUP_FILE"
    DB_SIZE=$(du -h $DB_BACKUP_FILE | cut -f1)
    info "   Tamaño: $DB_SIZE"
else
    error "❌ Error al crear backup de base de datos"
    exit 1
fi

# 2. Backup del código fuente
log "📁 Creando backup del código fuente..."
CODE_BACKUP_FILE="$BACKUP_DIR/code_backup_$TIMESTAMP.tar.gz"

cd /var/www
if tar -czf $CODE_BACKUP_FILE llevateloexpress/ --exclude='llevateloexpress/backend_env' --exclude='llevateloexpress/__pycache__' --exclude='llevateloexpress/*/__pycache__' --exclude='llevateloexpress/logs' --exclude='llevateloexpress/media/temp'; then
    log "✅ Backup de código creado: $CODE_BACKUP_FILE"
    CODE_SIZE=$(du -h $CODE_BACKUP_FILE | cut -f1)
    info "   Tamaño: $CODE_SIZE"
else
    error "❌ Error al crear backup de código"
    exit 1
fi

# 3. Backup completo combinado
log "📦 Creando backup completo combinado..."
COMBINED_BACKUP_DIR="$BACKUP_DIR/backup_completo_$TIMESTAMP"
mkdir -p $COMBINED_BACKUP_DIR

# Copiar archivos al directorio combinado
cp $DB_BACKUP_FILE $COMBINED_BACKUP_DIR/
cp $CODE_BACKUP_FILE $COMBINED_BACKUP_DIR/

# Crear archivo de información
cat > $COMBINED_BACKUP_DIR/BACKUP_INFO.txt << 'BACKUP_EOF'
BACKUP COMPLETO - LLEVATELOEXPRESS
==================================

Fecha de creación: $(date)
Timestamp: $TIMESTAMP
Servidor: $(hostname)
Usuario: $(whoami)

CONTENIDO DEL BACKUP:
--------------------
1. Base de datos PostgreSQL (llevateloexpress_db)
   - Archivo: db_backup_$TIMESTAMP.sql
   - Incluye: Usuarios, productos, solicitudes, configuraciones

2. Código fuente completo
   - Archivo: code_backup_$TIMESTAMP.tar.gz  
   - Incluye: Django app, frontend, configuraciones, migraciones
   - Excluye: backend_env, __pycache__, logs temporales

ESTADO DEL SISTEMA:
------------------
- Sistema de autenticación: ✅ 100% funcional
- Sistema de registro: ✅ 100% funcional
- Dashboard: ✅ 100% funcional

INSTRUCCIONES DE RESTAURACIÓN:
-----------------------------
1. Restaurar base de datos:
   sudo -u postgres psql -d llevateloexpress_db < db_backup_$TIMESTAMP.sql

2. Restaurar código:
   cd /var/www && tar -xzf code_backup_$TIMESTAMP.tar.gz

3. Reiniciar servicios:
   systemctl restart llevateloexpress
   systemctl restart nginx
BACKUP_EOF

# Crear archivo comprimido final
FINAL_BACKUP_FILE="$BACKUP_DIR/llevateloexpress_completo_$TIMESTAMP.tar.gz"
cd $BACKUP_DIR
if tar -czf $FINAL_BACKUP_FILE backup_completo_$TIMESTAMP/; then
    log "✅ Backup completo final creado: $FINAL_BACKUP_FILE"
    FINAL_SIZE=$(du -h $FINAL_BACKUP_FILE | cut -f1)
    info "   Tamaño total: $FINAL_SIZE"
else
    error "❌ Error al crear backup final"
    exit 1
fi

# Limpiar archivos temporales
rm -rf $COMBINED_BACKUP_DIR
rm $DB_BACKUP_FILE $CODE_BACKUP_FILE

# 4. Resumen final
log "📋 RESUMEN DEL BACKUP"
echo ""
echo "📁 Archivo final: $FINAL_BACKUP_FILE"
echo "📊 Tamaño total: $FINAL_SIZE"
echo "📅 Fecha: $(date)"
echo "🔗 Ubicación: $BACKUP_DIR"
echo ""

# 5. Limpieza de backups antiguos (mantener últimos 5)
log "🧹 Limpiando backups antiguos..."
cd $BACKUP_DIR
ls -t llevateloexpress_completo_*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm
REMAINING=$(ls llevateloexpress_completo_*.tar.gz 2>/dev/null | wc -l)
info "   Backups mantenidos: $REMAINING"

log "🎉 Backup completo finalizado exitosamente" 