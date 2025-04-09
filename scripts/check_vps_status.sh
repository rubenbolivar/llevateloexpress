#!/bin/bash
# Script para verificar el estado de los servicios en el VPS

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'  # Sin color

SERVER_USER="root"
SERVER_IP="203.161.55.87"
SSH_OPTS="-o StrictHostKeyChecking=no"

echo -e "${YELLOW}Verificando el estado de los servicios en el VPS...${NC}"

# Conectarse al servidor y ejecutar los comandos
ssh $SSH_OPTS $SERVER_USER@$SERVER_IP << EOF
    echo -e "\n${YELLOW}===== Estado de PostgreSQL =====${NC}"
    systemctl status postgresql --no-pager
    
    echo -e "\n${YELLOW}===== Estado de Nginx =====${NC}"
    systemctl status nginx --no-pager
    
    echo -e "\n${YELLOW}===== Estado del Servicio de Django =====${NC}"
    systemctl status llevateloexpress --no-pager || echo "El servicio llevateloexpress no está configurado aún"
    
    echo -e "\n${YELLOW}===== Verificación de puertos =====${NC}"
    echo "Verificando el puerto 80 (HTTP):"
    ss -tulpn | grep ":80" || echo "Ningún servicio en el puerto 80"
    
    echo -e "\nVerificando el puerto 443 (HTTPS):"
    ss -tulpn | grep ":443" || echo "Ningún servicio en el puerto 443"
    
    echo -e "\nVerificando el puerto 5432 (PostgreSQL):"
    ss -tulpn | grep ":5432" || echo "PostgreSQL no está escuchando en el puerto 5432"
    
    echo -e "\n${YELLOW}===== Espacio en disco =====${NC}"
    df -h
    
    echo -e "\n${YELLOW}===== Memoria disponible =====${NC}"
    free -h
    
    echo -e "\n${YELLOW}===== Directorio de la aplicación =====${NC}"
    ls -la /var/www/llevateloexpress
    
    echo -e "\n${YELLOW}===== Verificación de Nginx =====${NC}"
    nginx -t
    
    echo -e "\n${YELLOW}===== Logs de errores de Nginx =====${NC}"
    tail -n 20 /var/log/nginx/error.log || echo "No hay archivo de logs de error"
    
    echo -e "\n${YELLOW}===== Logs de errores de Django =====${NC}"
    tail -n 20 /var/log/llevateloexpress/error.log || echo "No hay archivo de logs de error para Django"
EOF

echo -e "\n${GREEN}Verificación de servicios completada.${NC}" 