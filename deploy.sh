#!/bin/bash

# Configuración del servidor
SERVER_IP="203.161.55.87"
USERNAME="root"
PASSWORD="53y2rAv4lzX9EY8WHn"
REMOTE_DIR="/var/www/html/llevateloexpress"
DOMAIN="llevateloexpress.com"
EMAIL="admin@llevateloexpress.com" # Cambia esto a tu email real

# Verificar servidor web e instalar si es necesario
echo "Verificando servidor web..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USERNAME@$SERVER_IP "
    if ! command -v nginx &> /dev/null; then
        echo 'Instalando Nginx...'
        apt update
        apt install -y nginx
    fi
    
    # Iniciar Nginx si no está corriendo
    if ! systemctl is-active --quiet nginx; then
        systemctl start nginx
    fi
    
    # Habilitar Nginx para que inicie con el sistema
    systemctl enable nginx
"

# Crear el directorio remoto si no existe
echo "Creando directorio remoto..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USERNAME@$SERVER_IP "mkdir -p $REMOTE_DIR"

# Transferir archivos
echo "Transfiriendo archivos al servidor..."
sshpass -p "$PASSWORD" rsync -avz --exclude-from='.gitignore' --exclude='.git' --exclude='deploy.sh' ./ $USERNAME@$SERVER_IP:$REMOTE_DIR/

# Configurar permisos
echo "Configurando permisos..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USERNAME@$SERVER_IP "chmod -R 755 $REMOTE_DIR"

# Crear configuración de Nginx
echo "Configurando Nginx con dominio $DOMAIN..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USERNAME@$SERVER_IP "
cat > /etc/nginx/sites-available/llevateloexpress << EOF
server {
    listen 80;
    listen [::]:80;
    
    root ${REMOTE_DIR};
    index index.html;
    
    server_name ${DOMAIN} www.${DOMAIN} ${SERVER_IP};
    
    location / {
        try_files \\\$uri \\\$uri/ =404;
    }

    # Mejoras adicionales
    # Caché de archivos estáticos
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 30d;
        add_header Cache-Control \"public\";
    }
}
EOF

# Habilitar el sitio
ln -sf /etc/nginx/sites-available/llevateloexpress /etc/nginx/sites-enabled/
# Verificar configuración
nginx -t
# Reiniciar Nginx
systemctl restart nginx
"

# Instalar y configurar Let's Encrypt
echo "Configurando HTTPS con Let's Encrypt..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USERNAME@$SERVER_IP "
    # Instalar Certbot y plugin de Nginx
    if ! command -v certbot &> /dev/null; then
        echo 'Instalando Certbot...'
        apt update
        apt install -y certbot python3-certbot-nginx
    fi
    
    # Nota: Este comando solo funcionará si el dominio ya apunta a este servidor
    # De lo contrario, generará un error que deberás resolver manualmente
    echo 'Ejecutando Certbot para obtener certificados SSL...'
    
    # Probar si el dominio ya resuelve a este servidor
    if host ${DOMAIN} | grep -q ${SERVER_IP}; then
        # El dominio ya apunta a este servidor, podemos proceder con la generación automática
        certbot --nginx --non-interactive --agree-tos --email ${EMAIL} -d ${DOMAIN} -d www.${DOMAIN}
    else
        echo 'AVISO: El dominio aún no apunta a este servidor.'
        echo 'Una vez que el dominio apunte a ${SERVER_IP}, ejecuta el siguiente comando para habilitar HTTPS:'
        echo \"certbot --nginx --non-interactive --agree-tos --email ${EMAIL} -d ${DOMAIN} -d www.${DOMAIN}\"
    fi
"

echo "¡Despliegue completado con éxito!"
echo "El sitio está configurado con el dominio: $DOMAIN"
echo "Nota: Asegúrate de que el dominio $DOMAIN tenga un registro DNS tipo A que apunte a $SERVER_IP"
echo "Puedes acceder temporalmente al sitio a través de: http://$SERVER_IP/"
echo ""
echo "IMPORTANTE PARA HTTPS:"
echo "1. Configura los registros DNS de tu dominio para que apunten a: $SERVER_IP"
echo "2. Una vez que los DNS se propaguen (puede tardar hasta 48 horas),"
echo "   ejecuta el siguiente comando en el servidor para habilitar HTTPS automáticamente:"
echo "   certbot --nginx --email $EMAIL -d $DOMAIN -d www.$DOMAIN" 