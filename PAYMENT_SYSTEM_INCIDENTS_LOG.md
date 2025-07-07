# Sistema de Pagos - Log de Incidentes y Soluciones

## Información General
- **Fecha de inicio de troubleshooting**: 2025-07-06
- **Sistema**: LlévateloExpress - Plataforma de Financiamiento
- **Usuario cliente de prueba**: 1@centrodelpan.com / 1Simon$$77
- **Usuario admin de prueba**: rubenbe9@gmail.com / 1Simon$$77
- **Servidor**: 203.161.55.87

## Problema Original
**Descripción**: El sistema de pagos había funcionado previamente, pero tras intentar resolver un problema de visualización de imágenes en Django admin, el flujo de pagos se rompió completamente.

---

## INCIDENTE #1: JavaScript "Auth is not defined"
**Fecha**: 2025-07-06
**Síntoma**: Error en consola "Auth is not defined" al cargar la página de pagos
**Ubicación**: `/realizar-pago.html` - Paso 1 se queda en "Cargando tus solicitudes..."

### Análisis
- El archivo `auth.js` tenía caracteres corruptos
- Línea 329: `\!` en lugar de `!`
- Esto rompía la sintaxis JavaScript completamente

### Código Original (CORRUPTO)
```javascript
// js/auth.js línea 329 - ANTES
if (\!user.is_staff) {
    profileLink.style.display = 'block';
}
```

### Código Corregido
```javascript
// js/auth.js línea 329 - DESPUÉS
if (!user.is_staff) {
    profileLink.style.display = 'block';
}
```

### Comando de Corrección
```bash
# Comando SSH ejecutado en servidor
ssh root@203.161.55.87 "cd /var/www/llevateloexpress && sed -i 's/\\\\!/!/g' js/auth.js"
```

### Archivo afectado
- `js/auth.js:329`

### Estado: ✅ RESUELTO

---

## INCIDENTE #2: "methods.filter is not a function"
**Fecha**: 2025-07-06
**Síntoma**: Error al cargar métodos de pago en el Paso 2
**Ubicación**: `js/realizar-pago.js` - loadPaymentMethods()

### Análisis
- El API `/api/financing/payment-methods/` devolvía estructura diferente
- El frontend esperaba array directamente, pero recibía `{success: true, data: [...]}` 
- `methods.filter()` fallaba porque `methods` no era un array

### Código Original (PROBLEMÁTICO)
```javascript
// js/realizar-pago.js línea 152 - ANTES
async loadPaymentMethods() {
    try {
        console.log('📡 Cargando métodos de pago...');
        const response = await API.users.authFetch('/api/financing/payment-methods/');
        
        if (response.success) {
            const methods = response.data; // ❌ PROBLEMA: response.data no es array
            const activeMethods = methods.filter(method => method.is_active); // ❌ ERROR AQUÍ
            this.renderPaymentMethods(activeMethods);
        }
    }
}
```

### Código Corregido
```javascript
// js/realizar-pago.js línea 152-153 - DESPUÉS
async loadPaymentMethods() {
    try {
        console.log('📡 Cargando métodos de pago...');
        const response = await API.users.authFetch('/api/financing/payment-methods/');
        
        if (response.success) {
            console.log("🔍 Response payment-methods:", response);
            // ✅ SOLUCIÓN: Manejar diferentes estructuras de respuesta
            const methods = response.data.data || response.data.results || response.data;
            const activeMethods = Array.isArray(methods) ? methods.filter(method => method.is_active) : [];
            console.log("🔍 Methods data:", methods);
            console.log("🔍 Active methods:", activeMethods);
            this.renderPaymentMethods(activeMethods);
        }
    }
}
```

### Comando de Corrección
```bash
# Comando SSH ejecutado en servidor
ssh root@203.161.55.87 "cd /var/www/llevateloexpress && sed -i 's/const methods = response.data;/const methods = response.data.data || response.data.results || response.data;/' js/realizar-pago.js"
```

### Estructura de Respuesta del API
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Transferencia Bancaria (VES)",
      "payment_type": "bank_transfer",
      "description": "Transferencia bancaria en bolívares...",
      "requires_reference": true,
      "requires_receipt": true
    }
  ]
}
```

### Archivo afectado
- `js/realizar-pago.js:152-153`

### Estado: ✅ RESUELTO

---

## INCIDENTE #3: Permisos de archivos en directorio media
**Fecha**: 2025-07-06
**Síntoma**: Error 403 al subir archivos de comprobantes
**Ubicación**: `/media/payments/` directory

### Análisis
- Directorio tenía permisos `root:root`
- Django corriendo como usuario `llevateloexpress:www-data`
- No podía escribir archivos en el directorio

### Estado Original del Directorio
```bash
# Verificación de permisos - ANTES
$ ls -la /var/www/llevateloexpress/media/
drwxr-xr-x root     root     payments/
# ❌ PROBLEMA: Propietario root, Django no puede escribir
```

### Error en Django
```python
# Error en financing/views.py al intentar guardar archivo
PermissionError: [Errno 13] Permission denied: '/var/www/llevateloexpress/media/payments/receipts/2025/07/06/test.jpg'
```

### Comandos de Corrección
```bash
# Comando 1: Cambiar propietario
sudo chown -R llevateloexpress:www-data /var/www/llevateloexpress/media/payments/

# Comando 2: Establecer permisos correctos
sudo chmod -R 755 /var/www/llevateloexpress/media/payments/

# Comando 3: Verificar estructura
sudo mkdir -p /var/www/llevateloexpress/media/payments/receipts/

# Comando 4: Establecer permisos para archivos futuros
sudo chmod -R g+w /var/www/llevateloexpress/media/payments/
```

### Estado Final del Directorio
```bash
# Verificación de permisos - DESPUÉS
$ ls -la /var/www/llevateloexpress/media/
drwxrwxr-x llevateloexpress www-data payments/
# ✅ CORRECTO: Django puede leer y escribir
```

### Configuración en Django
```python
# settings.py - Configuración de media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# models.py - Upload path para comprobantes
receipt_file = models.FileField(
    upload_to='payments/receipts/%Y/%m/%d/',
    null=True,
    blank=True,
    verbose_name="Comprobante de Pago"
)
```

### Estado: ✅ RESUELTO

---

## INCIDENTE #4: Error de Content-Type para FormData
**Fecha**: 2025-07-06
**Síntoma**: Error 415 "Unsupported Media Type" al enviar archivos
**Ubicación**: `Auth.fetch()` en `js/auth.js`

### Análisis
- `Auth.fetch()` forzaba `Content-Type: application/json` para todas las peticiones
- FormData requiere que el browser establezca automáticamente el Content-Type con boundary
- Django endpoint esperaba `multipart/form-data` pero recibía `application/json`

### Error Completo
```
POST https://llevateloexpress.com/api/financing/submit-payment/ 415 (Unsupported Media Type)
```

### Código Original (PROBLEMÁTICO)
```javascript
// js/auth.js línea 77-85 - ANTES
async function authenticatedFetch(url, options = {}) {
    const accessToken = localStorage.getItem('access_token');
    
    const authOptions = {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json', // ❌ PROBLEMA: Siempre JSON
        }
    };
    
    return fetch(url, authOptions);
}
```

### Código Corregido
```javascript
// js/auth.js línea 77-85 - DESPUÉS
async function authenticatedFetch(url, options = {}) {
    const accessToken = localStorage.getItem('access_token');
    
    const authOptions = {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${accessToken}`,
            // ✅ SOLUCIÓN: Solo establecer Content-Type si NO es FormData
            ...(options.body instanceof FormData ? {} : {"Content-Type": "application/json"}),
        }
    };
    
    return fetch(url, authOptions);
}
```

### Comando de Corrección
```bash
# Comando SSH ejecutado en servidor
ssh root@203.161.55.87 "cd /var/www/llevateloexpress && sed -i '80s/.*/            ...(options.body instanceof FormData ? {} : {\"Content-Type\": \"application\/json\"}),/' js/auth.js"
```

### Configuración Backend Django
```python
# financing/views.py - PaymentSubmissionView
class PaymentSubmissionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # ✅ Acepta multipart/form-data
    
    def post(self, request):
        # El endpoint espera multipart/form-data para archivos
        receipt_file = request.FILES.get('receipt_file')
        # ...
```

### Ejemplo de Headers Correctos
```http
# Para FormData (archivos)
Content-Type: multipart/form-data; boundary=----formdata-polyfill-123456

# Para JSON (datos simples)
Content-Type: application/json
```

### Archivo afectado
- `js/auth.js:80`

### Estado: ✅ RESUELTO

---

## INCIDENTE #5: Campo recorded_by_id NOT NULL constraint
**Fecha**: 2025-07-07
**Síntoma**: Error 500 "null value in column recorded_by_id violates not-null constraint"
**Ubicación**: Backend Django - creación de Payment

### Análisis
- La tabla `financing_payment` en PostgreSQL tiene columna `recorded_by_id NOT NULL`
- El modelo Django `Payment` NO tenía definido el campo `recorded_by`
- El código de creación intentaba usar `recorded_by=request.user` pero el modelo no lo reconocía

### Error Completo de Base de Datos
```
django.db.utils.IntegrityError: null value in column "recorded_by_id" violates not-null constraint
DETAIL:  Failing row contains (10, initial, pending, 151.67, USD, 2025-01-07 16:00:00+00:00, 
2025-07-07 03:00:38.123456+00:00, null, TEST999, , , , , 
payments/receipts/2025/07/07/525R.png, , , , 18, null, 151.0.0.1, Mozilla/5.0...).
```

### Estructura de Base de Datos Real
```sql
-- Consulta SQL para verificar estructura
\d financing_payment;

Column          | Type      | Nullable
recorded_by_id  | integer   | not null  ← ❌ CAMPO FALTANTE EN MODELO
submitted_by_id | integer   | null
notes           | text      | null
```

### Modelo Django Original (INCOMPLETO)
```python
# financing/models.py - ANTES
class Payment(models.Model):
    # ... otros campos ...
    
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='submitted_payments',
        verbose_name="Registrado por"
    )
    # ❌ FALTA: Campo recorded_by
    
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments',
        verbose_name="Verificado por"
    )
```

### Modelo Django Corregido
```python
# financing/models.py línea 494-501 - DESPUÉS
class Payment(models.Model):
    # ... otros campos ...
    
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='submitted_payments',
        verbose_name="Registrado por"
    )
    # ✅ AGREGADO: Campo recorded_by
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='recorded_payments',
        verbose_name="Grabado por"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments',
        verbose_name="Verificado por"
    )
```

### Vista Original (INCOMPLETA)
```python
# financing/views.py línea 1082-1103 - ANTES
payment = Payment.objects.create(
    application=application,
    payment_method=payment_method.payment_type,
    payment_type=request.data.get('payment_type', 'installment'),
    amount=amount,
    currency=request.data.get("currency", "USD"),
    payment_date=payment_date,
    reference_number=reference_number,
    # ... más campos ...
    submitted_by=request.user,
    # ❌ FALTA: recorded_by=request.user,
    ip_address=self.get_client_ip(request),
    user_agent=request.META.get('HTTP_USER_AGENT', '')
)
```

### Vista Corregida
```python
# financing/views.py línea 1082-1104 - DESPUÉS
payment = Payment.objects.create(
    application=application,
    payment_method=payment_method.payment_type,
    payment_type=request.data.get('payment_type', 'installment'),
    amount=amount,
    currency=request.data.get("currency", "USD"),
    payment_date=payment_date,
    reference_number=reference_number,
    # ... más campos ...
    submitted_by=request.user,
    recorded_by=request.user,  # ✅ AGREGADO: Campo requerido
    ip_address=self.get_client_ip(request),
    user_agent=request.META.get('HTTP_USER_AGENT', '')
)
```

### Comandos de Corrección
```bash
# 1. Subir modelo corregido al servidor
scp financing/models.py root@203.161.55.87:/var/www/llevateloexpress/financing/models.py

# 2. Subir vista corregida al servidor  
scp financing/views.py root@203.161.55.87:/var/www/llevateloexpress/financing/views.py

# 3. Reiniciar Django
ssh root@203.161.55.87 "systemctl restart llevateloexpress && sleep 3"
```

### Root Cause
Desincronización entre estructura de base de datos y modelo Django. En algún momento del desarrollo se agregó la columna a la BD pero no al modelo.

### Diferencia entre campos
- `submitted_by`: Usuario que envía el comprobante (cliente)
- `recorded_by`: Usuario que registra el pago en el sistema (mismo en este flujo)
- `verified_by`: Usuario que verifica/aprueba el pago (administrador)

### Archivos afectados
- `financing/models.py:494-501`
- `financing/views.py:1101`

### Estado: ✅ RESUELTO

---

## INCIDENTE #6: Filtro is_active en JavaScript
**Fecha**: 2025-07-07
**Síntoma**: Métodos de pago no cargan en frontend
**Ubicación**: `js/realizar-pago.js` - loadPaymentMethods()

### Análisis
- JavaScript filtraba métodos por `method.is_active`
- Backend ya filtra por `is_active=True` pero no incluye el campo en la respuesta
- Resultado: `activeMethods` quedaba vacío aunque el API devolvía métodos

### Error en Consola JavaScript
```javascript
// Error observado
console.log("🔍 Methods data:", methods); // [5 métodos]
console.log("🔍 Active methods:", activeMethods); // [] ← VACÍO!
```

### Backend PaymentMethodListView
```python
# financing/views.py línea 914 - Backend ya filtra
def get(self, request):
    methods = PaymentMethod.objects.filter(is_active=True).order_by('order')  # ✅ Ya filtrado
    
    data = []
    for method in methods:
        method_data = {
            'id': method.id,
            'name': method.name,
            'payment_type': method.payment_type,
            # ... otros campos ...
            # ❌ NO INCLUYE: 'is_active': method.is_active
        }
        data.append(method_data)
    
    return Response({'success': True, 'data': data})
```

### Código JavaScript Original (PROBLEMÁTICO)
```javascript
// js/realizar-pago.js línea 152-156 - ANTES
async loadPaymentMethods() {
    try {
        const response = await API.users.authFetch('/api/financing/payment-methods/');
        
        if (response.success) {
            const methods = response.data.data || response.data.results || response.data;
            // ❌ PROBLEMA: Filtra por campo que no existe en respuesta
            const activeMethods = Array.isArray(methods) ? methods.filter(method => method.is_active) : [];
            console.log("🔍 Active methods:", activeMethods); // Resultado: []
            this.renderPaymentMethods(activeMethods);
        }
    }
}
```

### Código JavaScript Corregido
```javascript
// js/realizar-pago.js línea 152-156 - DESPUÉS
async loadPaymentMethods() {
    try {
        const response = await API.users.authFetch('/api/financing/payment-methods/');
        
        if (response.success) {
            const methods = response.data.data || response.data.results || response.data;
            // ✅ SOLUCIÓN: No filtrar, backend ya devuelve solo métodos activos
            const activeMethods = Array.isArray(methods) ? methods : [];
            console.log("🔍 Active methods:", activeMethods); // Resultado: [5 métodos]
            this.renderPaymentMethods(activeMethods);
        }
    }
}
```

### Comando de Corrección
```bash
# Comando SSH ejecutado en servidor
ssh root@203.161.55.87 "cd /var/www/llevateloexpress && sed -i 's/methods.filter(method => method.is_active)/methods/g' js/realizar-pago.js"
```

### Estructura de Respuesta API (SIN is_active)
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Transferencia Bancaria (VES)",
      "payment_type": "bank_transfer",
      "description": "Transferencia bancaria en bolívares...",
      "requires_reference": true,
      "requires_receipt": true
      // ❌ NO INCLUYE: "is_active": true
    }
  ]
}
```

### Validación Final
```bash
# Verificar que API devuelve métodos
curl -X GET 'https://localhost/api/financing/payment-methods/' \
  -H "Authorization: Bearer [TOKEN]" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Methods count: {len(data[\"data\"])}')"
# Resultado: Methods count: 5 ✅
```

### Archivo afectado
- `js/realizar-pago.js:153`

### Estado: ✅ RESUELTO

---

## Pruebas de Validación Final

### Configuración de Pruebas
```bash
# Variables de entorno para pruebas
USUARIO_CLIENTE="1@centrodelpan.com"
PASSWORD_CLIENTE="1Simon$$77"
SERVIDOR="203.161.55.87"
BASE_URL="https://localhost"
```

### Prueba 1: Autenticación JWT
```bash
# Comando completo
curl -s -k -X POST 'https://localhost/api/users/token/' \
  -H 'Content-Type: application/json' \
  -d '{"username":"1@centrodelpan.com","password":"1Simon$$77"}'
```

**Resultado**: ✅ Token JWT generado correctamente
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUxOTQ0MTEzLCJpYXQiOjE3NTE4NTc3MTMsImp0aSI6IjVmNWU1NzNkMGNlYjQ2ODg5MjY2OTBhNjk5ODQzOTg1IiwidXNlcl9pZCI6MTh9.yOfho5XWNS56gc7mdVZ9DC6ulcbfXcteXXPKtr73uEI"
}
```

### Prueba 2: Solicitudes de Financiamiento
```bash
# Comando con token de autenticación
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -s -k -X GET 'https://localhost/api/financing/my-requests/' \
  -H "Authorization: Bearer $TOKEN"
```

**Resultado**: ✅ 75 solicitudes encontradas
```json
{
  "count": 75,
  "next": "https://localhost/api/financing/my-requests/?page=2",
  "previous": null,
  "results": [
    {
      "id": 181,
      "application_number": "APP202500181",
      "customer_name": "Ruben Bolivar",
      "product_name": "Suzuki DR 650",
      "status": "approved",
      "status_display": "Aprobada",
      "payment_amount": "230.21"
    }
  ]
}
```

### Prueba 3: Métodos de Pago
```bash
# Comando para obtener métodos de pago
curl -s -k -X GET 'https://localhost/api/financing/payment-methods/' \
  -H "Authorization: Bearer $TOKEN"
```

**Resultado**: ✅ 5 métodos de pago activos
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Transferencia Bancaria (VES)",
      "payment_type": "bank_transfer",
      "description": "Transferencia bancaria en bolívares desde cualquier banco venezolano",
      "requires_reference": true,
      "requires_receipt": true,
      "min_amount": 10.0,
      "max_amount": null,
      "processing_time_hours": 24,
      "accounts": [...]
    },
    {
      "id": 2,
      "name": "Pago Móvil",
      "payment_type": "mobile_payment",
      // ... más métodos
    }
  ]
}
```

### Prueba 4: Envío de Pago Completo (End-to-End)
```bash
# Comando completo con FormData
curl -s -k -X POST 'https://localhost/api/financing/submit-payment/' \
  -H "Authorization: Bearer $TOKEN" \
  -F 'application_id=180' \
  -F 'payment_method_id=1' \
  -F 'amount=151.67' \
  -F 'payment_date=2025-01-07' \
  -F 'reference_number=TEST999' \
  -F 'customer_notes=Pago final de prueba desde terminal' \
  -F 'receipt_file=@media/products/525R.png'
```

**Resultado**: ✅ Pago creado exitosamente
```json
{
  "success": true,
  "message": "Comprobante de pago enviado exitosamente. Será verificado en las próximas 24 horas.",
  "data": {
    "id": 10,
    "application_number": "APP202500180",
    "payment_type": "Cuota Mensual",
    "payment_method": "Transferencia Bancaria",
    "amount": 151.67,
    "currency": "USD",
    "status": "Pendiente de Verificación",
    "payment_date": "2025-01-07T12:00:00",
    "reference_number": "TEST999",
    "submitted_at": "2025-07-07T03:04:06.403514+00:00",
    "has_receipt": true
  }
}
```

### Prueba 5: Verificación en Base de Datos
```sql
-- Consulta SQL para verificar el pago creado
SELECT id, application_id, amount, reference_number, status, 
       submitted_by_id, recorded_by_id, created_at 
FROM financing_payment 
WHERE reference_number = 'TEST999';
```

**Resultado**: ✅ Registro creado correctamente
```
id | application_id | amount | reference_number | status  | submitted_by_id | recorded_by_id | created_at
10 | 180           | 151.67 | TEST999         | pending | 18             | 18            | 2025-07-07 03:04:06
```

### Prueba 6: Verificación de Archivo Subido
```bash
# Verificar que el archivo se guardó correctamente
ls -la /var/www/llevateloexpress/media/payments/receipts/2025/07/07/525R*.png
```

**Resultado**: ✅ Archivo guardado con permisos correctos
```
-rw-r--r-- 1 llevateloexpress www-data 45234 Jul  7 03:04 525R.png
```

---

## Flujo Completo de Pagos - Estados Finales

### ✅ Paso 1: Carga de Solicitudes
- **Endpoint**: `/api/financing/my-requests/`
- **Estado**: Funcional
- **Filtros**: Solo solicitudes con status 'approved'

### ✅ Paso 2: Métodos de Pago
- **Endpoint**: `/api/financing/payment-methods/`
- **Estado**: Funcional
- **Cantidad**: 5 métodos activos

### ✅ Paso 3: Detalles del Pago
- **Campos**: amount, payment_date, reference_number, customer_notes
- **Estado**: Funcional
- **Validaciones**: Frontend + Backend

### ✅ Paso 4: Subida de Comprobante
- **Endpoint**: `/api/financing/submit-payment/`
- **Estado**: Funcional
- **Formato**: multipart/form-data
- **Storage**: `/media/payments/receipts/YYYY/MM/DD/`

---

## Problemas Pendientes

### 🔴 PROBLEMA ORIGINAL: Visualización de imágenes en Django Admin
**Estado**: PENDIENTE
**Descripción**: Las imágenes de comprobantes no se visualizan correctamente en el panel administrativo de Django
**Prioridad**: Media
**Nota**: Este era el problema original que se intentaba resolver cuando se rompió el sistema de pagos

---

## Lecciones Aprendidas

1. **Sincronización**: Mantener archivos locales y servidor sincronizados usando git
2. **Backup**: Siempre hacer backup antes de modificaciones importantes
3. **Testing**: Probar cada cambio individualmente antes de continuar
4. **Logging**: Usar logs detallados para diagnostic más rápido
5. **Documentación**: Documentar cada cambio y su propósito

---

## Comandos de Gestión de Servicios

### Reiniciar Django
```bash
sudo systemctl restart llevateloexpress
sudo systemctl status llevateloexpress
```

### Ver logs en tiempo real
```bash
sudo journalctl -u llevateloexpress -f
tail -f /tmp/payment_debug.log
```

### Verificar archivos críticos
```bash
# Sintaxis JavaScript
node -c js/auth.js
node -c js/realizar-pago.js

# Permisos de media
ls -la media/payments/
```

### Sincronizar archivos
```bash
# Subir desde local a servidor
scp financing/models.py root@203.161.55.87:/var/www/llevateloexpress/financing/
scp financing/views.py root@203.161.55.87:/var/www/llevateloexpress/financing/
scp js/auth.js root@203.161.55.87:/var/www/llevateloexpress/js/
scp js/realizar-pago.js root@203.161.55.87:/var/www/llevateloexpress/js/

# Bajar desde servidor a local
scp root@203.161.55.87:/var/www/llevateloexpress/js/realizar-pago.js js/
```

---

**Documento creado**: 2025-07-07 03:15 UTC  
**Autor**: Claude Code  
**Última actualización**: 2025-07-07 03:15 UTC