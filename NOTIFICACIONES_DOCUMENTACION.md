# Sistema de Notificaciones por Email - LlévateloExpress

## Descripción General

El sistema de notificaciones por email de LlévateloExpress permite enviar comunicaciones automatizadas a los usuarios según diferentes eventos y acciones en la plataforma. El sistema está diseñado para ser escalable, configurable y fácil de gestionar.

## Características Principales

- **✉️ Gestión de Plantillas**: Plantillas HTML y texto personalizables
- **👤 Preferencias de Usuario**: Control granular de notificaciones por usuario
- **📊 Seguimiento de Estado**: Monitoreo completo del estado de envío
- **🔄 Cola de Procesamiento**: Sistema de cola para envío asíncrono
- **📈 Estadísticas**: Métricas detalladas de notificaciones
- **🛠️ Panel de Administración**: Gestión completa desde Django Admin
- **🔒 Desuscripción**: Mecanismo de opt-out para usuarios

## Tipos de Notificaciones

### Notificaciones de Usuario
- **Bienvenida**: Email de bienvenida para nuevos usuarios
- **Confirmación de Registro**: Confirmación de cuenta creada
- **Recordatorios**: Notificaciones programadas

### Notificaciones de Financiamiento
- **Solicitud de Financiamiento**: Confirmación de solicitud recibida
- **Solicitud Aprobada**: Notificación de aprobación
- **Solicitud Rechazada**: Notificación de rechazo
- **Solicitud Pendiente**: Status de revisión en proceso

### Notificaciones de Pagos
- **Recordatorio de Pago**: Recordatorios de cuotas pendientes
- **Confirmación de Pago**: Confirmación de pagos recibidos
- **Solicitud de Documentos**: Requerimiento de documentación adicional

### Notificaciones Promocionales
- **Boletín Informativo**: Newsletter con novedades
- **Promociones Especiales**: Ofertas y promociones
- **Mantenimiento del Sistema**: Notificaciones técnicas

## Configuración

### Variables de Entorno (.env.production)

```bash
# Configuración de Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=LlévateloExpress <noreply@llevateloexpress.com>
SERVER_EMAIL=LlévateloExpress <noreply@llevateloexpress.com>
```

### Configuración para Gmail

1. **Crear una App Password en Gmail**:
   - Ir a Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generar una contraseña para "Mail"

2. **Configurar las variables**:
   ```bash
   EMAIL_HOST_USER=tu-email@gmail.com
   EMAIL_HOST_PASSWORD=tu-app-password-de-16-digitos
   ```

### Configuración para otros proveedores

**SendGrid**:
```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=tu-sendgrid-api-key
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

**Amazon SES**:
```bash
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_HOST_USER=tu-access-key-id
EMAIL_HOST_PASSWORD=tu-secret-access-key
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

## Instalación y Configuración

### 1. Ejecutar Migraciones

```bash
python manage.py makemigrations notifications
python manage.py migrate
```

### 2. Configurar Tipos de Notificaciones y Plantillas

```bash
python manage.py setup_notifications
```

### 3. Configurar Procesamiento de Cola

**Para desarrollo (una vez)**:
```bash
python manage.py process_email_queue
```

**Para producción (continuo)**:
```bash
python manage.py process_email_queue --continuous --interval=60
```

### 4. Configurar Cron Job para Producción

Agregar al crontab del servidor:

```bash
# Procesar cola de emails cada 5 minutos
*/5 * * * * cd /var/www/llevateloexpress && python manage.py process_email_queue >> /var/log/llevateloexpress/email_queue.log 2>&1

# Reintentar notificaciones fallidas cada hora
0 * * * * cd /var/www/llevateloexpress && python manage.py shell -c "from notifications.services import notification_service; notification_service.retry_failed_notifications()" >> /var/log/llevateloexpress/email_retry.log 2>&1
```

## Uso del Sistema

### Envío Básico de Notificaciones

```python
from notifications.services import send_welcome_email, send_registration_confirmation
from django.contrib.auth.models import User

# Email de bienvenida
user = User.objects.get(email='usuario@ejemplo.com')
send_welcome_email(user)

# Confirmación de registro
send_registration_confirmation(user)
```

### Envío Personalizado

```python
from notifications.services import notification_service

# Envío con contexto personalizado
notification_service.send_notification(
    user=user,
    notification_type_code='financing_application',
    context={
        'application_id': 'APP-001',
        'product_name': 'Honda CB125F',
        'amount': '$1,500',
        'plan': 'Plan 50-50'
    }
)

# Envío programado
from django.utils import timezone
from datetime import timedelta

notification_service.send_notification(
    user=user,
    notification_type_code='payment_reminder',
    context={'amount_due': '$150'},
    schedule_at=timezone.now() + timedelta(days=7)
)
```

### Integración con Vistas

```python
# En views.py de la app users
from notifications.services import send_registration_confirmation

class RegisterView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Enviar email de confirmación
            send_registration_confirmation(user)
            
            return Response({
                "success": True,
                "message": "Usuario creado exitosamente",
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        # ... resto del código
```

## API Endpoints

### Notificaciones del Usuario

```
GET /api/notifications/
```
Obtiene las notificaciones del usuario autenticado con paginación.

**Parámetros**:
- `page`: Número de página (default: 1)
- `per_page`: Elementos por página (default: 20, max: 50)

**Respuesta**:
```json
{
  "success": true,
  "notifications": [...],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_count": 45,
    "has_next": true,
    "has_previous": false
  }
}
```

### Estadísticas de Notificaciones

```
GET /api/notifications/stats/
```

**Respuesta**:
```json
{
  "success": true,
  "stats": {
    "total": 25,
    "unread": 3,
    "failed": 1,
    "by_type": {
      "welcome": {"name": "Bienvenida", "count": 1},
      "financing_application": {"name": "Solicitud de Financiamiento", "count": 5}
    }
  }
}
```

### Preferencias de Notificación

```
GET /api/notifications/preferences/
PUT /api/notifications/preferences/
```

**Ejemplo de actualización**:
```json
{
  "email_notifications_enabled": true,
  "newsletter_enabled": false,
  "promotion_enabled": true,
  "frequency": "daily"
}
```

### Marcar como Leído

```
POST /api/notifications/{id}/read/
POST /api/notifications/mark-all-read/
```

### Desuscripción

```
POST /api/notifications/unsubscribe/
```

**Parámetros**:
```json
{
  "email": "usuario@ejemplo.com"
}
```

## Gestión desde el Admin

### Acceso al Panel

1. Acceder a `/admin/`
2. Navegar a la sección "Notifications"

### Gestión de Tipos de Notificación

- **Crear nuevos tipos**: Definir código, nombre y descripción
- **Activar/Desactivar**: Control de tipos disponibles
- **Editar descripciones**: Mantener documentación actualizada

### Gestión de Plantillas

- **Editor HTML/Texto**: Edición completa de plantillas
- **Variables disponibles**: Documentación de variables utilizables
- **Vista previa**: Previsualización del contenido
- **Activar/Desactivar**: Control de plantillas activas

### Monitoreo de Envíos

- **Estado de notificaciones**: Pendiente, Enviado, Error, etc.
- **Filtros avanzados**: Por usuario, tipo, fecha, estado
- **Acciones masivas**: Marcar como pendiente, reintentar envíos
- **Logs detallados**: Información de errores y reintentos

### Gestión de Preferencias

- **Vista por usuario**: Preferencias individuales
- **Búsqueda**: Por email, nombre, teléfono
- **Edición masiva**: Configuración de múltiples usuarios

## Comandos de Gestión

### setup_notifications

Inicializa el sistema con tipos y plantillas básicas.

```bash
python manage.py setup_notifications [--overwrite]
```

**Opciones**:
- `--overwrite`: Sobrescribir plantillas existentes

### process_email_queue

Procesa la cola de emails pendientes.

```bash
python manage.py process_email_queue [--batch-size=10] [--continuous] [--interval=60]
```

**Opciones**:
- `--batch-size`: Emails por lote (default: 10)
- `--continuous`: Modo continuo
- `--interval`: Segundos entre procesamiento (default: 60)

## Logs y Monitoreo

### Ubicación de Logs

- **Aplicación**: `/var/log/llevateloexpress/notifications.log`
- **Django mail**: Incluido en logs de notifications
- **Cron jobs**: Logs específicos por tarea

### Niveles de Log

- **INFO**: Envíos exitosos, estadísticas
- **WARNING**: Reintentos, preferencias
- **ERROR**: Fallos de envío, errores de configuración

### Ejemplo de Logs

```
[INFO] 2024-01-15 10:30:15 notifications Email enviado exitosamente a usuario@ejemplo.com
[WARNING] 2024-01-15 10:31:20 notifications Usuario juan.perez tiene deshabilitadas las notificaciones de tipo newsletter
[ERROR] 2024-01-15 10:32:45 notifications Error enviando email a correo@invalido.com: [Errno 101] Network is unreachable
```

## Troubleshooting

### Problemas Comunes

**1. Emails no se envían**
- Verificar configuración SMTP
- Revisar logs de Django
- Verificar credenciales de email
- Comprobar conectividad de red

**2. Emails van a spam**
- Configurar SPF, DKIM, DMARC
- Usar dominio verificado
- Evitar contenido promocional excesivo
- Mantener buena reputación del IP

**3. Cola de emails se acumula**
- Aumentar frecuencia de procesamiento
- Verificar rendimiento del servidor SMTP
- Considerar usar un servicio especializado

**4. Plantillas no se renderizan**
- Verificar sintaxis de Django templates
- Comprobar variables disponibles
- Revisar logs de errores de template

### Comandos de Diagnóstico

```bash
# Verificar configuración de email
python manage.py shell -c "
from django.core.mail import send_mail
from django.conf import settings
print('Email backend:', settings.EMAIL_BACKEND)
print('Email host:', settings.EMAIL_HOST)
try:
    send_mail('Test', 'Test message', settings.DEFAULT_FROM_EMAIL, ['test@example.com'])
    print('✓ Configuración correcta')
except Exception as e:
    print('✗ Error:', e)
"

# Verificar tipos de notificaciones
python manage.py shell -c "
from notifications.models import NotificationType
print('Tipos activos:', NotificationType.objects.filter(is_active=True).count())
for nt in NotificationType.objects.filter(is_active=True):
    print(f'  - {nt.code}: {nt.name}')
"

# Verificar cola de emails
python manage.py shell -c "
from notifications.models import EmailQueue
pending = EmailQueue.objects.filter(is_processed=False).count()
print(f'Emails pendientes en cola: {pending}')
"
```

## Mejores Prácticas

### Diseño de Plantillas

1. **Responsive Design**: Usar CSS que funcione en móviles
2. **Texto Alternativo**: Siempre incluir versión texto
3. **Enlaces absolutos**: Usar URLs completas
4. **Imágenes optimizadas**: Tamaño reducido, hosted externamente

### Gestión de Envíos

1. **Frecuencia apropiada**: No saturar a los usuarios
2. **Segmentación**: Respetar preferencias de usuario
3. **A/B Testing**: Probar diferentes versiones
4. **Métricas**: Monitorear tasas de apertura y click

### Seguridad

1. **Validación de datos**: Sanitizar contenido dinámico
2. **Autenticación**: Proteger endpoints de admin
3. **Rate limiting**: Limitar envíos por usuario/IP
4. **Logs seguros**: No registrar información sensible

## Roadmap de Mejoras

### Corto Plazo
- [ ] Plantillas adicionales (recuperación de contraseña, etc.)
- [ ] Métricas de apertura y clicks
- [ ] Interface de usuario para preferencias

### Mediano Plazo
- [ ] Integración con servicios de email marketing
- [ ] Notificaciones push web
- [ ] Análisis de engagement

### Largo Plazo
- [ ] Machine learning para optimización de envíos
- [ ] Notificaciones SMS
- [ ] Personalización avanzada por usuario

---

**Documentación actualizada**: Enero 2025
**Versión del sistema**: 1.0 