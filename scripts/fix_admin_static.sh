#!/bin/bash
# Script para corregir problemas con los archivos estáticos del admin en producción

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'  # Sin color

echo -e "${YELLOW}Iniciando corrección de archivos estáticos para Django Admin...${NC}"

# Detener el servicio de Django
echo -e "${YELLOW}Deteniendo el servicio de Django...${NC}"
sudo systemctl stop llevateloexpress

# Activar el entorno virtual
source /var/www/llevateloexpress/backend_env/bin/activate

# Limpiar los archivos estáticos existentes
echo -e "${YELLOW}Limpiando archivos estáticos existentes...${NC}"
rm -rf /var/www/llevateloexpress/staticfiles/*

# Recolectar los archivos estáticos
echo -e "${YELLOW}Recolectando archivos estáticos...${NC}"
cd /var/www/llevateloexpress/
python manage.py collectstatic --noinput --clear

# Ajustar permisos
echo -e "${YELLOW}Ajustando permisos...${NC}"
sudo chown -R llevateloexpress:www-data /var/www/llevateloexpress/staticfiles/
sudo chmod -R 755 /var/www/llevateloexpress/staticfiles/

# Reiniciar el servicio de Django
echo -e "${YELLOW}Reiniciando el servicio de Django...${NC}"
sudo systemctl start llevateloexpress

# Reiniciar Nginx
echo -e "${YELLOW}Reiniciando Nginx...${NC}"
sudo systemctl restart nginx

echo -e "${GREEN}¡Proceso completado! Intenta acceder al admin ahora.${NC}"
echo -e "Si el problema persiste, verifica los logs de error con:"
echo -e "sudo tail -n 100 /var/log/llevateloexpress/error.log"
echo -e "sudo tail -n 100 /var/log/nginx/error.log" 