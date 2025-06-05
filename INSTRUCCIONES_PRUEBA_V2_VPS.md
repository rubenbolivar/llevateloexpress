# 🔧 INSTRUCCIONES PARA PROBAR EL FLUJO V2 EN EL VPS

## ✅ Estado Actual
- **JavaScript V2 adaptado**: ✅ Sincronizado correctamente
- **Servicios Django/Nginx**: ✅ Funcionando normalmente  
- **Endpoint de planes**: ✅ Disponible sin autenticación
- **Endpoint de solicitudes**: ✅ Protegido (requiere login)
- **Página de solicitud**: ✅ Carga correctamente (HTTP 200)

## 🎯 Objetivo de la Prueba
Verificar que un usuario autenticado puede completar exitosamente el flujo de solicitud de financiamiento usando el V2 adaptado.

## 📋 Pasos para la Prueba

### 1. Acceder al Sistema
```
URL: https://llevateloexpress.com/login.html
Usuario: 1@centrodelpan.com
Contraseña: 12345678
```

### 2. Navegar a Solicitud de Financiamiento
Una vez autenticado, ir a:
```
https://llevateloexpress.com/solicitud-financiamiento.html
```

### 3. Verificar Carga del V2
En el navegador, abrir **DevTools (F12)** y verificar en la **Consola**:
- ✅ Debe aparecer: `🔧 FinancingRequestV2 adaptado para VPS inicializado correctamente`
- ❌ NO deben aparecer errores de JavaScript

### 4. Flujo de Prueba Completo

#### **Paso 1: Resumen de Cálculo**
- La página debe mostrar un resumen de cálculo (puede estar vacío si no viene desde calculadora)
- Hacer clic en **"Siguiente"**

#### **Paso 2: Información Personal** 
Completar los campos obligatorios:
- **Tipo de Empleo**: Seleccionar cualquier opción
- **Ingreso Mensual**: Ingresar un valor (ej: 800)
- Llenar otros campos opcionales si se desea
- Hacer clic en **"Siguiente"**

#### **Paso 3: Documentos (Opcional)**
- Se puede saltar este paso o subir archivos de prueba (PDF/imágenes, máx 5MB)
- Hacer clic en **"Siguiente"**

#### **Paso 4: Confirmación y Envío**
- Revisar el resumen final
- Marcar las casillas obligatorias:
  - ✅ **Acepto términos y condiciones**
  - ✅ **Autorizo tratamiento de datos**
- Hacer clic en **"Enviar Solicitud"**

### 5. Resultados Esperados

#### ✅ **Si Todo Funciona Correctamente:**
- Mensaje: `¡Solicitud enviada exitosamente!`
- En DevTools → Network: petición POST a `/api/financing/requests/` con status **201**
- Redirección automática al dashboard después de 3 segundos
- En el admin de Django debe aparecer una nueva solicitud

#### ❌ **Si Hay Problemas:**
- Error de autenticación → El usuario será redirigido al login
- Error de validación → Se mostrará mensaje específico del error
- Error de conexión → Mensaje genérico de error

## 🕵️ Monitoreo de la Prueba

### En DevTools (F12) verificar:

#### **1. Consola (Console)**
```javascript
// Mensajes esperados:
[INFO] Inicializando FinancingRequestV2 adaptado para VPS
[INFO] Planes de financiamiento cargados: X
[DEBUG] API Request: POST /api/financing/requests/
[INFO] Solicitud creada con ID: XX
```

#### **2. Red (Network)**
```
GET /api/financing/plans/ → 200 OK
POST /api/financing/requests/ → 201 Created (con datos de la solicitud)
```

#### **3. Elementos (Elements)**
Verificar que el HTML referencia:
```html
<script src="js/solicitud-financiamiento-v2-part2.js"></script>
```

## 🚀 Casos de Prueba Adicionales

### Caso 1: Usuario No Autenticado
1. Ir a solicitud-financiamiento.html sin hacer login
2. Completar el formulario hasta el final
3. **Resultado esperado**: Error de autenticación y redirección a login

### Caso 2: Datos Mínimos
1. Completar solo campos obligatorios
2. **Resultado esperado**: Solicitud exitosa con valores por defecto

### Caso 3: Con Datos de Calculadora
1. Ir primero a la calculadora y hacer un cálculo
2. Navegar a solicitud-financiamiento.html
3. **Resultado esperado**: Datos pre-cargados del cálculo

## 📊 Verificación en el Backend

### En el Admin de Django
1. Ir a `https://llevateloexpress.com/admin/`
2. Sección **Financing → Financing Requests**
3. Verificar que aparece la nueva solicitud con:
   - ✅ Usuario correcto
   - ✅ Datos del formulario
   - ✅ Estado "pending"
   - ✅ Timestamp correcto

### En los Logs del Servidor
```bash
# Conectarse al VPS y revisar logs
tail -f /var/log/llevateloexpress/debug.log
```

## 🔧 Solución de Problemas

### Si aparece Error 401 (No autenticado)
1. Verificar que el usuario está logueado
2. Revisar cookies de sesión en DevTools → Application → Cookies
3. Intentar logout/login nuevamente

### Si aparece Error 400 (Bad Request)
1. Revisar la respuesta JSON en DevTools → Network
2. Los errores de validación aparecerán detallados
3. Verificar formato de datos enviados

### Si aparece Error 500 (Server Error)
1. Revisar logs del servidor Django
2. Posible problema en el backend que necesita corrección

## 📈 Métricas de Éxito

### ✅ **Prueba Exitosa:**
- [ ] JavaScript V2 se carga sin errores
- [ ] Usuario puede navegar entre los 4 pasos
- [ ] Validaciones funcionan correctamente
- [ ] Solicitud se envía exitosamente (status 201)
- [ ] Aparece en el admin de Django
- [ ] No se afectan otras funcionalidades (login, catálogo, etc.)

### 🎯 **Objetivos Cumplidos:**
- [ ] Flujo de financiamiento V2 operativo
- [ ] Compatible con infraestructura existente
- [ ] Sin alteraciones a configuración crítica
- [ ] Mantenimiento de todas las funcionalidades previas

## 📞 Soporte
Si hay algún problema durante la prueba, revisar:
1. Consola del navegador para errores JavaScript
2. Network tab para errores de API
3. Logs del servidor para errores del backend

---
**Nota**: Esta versión V2 está específicamente adaptada para trabajar con la infraestructura existente del VPS sin alterar la configuración de autenticación, CSRF o Django que ya funciona correctamente. 