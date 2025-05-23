# Índice de Documentación de LlévateloExpress

Este archivo sirve como punto central de referencia para toda la documentación del proyecto LlévateloExpress.

## Documentos Principales

### 1. [README.md](README.md)
- **Propósito**: Introducción general al proyecto
- **Contenido**: Características, tecnologías, configuración básica, estructura del proyecto
- **Uso**: Lectura inicial para cualquier persona que se une al proyecto
- **Última actualización**: Mayo 2025

### 2. [PROTOCOLOS_GIT_Y_DESPLIEGUE.md](PROTOCOLOS_GIT_Y_DESPLIEGUE.md)
- **Propósito**: Guía completa para la gestión del código y despliegue
- **Contenido**: Flujo de trabajo Git, procedimientos de despliegue, sincronización
- **Uso**: Referencia obligatoria antes de realizar cambios en el código o desplegar
- **Última actualización**: Mayo 2025

### 3. [ADMIN_FIX_INSTRUCCIONES.md](ADMIN_FIX_INSTRUCCIONES.md)
- **Propósito**: Solución para problemas específicos con el panel de administración
- **Contenido**: Diagnóstico y pasos para resolver problemas con el admin de Django
- **Uso**: Cuando el panel de administración no funciona correctamente
- **Última actualización**: Mayo 2025

### 4. [API_DOCUMENTACION.md](API_DOCUMENTACION.md)
- **Propósito**: Documentación completa de la API REST
- **Contenido**: Descripción de endpoints, parámetros, respuestas y ejemplos de uso
- **Uso**: Para desarrolladores frontend y terceros que necesiten interactuar con la API
- **Última actualización**: Mayo 2025

## Documentos Específicos

### 5. [scripts/syncronizacion.md](scripts/syncronizacion.md)
- **Propósito**: Detalles sobre los scripts de sincronización
- **Contenido**: Explicación detallada de los scripts para mantener sincronizados los repositorios
- **Uso**: Para entender en detalle cómo funcionan los scripts de sincronización
- **Última actualización**: Mayo 2025

## Documentos en Desuso o Duplicados

Los siguientes documentos contienen información que ya está integrada en documentos más recientes:

- **GIT_WORKFLOW.md**: La información ahora está en PROTOCOLOS_GIT_Y_DESPLIEGUE.md
- **DEPLOYMENT_PROTOCOL.md**: La información ahora está en PROTOCOLOS_GIT_Y_DESPLIEGUE.md

## Flujo de Documentación

Para mantener la documentación actualizada y coherente:

1. Cualquier cambio en procedimientos debe reflejarse primero en el documento principal correspondiente
2. Actualizar la fecha de "Última actualización" cada vez que se modifique un documento
3. Si se crea un nuevo documento, añadirlo a este índice
4. Si se detecta información contradictoria, dar prioridad al documento con la fecha más reciente

## Responsables de Documentación

La documentación es mantenida por el equipo de desarrollo de LlévateloExpress.

Para cualquier consulta o sugerencia sobre la documentación, contactar a:
- Email: rubenbolivar@gmail.com

---

Última actualización: 25 de mayo de 2025 

# Documentación del Sistema LlévateloExpress

## Índice de Contenido

1. [Introducción](#introducción)
2. [Registro e Inicio de Sesión](#registro-e-inicio-de-sesión)
3. [Panel de Usuario](#panel-de-usuario)
4. [Calculadora de Financiamiento](#calculadora-de-financiamiento)
5. [Solicitud de Financiamiento](#solicitud-de-financiamiento)
6. [Preguntas Frecuentes](#preguntas-frecuentes)

## Introducción

LlévateloExpress es una plataforma para financiamiento y adquisición de vehículos, motocicletas, camiones, maquinaria agrícola y equipos industriales en Venezuela. Esta documentación explica el uso de la plataforma tanto desde la perspectiva del usuario final como del desarrollador.

## Registro e Inicio de Sesión

### Proceso de Registro

Para registrarse como usuario de LlévateloExpress, siga estos pasos:

1. Haga clic en el botón "Registrarse" en la esquina superior derecha del sitio.
2. Complete el formulario con la siguiente información:
   - Email (será su nombre de usuario para iniciar sesión)
   - Contraseña (mínimo 8 caracteres, debe incluir letras y números)
   - Nombre y Apellido
   - Número de teléfono
   - Documento de identidad (formato: V-12345678)
3. Haga clic en "Crear Cuenta".
4. Si todos los datos son correctos, recibirá un mensaje de confirmación y será redirigido a la página de inicio de sesión.

> **Nota**: El registro es un requisito para guardar simulaciones de financiamiento y realizar solicitudes, pero no es necesario para navegar por el catálogo o usar la calculadora.

### Inicio de Sesión

Para iniciar sesión:

1. Haga clic en el botón "Iniciar Sesión" en la esquina superior derecha.
2. Ingrese su email y contraseña.
3. Haga clic en "Entrar".
4. Una vez autenticado, la interfaz cambiará mostrando su email y un botón para cerrar sesión.

### Cierre de Sesión

Para cerrar sesión, simplemente haga clic en el botón "Cerrar Sesión" que aparece cuando está autenticado.

### Solución de Problemas Comunes

| Problema | Causa Posible | Solución |
|----------|---------------|----------|
| No puedo registrarme con mi email | El email ya está registrado | Intente recuperar su contraseña o use otro email |
| La página se cierra al intentar registrarme | Problemas con cookies o JavaScript | Asegúrese de tener habilitadas las cookies y JavaScript en su navegador |
| No recuerdo mi contraseña | N/A | Próximamente implementaremos el sistema de recuperación de contraseña |

## Panel de Usuario

Una vez que ha iniciado sesión, tendrá acceso a su panel de usuario donde podrá:

1. Ver su información personal
2. Revisar sus simulaciones guardadas
3. Dar seguimiento a sus solicitudes de financiamiento
4. Actualizar sus datos de contacto

> **Nota**: Para mantener la seguridad de su cuenta, le recomendamos cerrar sesión cuando utilice dispositivos compartidos.

## Sistema de Autenticación: Guía para Usuarios

El sistema de autenticación de LlévateloExpress está diseñado para proporcionar una experiencia segura y fácil de usar. A continuación se detalla cómo utilizarlo correctamente:

### Beneficios de Registrarse e Iniciar Sesión

Como usuario registrado y autenticado, usted puede:

1. **Guardar sus simulaciones de financiamiento** para revisarlas posteriormente
2. **Realizar solicitudes formales** de financiamiento
3. **Recibir atención personalizada** de nuestros asesores
4. **Acceder a ofertas exclusivas** para clientes registrados
5. **Gestionar múltiples solicitudes** desde un solo lugar

### Seguridad de su Cuenta

Para proteger su información personal:

- Utilice contraseñas seguras (mínimo 8 caracteres con letras, números y símbolos)
- No comparta sus credenciales con terceros
- Evite usar la misma contraseña que usa en otros servicios
- Cierre sesión después de usar el sitio en dispositivos compartidos
- Verifique que la URL sea https://llevateloexpress.com antes de iniciar sesión

### Guía Visual del Proceso de Autenticación

#### Registrarse como Nuevo Usuario:

1. Haga clic en "Registrarse" en la barra superior
2. Complete todos los campos obligatorios del formulario
3. Revise y acepte los términos y condiciones
4. Haga clic en "Crear Cuenta"
5. Recibirá confirmación y podrá iniciar sesión inmediatamente

#### Iniciar Sesión:

1. Haga clic en "Iniciar Sesión" en la barra superior
2. Ingrese su correo electrónico y contraseña
3. Haga clic en "Entrar"
4. La barra superior cambiará mostrando su correo y la opción de cerrar sesión

#### Verificar Estado de Autenticación:

Para confirmar que ha iniciado sesión correctamente, observe:
- Su correo aparecerá en la barra superior
- El botón "Cerrar Sesión" estará visible
- Tendrá acceso a funciones adicionales como guardar simulaciones

## Sistema de Autenticación: Guía para Desarrolladores

Esta sección está dirigida a desarrolladores que necesitan comprender o extender el sistema de autenticación.

### Arquitectura del Sistema de Autenticación

El sistema de autenticación de LlévateloExpress implementa un modelo basado en tokens JWT con protección CSRF adicional. La arquitectura incluye:

1. **Frontend (JavaScript)**:
   - Módulo centralizado (`auth.js`) para operaciones de autenticación
   - Manejo seguro de tokens JWT en localStorage
   - Actualización dinámica de la interfaz según el estado de autenticación

2. **Backend (Django + DRF)**:
   - API RESTful para autenticación
   - SimpleJWT para generación y validación de tokens
   - Middlewares CSRF para protección contra ataques

### Ejemplos de Código para Integración

#### Realizar Petición Autenticada (JavaScript)

Para realizar peticiones que requieren autenticación desde el frontend:

```javascript
// Importar módulo de autenticación
import { Auth } from './auth.js';

// Ejemplo: Obtener perfil de usuario
async function getUserProfile() {
    const result = await Auth.fetch('/api/users/profile/');
    
    if (result.success) {
        // Procesar datos del perfil
        const profile = result.data;
        console.log(`Perfil cargado para: ${profile.user.email}`);
        return profile;
    } else {
        // Manejar error
        console.error('Error al cargar perfil:', result.message);
        return null;
    }
}

// Ejemplo: Guardar simulación (petición POST)
async function saveSimulation(simulationData) {
    const result = await Auth.fetch('/api/financing/save-simulation/', {
        method: 'POST',
        body: JSON.stringify(simulationData)
    });
    
    if (result.success) {
        return {
            success: true,
            simulationId: result.data.id
        };
    } else {
        return {
            success: false,
            message: result.message || 'Error al guardar simulación'
        };
    }
}
```

#### Proteger una Vista en Django

Para proteger un endpoint del backend:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class SavedSimulationsView(APIView):
    """
    Vista para listar las simulaciones guardadas del usuario autenticado
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        simulations = Simulation.objects.filter(user=user).order_by('-created_at')
        serializer = SimulationSerializer(simulations, many=True)
        
        return Response({
            'success': True,
            'count': simulations.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
```

### Integración en Nuevas Páginas

Para integrar el sistema de autenticación en nuevas páginas:

1. **Incluir el módulo de autenticación**:
   ```html
   <script type="module">
       import { Auth } from '/js/auth.js';
       
       // Ejecutar al cargar la página
       document.addEventListener('DOMContentLoaded', async function() {
           // Actualizar UI según estado de autenticación
           Auth.updateAuthUI();
           
           // Para contenido exclusivo para usuarios autenticados
           if (Auth.isAuthenticated()) {
               // Código para usuarios autenticados
               loadUserSpecificContent();
           } else {
               // Código para usuarios no autenticados
               showLoginPrompt();
           }
       });
   </script>
   ```

2. **Utilizar atributos data para control de visibilidad**:
   ```html
   <!-- Solo visible para usuarios autenticados -->
   <div data-auth-container="authenticated">
       <h3>Bienvenido a su panel personal</h3>
       <button id="saveBtn">Guardar configuración</button>
   </div>
   
   <!-- Solo visible para usuarios NO autenticados -->
   <div data-auth-container="unauthenticated">
       <p>Inicie sesión para acceder a todas las funciones</p>
       <a href="/login.html" class="btn btn-primary">Iniciar Sesión</a>
   </div>
   ```

3. **Realizar peticiones autenticadas**:
   ```javascript
   // Para peticiones que requieren autenticación
   async function loadUserData() {
       const result = await Auth.fetch('/api/users/data/');
       
       if (result.success) {
           displayUserData(result.data);
       } else if (result.status === 401) {
           // Sesión expirada o no autenticado
           redirectToLogin();
       } else {
           showErrorMessage(result.message);
       }
   }
   ```

### Recomendaciones de Seguridad

1. **Nunca almacene información sensible** en localStorage o sessionStorage
2. **Utilice siempre los métodos del módulo Auth** para operaciones de autenticación
3. **No modifique los tiempos de expiración de tokens** sin razones de seguridad válidas
4. **Incluya siempre el token CSRF** en todas las peticiones POST/PUT/DELETE
5. **Para datos sensibles**, use conexiones HTTPS y cifrado adicional si es necesario

### Pruebas y Depuración

Para probar el sistema de autenticación:

1. **Verificar logs del navegador**: Los mensajes detallados se registran en la consola
2. **Inspeccionar localStorage**: Comprobar que los tokens se almacenan/eliminan correctamente
3. **Verificar cookies**: La cookie CSRF debe establecerse al cargar la página
4. **Probar expiración de tokens**: Verifique que la renovación automática funciona correctamente

## Preguntas Frecuentes

### Para Usuarios

**¿Es seguro proporcionar mi información personal?**
Sí, utilizamos protocolos de seguridad avanzados como HTTPS y autenticación JWT para proteger su información.

**¿Por qué necesito crear una cuenta?**
La creación de una cuenta nos permite ofrecerle un servicio personalizado, guardar sus simulaciones y procesar sus solicitudes de financiamiento.

**¿Qué hago si olvido mi contraseña?**
Por el momento, contacte con soporte en soporte@llevateloexpress.com. Próximamente implementaremos un sistema de recuperación de contraseña.

**¿Puedo usar el mismo correo para varias cuentas?**
No, cada correo electrónico solo puede estar asociado a una cuenta.

### Para Desarrolladores

**¿Cómo implemento una nueva funcionalidad que requiera autenticación?**
Utilice el módulo `Auth.js` para el frontend y las clases de permisos de DRF para el backend.

**¿Cómo puedo depurar problemas de autenticación?**
Revise los logs de consola, inspeccione localStorage y cookies, y verifique las respuestas de API.

**¿Es posible extender el modelo de usuario?**
Sí, puede extender el modelo de usuario a través de la aplicación `users` y su modelo `Profile`.

**¿Cómo manejo diferentes niveles de permiso?**
Utilice los grupos de Django y permisos personalizados en DRF. 