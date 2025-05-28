document.addEventListener('DOMContentLoaded', function() {
    // Elementos del formulario
    const loginForm = document.getElementById('loginForm');
    
    // Verificar parámetros de URL (para mostrar mensajes después del registro)
    checkUrlParams();
    
    // Inicializar validación de Bootstrap
    if (loginForm) {
        initializeFormValidation();
    }
    
    // Configurar botones de mostrar/ocultar contraseña
    setupPasswordToggle();
    
    // Manejar la redirección después del inicio de sesión
    setupLoginRedirection();
});

/**
 * Verificar parámetros de URL para mostrar mensajes
 */
function checkUrlParams() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Verificar si el usuario acaba de registrarse
    if (urlParams.get('registered') === 'true') {
        const email = urlParams.get('email');
        showSuccessMessage(`¡Registro exitoso! Ahora puedes iniciar sesión${email ? ' con ' + email : ''}.`);
        
        // Prellenar el campo de email si está disponible
        const emailInput = document.getElementById('email');
        if (emailInput && email) {
            emailInput.value = email;
        }
    }
    
    // Verificar si hubo un error de login anterior
    if (urlParams.get('error') === 'auth') {
        showErrorMessage('Credenciales incorrectas. Por favor, verifica tu email y contraseña.');
    }
}

/**
 * Inicializar validación del formulario
 */
function initializeFormValidation() {
    const form = document.getElementById('loginForm');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        event.stopPropagation();
        
        if (form.checkValidity()) {
            // Recopilar datos del formulario
            loginUser(form);
        } else {
            form.classList.add('was-validated');
        }
    });
}

/**
 * Iniciar sesión del usuario
 */
async function loginUser(form) {
    // Mostrar indicador de carga
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...';
    
    try {
        // Obtener email (usado como username) y contraseña
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        
        // Validaciones más estrictas
        if (!email) {
            showErrorMessage('Por favor, ingrese su correo electrónico');
            return;
        }
        
        if (!password) {
            showErrorMessage('Por favor, ingrese su contraseña');
            return;
        }
        
        // Validar formato de email
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailRegex.test(email)) {
            showErrorMessage('Por favor, ingrese un correo electrónico válido');
            return;
        }
        
        console.log("Iniciando sesión con email:", email);
        
        // Llamar a la API para iniciar sesión
        // Verificar que API esté disponible con reintentos
        let apiCheckAttempts = 0;
        while (typeof API === "undefined" && apiCheckAttempts < 10) {
            console.log("Esperando a que API esté disponible...", apiCheckAttempts + 1);
            await new Promise(resolve => setTimeout(resolve, 200));
            apiCheckAttempts++;
        }
        
        if (typeof API === "undefined") {
            console.error("API no se cargó después de esperar");
            showErrorMessage("Error del sistema. Por favor, recarga la página.");
            return;
        }
        
        console.log("API disponible, procediendo con login");
        const result = await API.users.login(email, password);
        
        if (result && result.success) {
            console.log("Inicio de sesión exitoso");
            
            // Redirigir a la página principal o dashboard
            redirectAfterLogin();
        } else {
            console.error("Error de inicio de sesión:", result);
            
            // Mostrar mensaje de error específico
            if (result && result.data) {
                // Formatear errores para mostrarlos de manera amigable
                const errorMessages = [];
                Object.keys(result.data).forEach(key => {
                    if (Array.isArray(result.data[key])) {
                        errorMessages.push(`${key}: ${result.data[key].join(', ')}`);
                    } else if (typeof result.data[key] === 'string') {
                        errorMessages.push(`${key}: ${result.data[key]}`);
                    }
                });
                
                if (errorMessages.length > 0) {
                    showErrorMessage(errorMessages.join('<br>'));
                } else if (result.data.detail) {
                    showErrorMessage(result.data.detail);
                } else {
                    showErrorMessage('Error de autenticación. Verifica tus credenciales.');
                }
            } else {
                showErrorMessage('Ocurrió un error durante el inicio de sesión. Por favor, intenta de nuevo.');
            }
        }
    } catch (error) {
        console.error('Error durante el inicio de sesión:', error);
        showErrorMessage('Ocurrió un error durante el inicio de sesión. Por favor, intenta de nuevo.');
    } finally {
        // Restaurar botón
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
    }
}

/**
 * Configurar botones de mostrar/ocultar contraseña
 */
function setupPasswordToggle() {
    const toggleButtons = document.querySelectorAll('.toggle-password');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            
            // Cambiar tipo de input
            if(input.type === 'password') {
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
 * Configurar la redirección después del inicio de sesión
 */
function setupLoginRedirection() {
    // Verificar si hay un parámetro redirect en la URL
    const urlParams = new URLSearchParams(window.location.search);
    const redirectUrl = urlParams.get('redirect');
    
    // Si ya hay un usuario autenticado, redirigir
    if (typeof API !== "undefined" && API.users.isAuthenticated()) {
        redirectAfterLogin(redirectUrl);
    }
}

/**
 * Redirigir después del inicio de sesión
 */
function redirectAfterLogin(redirectUrl) {
    // Si hay una URL de redirección específica, usarla
    if (redirectUrl) {
        // Si es 'dashboard', redirigir al dashboard
        if (redirectUrl === 'dashboard') {
            window.location.href = '/dashboard.html';
            return;
        }
        // Si es 'financing', guardar el cálculo pendiente y redirigir al catálogo
        if (redirectUrl === 'financing') {
            // TODO: Recuperar el cálculo pendiente del sessionStorage
            window.location.href = '/catalogo.html';
            return;
        }
        // Cualquier otra URL, usarla directamente
        window.location.href = redirectUrl;
        return;
    }
    
    // Redirección predeterminada al dashboard
    window.location.href = '/dashboard.html';
}

/**
 * Mostrar mensaje de éxito
 */
function showSuccessMessage(message) {
    showMessage(message, 'success');
}

/**
 * Mostrar mensaje de error
 */
function showErrorMessage(message) {
    showMessage(message, 'danger');
}

/**
 * Mostrar mensaje en el contenedor de alertas
 */
function showMessage(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) {
        // Crear contenedor de alertas si no existe
        const container = document.createElement('div');
        container.id = 'alert-container';
        container.className = 'mb-4';
        
        const form = document.getElementById('loginForm');
        if (form) {
            form.parentNode.insertBefore(container, form);
        }
    }
    
    // Mostrar mensaje
    const container = document.getElementById('alert-container') || document.createElement('div');
    container.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
        </div>
    `;
}

/**
 * Extraer mensaje de error de la respuesta de la API
 */
function getErrorMessage(result) {
    if (!result) return 'Error desconocido';
    
    if (result.data) {
        // Si hay un mensaje de detalle, mostrarlo
        if (result.data.detail) {
            return result.data.detail;
        }
        
        // Si no, construir mensaje a partir de los errores
        const errorMessages = [];
        
        // Recorrer todos los campos con errores
        Object.keys(result.data).forEach(key => {
            const errors = result.data[key];
            if (Array.isArray(errors)) {
                errorMessages.push(`${key}: ${errors.join(', ')}`);
            } else if (typeof errors === 'string') {
                errorMessages.push(`${key}: ${errors}`);
            }
        });
        
        return errorMessages.join('<br>') || 'Error en el formulario';
    }
    
    // Mensaje genérico para errores no controlados
    if (result.status === 401) {
        return 'Email o contraseña incorrectos';
    }
    
    return result.message || 'Error desconocido';
} 