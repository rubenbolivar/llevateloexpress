#!/bin/bash
# Backup Completo LlévateloExpress - Código + Base de Datos
# Creado: 28 Mayo 2025
# Descripción: Script que crea backup completo incluyendo código fuente y ambas bases de datos

TIMESTAMP=$(date +%Y%m%d_%H%M)
BACKUP_DIR="/var/www/backups"

echo "🚀 Backup completo iniciado..."
echo "📅 Timestamp: $TIMESTAMP"
echo ""

# Crear directorio de backups si no existe
mkdir -p $BACKUP_DIR

echo "📊 Creando backup de bases de datos..."
echo "   - Base de datos LATIN1..."
PGPASSWORD='llevateloexpress_pass' pg_dump -h localhost -U llevateloexpress_user llevateloexpress > $BACKUP_DIR/db_latin1_$TIMESTAMP.sql

echo "   - Base de datos UTF8..."
PGPASSWORD='llevateloexpress_pass' pg_dump -h localhost -U llevateloexpress_user llevateloexpress_utf8 > $BACKUP_DIR/db_utf8_$TIMESTAMP.sql

echo "✅ Backups de base de datos completados"
echo "   - LATIN1: $(du -h $BACKUP_DIR/db_latin1_$TIMESTAMP.sql | cut -f1)"
echo "   - UTF8: $(du -h $BACKUP_DIR/db_utf8_$TIMESTAMP.sql | cut -f1)"
echo ""

echo "📁 Creando backup de código fuente..."
cd /var/www
tar --exclude='llevateloexpress/backend_env' \
    --exclude='llevateloexpress/__pycache__' \
    --exclude='llevateloexpress/staticfiles' \
    --exclude='llevateloexpress/logs' \
    --exclude='llevateloexpress/media' \
    -czf $BACKUP_DIR/llevateloexpress_COMPLETO_$TIMESTAMP.tar.gz \
    llevateloexpress/ \
    $BACKUP_DIR/db_latin1_$TIMESTAMP.sql \
    $BACKUP_DIR/db_utf8_$TIMESTAMP.sql

echo "✅ Backup de código fuente completado"

# Limpiar archivos SQL temporales
rm $BACKUP_DIR/db_latin1_$TIMESTAMP.sql
rm $BACKUP_DIR/db_utf8_$TIMESTAMP.sql

echo ""
echo "🎉 BACKUP COMPLETO FINALIZADO"
echo "📁 Archivo: $BACKUP_DIR/llevateloexpress_COMPLETO_$TIMESTAMP.tar.gz"
echo "📊 Tamaño: $(du -h $BACKUP_DIR/llevateloexpress_COMPLETO_$TIMESTAMP.tar.gz | cut -f1)"
echo ""
echo "📋 Contenido del backup:"
echo "   ✅ Código fuente completo"
echo "   ✅ Base de datos LATIN1"
echo "   ✅ Base de datos UTF8"
echo "   ✅ Configuraciones"
echo "   ✅ Templates y archivos estáticos"
echo ""
echo "🔒 Para restaurar:"
echo "   tar -xzf llevateloexpress_COMPLETO_$TIMESTAMP.tar.gz"
echo "" 