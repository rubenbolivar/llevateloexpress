#!/bin/bash
# Script para actualizar la configuración de Nginx en el servidor

# Colorear la salida
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
SERVER_USER="llevateloexpress"
SERVER_IP="" # Completar con la IP del servidor

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

echo -e "${BLUE}=== Actualizando configuración de Nginx ===${NC}"

# Copiar la configuración al servidor
echo -e "${GREEN}Copiando configuración de Nginx al servidor...${NC}"
scp llevateloexpress_nginx.conf $SERVER_USER@$SERVER_IP:/tmp/

# Ejecutar comandos en el servidor
echo -e "${GREEN}Aplicando la configuración en el servidor...${NC}"
ssh $SERVER_USER@$SERVER_IP << EOF
    # Mover la configuración a su lugar
    sudo cp /tmp/llevateloexpress_nginx.conf /etc/nginx/sites-available/llevateloexpress
    
    # Verificar la sintaxis de la configuración
    echo "Verificando sintaxis de Nginx..."
    sudo nginx -t
    
    if [ $? -eq 0 ]; then
        echo "Sintaxis correcta. Reiniciando Nginx..."
        # Reiniciar Nginx
        sudo systemctl restart nginx
        
        # Verificar el estado
        sudo systemctl status nginx | head -n 20
        
        echo "Configuración de Nginx actualizada correctamente."
    else
        echo "Error en la sintaxis de la configuración. No se reinició Nginx."
    fi
EOF

echo -e "${BLUE}=== Proceso completado ===${NC}"
echo -e "Para verificar si los archivos estáticos se sirven correctamente, ejecuta:"
echo -e "${GREEN}curl -I https://llevateloexpress.com/js/products.js${NC}"
echo -e "Deberías ver 'Content-Type: application/javascript' en la respuesta." 