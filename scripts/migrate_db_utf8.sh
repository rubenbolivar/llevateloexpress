#!/bin/bash
# Script para migrar la base de datos de LATIN1 a UTF8

echo "=== MIGRACIÓN DE BASE DE DATOS A UTF8 ==="
echo "Fecha: $(date)"

cd /var/www/llevateloexpress

# Cargar variables de entorno
source backend_env/bin/activate

# Cargar variables del .env de forma segura
export DB_NAME=$(grep "^DB_NAME=" .env.production | cut -d'=' -f2)
export DB_USER=$(grep "^DB_USER=" .env.production | cut -d'=' -f2)
export DB_PASSWORD=$(grep "^DB_PASSWORD=" .env.production | cut -d'=' -f2)
export DB_HOST=$(grep "^DB_HOST=" .env.production | cut -d'=' -f2)
export DB_PORT=$(grep "^DB_PORT=" .env.production | cut -d'=' -f2)

# Verificar que tenemos el backup
BACKUP_FILE=$(ls -t backups/backup_latin1_*.sql 2>/dev/null | head -1)
if [ -z "$BACKUP_FILE" ]; then
    echo "ERROR: No se encontró archivo de backup"
    exit 1
fi

echo "Usando backup: $BACKUP_FILE"

# Paso 1: Crear la nueva base de datos con UTF8
echo ""
echo "1. Creando nueva base de datos con UTF8..."
sudo -u postgres createdb -E UTF8 -l en_US.UTF-8 -T template0 llevateloexpress_utf8

# Paso 2: Dar permisos al usuario
echo "2. Asignando permisos..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE llevateloexpress_utf8 TO $DB_USER;"

# Paso 3: Convertir el backup de LATIN1 a UTF8
echo "3. Convirtiendo backup a UTF8..."
iconv -f LATIN1 -t UTF8 "$BACKUP_FILE" -o backups/backup_utf8.sql

# Paso 4: Restaurar en la nueva base de datos
echo "4. Restaurando datos en la nueva base de datos..."
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d llevateloexpress_utf8 < backups/backup_utf8.sql

# Paso 5: Verificar la migración
echo "5. Verificando la migración..."
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d llevateloexpress_utf8 -c "SELECT COUNT(*) as total_productos FROM products_product;" 2>/dev/null

echo ""
echo "=== MIGRACIÓN COMPLETADA ==="
echo "La nueva base de datos 'llevateloexpress_utf8' ha sido creada."
echo ""
echo "PRÓXIMOS PASOS:"
echo "1. Actualizar .env.production cambiando DB_NAME=llevateloexpress_utf8"
echo "2. Probar la aplicación"
echo "3. Si todo funciona bien, renombrar las bases de datos" 