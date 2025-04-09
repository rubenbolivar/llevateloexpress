#!/bin/bash
# Script para actualizar el VPS con los cambios recientes

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'  # Sin color

# Configurar variables (ajustar según tu configuración)
SERVER_USER="llevateloexpress"
SERVER_IP="llevateloexpress.com"  # Cambiar por la IP o dominio del servidor
SERVER_PATH="/var/www/llevateloexpress"

# Opciones SSH para evitar problemas de verificación de host
SSH_OPTS="-o StrictHostKeyChecking=no"
SCP_OPTS="-o StrictHostKeyChecking=no"

echo -e "${YELLOW}Iniciando actualización del VPS...${NC}"

# Crear directorio temporal para archivos
mkdir -p tmp_deploy

# Copiar archivos a actualizar en tmp_deploy
echo -e "${YELLOW}Preparando archivos para envío...${NC}"
cp .env.production tmp_deploy/
cp llevateloexpress_backend/settings.py tmp_deploy/
cp llevateloexpress_nginx.conf tmp_deploy/
cp scripts/fix_admin_static.sh tmp_deploy/
cp ADMIN_FIX_INSTRUCCIONES.md tmp_deploy/

# Enviar archivos al servidor
echo -e "${YELLOW}Enviando archivos al servidor...${NC}"
scp $SCP_OPTS -r tmp_deploy/* $SERVER_USER@$SERVER_IP:/tmp/

# Verificar si el envío fue exitoso
if [ $? -ne 0 ]; then
    echo -e "${RED}Error al enviar archivos al servidor. Verifica la conexión SSH.${NC}"
    echo -e "${YELLOW}Puedes intentar ejecutar: ssh-keygen -R $SERVER_IP${NC}"
    rm -rf tmp_deploy
    exit 1
fi

# Ejecutar comandos en el servidor para actualizar los archivos
echo -e "${YELLOW}Actualizando archivos en el servidor...${NC}"
ssh $SSH_OPTS $SERVER_USER@$SERVER_IP << EOF
    # Mover los archivos a sus ubicaciones correctas
    sudo cp /tmp/.env.production $SERVER_PATH/
    sudo mkdir -p $SERVER_PATH/llevateloexpress_backend/
    sudo cp /tmp/settings.py $SERVER_PATH/llevateloexpress_backend/
    sudo cp /tmp/llevateloexpress_nginx.conf /etc/nginx/sites-available/llevateloexpress
    sudo mkdir -p $SERVER_PATH/scripts/
    sudo cp /tmp/fix_admin_static.sh $SERVER_PATH/scripts/
    sudo cp /tmp/ADMIN_FIX_INSTRUCCIONES.md $SERVER_PATH/
    
    # Establecer permisos
    sudo chown -R $SERVER_USER:www-data $SERVER_PATH/
    sudo chmod +x $SERVER_PATH/scripts/fix_admin_static.sh
    
    # Comprobar configuración de Nginx
    sudo nginx -t
    
    # Ejecutar el script de corrección de admin si la configuración de Nginx es correcta
    if [ \$? -eq 0 ]; then
        echo "Ejecutando script de corrección de admin..."
        cd $SERVER_PATH
        sudo ./scripts/fix_admin_static.sh
    else
        echo "Error en la configuración de Nginx. Por favor, revisa y corrige manualmente."
    fi
EOF

# Verificar si la ejecución en el servidor fue exitosa
if [ $? -ne 0 ]; then
    echo -e "${RED}Error al ejecutar comandos en el servidor.${NC}"
    rm -rf tmp_deploy
    exit 1
fi

# Limpiar archivos temporales
echo -e "${YELLOW}Limpiando archivos temporales...${NC}"
rm -rf tmp_deploy

echo -e "${GREEN}¡Actualización completada!${NC}"
echo -e "Recuerda verificar que el admin de Django funciona correctamente en producción." 