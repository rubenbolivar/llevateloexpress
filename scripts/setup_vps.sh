#!/bin/bash
# Script para la configuración inicial del servidor VPS

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'  # Sin color

# Configurar variables
SERVER_USER="root"
SERVER_IP="203.161.55.87"
PASSWORD="53y2rAv4lzX9EY8WHn"
SERVER_PATH="/var/www/llevateloexpress"
APP_USER="llevateloexpress"

# Opciones SSH para evitar problemas de verificación de host
SSH_OPTS="-o StrictHostKeyChecking=no"

echo -e "${YELLOW}Iniciando configuración del servidor...${NC}"

# Ejecutar comandos en el servidor para configurar el entorno
ssh $SSH_OPTS $SERVER_USER@$SERVER_IP << EOF
    # Actualizar el sistema
    echo -e "Actualizando el sistema..."
    apt-get update -y && apt-get upgrade -y
    
    # Instalar dependencias básicas
    echo -e "Instalando dependencias..."
    apt-get install -y python3-pip python3-venv git nginx postgresql postgresql-contrib python3-dev libjpeg-dev libpng-dev libfreetype6-dev certbot python3-certbot-nginx
    
    # Crear usuario para la aplicación si no existe
    if ! id -u $APP_USER > /dev/null 2>&1; then
        echo -e "Creando usuario $APP_USER..."
        useradd -m -s /bin/bash $APP_USER
    fi
    
    # Crear directorios para la aplicación
    echo -e "Configurando directorios..."
    mkdir -p $SERVER_PATH
    mkdir -p $SERVER_PATH/llevateloexpress_backend
    mkdir -p $SERVER_PATH/scripts
    mkdir -p $SERVER_PATH/static
    mkdir -p $SERVER_PATH/media
    mkdir -p $SERVER_PATH/staticfiles
    mkdir -p /var/log/llevateloexpress
    
    # Establecer permisos
    chown -R $APP_USER:www-data $SERVER_PATH
    chmod -R 755 $SERVER_PATH
    chmod -R 775 $SERVER_PATH/media $SERVER_PATH/staticfiles
    chown -R $APP_USER:www-data /var/log/llevateloexpress
    
    # Configurar PostgreSQL
    echo -e "Configurando PostgreSQL..."
    if ! su - postgres -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='llevateloexpress_user'\"" | grep -q 1; then
        su - postgres -c "psql -c \"CREATE USER llevateloexpress_user WITH PASSWORD 'llevateloexpress_pass';\""
        su - postgres -c "psql -c \"CREATE DATABASE llevateloexpress OWNER llevateloexpress_user;\""
        su - postgres -c "psql -c \"ALTER USER llevateloexpress_user CREATEDB;\""
    else
        echo "El usuario llevateloexpress_user ya existe en PostgreSQL"
    fi
    
    # Verificar si existe el archivo de configuración de Nginx
    if [ -f "/etc/nginx/sites-available/llevateloexpress" ]; then
        echo "El archivo de configuración de Nginx ya existe"
    else
        echo "Creando archivo de configuración de Nginx"
        cp /tmp/llevateloexpress_nginx.conf /etc/nginx/sites-available/llevateloexpress
    fi
    
    # Crear enlace simbólico para Nginx si no existe
    if [ ! -L "/etc/nginx/sites-enabled/llevateloexpress" ]; then
        ln -sf /etc/nginx/sites-available/llevateloexpress /etc/nginx/sites-enabled/
    fi
    
    # Configurar entorno virtual de Python
    if [ ! -d "$SERVER_PATH/backend_env" ]; then
        echo "Creando entorno virtual de Python..."
        cd $SERVER_PATH
        python3 -m venv backend_env
    fi
    
    # Verificar si los archivos del proyecto han sido copiados
    if [ -f "$SERVER_PATH/.env.production" ]; then
        echo "Los archivos de configuración ya existen"
    else
        echo "Copiando archivos de configuración"
        cp /tmp/.env.production $SERVER_PATH/
        cp /tmp/settings.py $SERVER_PATH/llevateloexpress_backend/
    fi
    
    # Actualizar archivos del entorno
    echo "Ajustando el archivo .env.production"
    sed -i 's/DB_USER=.*/DB_USER=llevateloexpress_user/' $SERVER_PATH/.env.production
    sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=llevateloexpress_pass/' $SERVER_PATH/.env.production
    
    # Configurar servicio systemd
    if [ ! -f "/etc/systemd/system/llevateloexpress.service" ]; then
        echo "Creando archivo de servicio systemd..."
        cat > /etc/systemd/system/llevateloexpress.service << SERVICEFILE
[Unit]
Description=LlévateloExpress Gunicorn Service
After=network.target postgresql.service
Wants=postgresql.service

[Service]
User=$APP_USER
Group=www-data
WorkingDirectory=$SERVER_PATH
ExecStart=$SERVER_PATH/backend_env/bin/gunicorn -c $SERVER_PATH/gunicorn_conf.py llevateloexpress_backend.wsgi:application
Restart=on-failure
RestartSec=5
Environment="PATH=$SERVER_PATH/backend_env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=$SERVER_PATH/.env.production

[Install]
WantedBy=multi-user.target
SERVICEFILE
    fi
    
    # Crear archivo de configuración de Gunicorn si no existe
    if [ ! -f "$SERVER_PATH/gunicorn_conf.py" ]; then
        echo "Creando archivo de configuración de Gunicorn..."
        cat > $SERVER_PATH/gunicorn_conf.py << GUNICORNFILE
# Gunicorn config file
import multiprocessing

# Servidor y workers
bind = "unix:/run/llevateloexpress.sock"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 2

# Logs
loglevel = "info"
accesslog = "/var/log/llevateloexpress/access.log"
errorlog = "/var/log/llevateloexpress/error.log"

# Seguridad y optimización
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30
limit_request_line = 4096
limit_request_fields = 100
GUNICORNFILE
    fi
    
    # Verificar la configuración de Nginx
    echo "Comprobando configuración de Nginx..."
    nginx -t
    
    echo "Configuración inicial completada."
    echo "El siguiente paso es clonar el repositorio en $SERVER_PATH"
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Error al ejecutar comandos en el servidor.${NC}"
    exit 1
fi

echo -e "${GREEN}Configuración inicial del servidor completada.${NC}"
echo -e "Para completar la instalación, necesitas:"
echo -e "1. Clonar el repositorio en el servidor"
echo -e "2. Instalar las dependencias de Python"
echo -e "3. Realizar las migraciones de Django"
echo -e "4. Recolectar los archivos estáticos"
echo -e "5. Reiniciar los servicios"
echo -e "\nConsulta el archivo DEPLOYMENT_PROTOCOL.md para más detalles." 