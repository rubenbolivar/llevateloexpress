# Gestión del Servicio Gunicorn - LlévateloExpress

Este documento detalla la gestión completa del servicio Gunicorn que ejecuta el backend Django de LlévateloExpress en producción.

## 📋 Información del Servicio

- **Nombre del servicio**: `llevateloexpress`
- **Usuario de ejecución**: `llevateloexpress`
- **Directorio de trabajo**: `/var/www/llevateloexpress`
- **Socket Unix**: `/tmp/llevateloexpress.sock`
- **Entorno virtual**: `/var/www/llevateloexpress/backend_env`
- **Configuración**: `/var/www/llevateloexpress/gunicorn_conf.py`
- **Archivo de servicio**: `/etc/systemd/system/llevateloexpress.service`

## 🔍 Verificación del Estado

### Comandos de Estado Básicos

```bash
# Estado actual del servicio
sudo systemctl status llevateloexpress

# Verificar si está habilitado para inicio automático
sudo systemctl is-enabled llevateloexpress

# Ver si el servicio está activo
sudo systemctl is-active llevateloexpress
```

### Verificación de Procesos

```bash
# Ver procesos de Gunicorn en ejecución
ps aux | grep gunicorn

# Ver procesos con detalles del comando
ps aux | grep -E "(gunicorn|llevateloexpress)" | grep -v grep

# Ver árbol de procesos
pstree -p | grep gunicorn
```

### Verificación de Socket y Conectividad

```bash
# Verificar socket Unix
ls -la /tmp/llevateloexpress.sock

# Verificar permisos del socket
stat /tmp/llevateloexpress.sock

# Probar conectividad local
curl -I http://localhost/api/financing/plans/
curl -I http://localhost/admin/
```

## ▶️ Inicio del Servicio

### Inicio Normal

```bash
# Iniciar el servicio
sudo systemctl start llevateloexpress

# Verificar que se inició correctamente
sudo systemctl status llevateloexpress

# Ver logs de inicio
sudo journalctl -u llevateloexpress -f
```

### Inicio con Verificación Completa

```bash
# 1. Verificar que no hay procesos previos
ps aux | grep gunicorn

# 2. Limpiar socket si existe
sudo rm -f /tmp/llevateloexpress.sock

# 3. Iniciar servicio
sudo systemctl start llevateloexpress

# 4. Verificar estado
sudo systemctl status llevateloexpress

# 5. Verificar socket creado
ls -la /tmp/llevateloexpress.sock

# 6. Probar API
curl -I http://localhost/api/financing/plans/
```

## 🔄 Reinicio del Servicio

### Reinicio Estándar

```bash
# Reinicio completo (recomendado para cambios de código)
sudo systemctl restart llevateloexpress
```

### Recarga Suave

```bash
# Recarga de workers sin perder conexiones (para cambios menores)
sudo systemctl reload llevateloexpress
```

### Reinicio con Verificación

```bash
# 1. Verificar estado actual
sudo systemctl status llevateloexpress

# 2. Reiniciar
sudo systemctl restart llevateloexpress

# 3. Verificar nuevo estado
sudo systemctl status llevateloexpress

# 4. Ver logs de reinicio
sudo journalctl -u llevateloexpress -n 20
```

### Reinicio Después de Cambios de Configuración

```bash
# Si modificaste archivos de configuración de systemd
sudo systemctl daemon-reload
sudo systemctl restart llevateloexpress
```

## ⏹️ Detener el Servicio

### Detención Normal

```bash
# Detener el servicio
sudo systemctl stop llevateloexpress

# Verificar que se detuvo
sudo systemctl status llevateloexpress

# Verificar que no hay procesos residuales
ps aux | grep gunicorn
```

### Detención Forzada (Solo en emergencias)

```bash
# Si systemctl stop no funciona, forzar detención
sudo systemctl kill llevateloexpress

# O matar procesos manualmente (último recurso)
sudo pkill -f "gunicorn.*llevateloexpress"
```

## 🔧 Configuración de Inicio Automático

### Habilitar/Deshabilitar

```bash
# Habilitar inicio automático al boot
sudo systemctl enable llevateloexpress

# Deshabilitar inicio automático
sudo systemctl disable llevateloexpress

# Verificar estado de habilitación
sudo systemctl is-enabled llevateloexpress
```

## 📊 Monitoreo y Logs

### Logs en Tiempo Real

```bash
# Logs del servicio systemd
sudo journalctl -u llevateloexpress -f

# Logs de error de Gunicorn
sudo tail -f /var/log/llevateloexpress/error.log

# Logs de acceso de Gunicorn
sudo tail -f /var/log/llevateloexpress/access.log
```

### Logs Históricos

```bash
# Últimos 50 logs del servicio
sudo journalctl -u llevateloexpress -n 50

# Logs de las últimas 24 horas
sudo journalctl -u llevateloexpress --since "24 hours ago"

# Logs con más detalle
sudo journalctl -u llevateloexpress -l

# Logs de error específicos
sudo grep ERROR /var/log/llevateloexpress/error.log | tail -10
```

### Estadísticas de Rendimiento

```bash
# Uso de memoria de los procesos Gunicorn
ps aux | grep gunicorn | awk '{print $2, $4, $6, $11}' | column -t

# Número de workers activos
ps aux | grep gunicorn | grep -v grep | wc -l

# Conexiones al socket
sudo netstat -x | grep llevateloexpress
```

## 🛠️ Troubleshooting

### Servicio No Inicia

```bash
# 1. Verificar configuración de Django
cd /var/www/llevateloexpress
sudo -u llevateloexpress bash -c "source backend_env/bin/activate && python manage.py check"

# 2. Probar configuración de Gunicorn
sudo -u llevateloexpress bash -c "source backend_env/bin/activate && gunicorn -c gunicorn_conf.py --check-config llevateloexpress_backend.wsgi:application"

# 3. Verificar permisos
ls -la /var/www/llevateloexpress/
ls -la /var/log/llevateloexpress/

# 4. Ver logs detallados
sudo journalctl -u llevateloexpress -l
```

### Socket No Se Crea

```bash
# 1. Verificar directorio /tmp
ls -la /tmp/ | grep llevateloexpress

# 2. Limpiar socket previo
sudo rm -f /tmp/llevateloexpress.sock

# 3. Verificar permisos del directorio
sudo chmod 1777 /tmp

# 4. Reiniciar servicio
sudo systemctl restart llevateloexpress
```

### Workers No Responden

```bash
# 1. Ver procesos bloqueados
ps aux | grep gunicorn | grep -v grep

# 2. Verificar carga del sistema
top -p $(pgrep -d, -f gunicorn)

# 3. Reinicio forzado si es necesario
sudo systemctl kill llevateloexpress
sudo systemctl start llevateloexpress
```

### Errores de Conectividad

```bash
# 1. Verificar nginx está funcionando
sudo systemctl status nginx

# 2. Verificar configuración de nginx
sudo nginx -t

# 3. Probar conectividad directa al socket
echo -e "GET /api/financing/plans/ HTTP/1.0\r\n\r\n" | nc -U /tmp/llevateloexpress.sock

# 4. Verificar logs de nginx
sudo tail -f /var/log/nginx/error.log
```

## 🔄 Reinicio Completo del Stack

Para problemas complejos, reiniciar todo el stack en orden:

```bash
# 1. Detener servicios
sudo systemctl stop llevateloexpress
sudo systemctl stop nginx

# 2. Limpiar archivos temporales
sudo rm -f /tmp/llevateloexpress.sock

# 3. Verificar que no hay procesos residuales
ps aux | grep -E "(gunicorn|nginx)" | grep -v grep

# 4. Iniciar servicios en orden
sudo systemctl start llevateloexpress
sleep 5  # Esperar que se cree el socket
sudo systemctl start nginx

# 5. Verificar que todo funciona
sudo systemctl status llevateloexpress nginx postgresql
curl -I http://localhost/api/financing/plans/
```

## 📝 Mantenimiento Rutinario

### Verificación Diaria

```bash
# Script para verificación diaria
#!/bin/bash
echo "=== Estado de Servicios ==="
sudo systemctl status llevateloexpress nginx postgresql --no-pager
echo "=== Socket ==="
ls -la /tmp/llevateloexpress.sock
echo "=== API Test ==="
curl -I http://localhost/api/financing/plans/
echo "=== Workers ==="
ps aux | grep gunicorn | grep -v grep | wc -l
```

### Rotación de Logs

```bash
# Los logs rotan automáticamente, pero puedes verificar:
sudo logrotate -d /etc/logrotate.d/llevateloexpress

# Forzar rotación manual si es necesario
sudo logrotate -f /etc/logrotate.d/llevateloexpress
```

### Limpieza de Procesos Zombi

```bash
# Verificar procesos zombi
ps aux | grep 'defunct\|<defunct>'

# Limpiar si es necesario (raro con systemd)
sudo systemctl restart llevateloexpress
```

## 🚨 Comandos de Emergencia

### Parada de Emergencia

```bash
# Detener todo inmediatamente
sudo systemctl stop llevateloexpress nginx
sudo pkill -f gunicorn
```

### Inicio de Emergencia

```bash
# Inicio mínimo para restaurar servicio
sudo rm -f /tmp/llevateloexpress.sock
sudo systemctl start llevateloexpress
sudo systemctl start nginx
```

### Verificación Post-Emergencia

```bash
# Verificar que todo volvió a la normalidad
sudo systemctl status llevateloexpress nginx postgresql
curl -I http://localhost/api/financing/plans/
sudo tail -n 20 /var/log/llevateloexpress/error.log
```

---

## 📞 Contacto

Para problemas que no se resuelvan con esta documentación:
- Revisar logs detallados con `sudo journalctl -u llevateloexpress -l`
- Contactar al equipo de desarrollo con los logs relevantes
- En caso de emergencia, usar los comandos de parada/inicio de emergencia

**Última actualización**: 30 de junio de 2025