#!/usr/bin/env python
import os
import sys
import django
import json
from pathlib import Path

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

def create_production_env():
    """Crear archivo .env para producción"""
    base_dir = Path(__file__).resolve().parent.parent
    env_file = base_dir / '.env.production'
    
    # Valores por defecto
    env_values = {
        'DJANGO_SECRET_KEY': 'django-insecure-please-change-in-real-production',
        'DJANGO_DEBUG': 'False',
        'DJANGO_ALLOWED_HOSTS': 'llevateloexpress.com www.llevateloexpress.com',
        'DB_NAME': 'llevateloexpress',
        'DB_USER': 'llevateloexpress_user',
        'DB_PASSWORD': 'change_this_password_in_production',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'CORS_ALLOWED_ORIGINS': 'https://llevateloexpress.com https://www.llevateloexpress.com'
    }
    
    # Crear el archivo .env.production
    with open(env_file, 'w') as f:
        for key, value in env_values.items():
            f.write(f'{key}={value}\n')
    
    print(f"✓ Archivo .env.production creado en {env_file}")
    return True

def create_gunicorn_conf():
    """Crear archivo de configuración para Gunicorn"""
    base_dir = Path(__file__).resolve().parent.parent
    gunicorn_file = base_dir / 'gunicorn_conf.py'
    
    gunicorn_config = """# Gunicorn config file
import multiprocessing

# Servidor y workers
bind = "unix:/run/llevateloexpress.sock"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
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
"""
    
    # Escribir el archivo
    with open(gunicorn_file, 'w') as f:
        f.write(gunicorn_config)
    
    print(f"✓ Archivo de configuración de Gunicorn creado en {gunicorn_file}")
    return True

def create_nginx_conf():
    """Crear archivo de configuración para Nginx"""
    base_dir = Path(__file__).resolve().parent.parent
    nginx_file = base_dir / 'llevateloexpress_nginx.conf'
    
    nginx_config = """# Configuración Nginx para LlévateloExpress
server {
    listen 80;
    server_name llevateloexpress.com www.llevateloexpress.com;
    
    # Redireccionar a HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name llevateloexpress.com www.llevateloexpress.com;
    
    # Certificados SSL
    ssl_certificate /etc/letsencrypt/live/llevateloexpress.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/llevateloexpress.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/llevateloexpress.com/chain.pem;
    
    # Configuración SSL
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozSSL:10m;
    ssl_session_tickets off;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Archivos estáticos
    location /static/ {
        alias /var/www/llevateloexpress/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000";
    }
    
    # Archivos media
    location /media/ {
        alias /var/www/llevateloexpress/media/;
        expires 1M;
        add_header Cache-Control "public, max-age=2592000";
    }
    
    # API y aplicación
    location / {
        proxy_pass http://unix:/run/llevateloexpress.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/rss+xml application/atom+xml image/svg+xml;
}
"""
    
    # Escribir el archivo
    with open(nginx_file, 'w') as f:
        f.write(nginx_config)
    
    print(f"✓ Archivo de configuración de Nginx creado en {nginx_file}")
    return True

def create_systemd_service():
    """Crear archivo de servicio para systemd"""
    base_dir = Path(__file__).resolve().parent.parent
    service_file = base_dir / 'llevateloexpress.service'
    
    service_config = """[Unit]
Description=LlévateloExpress Gunicorn Service
After=network.target postgresql.service
Wants=postgresql.service

[Service]
User=llevateloexpress
Group=www-data
WorkingDirectory=/var/www/llevateloexpress
ExecStart=/var/www/llevateloexpress/backend_env/bin/gunicorn -c gunicorn_conf.py llevateloexpress_backend.wsgi:application
Restart=on-failure
RestartSec=5
Environment="PATH=/var/www/llevateloexpress/backend_env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=/var/www/llevateloexpress/.env.production

[Install]
WantedBy=multi-user.target
"""
    
    # Escribir el archivo
    with open(service_file, 'w') as f:
        f.write(service_config)
    
    print(f"✓ Archivo de servicio systemd creado en {service_file}")
    return True

def update_deploy_script():
    """Actualizar el script de despliegue deploy.sh"""
    base_dir = Path(__file__).resolve().parent.parent
    deploy_file = base_dir / 'deploy.sh'
    
    deploy_script = """#!/bin/bash
# Script de despliegue para LlévateloExpress

set -e  # Detener en caso de error

# Configuraciones
SERVER_USER="llevateloexpress"
SERVER_IP=""  # Completar con la IP del servidor
SERVER_PATH="/var/www/llevateloexpress"
REPO_URL="https://github.com/tu-usuario/llevateloexpress.git"  # Actualizar con la URL real del repositorio

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'  # Sin color

# Funciones
print_section() {
    echo -e "\n${YELLOW}==== $1 ====${NC}\n"
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
tar -czf deploy.tar.gz \
    --exclude='.git' \
    --exclude='backend_env' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='node_modules' \
    --exclude='deploy.tar.gz' \
    .

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
"""
    
    # Escribir el archivo
    with open(deploy_file, 'w', encoding='utf-8') as f:
        f.write(deploy_script)
    
    # Hacer el script ejecutable
    os.chmod(deploy_file, 0o755)
    
    print(f"✓ Script de despliegue actualizado en {deploy_file}")
    return True

def main():
    """Función principal del script"""
    print("=== Preparando LlévateloExpress para producción ===\n")
    
    success = True
    success = success and create_production_env()
    success = success and create_gunicorn_conf()
    success = success and create_nginx_conf()
    success = success and create_systemd_service()
    success = success and update_deploy_script()
    
    if success:
        print("\n✅ Preparación para producción completada con éxito!")
        print("\nPasos para el despliegue:")
        print("1. Actualiza la IP del servidor en deploy.sh")
        print("2. Configura los valores correctos en .env.production")
        print("3. Ejecuta deploy.sh para desplegar la aplicación")
    else:
        print("\n❌ Hubo errores durante la preparación para producción")

if __name__ == "__main__":
    main() 