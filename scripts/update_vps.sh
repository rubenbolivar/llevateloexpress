#!/bin/bash
# Script para actualizar el VPS con los cambios recientes

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'  # Sin color

# Configurar variables
SERVER_USER="root"
SERVER_IP="203.161.55.87"
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
cp DEPLOYMENT_PROTOCOL.md tmp_deploy/

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
    # Verificar y crear directorios necesarios
    mkdir -p $SERVER_PATH
    mkdir -p $SERVER_PATH/llevateloexpress_backend
    mkdir -p $SERVER_PATH/scripts
    mkdir -p /var/log/llevateloexpress
    
    # Mover los archivos a sus ubicaciones correctas
    cp /tmp/.env.production $SERVER_PATH/
    cp /tmp/settings.py $SERVER_PATH/llevateloexpress_backend/
    cp /tmp/llevateloexpress_nginx.conf /etc/nginx/sites-available/llevateloexpress 2>/dev/null || cp /tmp/llevateloexpress_nginx.conf /tmp/
    cp /tmp/fix_admin_static.sh $SERVER_PATH/scripts/
    cp /tmp/ADMIN_FIX_INSTRUCCIONES.md $SERVER_PATH/
    cp /tmp/DEPLOYMENT_PROTOCOL.md $SERVER_PATH/
    
    # Establecer permisos
    chmod +x $SERVER_PATH/scripts/fix_admin_static.sh
    
    # Comprobar si Nginx está instalado
    if command -v nginx &> /dev/null; then
        echo "Nginx está instalado, verificando configuración..."
        # Verificar si existe el directorio sites-available
        if [ -d "/etc/nginx/sites-available" ]; then
            # Crear enlace simbólico si no existe
            if [ ! -L "/etc/nginx/sites-enabled/llevateloexpress" ]; then
                ln -sf /etc/nginx/sites-available/llevateloexpress /etc/nginx/sites-enabled/ 2>/dev/null || echo "No se pudo crear el enlace simbólico"
            fi
            # Comprobar configuración de Nginx
            nginx -t 2>/dev/null
            if [ \$? -eq 0 ]; then
                echo "Configuración de Nginx correcta, reiniciando servicio..."
                systemctl restart nginx 2>/dev/null || service nginx restart 2>/dev/null || echo "No se pudo reiniciar Nginx"
            else
                echo "Error en la configuración de Nginx. Revisa manualmente."
            fi
        else
            echo "No se encontró el directorio /etc/nginx/sites-available"
        fi
    else
        echo "Nginx no está instalado en el sistema"
    fi
    
    # Verificar si Django está instalado 
    if command -v python3 &> /dev/null; then
        # Verificar si existe el entorno virtual
        if [ -d "$SERVER_PATH/backend_env" ]; then
            echo "Entorno virtual encontrado, ejecutando collectstatic..."
            cd $SERVER_PATH
            source backend_env/bin/activate 2>/dev/null && python manage.py collectstatic --noinput || echo "No se pudo ejecutar collectstatic"
        else
            echo "No se encontró el entorno virtual Django"
        fi
    else
        echo "Python3 no está instalado en el sistema"
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
echo -e "Se han transferido los archivos de configuración al servidor."
echo -e "Para continuar con la configuración completa, sigue las instrucciones en DEPLOYMENT_PROTOCOL.md" 