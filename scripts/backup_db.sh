#!/bin/bash
# Script para hacer backup de la base de datos

echo "=== Iniciando backup de la base de datos ==="
cd /var/www/llevateloexpress

# Cargar variables de entorno
source backend_env/bin/activate
export $(grep -v '^#' .env.production | xargs)

# Crear directorio de backups si no existe
mkdir -p backups

# Nombre del archivo con timestamp
BACKUP_FILE="backups/backup_latin1_$(date +%Y%m%d_%H%M%S).sql"

echo "Creando backup en: $BACKUP_FILE"

# Hacer el backup usando las credenciales del .env
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h $DB_HOST -d $DB_NAME > $BACKUP_FILE

# Verificar el tamaño del backup
if [ -s "$BACKUP_FILE" ]; then
    SIZE=$(ls -lh $BACKUP_FILE | awk '{print $5}')
    echo "✓ Backup creado exitosamente: $BACKUP_FILE ($SIZE)"
    
    # Comprimir el backup
    echo "Comprimiendo backup..."
    gzip -c $BACKUP_FILE > ${BACKUP_FILE}.gz
    echo "✓ Backup comprimido: ${BACKUP_FILE}.gz"
else
    echo "✗ Error: El backup está vacío"
    exit 1
fi

echo "=== Backup completado ===" 