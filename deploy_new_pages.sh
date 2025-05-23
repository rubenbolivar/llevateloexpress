#!/bin/bash
# Script para desplegar las nuevas páginas de políticas de privacidad y términos de condiciones

# Colorear la salida
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
SERVER_USER="llevateloexpress"
SERVER_IP=$1 # IP del servidor como argumento
SERVER_PATH="/var/www/llevateloexpress"

# Comprobar si se ha proporcionado la IP
if [ -z "$SERVER_IP" ]; then
    echo -e "${RED}Error: Debes proporcionar la IP del servidor como argumento.${NC}"
    echo "Uso: $0 [IP_DEL_SERVIDOR]"
    exit 1
fi

echo -e "${BLUE}=== Iniciando despliegue de nuevas páginas legales ===${NC}"

# Transferir nuevas páginas
echo -e "${GREEN}Transfiriendo nuevas páginas legales...${NC}"
scp templates/politicas-privacidad.html $SERVER_USER@$SERVER_IP:$SERVER_PATH/templates/
scp templates/terminos-condiciones.html $SERVER_USER@$SERVER_IP:$SERVER_PATH/templates/

# Transferir archivos HTML modificados 
echo -e "${GREEN}Actualizando archivos HTML con nuevos enlaces...${NC}"
scp index.html $SERVER_USER@$SERVER_IP:$SERVER_PATH/
scp templates/calculadora.html $SERVER_USER@$SERVER_IP:$SERVER_PATH/templates/
scp templates/catalogo.html $SERVER_USER@$SERVER_IP:$SERVER_PATH/templates/
scp templates/contacto.html $SERVER_USER@$SERVER_IP:$SERVER_PATH/templates/
scp templates/detalle-producto.html $SERVER_USER@$SERVER_IP:$SERVER_PATH/templates/
scp templates/nosotros.html $SERVER_USER@$SERVER_IP:$SERVER_PATH/templates/
scp templates/planes.html $SERVER_USER@$SERVER_IP:$SERVER_PATH/templates/
scp templates/registro.html $SERVER_USER@$SERVER_IP:$SERVER_PATH/templates/

# Ajustar permisos en el servidor
echo -e "${BLUE}=== Verificando permisos en el servidor ===${NC}"
ssh $SERVER_USER@$SERVER_IP << EOF
    echo "Ajustando permisos de archivos..."
    sudo chown -R $SERVER_USER:www-data $SERVER_PATH
    sudo chmod -R 755 $SERVER_PATH
    
    echo "Verificando archivos..."
    ls -la $SERVER_PATH/templates/politicas-privacidad.html
    ls -la $SERVER_PATH/templates/terminos-condiciones.html
EOF

echo -e "${BLUE}=== Proceso completado ===${NC}"
echo -e "Las nuevas páginas y las actualizaciones han sido desplegadas con éxito."
echo -e "Puedes verificar las nuevas páginas en:"
echo -e "${GREEN}https://llevateloexpress.com/templates/politicas-privacidad.html${NC}"
echo -e "${GREEN}https://llevateloexpress.com/templates/terminos-condiciones.html${NC}" 