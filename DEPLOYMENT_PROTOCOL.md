# Protocolo de Despliegue para LlévateloExpress

Este documento describe los procedimientos para mantener y desplegar la aplicación LlévateloExpress en el servidor de producción.

## Estructura del Proyecto

- **Backend**: Django REST API
- **Frontend**: HTML/CSS/JS (Servido como archivos estáticos por Nginx)
- **Base de datos**: PostgreSQL
- **Servidor web**: Nginx + Gunicorn

## Requisitos de Servidor

- Ubuntu 20.04 LTS o posterior
- Python 3.9+
- PostgreSQL 12+
- Nginx
- Certificados SSL (Let's Encrypt)
- Usuario con permisos sudo

## Procedimiento de Despliegue Inicial

### 1. Preparación del Servidor

```bash
# Actualización del sistema
sudo apt update
sudo apt upgrade -y

# Instalación de dependencias básicas
sudo apt install -y python3-pip python3-venv git nginx postgresql postgresql-contrib

# Instalación de dependencias para procesamiento de imágenes
sudo apt install -y python3-dev libjpeg-dev libpng-dev libfreetype6-dev
```

### 2. Configuración de PostgreSQL

```bash
# Crear usuario y base de datos
sudo -u postgres psql -c "CREATE USER llevateloexpress_user WITH PASSWORD 'tu_contraseña_segura';"
sudo -u postgres psql -c "CREATE DATABASE llevateloexpress OWNER llevateloexpress_user;"
sudo -u postgres psql -c "ALTER USER llevateloexpress_user CREATEDB;"
```

### 3. Configuración del Proyecto

```bash
# Crear directorio y usuario para la aplicación
sudo useradd -m -s /bin/bash llevateloexpress
sudo mkdir -p /var/www/llevateloexpress
sudo chown -R llevateloexpress:www-data /var/www/llevateloexpress
sudo chmod -R 755 /var/www/llevateloexpress

# Clonar el repositorio
cd /var/www/llevateloexpress
sudo -u llevateloexpress git clone https://url-del-repositorio.git .

# Crear y activar entorno virtual
sudo -u llevateloexpress python3 -m venv backend_env
sudo -u llevateloexpress sh -c "source backend_env/bin/activate && pip install -r requirements.txt"
sudo -u llevateloexpress sh -c "source backend_env/bin/activate && pip install gunicorn gevent"

# Configurar archivo .env.production
sudo cp /path/to/.env.production /var/www/llevateloexpress/.env.production
sudo chown llevateloexpress:www-data /var/www/llevateloexpress/.env.production
sudo chmod 640 /var/www/llevateloexpress/.env.production
```

### 4. Configuración de Nginx y Gunicorn

```bash
# Copiar archivos de configuración
sudo cp /var/www/llevateloexpress/llevateloexpress_nginx.conf /etc/nginx/sites-available/llevateloexpress
sudo ln -s /etc/nginx/sites-available/llevateloexpress /etc/nginx/sites-enabled/
sudo cp /var/www/llevateloexpress/llevateloexpress.service /etc/systemd/system/

# Certificados SSL con Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d llevateloexpress.com -d www.llevateloexpress.com

# Reiniciar servicios
sudo systemctl daemon-reload
sudo systemctl enable llevateloexpress
sudo systemctl start llevateloexpress
sudo systemctl restart nginx
```

### 5. Recolección de archivos estáticos y migraciones

```bash
cd /var/www/llevateloexpress
sudo -u llevateloexpress sh -c "source backend_env/bin/activate && python manage.py migrate"
sudo -u llevateloexpress sh -c "source backend_env/bin/activate && python manage.py collectstatic --noinput"
```

### 6. Crear superusuario para el admin

```bash
cd /var/www/llevateloexpress
sudo -u llevateloexpress sh -c "source backend_env/bin/activate && python manage.py createsuperuser"
```

## Actualizaciones y Mantenimiento

### Actualización del Código

Para actualizar la aplicación con cambios recientes:

1. Ejecutar el script de actualización:

```bash
./scripts/update_vps.sh
```

O manualmente:

```bash
# Desde tu entorno local
git push origin main

# En el servidor
cd /var/www/llevateloexpress
sudo -u llevateloexpress git pull
sudo -u llevateloexpress sh -c "source backend_env/bin/activate && pip install -r requirements.txt"
sudo -u llevateloexpress sh -c "source backend_env/bin/activate && python manage.py migrate"
sudo -u llevateloexpress sh -c "source backend_env/bin/activate && python manage.py collectstatic --noinput"
sudo systemctl restart llevateloexpress
sudo systemctl restart nginx
```

### Solución de Problemas

#### Problema con el Admin de Django

Si el admin de Django no carga correctamente en producción:

```bash
cd /var/www/llevateloexpress
sudo ./scripts/fix_admin_static.sh
```

Ver el archivo `ADMIN_FIX_INSTRUCCIONES.md` para más detalles.

#### Verificación de Logs

```bash
# Logs de la aplicación
sudo tail -n 100 /var/log/llevateloexpress/error.log
sudo tail -n 100 /var/log/llevateloexpress/access.log

# Logs de Nginx
sudo tail -n 100 /var/log/nginx/error.log
sudo tail -n 100 /var/log/nginx/access.log

# Logs del sistema
sudo journalctl -u llevateloexpress
```

#### Reinicio de Servicios

```bash
sudo systemctl restart llevateloexpress
sudo systemctl restart nginx
```

## Copias de Seguridad

### Base de Datos

```bash
# Crear directorio para backups
sudo mkdir -p /var/backups/llevateloexpress
sudo chown llevateloexpress:www-data /var/backups/llevateloexpress

# Backup manual
sudo -u llevateloexpress pg_dump -U llevateloexpress_user -h localhost llevateloexpress > /var/backups/llevateloexpress/db_backup_$(date +%Y%m%d).sql

# Restaurar backup
sudo -u llevateloexpress psql -U llevateloexpress_user -h localhost llevateloexpress < /path/to/backup.sql
```

### Configuración de Backup Automático

Agregar al crontab:

```bash
sudo -u llevateloexpress crontab -e
```

Añadir:

```
# Backup diario a las 2 AM
0 2 * * * pg_dump -U llevateloexpress_user -h localhost llevateloexpress > /var/backups/llevateloexpress/db_backup_$(date +\%Y\%m\%d).sql

# Eliminar backups más antiguos de 30 días
0 3 * * * find /var/backups/llevateloexpress/ -name "db_backup_*.sql" -type f -mtime +30 -delete
```

## Seguridad

- Cambiar las contraseñas por defecto en `.env.production`
- Mantener el servidor actualizado con `sudo apt update && sudo apt upgrade -y`
- Configurar firewall (UFW) para permitir solo tráfico necesario
- Revisar logs regularmente para detectar actividades sospechosas 