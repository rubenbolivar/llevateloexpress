/**
 * Login.js - Controlador para la página de inicio de sesión
 * Utiliza el módulo Auth para realizar la autenticación
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del formulario
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const submitButton = loginForm ? loginForm.querySelector('button[type="submit"]') : null;
    const alertContainer = document.getElementById('alert-container');
    
    // Verificar parámetros de URL (para mostrar mensajes después del registro)
    checkUrlParams();
    
    // Inicializar validación del formulario
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }
    
    // Configurar botones de mostrar/ocultar contraseña
    setupPasswordToggle();
    
    /**
     * Maneja el envío del formulario de login
     */
    async function handleLoginSubmit(event) {
        event.preventDefault();
        
        // Validar formulario
        if (!loginForm.checkValidity()) {
            loginForm.classList.add('was-validated');
            return;
        }
        
        // Obtener datos
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        
        // Mostrar indicador de carga
        const originalBtnText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...';
        
        try {
            // Asegurar que tenemos token CSRF antes de intentar login
            await Auth.fetchCsrfToken();
            
            // Intentar login
            const result = await Auth.login(email, password);
            
            if (result.success) {
                // Login exitoso
                showSuccessMessage('Inicio de sesión exitoso. Redirigiendo...');
                
                // Evitar cualquier posible carrera de condición con un pequeño retraso
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1000);
            } else {
                // Error en el login
                showErrorMessage(getErrorMessage(result));
            }
        } catch (error) {
            console.error('Error durante el inicio de sesión:', error);
            showErrorMessage('Error de conexión. Por favor, intente de nuevo más tarde.');
        } finally {
            // Restaurar botón
            submitButton.disabled = false;
            submitButton.innerHTML = originalBtnText;
        }
    }
    
    /**
     * Configura la funcionalidad de mostrar/ocultar contraseña
     */
    function setupPasswordToggle() {
        const toggleButtons = document.querySelectorAll('.toggle-password');
        toggleButtons.forEach(button => {
            button.addEventListener('click', function() {
                const input = this.closest('.input-group').querySelector('input');
                const icon = this.querySelector('i');
                
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
     * Verifica parámetros de URL para mostrar mensajes
     */
    function checkUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        
        // Verificar si el usuario acaba de registrarse
        if (urlParams.get('registered') === 'true') {
            const email = urlParams.get('email');
            showSuccessMessage(`¡Registro exitoso! Ahora puedes iniciar sesión${email ? ' con ' + email : ''}.`);
            
            // Prellenar el campo de email si está disponible
            if (emailInput && email) {
                emailInput.value = email;
            }
        }
        
        // Verificar si hay mensaje de error
        if (urlParams.get('error') === 'auth') {
            showErrorMessage('Credenciales incorrectas. Por favor, verifica tu email y contraseña.');
        }
        
        // Verificar si es logout
        if (urlParams.get('action') === 'logout') {
            showSuccessMessage('Has cerrado sesión correctamente.');
        }
    }
    
    /**
     * Muestra un mensaje de error
     */
    function showErrorMessage(message) {
        showMessage(message, 'danger');
    }
    
    /**
     * Muestra un mensaje de éxito
     */
    function showSuccessMessage(message) {
        showMessage(message, 'success');
    }
    
    /**
     * Muestra un mensaje en el contenedor de alertas
     */
    function showMessage(message, type = 'info') {
        if (!alertContainer) {
            console.warn('No se encontró contenedor de alertas');
            return;
        }
        
        alertContainer.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
            </div>
        `;
    }
    
    /**
     * Extrae mensaje de error de respuesta API
     */
    function getErrorMessage(result) {
        if (!result) return 'Error desconocido';
        
        if (result.data) {
            // Si hay un mensaje de detalle
            if (result.data.detail) {
                return result.data.detail;
            }
            
            // Construir mensaje a partir de campos con error
            const errorMessages = [];
            for (const key in result.data) {
                if (Object.hasOwnProperty.call(result.data, key)) {
                    const errors = result.data[key];
                    if (Array.isArray(errors)) {
                        errorMessages.push(`${key}: ${errors.join(', ')}`);
                    } else if (typeof errors === 'string') {
                        errorMessages.push(`${key}: ${errors}`);
                    }
                }
            }
            
            return errorMessages.join('<br>') || 'Error en el formulario';
        }
        
        // Mensaje genérico para errores no controlados
        if (result.status === 401) {
            return 'Email o contraseña incorrectos';
        }
        
        return result.message || 'Error desconocido';
    }
}); 