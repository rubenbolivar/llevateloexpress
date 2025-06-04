#!/bin/bash
# Script para sincronizar TODOS los archivos necesarios con el servidor y arreglar
# los problemas de carga de recursos

# Colorear la salida
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Variables - Actualizado con la información correcta
SERVER_USER="root"
SERVER_IP="203.161.55.87"
SERVER_PATH="/var/www/llevateloexpress"

echo -e "${BLUE}=== INICIANDO SINCRONIZACIÓN COMPLETA DE ARCHIVOS ===${NC}"
echo -e "${YELLOW}Este script resolverá los problemas de carga de recursos estáticos en el servidor.${NC}"

# Paso 1: Verificar primero si podemos conectarnos al servidor
echo -e "${BLUE}=== Verificando conectividad con el servidor ===${NC}"
if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no -q $SERVER_USER@$SERVER_IP exit; then
    echo -e "${RED}Error: No se puede conectar al servidor $SERVER_IP con el usuario $SERVER_USER.${NC}"
    echo "Verifica que la IP sea correcta y que tengas acceso SSH configurado."
    exit 1
fi
echo -e "${GREEN}Conectividad OK.${NC}"

# Paso 2: Primero transferir la configuración de Nginx
echo -e "${BLUE}=== Actualizando configuración de Nginx ===${NC}"
scp -o StrictHostKeyChecking=no llevateloexpress_nginx.conf $SERVER_USER@$SERVER_IP:/tmp/
ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << EOF
    # Mover la configuración a su lugar
    cp /tmp/llevateloexpress_nginx.conf /etc/nginx/sites-available/llevateloexpress
    
    # Asegurarse de que el enlace simbólico exista
    ln -sf /etc/nginx/sites-available/llevateloexpress /etc/nginx/sites-enabled/
    
    # Verificar la sintaxis
    echo "Verificando sintaxis de Nginx..."
    if nginx -t; then
        echo "Sintaxis correcta."
    else
        echo "Error en la sintaxis de la configuración."
        exit 1
    fi
EOF

# Paso 3: Preparar directorio para archivos estáticos
echo -e "${BLUE}=== Preparando estructura de directorios en el servidor ===${NC}"
ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << EOF
    # Asegurarse de que el directorio principal existe y tiene los permisos correctos
    mkdir -p $SERVER_PATH
    chown -R $SERVER_USER:www-data $SERVER_PATH
    chmod -R 755 $SERVER_PATH

    # Limpiar directorios antiguos para evitar archivos huérfanos
    rm -rf $SERVER_PATH/js
    rm -rf $SERVER_PATH/css
    rm -rf $SERVER_PATH/img/products
    mkdir -p $SERVER_PATH/js
    mkdir -p $SERVER_PATH/css
    mkdir -p $SERVER_PATH/img/products
EOF

# Paso 4: Sincronizar todos los archivos HTML
echo -e "${BLUE}=== Sincronizando archivos HTML ===${NC}"
for html_file in *.html; do
    if [ -f "$html_file" ]; then
        echo "Transfiriendo $html_file..."
        scp -o StrictHostKeyChecking=no "$html_file" $SERVER_USER@$SERVER_IP:$SERVER_PATH/
    fi
done

# Paso 5: Sincronizar todos los archivos JavaScript
echo -e "${BLUE}=== Sincronizando archivos JavaScript ===${NC}"
if [ -d "js" ]; then
    echo "Transfiriendo archivos JS..."
    rsync -avz -e "ssh -o StrictHostKeyChecking=no" --progress js/ $SERVER_USER@$SERVER_IP:$SERVER_PATH/js/
else
    echo -e "${RED}Error: No se encontró el directorio js/ local.${NC}"
    exit 1
fi

# Paso 6: Sincronizar todos los archivos CSS
echo -e "${BLUE}=== Sincronizando archivos CSS ===${NC}"
if [ -d "css" ]; then
    echo "Transfiriendo archivos CSS..."
    rsync -avz -e "ssh -o StrictHostKeyChecking=no" --progress css/ $SERVER_USER@$SERVER_IP:$SERVER_PATH/css/
else
    echo -e "${RED}Error: No se encontró el directorio css/ local.${NC}"
    exit 1
fi

# Paso 7: Sincronizar imágenes de productos
echo -e "${BLUE}=== Sincronizando imágenes de productos ===${NC}"
# Primero desde la carpeta products
if [ -d "products" ]; then
    echo "Transfiriendo imágenes desde products/..."
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "mkdir -p $SERVER_PATH/products"
    rsync -avz -e "ssh -o StrictHostKeyChecking=no" --progress products/ $SERVER_USER@$SERVER_IP:$SERVER_PATH/products/
    
    # Copiar las imágenes también a img/products para mantener ambas rutas funcionando
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << EOF
        echo "Copiando imágenes a img/products/..."
        find $SERVER_PATH/products -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" -o -name "*.gif" \) -exec cp {} $SERVER_PATH/img/products/ \;
EOF
fi

# Paso 8: Sincronizar directorio completo de imágenes
echo -e "${BLUE}=== Sincronizando directorio de imágenes ===${NC}"
if [ -d "img" ]; then
    echo "Transfiriendo directorio img/..."
    rsync -avz -e "ssh -o StrictHostKeyChecking=no" --progress img/ $SERVER_USER@$SERVER_IP:$SERVER_PATH/img/
fi

# Paso 9: Ajustar permisos finales
echo -e "${BLUE}=== Ajustando permisos finales ===${NC}"
ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << EOF
    echo "Ajustando permisos de archivos estáticos..."
    chown -R www-data:www-data $SERVER_PATH
    chmod -R 755 $SERVER_PATH
    find $SERVER_PATH -type f -exec chmod 644 {} \;
EOF

# Paso 10: Reiniciar Nginx
echo -e "${BLUE}=== Reiniciando Nginx ===${NC}"
ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << EOF
    echo "Reiniciando Nginx..."
    systemctl restart nginx
EOF

# Paso 11: Verificar los archivos transferidos
echo -e "${BLUE}=== Verificando los archivos transferidos ===${NC}"
ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << EOF
    echo "== Archivos JavaScript =="
    find $SERVER_PATH/js -type f | wc -l
    find $SERVER_PATH/js -type f | sort

    echo -e "\n== Archivos CSS =="
    find $SERVER_PATH/css -type f | wc -l
    
    echo -e "\n== Imágenes de productos =="
    find $SERVER_PATH/img/products -type f | wc -l
    find $SERVER_PATH/products -type f | wc -l
    
    echo -e "\n== Archivos HTML =="
    find $SERVER_PATH -maxdepth 1 -name "*.html" | wc -l
EOF

echo -e "${GREEN}=== SINCRONIZACIÓN COMPLETA ===${NC}"
echo -e "${YELLOW}Para verificar si el sitio funciona correctamente, abre:${NC}"
echo -e "${GREEN}https://llevateloexpress.com/${NC}"
echo -e "${YELLOW}Y verifica si los siguientes recursos cargan correctamente:${NC}"
echo -e "${GREEN}curl -I https://llevateloexpress.com/js/products.js${NC}"
echo -e "${GREEN}curl -I https://llevateloexpress.com/js/main.js${NC}"
echo -e "${GREEN}curl -I https://llevateloexpress.com/js/models.js${NC}"
echo -e "${GREEN}curl -I https://llevateloexpress.com/css/styles.css${NC}" 