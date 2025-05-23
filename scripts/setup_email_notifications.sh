#!/bin/bash
# Script para configurar el sistema de notificaciones por email en producción

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # Sin color

echo -e "${GREEN}=== Configuración del Sistema de Notificaciones por Email ===${NC}"

# Verificar si estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: Este script debe ejecutarse desde el directorio raíz del proyecto${NC}"
    exit 1
fi

# Función para preguntar al usuario
ask_user() {
    local prompt="$1"
    local var_name="$2"
    local default_value="$3"
    
    if [ -n "$default_value" ]; then
        read -p "$prompt (default: $default_value): " input
        eval "$var_name=\"\${input:-$default_value}\""
    else
        read -p "$prompt: " input
        eval "$var_name=\"$input\""
    fi
}

echo -e "\n${YELLOW}Configurando variables de email...${NC}"

# Recopilar información del usuario
ask_user "Proveedor de email (gmail/sendgrid/ses/other)" EMAIL_PROVIDER "gmail"
ask_user "Email del remitente" EMAIL_FROM ""
ask_user "Contraseña de aplicación o API key" EMAIL_PASSWORD ""

# Configurar según el proveedor
case $EMAIL_PROVIDER in
    "gmail")
        EMAIL_HOST="smtp.gmail.com"
        EMAIL_PORT="587"
        EMAIL_USE_TLS="True"
        EMAIL_USE_SSL="False"
        EMAIL_HOST_USER="$EMAIL_FROM"
        ;;
    "sendgrid")
        EMAIL_HOST="smtp.sendgrid.net"
        EMAIL_PORT="587"
        EMAIL_USE_TLS="True"
        EMAIL_USE_SSL="False"
        EMAIL_HOST_USER="apikey"
        ;;
    "ses")
        EMAIL_HOST="email-smtp.us-east-1.amazonaws.com"
        EMAIL_PORT="587"
        EMAIL_USE_TLS="True"
        EMAIL_USE_SSL="False"
        ask_user "Access Key ID de AWS" EMAIL_HOST_USER ""
        ;;
    *)
        ask_user "Servidor SMTP" EMAIL_HOST ""
        ask_user "Puerto SMTP" EMAIL_PORT "587"
        ask_user "Usar TLS (True/False)" EMAIL_USE_TLS "True"
        ask_user "Usar SSL (True/False)" EMAIL_USE_SSL "False"
        ask_user "Usuario SMTP" EMAIL_HOST_USER "$EMAIL_FROM"
        ;;
esac

# Crear/actualizar .env.production
ENV_FILE=".env.production"

echo -e "\n${YELLOW}Actualizando archivo $ENV_FILE...${NC}"

# Backup del archivo existente si existe
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${GREEN}Backup creado: $ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)${NC}"
fi

# Función para actualizar o agregar variable en .env
update_env_var() {
    local key="$1"
    local value="$2"
    local file="$3"
    
    if grep -q "^$key=" "$file" 2>/dev/null; then
        # Actualizar variable existente
        sed -i "s/^$key=.*/$key=$value/" "$file"
    else
        # Agregar nueva variable
        echo "$key=$value" >> "$file"
    fi
}

# Crear archivo base si no existe
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << 'EOF'
# Configuración de Django para Producción
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=change-this-in-production
DJANGO_ALLOWED_HOSTS=llevateloexpress.com www.llevateloexpress.com 203.161.55.87

# Configuración de Base de Datos
DB_NAME=llevateloexpress
DB_USER=llevateloexpress_user
DB_PASSWORD=llevateloexpress_pass
DB_HOST=localhost
DB_PORT=5432

# Configuración de Archivos Estáticos
STATIC_URL=/static/
STATIC_ROOT=/var/www/llevateloexpress/staticfiles

# Configuración de Seguridad
CSRF_TRUSTED_ORIGINS=https://llevateloexpress.com,http://llevateloexpress.com
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
EOF
fi

# Agregar configuración de email
cat >> "$ENV_FILE" << EOF

# Configuración de Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=$EMAIL_HOST
EMAIL_PORT=$EMAIL_PORT
EMAIL_USE_TLS=$EMAIL_USE_TLS
EMAIL_USE_SSL=$EMAIL_USE_SSL
EMAIL_HOST_USER=$EMAIL_HOST_USER
EMAIL_HOST_PASSWORD=$EMAIL_PASSWORD
DEFAULT_FROM_EMAIL=LlévateloExpress <noreply@llevateloexpress.com>
SERVER_EMAIL=LlévateloExpress <admin@llevateloexpress.com>
EOF

echo -e "${GREEN}Archivo $ENV_FILE actualizado${NC}"

# Aplicar migraciones
echo -e "\n${YELLOW}Aplicando migraciones de notificaciones...${NC}"
python manage.py makemigrations notifications
python manage.py migrate

# Configurar tipos de notificaciones y plantillas
echo -e "\n${YELLOW}Configurando tipos de notificaciones y plantillas...${NC}"
python manage.py setup_notifications

# Crear directorio de logs si no existe
echo -e "\n${YELLOW}Configurando logs...${NC}"
mkdir -p logs
touch logs/notifications.log
chmod 644 logs/notifications.log

# Crear script para procesar cola de emails
QUEUE_SCRIPT="scripts/process_email_queue_daemon.sh"
cat > "$QUEUE_SCRIPT" << 'EOF'
#!/bin/bash
# Script daemon para procesar cola de emails

cd /var/www/llevateloexpress
source backend_env/bin/activate
python manage.py process_email_queue --continuous --interval=60
EOF

chmod +x "$QUEUE_SCRIPT"
echo -e "${GREEN}Script daemon creado: $QUEUE_SCRIPT${NC}"

# Mostrar configuración de crontab sugerida
echo -e "\n${YELLOW}=== Configuración sugerida para crontab ===${NC}"
echo -e "Agregar las siguientes líneas al crontab del servidor:"
echo -e "${GREEN}"
cat << 'EOF'
# Procesar cola de emails cada 5 minutos
*/5 * * * * cd /var/www/llevateloexpress && source backend_env/bin/activate && python manage.py process_email_queue >> /var/log/llevateloexpress/email_queue.log 2>&1

# Reintentar notificaciones fallidas cada hora
0 * * * * cd /var/www/llevateloexpress && source backend_env/bin/activate && python manage.py shell -c "from notifications.services import notification_service; notification_service.retry_failed_notifications()" >> /var/log/llevateloexpress/email_retry.log 2>&1
EOF
echo -e "${NC}"

# Probar configuración de email
echo -e "\n${YELLOW}¿Deseas probar la configuración de email? (y/n)${NC}"
read -p "" test_email

if [ "$test_email" = "y" ] || [ "$test_email" = "Y" ]; then
    echo -e "\n${YELLOW}Probando configuración de email...${NC}"
    
    python manage.py shell << EOF
from django.core.mail import send_mail
from django.conf import settings
import traceback

try:
    send_mail(
        'Prueba de configuración - LlévateloExpress',
        'Este es un email de prueba para verificar la configuración del sistema de notificaciones.',
        settings.DEFAULT_FROM_EMAIL,
        ['$EMAIL_FROM'],
        fail_silently=False,
    )
    print("✓ Email de prueba enviado exitosamente")
except Exception as e:
    print(f"✗ Error enviando email de prueba: {e}")
    traceback.print_exc()
EOF
fi

echo -e "\n${GREEN}=== Configuración completada ===${NC}"
echo -e "\n${YELLOW}Próximos pasos:${NC}"
echo -e "1. Verificar que el archivo $ENV_FILE tiene las credenciales correctas"
echo -e "2. Configurar el crontab con las tareas sugeridas"
echo -e "3. Reiniciar el servicio Django: systemctl restart llevateloexpress"
echo -e "4. Probar el sistema registrando un nuevo usuario"
echo -e "\n${YELLOW}Para monitorear:${NC}"
echo -e "- Logs de notificaciones: tail -f logs/notifications.log"
echo -e "- Panel de admin: https://llevateloexpress.com/admin/ > Notifications"
echo -e "- API de notificaciones: https://llevateloexpress.com/api/notifications/" 