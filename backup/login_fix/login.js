document.addEventListener('DOMContentLoaded', function() {
    // Inicializar el formulario
    initLoginForm();
    
    // Configurar toggle de contraseña
    setupPasswordToggle();
    
    // Verificar si el usuario ya está autenticado
    checkAuthStatus();
    
    // Verificar si viene de registro
    checkIfComingFromRegistration();
});

/**
 * Verificar si el usuario viene de la página de registro
 */
function checkIfComingFromRegistration() {
    const urlParams = new URLSearchParams(window.location.search);
    const registered = urlParams.get('registered');
    const email = urlParams.get('email');
    
    if (registered === 'true') {
        // Mostrar mensaje de bienvenida
        showSuccessMessage('¡Bienvenido! Tu cuenta ha sido creada exitosamente. Por favor, inicia sesión con tus credenciales.');
        
        // Prellenar el campo de email si está disponible
        if (email && document.getElementById('email')) {
            document.getElementById('email').value = email;
            // Enfocar el campo de contraseña
            if (document.getElementById('password')) {
                document.getElementById('password').focus();
            }
        }
    }
}

/**
 * Inicializar formulario de inicio de sesión
 */
function initLoginForm() {
    const form = document.getElementById('loginForm');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            event.stopPropagation();
            
            if (form.checkValidity()) {
                // Intentar iniciar sesión
                loginUser();
            } else {
                form.classList.add('was-validated');
            }
        });
    }
}

/**
 * Intentar iniciar sesión con las credenciales proporcionadas
 */
async function loginUser() {
    // Mostrar indicador de carga
    const submitBtn = document.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...';
    
    // Limpiar mensajes previos
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) {
        alertContainer.innerHTML = '';
    }
    
    try {
        // Obtener datos del formulario
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const rememberMe = document.getElementById('rememberMe').checked;
        
        // Validar que los campos no estén vacíos
        if (!email || !password) {
            showErrorMessage('Por favor completa todos los campos');
            return;
        }
        
        console.log("Intentando iniciar sesión con email:", email);
        
        // Llamar a la API
        const result = await API.users.login({
            username: email,
            password: password
        }).catch(error => {
            console.error("Error en llamada a API.users.login:", error);
            return {
                error: true,
                status: 0,
                message: "Error de conexión. Comprueba tu conexión a internet o inténtalo más tarde."
            };
        });
        
        console.log("Resultado login:", result);
        
        if (result && !result.error) {
            // Login exitoso
            
            // Si está marcado "recordarme", guardar preferencia
            if (rememberMe) {
                localStorage.setItem('rememberMe', 'true');
            }
            
            // Mostrar mensaje de éxito
            showSuccessMessage('Inicio de sesión exitoso. Redirigiendo...');
            
            // Redireccionar a página principal o perfil después de 1.5 segundos
            setTimeout(() => {
                console.log("Intentando redirección a index.html...");
                try {
                    // Intentar redirección con URL absoluta si la relativa falla
                    const currentUrl = window.location.href;
                    const baseUrl = currentUrl.substring(0, currentUrl.lastIndexOf('/') + 1);
                    console.log("URL base:", baseUrl);
                    
                    // Primero intentar con ruta relativa
                    window.location.href = 'index.html';
                    
                    // Como fallback, intentar después con ruta absoluta (esto puede no ejecutarse si la primera redirección funciona)
                    setTimeout(() => {
                        console.log("Intentando redirección alternativa...");
                        window.location.replace(baseUrl + 'index.html');
                    }, 500);
                } catch (error) {
                    console.error("Error durante la redirección:", error);
                    // Intento alternativo si falla
                    alert("Redirección fallida. Haga clic en Aceptar para continuar a la página principal.");
                    window.location.replace('/');
                }
            }, 1500);
        } else {
            // Error de inicio de sesión
            if (result && result.status === 0) {
                showErrorMessage('No se pudo conectar con el servidor. Por favor, verifica tu conexión a internet.');
            } else {
                showErrorMessage(getErrorMessage(result));
            }
        }
    } catch (error) {
        console.error('Error durante el inicio de sesión:', error);
        showErrorMessage('Ocurrió un error inesperado. Por favor, intenta nuevamente.');
    } finally {
        // Restaurar botón
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
    }
}

/**
 * Verificar si el usuario ya está autenticado
 */
function checkAuthStatus() {
    if (API.users.isAuthenticated()) {
        // Usuario ya autenticado, mostrar mensaje y opción de redirigir
        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            alertContainer.innerHTML = `
                <div class="alert alert-info alert-dismissible fade show" role="alert">
                    Ya has iniciado sesión. ¿Quieres ir a la <a href="index.html" class="alert-link">página principal</a>?
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
                </div>
            `;
        }
    }
}

/**
 * Configurar toggle de visibilidad de contraseña
 */
function setupPasswordToggle() {
    const toggleButtons = document.querySelectorAll('.toggle-password');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            
            // Cambiar tipo de input
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
}

/**
 * Mostrar mensaje de éxito
 */
function showSuccessMessage(message) {
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) {
        alertContainer.innerHTML = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
            </div>
        `;
    }
}

/**
 * Mostrar mensaje de error
 */
function showErrorMessage(message) {
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) {
        alertContainer.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
            </div>
        `;
    }
}

/**
 * Obtener mensaje de error legible
 */
function getErrorMessage(result) {
    console.log("Analizando error:", result);
    
    if (!result) return 'Error desconocido';
    
    // Si es un error de autenticación 401
    if (result.status === 401) {
        if (result.data && result.data.detail) {
            return result.data.detail;
        }
        return 'Credenciales inválidas. Por favor, verifica tu correo y contraseña.';
    }
    
    if (result.data) {
        if (result.data.detail) {
            return result.data.detail;
        }
        
        // Si hay errores específicos de inicio de sesión sin detalles
        if (result.data.non_field_errors) {
            return result.data.non_field_errors.join(', ');
        }
        
        // Mensajes específicos por campo
        const errorMessages = [];
        
        // Recorrer todos los campos con errores
        Object.keys(result.data).forEach(key => {
            const errors = result.data[key];
            if (Array.isArray(errors)) {
                errorMessages.push(`${key}: ${errors.join(', ')}`);
            } else if (typeof errors === 'string') {
                errorMessages.push(`${key}: ${errors}`);
            } else if (typeof errors === 'object') {
                errorMessages.push(`${key}: ${JSON.stringify(errors)}`);
            }
        });
        
        if (errorMessages.length > 0) {
            return errorMessages.join('<br>');
        }
        
        // Si no hay mensajes específicos pero tenemos datos
        return JSON.stringify(result.data) || 'Error en la autenticación';
    }
    
    // Si hay un código de estado HTTP
    if (result.status) {
        switch(result.status) {
            case 400: return 'Datos de inicio de sesión incorrectos.';
            case 404: return 'El servicio de autenticación no está disponible.';
            case 500: return 'Error interno del servidor. Por favor, intenta más tarde.';
            default: return `Error en la autenticación (${result.status})`;
        }
    }
    
    if (result.message) {
        return result.message;
    }
    
    // Si no podemos determinar un mensaje específico
    return 'Error de autenticación desconocido. Por favor, intenta más tarde.';
} 