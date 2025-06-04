#!/bin/bash
# Script para sincronizar archivos estáticos con el servidor

# Colorear la salida
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
SERVER_USER="llevateloexpress"
SERVER_IP="" # Completar con la IP del servidor
SERVER_PATH="/var/www/llevateloexpress"
# Actualizado para incluir la carpeta products con las imágenes
LOCAL_STATIC_DIRS=("js" "css" "img" "products" "*.html")

# Comprobar si se ha proporcionado la IP
if [ -z "$SERVER_IP" ]; then
    echo -e "${RED}Error: Debes proporcionar la IP del servidor como argumento o configurarla en el script.${NC}"
    echo "Uso: $0 [IP_DEL_SERVIDOR]"
    exit 1
fi

# Si se proporciona la IP como argumento, usarla
if [ "$#" -eq 1 ]; then
    SERVER_IP=$1
fi

echo -e "${BLUE}=== Sincronizando archivos estáticos con el servidor ===${NC}"

# Para cada directorio estático
for dir in "${LOCAL_STATIC_DIRS[@]}"; do
    if [[ $dir == *.html ]]; then
        echo -e "${GREEN}Sincronizando archivos HTML...${NC}"
        # Transferir archivos HTML
        scp *.html $SERVER_USER@$SERVER_IP:$SERVER_PATH/
    else
        echo -e "${GREEN}Sincronizando directorio $dir...${NC}"
        # Verificar si el directorio existe localmente
        if [ -d "$dir" ]; then
            # Crear el directorio en el servidor si no existe
            ssh $SERVER_USER@$SERVER_IP "mkdir -p $SERVER_PATH/$dir"
            
            # Transferir archivos
            rsync -avz --progress $dir/ $SERVER_USER@$SERVER_IP:$SERVER_PATH/$dir/
        else
            echo -e "${RED}El directorio $dir no existe localmente.${NC}"
        fi
    fi
done

# Crear estructura correcta para las imágenes de productos
echo -e "${BLUE}=== Asegurando estructura de directorios de imágenes ===${NC}"
ssh $SERVER_USER@$SERVER_IP << EOF
    # Crear directorio img/products si no existe
    echo "Creando estructura de directorios para imágenes de productos..."
    mkdir -p $SERVER_PATH/img/products
    
    # Copiar las imágenes de /products/ a /img/products/ 
    # (esto asegura que las imágenes estén disponibles en ambas ubicaciones)
    if [ -d "$SERVER_PATH/products" ]; then
        echo "Copiando imágenes a la estructura esperada por el código..."
        find $SERVER_PATH/products -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" -o -name "*.gif" | xargs -I {} cp {} $SERVER_PATH/img/products/
    fi
EOF

echo -e "${BLUE}=== Verificando permisos en el servidor ===${NC}"
# Ejecutar comandos en el servidor para corregir permisos
ssh $SERVER_USER@$SERVER_IP << EOF
    echo "Ajustando permisos de archivos estáticos..."
    sudo chown -R $SERVER_USER:www-data $SERVER_PATH
    sudo chmod -R 755 $SERVER_PATH
    
    echo "Verificando archivos..."
    find $SERVER_PATH/js -type f | wc -l
    find $SERVER_PATH/css -type f | wc -l
    find $SERVER_PATH/img -type f | wc -l
    find $SERVER_PATH/products -type f -name "*.jpg" | wc -l
    find $SERVER_PATH/img/products -type f | wc -l
    find $SERVER_PATH -maxdepth 1 -name "*.html" | wc -l
EOF

echo -e "${BLUE}=== Proceso completado ===${NC}"
echo -e "Para verificar si los archivos estáticos se sirven correctamente, ejecuta:"
echo -e "${GREEN}curl -I https://llevateloexpress.com/js/products.js${NC}"
echo -e "${GREEN}curl -I https://llevateloexpress.com/img/products/300.jpg${NC}"
echo -e "Deberías ver los tipos MIME correctos en las respuestas." 