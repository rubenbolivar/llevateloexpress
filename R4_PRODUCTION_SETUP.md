# CONFIGURACIÓN DE PRODUCCIÓN R4 CONECTA
## Setup completo para ambiente de producción

**Fecha**: 2025-07-07  
**Sistema**: LlévateloExpress + R4 Conecta  
**Estado**: Listo para configuración en servidor  

---

## 🔧 CONFIGURACIÓN IP WHITELIST

### 1. IPs Oficiales R4 Conecta

Según documentación oficial, configurar estas IPs en el firewall:

```bash
# IPs oficiales R4 Conecta que deben tener acceso
45.175.213.98
200.74.203.91
190.202.123.66
```

### 2. Configuración en UFW (Ubuntu Firewall)

```bash
# Permitir IPs específicas de R4 para webhooks
sudo ufw allow from 45.175.213.98 to any port 443
sudo ufw allow from 200.74.203.91 to any port 443 
sudo ufw allow from 190.202.123.66 to any port 443

# Verificar reglas
sudo ufw status numbered

# Recargar firewall
sudo ufw reload
```

### 3. Configuración en Nginx (si aplica)

Agregar en `/etc/nginx/sites-available/llevateloexpress`:

```nginx
# Restricción IP para webhooks R4
location /api/payments/webhooks/r4/ {
    allow 45.175.213.98;
    allow 200.74.203.91;
    allow 190.202.123.66;
    deny all;
    
    proxy_pass http://unix:/run/llevateloexpress.sock;
    include /etc/nginx/proxy_params;
}
```

### 4. Configuración en Apache (alternativo)

```apache
<Location "/api/payments/webhooks/r4/">
    Require ip 45.175.213.98
    Require ip 200.74.203.91
    Require ip 190.202.123.66
</Location>
```

---

## 📡 ENDPOINTS DE WEBHOOK IMPLEMENTADOS

### 1. MBnotifica - Notificaciones de Pagos Entrantes

**URL**: `https://llevateloexpress.com/api/payments/webhooks/r4/notify/`

**Request esperado de R4**:
```json
{
    "IdComercio": "13536734",
    "TelefonoComercio": "04129196679", 
    "TelefonoEmisor": "04141300132",
    "Concepto": "PRUEBA",
    "BancoEmisor": "134",
    "Monto": "123.13",
    "FechaHora": "2024-12-05T16:50:48.421Z",
    "Referencia": "83736278",
    "CodigoRed": "00"
}
```

**Headers requeridos**:
```
Content-Type: application/json
Authorization: [UUID-generado-por-comercio]
```

**Response del sistema**:
```json
{
    "abono": true,
    "message": "Pago procesado exitosamente",
    "payment_id": 123
}
```

### 2. MBconsulta - Validación de Clientes

**URL**: `https://llevateloexpress.com/api/payments/webhooks/r4/validate-client/`

**Request esperado de R4**:
```json
{
    "IdCliente": "13536734",
    "Monto": "135.36",
    "TelefonoComercio": "04129196699"
}
```

**Response del sistema**:
```json
{
    "status": true,
    "message": "Cliente autorizado"
}
```

---

## 🔐 CONFIGURACIÓN DE VARIABLES DE ENTORNO

### 1. Archivo .env.production

Agregar/verificar estas variables:

```bash
# R4 Conecta Configuration
R4_BASE_URL=https://r4conecta.mibanco.com.ve/
R4_COMMERCE_TOKEN=TU_COMMERCE_TOKEN_REAL_AQUI
R4_SECRET_KEY=TU_SECRET_KEY_REAL_AQUI
R4_TIMEOUT=30
R4_DEBUG=false

# Logging para R4
LOGGING_R4_LEVEL=INFO
```

### 2. Configuración de Logging

Agregar en `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'r4_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/llevateloexpress/r4_webhooks.log',
        },
    },
    'loggers': {
        'payments.webhooks.r4_webhooks': {
            'handlers': ['r4_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## 🚀 COMANDOS DE DESPLIEGUE

### 1. Actualizar código en servidor

```bash
# SSH al servidor
ssh llevateloexpress@tu-servidor.com

# Ir al directorio del proyecto
cd /var/www/llevateloexpress

# Actualizar código
git pull origin main

# Verificar archivos nuevos
ls -la payments/webhooks/

# Verificar configuración
python manage.py check
```

### 2. Reiniciar servicios

```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Aplicar migraciones (si hay)
python manage.py migrate

# Reiniciar Gunicorn
sudo systemctl restart llevateloexpress

# Reiniciar Nginx
sudo systemctl restart nginx

# Verificar servicios
sudo systemctl status llevateloexpress
sudo systemctl status nginx
```

### 3. Crear logs directory

```bash
# Crear directorio de logs
sudo mkdir -p /var/log/llevateloexpress

# Cambiar permisos
sudo chown llevateloexpress:www-data /var/log/llevateloexpress
sudo chmod 755 /var/log/llevateloexpress
```

---

## 🧪 TESTING DE WEBHOOKS

### 1. Script de Prueba

Crear `test_r4_webhooks.py`:

```python
#!/usr/bin/env python
import requests
import json
import uuid
from datetime import datetime

# URL de test
WEBHOOK_URL = "https://llevateloexpress.com/api/payments/webhooks/r4/notify/"
VALIDATE_URL = "https://llevateloexpress.com/api/payments/webhooks/r4/validate-client/"

def test_notification_webhook():
    """Probar webhook de notificación"""
    
    # Headers según documentación
    headers = {
        'Content-Type': 'application/json',
        'Authorization': str(uuid.uuid4())
    }
    
    # Datos de prueba
    data = {
        "IdComercio": "12345678",
        "TelefonoComercio": "04129196679", 
        "TelefonoEmisor": "04141300132",
        "Concepto": "PRUEBA WEBHOOK",
        "BancoEmisor": "134",
        "Monto": "10.00",
        "FechaHora": datetime.now().isoformat() + "Z",
        "Referencia": "12345678",
        "CodigoRed": "00"
    }
    
    response = requests.post(WEBHOOK_URL, json=data, headers=headers)
    print(f"Notification webhook: {response.status_code}")
    print(f"Response: {response.json()}")

def test_validation_webhook():
    """Probar webhook de validación"""
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': str(uuid.uuid4())
    }
    
    data = {
        "IdCliente": "12345678",
        "Monto": "10.00",
        "TelefonoComercio": "04129196699"
    }
    
    response = requests.post(VALIDATE_URL, json=data, headers=headers)
    print(f"Validation webhook: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    print("🧪 Testing R4 Webhooks...")
    test_notification_webhook()
    test_validation_webhook()
```

### 2. Comandos de Testing

```bash
# Probar endpoint de notificación
curl -X POST https://llevateloexpress.com/api/payments/webhooks/r4/notify/ \
  -H "Content-Type: application/json" \
  -H "Authorization: $(uuidgen)" \
  -d '{
    "IdComercio": "12345678",
    "TelefonoComercio": "04129196679",
    "TelefonoEmisor": "04141300132", 
    "Concepto": "PRUEBA",
    "BancoEmisor": "134",
    "Monto": "10.00",
    "FechaHora": "2024-12-05T16:50:48.421Z",
    "Referencia": "12345678",
    "CodigoRed": "00"
  }'

# Probar endpoint de validación
curl -X POST https://llevateloexpress.com/api/payments/webhooks/r4/validate-client/ \
  -H "Content-Type: application/json" \
  -H "Authorization: $(uuidgen)" \
  -d '{
    "IdCliente": "12345678",
    "Monto": "10.00",
    "TelefonoComercio": "04129196699"
  }'
```

---

## 📊 MONITOREO Y LOGS

### 1. Logs a Monitorear

```bash
# Logs de webhooks R4
tail -f /var/log/llevateloexpress/r4_webhooks.log

# Logs de Django
tail -f /var/log/llevateloexpress/django.log

# Logs de Nginx
tail -f /var/log/nginx/access.log | grep webhook

# Logs de sistema
tail -f /var/log/syslog | grep llevateloexpress
```

### 2. Métricas Importantes

- Número de webhooks recibidos por hora
- Tiempo de respuesta de webhooks
- Errores de validación IP
- Pagos procesados automáticamente
- Clientes validados/rechazados

### 3. Alertas Recomendadas

- Webhook failures > 5% en 1 hora
- IPs no autorizadas intentando acceder
- Errores de formato en datos de R4
- Pagos duplicados detectados

---

## 🔒 CONFIGURACIÓN R4 EN EL BANCO

### Información a proporcionar a R4:

1. **URLs de Webhook**:
   - Notificaciones: `https://llevateloexpress.com/api/payments/webhooks/r4/notify/`
   - Validación: `https://llevateloexpress.com/api/payments/webhooks/r4/validate-client/`

2. **Certificado TLS**: Verificar que el servidor tenga TLS 1.2+

3. **Dominio registrado**: llevateloexpress.com

4. **Datos de contacto técnico** para configuración

---

## ✅ CHECKLIST DE DESPLIEGUE

### Pre-deployment:
- [ ] Variables de entorno configuradas
- [ ] Código actualizado en repositorio
- [ ] Tests de webhook funcionando localmente

### Deployment:
- [ ] Código desplegado en servidor
- [ ] Servicios reiniciados
- [ ] IP whitelist configurado en firewall
- [ ] Logs directory creado

### Post-deployment:
- [ ] Webhooks accesibles desde internet
- [ ] Tests de webhook exitosos
- [ ] Logs funcionando correctamente
- [ ] Información enviada a R4 para configuración

### R4 Configuration:
- [ ] URLs proporcionadas a R4
- [ ] Commerce token recibido
- [ ] Secret key configurado
- [ ] Pruebas en ambiente R4 exitosas

---

**ESTADO**: ✅ **LISTO PARA PRODUCCIÓN**  
**PRÓXIMO PASO**: Configurar IP whitelist y coordinar con R4 para activación