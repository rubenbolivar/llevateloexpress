# LlévateloExpress - Plataforma de Financiamiento

Aplicación web para LlévateloExpress.com, una plataforma para financiamiento y adquisición de vehículos, motocicletas, camiones, maquinaria agrícola y equipos industriales en Venezuela.

## Características Principales

- **Catálogo de Productos**: Amplia variedad de vehículos, motocicletas, camiones, maquinaria agrícola y equipos industriales disponibles para financiamiento.
- **Planes de Financiamiento**: Diferentes opciones adaptadas a las necesidades de cada cliente (Plan 50-50, Plan 70-30, Plan Agrícola).
- **Calculadora Interactiva**: Permite al usuario simular diferentes escenarios de financiamiento y ver las cuotas resultantes con tabla de amortización.
- **Registro de Clientes**: Sistema seguro para recolectar información de los potenciales clientes interesados en adquirir un producto.
- **Formulario de Contacto**: Integrado con WhatsApp para comunicación directa con los asesores.
- **Diseño Responsive**: Experiencia de usuario optimizada para dispositivos móviles, tablets y escritorio.
- **Despliegue Automatizado**: Script de despliegue para configuración rápida del servidor de producción.
- **Backend Django**: Panel de administración Django para gestionar productos, planes de financiamiento y solicitudes.
- **API REST**: API RESTful para la comunicación entre el frontend y el backend.

## Tecnologías Utilizadas

- **Frontend**:
  - HTML5 y CSS3 para estructuración y estilización
  - JavaScript (ES6+) para funcionalidades dinámicas
  - Bootstrap 5 como framework de UI
  - Font Awesome para iconografía

- **Backend**:
  - Django 4.2 como framework principal
  - Django REST Framework para API RESTful
  - PostgreSQL como base de datos
  - Autenticación JWT para seguridad

- **Infraestructura**:
  - Servidor Nginx con configuración optimizada
  - Gunicorn como servidor WSGI
  - Certificados SSL vía Let's Encrypt
  - API de WhatsApp para formulario de contacto
  - Optimización de rendimiento para producción

## Estructura del Proyecto

```
/
├── backend_env/             # Entorno virtual de Python para el backend
├── .env.production          # Variables de entorno para producción
├── css/                     # Estilos CSS del frontend
├── deploy.sh                # Script de despliegue automatizado
├── gunicorn_conf.py         # Configuración de Gunicorn
├── img/                     # Imágenes y recursos visuales
├── js/                      # JavaScript del frontend
├── llevateloexpress_backend/# Configuración principal de Django
├── llevateloexpress.service # Configuración del servicio systemd
├── llevateloexpress_nginx.conf # Configuración de Nginx
├── manage.py                # Script de gestión de Django
├── media/                   # Archivos subidos por usuarios
├── products/                # App de Django para gestión de productos
├── financing/               # App de Django para gestión de financiamiento
├── users/                   # App de Django para gestión de usuarios
├── requirements.txt         # Dependencias de Python
├── scripts/                 # Scripts de utilidad
├── static/                  # Archivos estáticos para Django
├── staticfiles/             # Archivos estáticos recopilados para producción
├── templates/               # Plantillas HTML servidas por Django
│   ├── index.html           # Página principal con catálogo
│   ├── catalogo.html        # Catálogo completo de productos
│   ├── detalle-producto.html# Vista detallada de productos
│   ├── registro.html        # Formulario de registro de clientes
│   ├── planes.html          # Información sobre planes de financiamiento
│   ├── calculadora.html     # Calculadora interactiva de financiamiento
│   ├── nosotros.html        # Información sobre la empresa
│   └── contacto.html        # Formulario de contacto con integración WhatsApp
```

## Categorías de Productos

El sistema incluye las siguientes categorías de productos, cada una con su estructura de datos optimizada:

1. **Motocicletas**: Modelos de diferentes cilindradas y estilos, desde económicas hasta deportivas.
2. **Vehículos**: Automóviles, camionetas y vehículos de pasajeros.
3. **Camiones**: Unidades de carga, transporte y distribución de diferentes capacidades.
4. **Maquinaria Agrícola**: Tractores y equipos para optimizar la producción agrícola.
5. **Maquinaria y Equipos**: Equipamiento especializado para la industria y el comercio.

Cada categoría está modelada para permitir filtrado, búsqueda y presentación específica acorde a sus características particulares.

## API REST

El sistema proporciona una API RESTful para comunicación entre el frontend y el backend, con los siguientes endpoints principales:

- `/api/products/categories/`: Lista de categorías de productos
- `/api/products/products/`: Lista de productos
- `/api/products/products/<id>/`: Detalle de un producto específico
- `/api/products/featured-products/`: Lista de productos destacados
- `/api/products/products-by-category/<slug>/`: Productos por categoría
- `/api/financing/plans/`: Planes de financiamiento disponibles
- `/api/financing/simulate/`: Simulación de financiamiento
- `/api/financing/save-simulation/`: Guardar simulación de financiamiento
- `/api/users/register/`: Registro de usuarios
- `/api/users/token/`: Autenticación de usuarios
- `/api/users/profile/`: Perfil de usuario
- `/api/users/applications/`: Solicitudes de financiamiento

## Sistema de Autenticación

El sistema de autenticación de LlévateloExpress implementa un enfoque moderno basado en tokens JWT (JSON Web Tokens) con protección CSRF adicional. La autenticación está integrada entre el backend Django y el frontend JavaScript, ofreciendo una experiencia segura y fluida.

### Componentes de autenticación

#### Backend (Django + DRF + SimpleJWT)

1. **Middleware y configuración CSRF**:
   - Django proporciona protección CSRF integrada mediante tokens
   - El endpoint `/api/users/csrf-token/` establece la cookie CSRF necesaria para operaciones seguras
   - Decorador `@ensure_csrf_cookie` garantiza la disponibilidad del token

2. **Autenticación JWT**:
   - La biblioteca `djangorestframework-simplejwt` gestiona la generación y validación de tokens
   - Dos tokens son generados: access_token (corta duración) y refresh_token (larga duración)
   - El endpoint `/api/users/token/` emite tokens al autenticar credenciales
   - El endpoint `/api/users/token/refresh/` permite renovar tokens caducados

3. **Vistas de Django para autenticación**:
   - `RegisterView`: Para crear nuevas cuentas de usuario
   - `CustomTokenObtainPairView`: Personalización del proceso de login
   - `GetCSRFToken`: Para establecer tokens CSRF

#### Frontend (JavaScript)

1. **Módulo de Autenticación (`auth.js`)**:
   - Sistema centralizado para gestionar todas las operaciones de autenticación
   - Funciones principales:
     * `loginUser()`: Gestiona el inicio de sesión y almacenamiento de tokens
     * `registerUser()`: Maneja el registro de nuevos usuarios
     * `logoutUser()`: Cierra sesión y limpia tokens almacenados
     * `isAuthenticated()`: Verifica el estado de autenticación
     * `refreshAccessToken()`: Renueva tokens caducados automáticamente
     * `authenticatedFetch()`: Realiza peticiones autenticadas a la API

2. **Gestión de Tokens CSRF**:
   - La función `fetchCsrfToken()` solicita y almacena el token CSRF de Django
   - Todas las solicitudes POST incluyen el token CSRF en el encabezado `X-CSRFToken`

3. **Almacenamiento Seguro**:
   - Los tokens JWT se almacenan en `localStorage` para persistencia
   - La cookie CSRF se gestiona automáticamente por el navegador

4. **Interfaz de Usuario adaptativa**:
   - La función `updateAuthUI()` actualiza dinámicamente la interfaz según el estado de autenticación
   - Botones "Iniciar Sesión"/"Registrarse" o "Cerrar Sesión" se muestran según corresponda

### Flujo de Autenticación

1. **Registro de Usuario**:
   - Usuario completa formulario en `registro.html`
   - Frontend solicita token CSRF mediante `fetchCsrfToken()`
   - `registerUser()` envía los datos a `/api/users/register/` con protección CSRF
   - Al registrarse exitosamente, se muestra modal de confirmación y redirección a login

2. **Inicio de Sesión**:
   - Usuario introduce credenciales en `login.html`
   - `loginUser()` envía datos a `/api/users/token/` con token CSRF
   - Backend valida credenciales y emite tokens JWT
   - Frontend almacena tokens y actualiza UI para mostrar estado autenticado

3. **Peticiones Autenticadas**:
   - Módulo `api.js` utiliza `Auth.fetch()` para solicitudes que requieren autenticación
   - `authenticatedFetch()` incluye token JWT en encabezado `Authorization`
   - Si el token está caducado, se renueva automáticamente y reintenta la petición

4. **Cierre de Sesión**:
   - Al hacer clic en "Cerrar Sesión", `logoutUser()` elimina tokens y limpia cookie CSRF
   - UI se actualiza para mostrar elementos para usuarios no autenticados

### Integración Backend-Frontend

La comunicación entre el backend y el frontend se realiza mediante:

1. **API RESTful**:
   - Endpoints JSON bien definidos para cada operación
   - Respuestas estructuradas con códigos HTTP apropiados

2. **Middleware CORS**:
   - Configuración de Django usando `django-cors-headers`
   - Permite solicitudes seguras desde dominios específicos

3. **Serialización de datos**:
   - Serializers de Django REST Framework transforman modelos a JSON
   - Frontend deserializa y gestiona respuestas para actualizaciones de UI

4. **Manejo de errores**:
   - Respuestas de error detalladas desde el backend
   - Frontend muestra mensajes de error específicos al usuario

### Seguridad Implementada

1. **Protección contra CSRF**:
   - Token CSRF requerido para todas las operaciones POST/PUT/DELETE
   - Implementación siguiendo las mejores prácticas de Django

2. **Tokens JWT con corta duración**:
   - Los tokens de acceso caducan rápidamente (15 minutos)
   - Renovación automática mediante refresh token (válido por 7 días)

3. **Validación en ambos lados**:
   - Frontend: Validación de formularios JavaScript y HTML5
   - Backend: Validación robusta con Django REST Framework serializers

4. **Logging**:
   - Sistema de logging para rastrear intentos de autenticación
   - Alertas para intentos fallidos repetidos

### Próximas mejoras

- Implementación de autenticación social (Google, Facebook)
- Verificación por correo electrónico para nuevos registros
- Recuperación de contraseña mediante tokens seguros
- Autenticación de dos factores para operaciones sensibles

## Panel Administrativo de Django

El panel administrativo de Django permite:

- Gestión completa de productos y categorías
- Administración de planes de financiamiento
- Revisión y gestión de simulaciones
- Gestión de solicitudes de financiamiento
- Administración de usuarios y clientes

## Configuración de Desarrollo

### Requisitos previos
- Python 3.9 o superior
- PostgreSQL 13 o superior
- Node.js y npm (opcional, para desarrollo frontend)

### Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/llevateloexpress.git
   cd llevateloexpress
   ```

2. Crear y activar el entorno virtual:
   ```bash
   python -m venv backend_env
   source backend_env/bin/activate  # En Windows: backend_env\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar la base de datos:
   ```bash
   createdb llevateloexpress
   python manage.py migrate
   ```

5. Crear superusuario:
   ```bash
   python manage.py createsuperuser
   ```

6. Importar datos de muestra:
   ```bash
   python scripts/import_products.py
   ```

7. Iniciar el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

8. Accede a:
   - Frontend: http://localhost:8000/
   - Panel de administración: http://localhost:8000/admin/
   - API: http://localhost:8000/api/products/products/

## Despliegue a Producción

El proyecto incluye un script `deploy.sh` que automatiza:

1. Configuración de servidor Nginx
2. Transferencia de archivos al servidor
3. Configuración de permisos
4. Implementación de HTTPS con Let's Encrypt
5. Optimización para producción

### Preparación para despliegue

1. Ejecutar el script de preparación:
   ```bash
   python scripts/prepare_production.py
   ```

2. Actualizar la configuración en los archivos generados:
   - `.env.production`: Variables de entorno
   - `deploy.sh`: Dirección del servidor y credenciales

3. Ejecutar el script de despliegue:
   ```bash
   ./deploy.sh
   ```

### Requisitos para Despliegue

- Servidor con Ubuntu/Debian
- Acceso SSH con privilegios de administrador
- Dominio configurado apuntando al servidor
- Puertos 80 y 443 abiertos

## Mantenimiento

### Actualización de Productos
Para actualizar el catálogo de productos, se recomienda usar el panel administrativo de Django.

### Actualización de Categorías
Para añadir nuevas categorías o modificar las existentes, use el panel administrativo de Django.

### Cambios en la Interfaz
Los estilos personalizados se encuentran en `css/styles.css`. Para modificaciones mayores, considere editar los archivos HTML correspondientes.

## Contacto y Soporte

Para consultas técnicas o soporte relacionado con la implementación:
- Email: soporte@llevateloexpress.com
- Teléfono: (0212) 555-1234
- WhatsApp: +584121010744

## Desarrollado por

LlévateloExpress © 2023-2024 - Todos los derechos reservados

## Requisitos

- Python 3.8+
- PostgreSQL 12+
- Nginx

## Configuración del entorno de desarrollo

### Instalación de dependencias

```bash
# Crear entorno virtual
python -m venv backend_env
source backend_env/bin/activate  # En Windows: backend_env\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Configuración local

Para desarrollo local, el proyecto utiliza SQLite en lugar de PostgreSQL. La configuración necesaria ya está en `llevateloexpress_backend/local_settings.py` que se carga automáticamente.

### Ejecución del servidor de desarrollo

```bash
python manage.py migrate  # Aplicar migraciones
python manage.py runserver  # Iniciar servidor
```

## Despliegue en producción

### Configuración de acceso SSH sin contraseña

Para facilitar el despliegue, configura el acceso SSH con clave pública:

```bash
# Generar par de claves SSH si no lo tienes
ssh-keygen -t rsa -b 4096

# Enviar clave pública al servidor
ssh-copy-id root@203.161.55.87
```

### Script de despliegue automatizado

El proyecto incluye un script para automatizar el proceso de despliegue en el servidor de producción.

```bash
# Ver opciones disponibles
./scripts/deploy_to_server.sh

# Despliegue completo (código, dependencias, DB, migraciones, estáticos)
./scripts/deploy_to_server.sh --full-deploy

# Solo sincronizar código
./scripts/deploy_to_server.sh --sync-code

# Ejecutar migraciones
./scripts/deploy_to_server.sh --migrate

# Corregir configuración de base de datos
./scripts/deploy_to_server.sh --fix-db

# Verificar estado de servicios
./scripts/deploy_to_server.sh --check-status

# Abrir shell en el servidor
./scripts/deploy_to_server.sh --shell

# Ejecutar un comando específico en el servidor
./scripts/deploy_to_server.sh --execute "comando"
```

## Estructura del proyecto

- `llevateloexpress_backend/`: Configuración principal de Django
- `core/`: Funcionalidades centrales
- `products/`: Gestión de productos
- `financing/`: Planes de financiamiento
- `users/`: Gestión de usuarios y clientes
- `templates/`: Plantillas HTML
- `static/`: Archivos estáticos (CSS, JS, imágenes)
- `media/`: Archivos subidos por usuarios
- `scripts/`: Scripts de utilidad para desarrollo y despliegue

## Acceso al Admin

- Local: http://localhost:8000/admin/
- Producción: https://llevateloexpress.com/admin/

## Recursos adicionales

- [DEPLOYMENT_PROTOCOL.md](DEPLOYMENT_PROTOCOL.md): Protocolo detallado de despliegue
- [ADMIN_FIX_INSTRUCCIONES.md](ADMIN_FIX_INSTRUCCIONES.md): Solución para problemas con el admin en producción 