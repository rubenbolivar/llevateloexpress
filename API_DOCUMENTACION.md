# Documentación Técnica de la API de LlévateloExpress

Esta documentación detalla el funcionamiento técnico de la API de LlévateloExpress, con especial énfasis en el sistema de autenticación y la integración entre backend y frontend.

## Endpoints de Autenticación

### Obtener Token CSRF

```
GET /api/users/csrf-token/
```

**Descripción**: Establece una cookie CSRF necesaria para operaciones seguras.

**Respuesta exitosa**:
```json
{
  "success": "CSRF cookie set"
}
```

**Headers de respuesta**:
- `Set-Cookie: csrftoken=<token>; expires=<fecha>; Max-Age=31449600; Path=/; SameSite=Lax`

**Notas**:
- Esta solicitud debe realizarse antes de cualquier operación que requiera protección CSRF.
- La cookie se establece automáticamente en el navegador.

### Registro de Usuario

```
POST /api/users/register/
```

**Descripción**: Registra un nuevo usuario en el sistema.

**Headers requeridos**:
- `Content-Type: application/json`
- `X-CSRFToken: <token>`

**Cuerpo de la solicitud**:
```json
{
  "username": "usuario@ejemplo.com",
  "email": "usuario@ejemplo.com",
  "password": "ContraseñaSegura123",
  "password2": "ContraseñaSegura123",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "phone": "+584141234567",
  "identity_document": "V-12345678"
}
```

**Respuesta exitosa**:
```json
{
  "success": true,
  "message": "Usuario creado exitosamente",
  "user_id": 123,
  "username": "usuario@ejemplo.com",
  "email": "usuario@ejemplo.com"
}
```

**Respuesta de error**:
```json
{
  "success": false,
  "errors": {
    "email": ["Este correo electrónico ya está en uso."],
    "password": ["Las contraseñas no coinciden."]
  }
}
```

### Obtener Token JWT

```
POST /api/users/token/
```

**Descripción**: Autentica un usuario y emite tokens JWT para acceso a la API.

**Headers requeridos**:
- `Content-Type: application/json`
- `X-CSRFToken: <token>`

**Cuerpo de la solicitud**:
```json
{
  "username": "usuario@ejemplo.com",
  "password": "ContraseñaSegura123"
}
```

**Respuesta exitosa**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Respuesta de error**:
```json
{
  "detail": "No se encontró ninguna cuenta activa con las credenciales proporcionadas"
}
```

### Refrescar Token JWT

```
POST /api/users/token/refresh/
```

**Descripción**: Renueva un token de acceso caducado usando el token de refresco.

**Headers requeridos**:
- `Content-Type: application/json`

**Cuerpo de la solicitud**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Respuesta exitosa**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Respuesta de error**:
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

### Obtener Perfil de Usuario

```
GET /api/users/profile/
```

**Descripción**: Obtiene información detallada del perfil del usuario autenticado.

**Headers requeridos**:
- `Authorization: Bearer <access_token>`

**Respuesta exitosa**:
```json
{
  "id": 123,
  "user": {
    "username": "usuario@ejemplo.com",
    "email": "usuario@ejemplo.com",
    "first_name": "Nombre",
    "last_name": "Apellido"
  },
  "phone": "+584141234567",
  "identity_document": "V-12345678",
  "address": "...",
  "created_at": "2023-06-15T14:30:00Z",
  "updated_at": "2023-06-15T14:30:00Z"
}
```

## Implementación de Autenticación en Frontend

### Módulo `auth.js`

Este módulo centraliza toda la lógica de autenticación en el frontend:

#### Funciones principales:

##### `getCsrfToken()`
```javascript
function getCsrfToken() {
    const name = 'csrftoken=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');
    
    for (let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i].trim();
        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
    return null;
}
```

##### `fetchCsrfToken()`
```javascript
async function fetchCsrfToken() {
    try {
        console.log('Solicitando token CSRF...');
        const response = await fetch(`${API_BASE_URL}/users/csrf-token/`, {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            console.log('Token CSRF obtenido correctamente');
            return true;
        } else {
            console.error('Error al obtener token CSRF:', response.status);
            return false;
        }
    } catch (error) {
        console.error('Error al solicitar token CSRF:', error);
        return false;
    }
}
```

##### `loginUser(email, password)`
```javascript
async function loginUser(email, password) {
    // Validación básica de parámetros
    if (!email || typeof email !== 'string') {
        return {
            error: true,
            data: { username: ["Campo requerido"] },
            status: 400
        };
    }
    
    if (!password || typeof password !== 'string') {
        return {
            error: true,
            data: { password: ["Campo requerido"] },
            status: 400
        };
    }
    
    try {
        // Asegurar que tenemos token CSRF
        await fetchCsrfToken();
        
        console.log(`Iniciando sesión para: ${email}`);
        
        // Realizar petición de login
        const response = await fetch(`${API_BASE_URL}/users/token/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            credentials: 'include',
            body: JSON.stringify({ username: email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Guardar tokens en localStorage
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            
            // También guardar email para identificación rápida
            localStorage.setItem('user_email', email);
            
            console.log('Inicio de sesión exitoso');
            return { success: true };
        } else {
            console.error('Error en inicio de sesión:', data);
            return { error: true, data, status: response.status };
        }
    } catch (error) {
        console.error('Error durante login:', error);
        return { error: true, message: 'Error de conexión' };
    }
}
```

##### `authenticatedFetch(url, options)`
```javascript
async function authenticatedFetch(url, options = {}) {
    // Obtener token de acceso
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
        return { error: true, message: 'No autenticado' };
    }
    
    // Configurar headers autenticados
    const authOptions = {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    };
    
    try {
        // Realizar petición
        let response = await fetch(url, authOptions);
        
        // Si es error 401 (Unauthorized), intentar refrescar token
        if (response.status === 401) {
            const refreshSuccess = await refreshAccessToken();
            
            if (refreshSuccess) {
                // Actualizar token en headers y reintentar
                authOptions.headers.Authorization = `Bearer ${localStorage.getItem('access_token')}`;
                response = await fetch(url, authOptions);
            } else {
                // Si no se pudo refrescar, cerrar sesión
                logoutUser();
                return { error: true, message: 'Sesión expirada' };
            }
        }
        
        // Procesar respuesta
        let data;
        try {
            data = await response.json();
        } catch {
            data = {};
        }
        
        if (response.ok) {
            return { success: true, data };
        } else {
            return { error: true, data, status: response.status };
        }
    } catch (error) {
        console.error('Error en petición autenticada:', error);
        return { error: true, message: 'Error de conexión' };
    }
}
```

##### `updateAuthUI()`
```javascript
function updateAuthUI() {
    const authenticated = isAuthenticated();
    
    // Actualizar botones de autenticación en la barra de navegación
    const authButtonsContainer = document.getElementById('auth-buttons');
    if (authButtonsContainer) {
        if (authenticated) {
            // Usuario autenticado: Mostrar "Mi Perfil" y "Cerrar Sesión"
            const userEmail = localStorage.getItem('user_email') || 'Usuario';
            authButtonsContainer.innerHTML = `
                <span class="me-3 text-muted">Bienvenido, ${userEmail}</span>
                <button id="logoutBtn" class="btn btn-outline-danger">Cerrar Sesión</button>
            `;
            
            // Añadir evento de logout
            const logoutBtn = document.getElementById('logoutBtn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    logoutUser();
                });
            }
        } else {
            // Usuario no autenticado: Mostrar "Registrarse" e "Iniciar Sesión"
            authButtonsContainer.innerHTML = `
                <a href="registro.html" class="btn btn-outline-primary me-2">Registrarse</a>
                <a href="login.html" class="btn btn-primary">Iniciar Sesión</a>
            `;
        }
    }
    
    // Actualizar contenedores con atributos data-auth
    const authContainers = document.querySelectorAll('[data-auth-container]');
    if (authContainers.length > 0) {
        authContainers.forEach(container => {
            const forAuthenticated = container.getAttribute('data-auth-container') === 'authenticated';
            
            if ((forAuthenticated && authenticated) || (!forAuthenticated && !authenticated)) {
                container.style.display = '';
            } else {
                container.style.display = 'none';
            }
        });
    }
}
```

## Implementación de Autenticación en Backend

### Middlewares y configuración de seguridad

Django y Django REST Framework proporcionan varios mecanismos de seguridad para la API. La configuración clave en `settings.py` incluye:

```python
# CSRF Protection
CSRF_COOKIE_SECURE = True  # En producción
CSRF_COOKIE_HTTPONLY = False  # Permitir acceso desde JavaScript
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = ['https://llevateloexpress.com']

# CORS Configuration
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'https://llevateloexpress.com',
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Django REST Framework Authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### Vistas de autenticación 

Las vistas principales para autenticación están en `users/views.py`:

```python
@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    """
    Vista para establecer una cookie CSRF cuando se carga la página.
    Esto debe ser llamado antes de realizar cualquier solicitud POST.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        return Response({"success": "CSRF cookie set"})

class RegisterView(generics.CreateAPIView):
    """
    Vista estándar para registrar usuarios a través de la API.
    Utiliza protección CSRF estándar.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": "Usuario creado exitosamente",
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
```

## Integración entre componentes

### Comunicación Frontend-Backend

El sistema utiliza los siguientes patrones para la comunicación entre componentes:

1. **Solicitudes AJAX**: El frontend utiliza la API Fetch para realizar solicitudes al backend.

2. **Formato JSON**: Todas las solicitudes y respuestas utilizan formato JSON para intercambio de datos.

3. **Serialización/Deserialización**: Django REST Framework serializa modelos de Django a JSON, mientras que JavaScript deserializa las respuestas JSON.

4. **Manejo de Tokens**: 
   - El frontend solicita tokens JWT al iniciar sesión
   - Los tokens se almacenan en localStorage
   - Cada solicitud autenticada incluye el token JWT en el encabezado Authorization

5. **Manejo de Errores**:
   - El backend envía respuestas de error con detalles específicos
   - El frontend muestra mensajes de error adaptados al usuario

## Ejemplos de Flujos Completos

### Registro e Inicio de Sesión

1. **Usuario navega a la página de registro**:
   - `auth.js` verifica si ya existe una sesión
   - Si no existe, muestra el formulario de registro

2. **Usuario completa y envía el formulario**:
   - Se validan los datos en el frontend
   - `auth.js` solicita token CSRF
   - Datos enviados a `/api/users/register/`
   - Backend valida, guarda y responde

3. **Usuario ve confirmación y va a login**:
   - Se muestra modal de éxito
   - Al hacer clic en "Iniciar Sesión", se redirige a login.html

4. **Usuario inicia sesión**:
   - Completa formulario en login.html
   - `auth.js` solicita token CSRF
   - Datos enviados a `/api/users/token/`
   - Backend valida y emite tokens JWT
   - Frontend almacena tokens
   - UI se actualiza para mostrar estado autenticado

### Acciones autenticadas (ejemplo: guardar simulación)

1. **Usuario autenticado realiza una simulación**:
   - Completa formulario en calculadora.html
   - Frontend muestra resultados

2. **Usuario guarda la simulación**:
   - Hace clic en "Guardar simulación"
   - `api.js` utiliza `Auth.fetch()` con el endpoint correcto
   - Backend verifica token JWT
   - Datos guardados en la base de datos
   - Respuesta exitosa
   - Frontend muestra confirmación

## Recomendaciones para Desarrolladores

1. **Gestión de tokens**:
   - No modificar directamente localStorage para tokens JWT
   - Usar siempre `Auth.login()`, `Auth.logout()` y `Auth.fetch()`
   - No crear nuevas implementaciones de autenticación

2. **Depuración**:
   - Revisar console.log para mensajes relacionados con autenticación
   - Utilizar herramientas de desarrollo del navegador para inspeccionar cookies y localStorage
   - Comprobar respuestas de API con herramientas como Postman

3. **Seguridad**:
   - No almacenar información sensible en localStorage o sessionStorage
   - Siempre incluir token CSRF en solicitudes POST
   - No aumentar tiempos de expiración de tokens sin justificación

4. **Ampliación del sistema**:
   - Seguir el patrón establecido para nuevas funcionalidades autenticadas
   - Utilizar decoradores `permission_classes` en vistas de Django para controlar acceso
   - Documentar nuevos endpoints y parámetros

## Errores Comunes y Soluciones

| Error | Causa Posible | Solución |
|-------|--------------|----------|
| 401 Unauthorized | Token JWT caducado o inválido | Verificar que `refreshAccessToken()` funciona correctamente |
| 403 Forbidden CSRF Failed | No se incluyó token CSRF | Llamar a `fetchCsrfToken()` antes de POST/PUT/DELETE |
| 400 Bad Request en registro | Validación fallida (contraseña débil, email duplicado) | Revisar respuesta de API para detalles específicos |
| Redirección inesperada | Detección incorrecta de autenticación | Verificar lógica en `updateAuthUI()` y `DOMContentLoaded` |
| Error al cargar perfil | Token almacenado pero inválido en backend | Implementar verificación periódica de tokens |

## Changelog

### Versión 1.1.0 (Actual)
- Implementación de botón de cerrar sesión
- Mejora en manejo de tokens CSRF
- Corrección de redirecciones en registro/login
- Adición de mensajes informativos al cerrar sesión

### Versión 1.0.0
- Implementación inicial del sistema de autenticación
- Registro de usuarios e inicio de sesión
- Protección CSRF básica
- Tokens JWT para acceso a API 