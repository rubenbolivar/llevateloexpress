#!/bin/bash
# Script para desplegar archivos de backend relacionados con la autenticación

# Colores para la salida
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Variables
SERVER_USER="root"
SERVER_IP="203.161.55.87"
SERVER_PATH="/var/www/llevateloexpress"

echo -e "${YELLOW}Desplegando archivos de backend para autenticación...${NC}"

# Verificar conexión
echo -e "${YELLOW}Verificando conexión con el servidor...${NC}"
if ! ssh -o StrictHostKeyChecking=no -q $SERVER_USER@$SERVER_IP exit; then
    echo -e "${RED}Error: No se puede conectar al servidor.${NC}"
    exit 1
fi
echo -e "${GREEN}Conexión establecida.${NC}"

# Transferir archivos de backend
echo -e "${YELLOW}Transfiriendo archivos de autenticación al servidor...${NC}"
scp -o StrictHostKeyChecking=no users/views.py $SERVER_USER@$SERVER_IP:$SERVER_PATH/users/
scp -o StrictHostKeyChecking=no users/urls.py $SERVER_USER@$SERVER_IP:$SERVER_PATH/users/

# Configurar permisos y reiniciar servicios
echo -e "${YELLOW}Configurando permisos y reiniciando servicios...${NC}"
ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << EOF
    # Ajustar permisos
    chown -R www-data:www-data $SERVER_PATH/users
    
    # Reiniciar el servicio Django
    echo "Reiniciando servicios..."
    systemctl restart llevateloexpress
    systemctl restart nginx
    
    # Verificar que los archivos se hayan transferido correctamente
    echo "Verificando archivos transferidos:"
    ls -la $SERVER_PATH/users/views.py
    ls -la $SERVER_PATH/users/urls.py
EOF

echo -e "${GREEN}¡Despliegue de backend completado!${NC}"
echo -e "${YELLOW}Ya debería estar disponible el endpoint de CSRF: ${GREEN}https://llevateloexpress.com/api/users/csrf-token/${NC}"
echo -e "${YELLOW}Puedes verificarlo con: ${NC}curl -I https://llevateloexpress.com/api/users/csrf-token/" 