#!/bin/bash
# Script para configurar las claves SSH en el servidor

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'  # Sin color

# Configuración
SERVER_USER="root"
SERVER_IP="203.161.55.87"
SSH_KEY_FILE="$HOME/.ssh/llevateloexpress_rsa"
SERVER_PASSWORD="53y2rAv4lzX9EY8WHn"

echo -e "${YELLOW}Iniciando configuración de claves SSH para el servidor...${NC}"

# Verificar si ya existe la clave SSH
if [ ! -f "$SSH_KEY_FILE" ]; then
    echo -e "${YELLOW}Generando par de claves SSH...${NC}"
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_FILE" -N ""
fi

# Configurar SSH para usar esta clave específica para este servidor
CONFIG_FILE="$HOME/.ssh/config"

# Verificar si ya existe la configuración
if grep -q "Host $SERVER_IP" "$CONFIG_FILE" 2>/dev/null; then
    echo -e "${YELLOW}La configuración SSH para el servidor ya existe.${NC}"
else
    echo -e "${YELLOW}Añadiendo configuración SSH para el servidor...${NC}"
    cat >> "$CONFIG_FILE" << EOF

# Configuración para LlévateloExpress
Host $SERVER_IP llevateloexpress.com
    HostName $SERVER_IP
    User $SERVER_USER
    IdentityFile $SSH_KEY_FILE
    StrictHostKeyChecking no
EOF
fi

# Instalar la clave en el servidor usando sshpass (necesita ser instalado: brew install sshpass)
echo -e "${YELLOW}Intentando instalar la clave pública en el servidor...${NC}"
if command -v sshpass &> /dev/null; then
    sshpass -p "$SERVER_PASSWORD" ssh-copy-id -i "$SSH_KEY_FILE.pub" "$SERVER_USER@$SERVER_IP"
else
    echo -e "${YELLOW}sshpass no está instalado. Copiando clave manualmente...${NC}"
    cat "$SSH_KEY_FILE.pub"
    echo -e "\n${YELLOW}Por favor, copia esta clave pública y agrégala manualmente al archivo ${SERVER_USER}@${SERVER_IP}:~/.ssh/authorized_keys${NC}"
    echo -e "Puedes usar el siguiente comando:"
    echo -e "cat ~/.ssh/llevateloexpress_rsa.pub | ssh $SERVER_USER@$SERVER_IP \"mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys\""
fi

# Probar la conexión SSH
echo -e "${YELLOW}Probando conexión SSH...${NC}"
ssh -i "$SSH_KEY_FILE" "$SERVER_USER@$SERVER_IP" "echo 'Conexión SSH exitosa!'"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}¡Configuración SSH completada con éxito!${NC}"
    echo -e "Ahora puedes ejecutar los scripts de despliegue sin necesidad de ingresar contraseñas."
else
    echo -e "${RED}La configuración SSH no se completó correctamente.${NC}"
    echo -e "Por favor, verifica la instalación de la clave pública manualmente."
fi 