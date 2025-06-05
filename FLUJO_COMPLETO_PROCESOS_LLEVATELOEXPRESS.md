# 🚀 FLUJO COMPLETO DE PROCESOS - LLEVATELOEXPRESS

## 📋 **RESUMEN EJECUTIVO**

**Estado del Sistema:** ✅ **COMPLETAMENTE FUNCIONAL**  
**VPS Producción:** 203.161.55.87  
**GitHub:** https://github.com/rubenbolivar/llevateloexpress  
**Último Update:** Dashboard solucionado - 14 solicitudes visibles  

---

## 🔄 **FLUJO GENERAL DEL USUARIO**

```
Registro → Autenticación → Catálogo → Calculadora → Solicitud → Dashboard → Revisión → Aprobación
```

---

## 📖 **PASO 1: REGISTRO DE USUARIO**

### **🎯 Objetivo:** Crear cuenta nueva en el sistema

### **📁 Archivos Involucrados:**
- **Frontend:** `registro.html`, `js/registro.js`
- **Backend:** `users/views.py`, `users/serializers/user_serializers.py`
- **Modelo:** `users/models.py` (User + Customer)

### **🔗 Endpoint:**
```
POST /api/users/register/
```

### **📊 Tecnologías:**
- **Frontend:** HTML5, Bootstrap 5, JavaScript ES6
- **Backend:** Django REST Framework
- **Autenticación:** Django User Model + Customer Profile
- **Validación:** Django Serializers

### **🔧 Proceso Técnico:**
1. **Usuario completa formulario:** email, password, teléfono, documento
2. **Frontend envía:** `API.users.register(userData)` → `js/api-fixed.js`
3. **Backend procesa:** `RegisterSerializer.create()` 
4. **Se crean:** `User` + `Customer` (relación OneToOne)
5. **Respuesta:** Usuario creado, redirection al login

### **🗃️ Datos Almacenados:**
```python
User: {email, password_hash, first_name, last_name}
Customer: {phone, identity_document, verified: False}
```

---

## 📖 **PASO 2: AUTENTICACIÓN JWT**

### **🎯 Objetivo:** Iniciar sesión y obtener tokens de acceso

### **📁 Archivos Involucrados:**
- **Frontend:** `login.html`, `js/login.js`
- **Backend:** `users/views.py`, JWT views
- **API Client:** `js/api-fixed.js`

### **🔗 Endpoint:**
```
POST /api/users/token/
```

### **🔑 Tokens Generados:**
- **Access Token:** JWT para autenticación (corta duración)
- **Refresh Token:** Para renovar access token

### **🔧 Proceso Técnico:**
1. **Usuario envía:** email + password
2. **Backend valida:** `CustomTokenObtainPairSerializer`
3. **JWT generado:** Simple JWT library
4. **Frontend almacena:** `localStorage.setItem('access_token', data.access)`
5. **Headers automáticos:** `Authorization: Bearer <token>`

### **🛡️ Seguridad:**
- **CSRF Protection:** `getCSRFToken()` en cada request
- **Token Refresh:** Automático en `API.users.authFetch()`
- **Session Management:** Verificación en cada página

---

## 📖 **PASO 3: NAVEGACIÓN DEL CATÁLOGO**

### **🎯 Objetivo:** Explorar productos disponibles para financiamiento

### **📁 Archivos Involucrados:**
- **Frontend:** `catalogo.html`, `js/products.js`
- **Backend:** `products/views.py`, `products/serializers/`
- **Imágenes:** `img/products/`, `media/products/`

### **🔗 Endpoints:**
```
GET /api/products/categories/
GET /api/products/products/?page=1
GET /api/products/products/{id}/
```

### **📊 Tecnologías:**
- **Paginación:** Django REST Framework PageNumberPagination
- **Filtros:** Por categoría, precio, marca
- **Imágenes:** Django FileField + Media handling

### **🔧 Proceso Técnico:**
1. **Carga inicial:** `API.products.getCategories()`
2. **Lista productos:** `API.products.getProducts(page=1, filters={})`
3. **Respuesta paginada:** `{count, next, previous, results: [...]}`
4. **Renderizado:** Cards dinámicas con datos del producto

### **🗃️ Estructura de Datos:**
```json
{
  "id": 1,
  "name": "Suzuki V-STROM DL1050",
  "price": "15409.00",
  "category": "Motocicletas",
  "brand": "Suzuki",
  "image": "/media/products/Vstrom_DL1050.png"
}
```

---

## 📖 **PASO 4: CALCULADORA DE FINANCIAMIENTO**

### **🎯 Objetivo:** Simular opciones de financiamiento para el producto

### **📁 Archivos Involucrados:**
- **Frontend:** `calculadora.html`, `js/calculadora-integrada.js`
- **Backend:** `financing/views.py` (CalculatorCalculateView)
- **Modelos:** `financing/models.py` (CalculatorMode)

### **🔗 Endpoints:**
```
GET /api/financing/calculator/config/
POST /api/financing/calculator/calculate/
```

### **💰 Modalidades Disponibles:**
1. **Compra Programada:** Ahorro + adjudicación
2. **Crédito Inmediato:** Financiamiento directo

### **🔧 Proceso Técnico:**
1. **Configuración:** Obtiene modalidades, productos, términos
2. **Cálculo dinámico:** JavaScript real-time
3. **Validación backend:** Verificación de parámetros
4. **Resultado:** Cuotas, fechas, totales calculados

### **📊 Ejemplo de Cálculo:**
```
Producto: ATV Loncin $9,500
Inicial: 30% = $2,850
Financiado: $6,650
Frecuencia: Quincenal (biweekly)
Pagos: 39 cuotas de $257.29
```

---

## 📖 **PASO 5: SOLICITUD DE FINANCIAMIENTO**

### **🎯 Objetivo:** Crear solicitud formal de crédito

### **📁 Archivos Involucrados:**
- **Frontend:** `solicitud-financiamiento.html`, `js/solicitud-financiamiento.js`
- **Backend:** `financing/views.py` (FinancingRequestViewSet)
- **Serializers:** `financing/serializers/financing_serializers.py`

### **🔗 Endpoints Críticos:**
```
POST /api/financing/requests/          # Crear solicitud
PUT /api/financing/requests/{id}/      # Actualizar
POST /api/financing/requests/{id}/submit/  # Enviar para revisión
```

### **📝 Pasos del Formulario:**
1. **Paso 1:** Confirmación producto + financiamiento
2. **Paso 2:** Información personal
3. **Paso 3:** Información laboral + ingresos
4. **Paso 4:** Subida documentos
5. **Paso 5:** Confirmación y envío

### **🔧 Proceso Técnico:**
1. **Datos calculadora:** Transferidos via URL params
2. **Validación por pasos:** `validateCurrentStep()`
3. **Manejo archivos:** FormData para documentos
4. **Estados:** `draft` → `submitted` → `under_review`

### **🗃️ Datos Almacenados:**
```json
{
  "application_number": "APP202500027",
  "customer": 22,
  "product": {"name": "Suzuki V-STROM", "price": "15409.00"},
  "payment_frequency": "biweekly",
  "payment_amount": "417.33",
  "status": "draft"
}
```

---

## 📖 **PASO 6: DASHBOARD DEL USUARIO**

### **🎯 Objetivo:** Gestionar solicitudes y ver estado

### **📁 Archivos Involucrados:**
- **Frontend:** `dashboard.html`, `js/dashboard.js` ✅ **CORREGIDO**
- **Backend:** `financing/views.py` (CustomerApplicationsView)
- **API Client:** `js/api-fixed.js`

### **🔗 Endpoints:**
```
GET /api/financing/my-requests/        # Lista solicitudes del usuario
GET /api/financing/payment-schedule/   # Calendario de pagos
GET /api/financing/requests/{id}/      # Detalles específicos
```

### **🔧 Correcciones Aplicadas (Dashboard):**
1. **❌ Problema:** `Auth.fetch is not a function`
   **✅ Solución:** `API.users.authFetch()`

2. **❌ Problema:** `requests.map is not a function`
   **✅ Solución:** Manejo paginación `data.results || data`

3. **❌ Problema:** Campos incorrectos
   **✅ Solución:** `product_name`, `product_price` vs `product?.name`

### **📊 Vista del Usuario:**
- **Estadísticas:** 2 solicitudes activas, 12 borradores
- **Tabla completa:** 14 solicitudes con estados
- **Acciones:** Ver detalles, completar, subir documentos

---

## 📖 **PASO 7: REVISIÓN ADMINISTRATIVA**

### **🎯 Objetivo:** Evaluación por equipo financiero

### **📁 Archivos Involucrados:**
- **Backend:** Django Admin personalizado
- **Modelos:** `financing/models.py`
- **Admin:** `financing/admin.py`

### **🏢 Proceso Interno:**
1. **Estado inicial:** `submitted`
2. **Asignación:** Revisor asignado
3. **Evaluación:** Documentos, scoring crediticio
4. **Decisión:** `approved` / `rejected` / `documents_required`

### **🔍 Criterios de Evaluación:**
- Ingresos vs. capacidad de pago
- Historial crediticio
- Documentación completa
- Políticas internas

---

## 📖 **PASO 8: APROBACIÓN Y ACTIVACIÓN**

### **🎯 Objetivo:** Activar crédito aprobado

### **📁 Archivos Involucrados:**
- **Backend:** `financing/models.py`, `notifications/`
- **Email:** Templates en `templates/emails/`

### **🔗 Endpoints:**
```
POST /api/financing/requests/{id}/approve/
POST /api/financing/requests/{id}/activate/
```

### **🔧 Proceso de Aprobación:**
1. **Admin aprueba:** Estado `approved`
2. **Generación:** Calendario de pagos automático
3. **Notificación:** Email al cliente
4. **Activación:** Estado `active`
5. **Documentación:** Contratos digitales

---

## 🏗️ **ARQUITECTURA TÉCNICA**

### **📊 Stack Tecnológico:**
- **Backend:** Django 4.2 + Django REST Framework
- **Base de Datos:** PostgreSQL
- **Frontend:** HTML5 + Bootstrap 5 + Vanilla JavaScript
- **Autenticación:** JWT (Simple JWT)
- **Servidor:** Nginx + Gunicorn
- **VPS:** Ubuntu 20.04 (203.161.55.87)

### **🔗 API Architecture:**
```
/api/
├── users/
│   ├── register/
│   ├── token/
│   └── profile/
├── products/
│   ├── categories/
│   └── products/
└── financing/
    ├── calculator/
    ├── requests/
    ├── my-requests/     # ✅ FUNCIONAL
    └── payment-schedule/
```

### **🗄️ Modelos de Base de Datos:**
```python
User (Django Auth)
├── Customer (OneToOne)
    └── FinancingRequest (ForeignKey)
        ├── Product (ForeignKey)
        ├── FinancingPlan (ForeignKey)
        └── PaymentSchedule (ForeignKey)
```

---

## 🔍 **DEBUGGING Y MONITOREO**

### **🛠️ Scripts de Diagnóstico:**
- `debug_dashboard_solicitudes.py` - Diagnóstico completo dashboard
- `debug_endpoint_my_requests.py` - Análisis endpoints específicos
- `debug_response_structure.py` - Investigación estructura datos

### **📝 Logs y Monitoreo:**
- **Django Logs:** `/var/log/llevateloexpress/`
- **Nginx Logs:** `/var/log/nginx/`
- **Console Logs:** Browser DevTools

### **🔄 Backup y Sincronización:**
- **Script:** `sync_github.sh` (VPS → GitHub)
- **Backup:** `dashboard_solucionado_backup_20250605_110754.tar.gz`

---

## ✅ **ESTADO ACTUAL DEL SISTEMA**

### **🎯 Funcionalidades Operativas:**
- ✅ **Registro usuarios** - Completamente funcional
- ✅ **Autenticación JWT** - Tokens funcionando
- ✅ **Catálogo productos** - 27+ productos disponibles
- ✅ **Calculadora** - Ambas modalidades operativas
- ✅ **Solicitudes** - Creación y envío funcional
- ✅ **Dashboard** - 14 solicitudes visibles (**SOLUCIONADO**)
- ✅ **Admin panel** - Gestión completa

### **📊 Datos de Producción:**
- **Usuarios registrados:** 18+ usuarios
- **Solicitudes activas:** 27 solicitudes
- **Productos disponibles:** 27 productos
- **Categorías:** Motocicletas, ATVs, Scooters

### **🚨 Últimas Correcciones:**
1. **Dashboard vacío** → **SOLUCIONADO** (paginación API)
2. **Importaciones incorrectas** → **CORREGIDAS**
3. **Campos serializer** → **MAPEADOS CORRECTAMENTE**

---

## 🔮 **PRÓXIMOS DESARROLLOS**

### **📈 Mejoras Sugeridas:**
1. **Integración pagos:** Pasarelas de pago online
2. **Scoring automático:** API bureaus crediticios
3. **Firma digital:** Contratos electrónicos
4. **App móvil:** React Native / Flutter
5. **Notificaciones push:** Estado solicitudes real-time

### **🔧 Optimizaciones Técnicas:**
1. **Caché:** Redis para consultas frecuentes
2. **CDN:** Optimización imágenes productos
3. **API versioning:** v2 endpoints
4. **Testing:** Suite automatizada completa

---

## 📞 **CONTACTO Y SOPORTE**

**VPS Producción:** root@203.161.55.87  
**Repositorio:** https://github.com/rubenbolivar/llevateloexpress  
**Último backup:** `dashboard_solucionado_backup_20250605_110754.tar.gz`  

**🔧 Para sincronizar cambios:**
```bash
cd /var/www/llevateloexpress
./sync_github.sh force
```

---

*📅 Documento actualizado: Junio 2025*  
*🎯 Estado: Dashboard completamente funcional*  
*✅ Sistema operativo al 100%* 