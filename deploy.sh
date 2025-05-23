#!/bin/bash
# Script de despliegue para LlévateloExpress

set -e  # Detener en caso de error

# Configuraciones
SERVER_USER="llevateloexpress"
SERVER_IP=""  # Completar con la IP del servidor
SERVER_PATH="/var/www/llevateloexpress"
REPO_URL="https://github.com/tu-usuario/llevateloexpress.git"  # Actualizar con la URL real del repositorio

# Colores para la salida
RED='[0;31m'
GREEN='[0;32m'
YELLOW='[0;33m'
NC='[0m'  # Sin color

# Funciones
print_section() {
    echo -e "
${YELLOW}==== $1 ====${NC}
"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# Verificar que se ha proporcionado la IP del servidor
if [ -z "$SERVER_IP" ]; then
    print_error "Debes configurar la IP del servidor en el script deploy.sh"
fi

print_section "Iniciando despliegue a producción"

# Crear archivos estáticos localmente
print_section "Recopilando archivos estáticos"
source backend_env/bin/activate
python manage.py collectstatic --no-input
deactivate

# Comprimir proyecto para transferencia
print_section "Preparando archivos para transferencia"
tar -czf deploy.tar.gz     --exclude='.git'     --exclude='backend_env'     --exclude='__pycache__'     --exclude='*.pyc'     --exclude='.DS_Store'     --exclude='node_modules'     --exclude='deploy.tar.gz'     .

# Transferir archivos al servidor
print_section "Transfiriendo archivos al servidor"
scp deploy.tar.gz $SERVER_USER@$SERVER_IP:/tmp/
scp .env.production $SERVER_USER@$SERVER_IP:/tmp/

# Ejecutar comandos remotos
print_section "Configurando servidor"
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
    set -e  # Detener en caso de error
    
    # Crear estructura de directorios
    sudo mkdir -p $SERVER_PATH
    sudo mkdir -p /var/log/llevateloexpress
    
    # Extraer archivos
    cd $SERVER_PATH
    sudo rm -rf *  # Limpiar directorio
    sudo tar -xzf /tmp/deploy.tar.gz -C .
    sudo mv /tmp/.env.production .
    
    # Configurar permisos
    sudo chown -R $SERVER_USER:www-data .
    sudo chmod -R 755 .
    sudo chmod -R 775 media staticfiles
    
    # Configurar entorno virtual
    python3 -m venv backend_env
    source backend_env/bin/activate
    pip install -r requirements.txt
    pip install gunicorn gevent
    
    # Aplicar migraciones
    python manage.py migrate
    
    # Configurar servicios
    sudo cp llevateloexpress_nginx.conf /etc/nginx/sites-available/llevateloexpress
    sudo ln -sf /etc/nginx/sites-available/llevateloexpress /etc/nginx/sites-enabled/
    sudo cp llevateloexpress.service /etc/systemd/system/
    
    # Reiniciar servicios
    sudo systemctl daemon-reload
    sudo systemctl enable llevateloexpress
    sudo systemctl restart llevateloexpress
    sudo systemctl restart nginx
    
    # Configurar certificado SSL (si no existe)
    if [ ! -d "/etc/letsencrypt/live/llevateloexpress.com" ]; then
        sudo apt-get update
        sudo apt-get install -y certbot python3-certbot-nginx
        sudo certbot --nginx -d llevateloexpress.com -d www.llevateloexpress.com --non-interactive --agree-tos --email info@llevateloexpress.com
    fi
    
    # Limpiar archivos temporales
    rm /tmp/deploy.tar.gz
ENDSSH

# Limpiar archivos locales
rm deploy.tar.gz

print_section "Despliegue completado"
print_success "LlévateloExpress se ha desplegado con éxito en el servidor $SERVER_IP"
