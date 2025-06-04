# Instrucciones para solucionar problemas con el Admin de Django en Producción

## Problema identificado

El panel de administración de Django (`/admin/`) en el entorno de producción no carga correctamente. Esto suele ocurrir debido a:

1. Problemas con los archivos estáticos (CSS/JS) en producción con `DEBUG = False`
2. Configuración incorrecta de `ALLOWED_HOSTS`
3. Problemas con el servidor web (Nginx) al servir los archivos estáticos

## Solución implementada

Se han realizado las siguientes modificaciones en el código:

1. Ajuste de `.env.production` con configuración adecuada para los archivos estáticos
2. Actualización de `settings.py` para leer correctamente las variables de entorno
3. Mejora en la configuración de Nginx para servir correctamente los archivos estáticos
4. Creación de un script para corregir problemas de archivos estáticos del admin

## Pasos para solucionar el problema en el servidor

### 1. Actualiza los archivos de configuración

Asegúrate de subir al servidor los archivos modificados:
- `.env.production`
- `llevateloexpress_backend/settings.py`
- `llevateloexpress_nginx.conf`
- `scripts/fix_admin_static.sh`

### 2. Ejecuta el script de corrección

```bash
# Asegúrate de darle permisos de ejecución
chmod +x /var/www/llevateloexpress/scripts/fix_admin_static.sh

# Ejecuta el script
cd /var/www/llevateloexpress
sudo ./scripts/fix_admin_static.sh
```

### 3. Verifica los archivos estáticos

Confirma que los archivos estáticos del admin se han copiado correctamente:

```bash
ls -la /var/www/llevateloexpress/staticfiles/admin/
```

Deberías ver directorios como `css`, `js`, `img`, etc.

### 4. Verifica la configuración de Nginx

Asegúrate de que Nginx está configurado correctamente:

```bash
sudo nginx -t
```

Si hay errores, corrígelos antes de continuar.

### 5. Reinicia los servicios

```bash
sudo systemctl restart llevateloexpress
sudo systemctl restart nginx
```

### 6. Verifica los logs

Si el problema persiste, revisa los logs:

```bash
sudo tail -n 100 /var/log/llevateloexpress/error.log
sudo tail -n 100 /var/log/nginx/error.log
```

### 7. Verificación adicional: Permisos

Asegúrate de que los permisos sean correctos:

```bash
sudo chown -R llevateloexpress:www-data /var/www/llevateloexpress/staticfiles/
sudo chmod -R 755 /var/www/llevateloexpress/staticfiles/
```

## Prueba en desarrollo

Para probar que todo funciona correctamente en desarrollo:

1. Ejecuta `python manage.py collectstatic --noinput`
2. Ejecuta `python manage.py runserver`
3. Accede a `http://localhost:8000/admin/`

Si el admin funciona en desarrollo pero no en producción, el problema está relacionado con la configuración del servidor.

## Notas adicionales

- La aplicación `admin_interface` podría estar causando conflictos con los archivos estáticos del admin estándar
- Si continúas teniendo problemas, prueba a establecer temporalmente `DEBUG = True` en producción para identificar el error específico
- Considera añadir `django-debug-toolbar` en desarrollo para una mejor depuración 