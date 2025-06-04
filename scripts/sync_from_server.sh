#!/bin/bash

# Script para sincronizar archivos desde el servidor hacia el entorno local
# Esto permite asegurar que el entorno local tenga todos los archivos del servidor
# antes de comenzar a trabajar

SERVER="root@203.161.55.87"
REMOTE_DIR="/var/www/llevateloexpress/"
LOCAL_DIR="./"
EXCLUDE_DIRS=".git node_modules backend_env __pycache__"

# Construir la cadena de exclusiones
EXCLUDE_PARAMS=""
for dir in $EXCLUDE_DIRS; do
    EXCLUDE_PARAMS="$EXCLUDE_PARAMS --exclude=$dir"
done

echo "=== SINCRONIZACIÓN DESDE SERVIDOR ==="
echo "Este proceso sincronizará archivos desde el servidor hacia tu entorno local."
echo "IMPORTANTE: Cualquier cambio local no guardado podría perderse."
echo ""
read -p "¿Deseas continuar? (s/n): " CONFIRM

if [[ "$CONFIRM" != "s" && "$CONFIRM" != "S" ]]; then
    echo "Operación cancelada."
    exit 0
fi

echo "Iniciando sincronización desde $SERVER:$REMOTE_DIR hacia $LOCAL_DIR..."
echo "Se excluirán los siguientes directorios: $EXCLUDE_DIRS"

# Crear un respaldo local antes de la sincronización
BACKUP_NAME="local_backup_$(date +%Y%m%d%H%M%S).tar.gz"
echo "Creando respaldo del entorno local en $BACKUP_NAME..."
tar -czf $BACKUP_NAME --exclude=backend_env --exclude=node_modules --exclude=.git .

# Realizar la sincronización con rsync
echo "Sincronizando archivos..."
rsync -avz --delete $EXCLUDE_PARAMS $SERVER:$REMOTE_DIR $LOCAL_DIR

if [ $? -eq 0 ]; then
    echo "Sincronización completada con éxito."
    echo "Ahora tu entorno local está sincronizado con el servidor."
    echo "Respaldo creado en: $BACKUP_NAME"
else
    echo "ERROR: La sincronización falló."
    echo "Por favor, revisa la conexión con el servidor y los permisos."
    echo "Respaldo creado en: $BACKUP_NAME"
    exit 1
fi

# Asignar permisos adecuados
echo "Ajustando permisos de archivos..."
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
chmod +x scripts/*.sh

echo "Proceso completo. Entorno local actualizado desde el servidor."
exit 0 