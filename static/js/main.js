document.addEventListener('DOMContentLoaded', function() {
    // Configurar navbar activa según la página actual
    setupActiveNavItem();
    
    // Configurar manejo de contraseñas (para página de registro)
    setupPasswordVisibility();
    setupPasswordStrength();
    
    // Configurar formulario de registro (para página de registro)
    setupRegistrationForm();
    
    // Inicializar tooltips de Bootstrap
    initTooltips();
    
    // Comprobar mensajes por URL
    checkUrlMessages();
});

/**
 * Configurar item activo en la navegación según la página actual
 */
function setupActiveNavItem() {
    const currentPage = window.location.pathname.split('/').pop();
    
    // Remover clase activa de todos los elementos de navegación
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Agregar clase activa al elemento correspondiente
    let activeLink;
    
    switch(currentPage) {
        case '':
        case 'index.html':
            activeLink = document.querySelector('.navbar-nav .nav-link[href="index.html"]');
            break;
        case 'catalogo.html':
            activeLink = document.querySelector('.navbar-nav .nav-link[href="catalogo.html"]');
            break;
        case 'planes.html':
            activeLink = document.querySelector('.navbar-nav .nav-link[href="planes.html"]');
            break;
        case 'calculadora.html':
            activeLink = document.querySelector('.navbar-nav .nav-link[href="planes.html"]');
            break;
        case 'registro.html':
            // Destacar botón de registro en lugar de item de navegación
            document.querySelector('a.btn[href="registro.html"]').classList.add('active');
            break;
        case 'nosotros.html':
            activeLink = document.querySelector('.navbar-nav .nav-link[href="nosotros.html"]');
            break;
        default:
            // Si es una subcategoría, activar la categoría padre
            if(currentPage.includes('producto')) {
                activeLink = document.querySelector('.navbar-nav .nav-link[href="catalogo.html"]');
            }
    }
    
    if(activeLink) {
        activeLink.classList.add('active');
    }
}

/**
 * Configurar visibilidad de contraseñas
 */
function setupPasswordVisibility() {
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    
    if(togglePasswordButtons.length > 0) {
        togglePasswordButtons.forEach(button => {
            button.addEventListener('click', function() {
                const input = this.previousElementSibling;
                
                // Cambiar tipo de input
                if(input.type === 'password') {
                    input.type = 'text';
                    this.querySelector('i').classList.remove('fa-eye');
                    this.querySelector('i').classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    this.querySelector('i').classList.remove('fa-eye-slash');
                    this.querySelector('i').classList.add('fa-eye');
                }
            });
        });
    }
}

/**
 * Configurar validación de fuerza de contraseña
 */
function setupPasswordStrength() {
    const passwordInput = document.getElementById('password');
    
    if(passwordInput) {
        const lengthCheck = document.getElementById('length-check');
        const uppercaseCheck = document.getElementById('uppercase-check');
        const lowercaseCheck = document.getElementById('lowercase-check');
        const numberCheck = document.getElementById('number-check');
        
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            
            // Verificar longitud
            if(password.length >= 8) {
                lengthCheck.innerHTML = '<i class="fas fa-check-circle me-1"></i> Al menos 8 caracteres';
                lengthCheck.classList.remove('text-muted');
                lengthCheck.classList.add('text-success');
            } else {
                lengthCheck.innerHTML = '<i class="fas fa-times-circle me-1"></i> Al menos 8 caracteres';
                lengthCheck.classList.remove('text-success');
                lengthCheck.classList.add('text-muted');
            }
            
            // Verificar mayúsculas
            if(/[A-Z]/.test(password)) {
                uppercaseCheck.innerHTML = '<i class="fas fa-check-circle me-1"></i> Una mayúscula';
                uppercaseCheck.classList.remove('text-muted');
                uppercaseCheck.classList.add('text-success');
            } else {
                uppercaseCheck.innerHTML = '<i class="fas fa-times-circle me-1"></i> Una mayúscula';
                uppercaseCheck.classList.remove('text-success');
                uppercaseCheck.classList.add('text-muted');
            }
            
            // Verificar minúsculas
            if(/[a-z]/.test(password)) {
                lowercaseCheck.innerHTML = '<i class="fas fa-check-circle me-1"></i> Una minúscula';
                lowercaseCheck.classList.remove('text-muted');
                lowercaseCheck.classList.add('text-success');
            } else {
                lowercaseCheck.innerHTML = '<i class="fas fa-times-circle me-1"></i> Una minúscula';
                lowercaseCheck.classList.remove('text-success');
                lowercaseCheck.classList.add('text-muted');
            }
            
            // Verificar números
            if(/[0-9]/.test(password)) {
                numberCheck.innerHTML = '<i class="fas fa-check-circle me-1"></i> Un número';
                numberCheck.classList.remove('text-muted');
                numberCheck.classList.add('text-success');
            } else {
                numberCheck.innerHTML = '<i class="fas fa-times-circle me-1"></i> Un número';
                numberCheck.classList.remove('text-success');
                numberCheck.classList.add('text-muted');
            }
        });
        
        // Verificar que las contraseñas coincidan
        const confirmPassword = document.getElementById('confirmPassword');
        
        if(confirmPassword) {
            confirmPassword.addEventListener('input', function() {
                if(this.value === passwordInput.value) {
                    this.setCustomValidity('');
                } else {
                    this.setCustomValidity('Las contraseñas no coinciden');
                }
            });
        }
    }
}

/**
 * Configurar formulario de registro
 */
function setupRegistrationForm() {
    const registrationForm = document.getElementById('registrationForm');
    
    if(registrationForm) {
        // Prevenir el envío del formulario
        registrationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Activar validación de Bootstrap
            this.classList.add('was-validated');
            
            // Verificar validez del formulario
            if(this.checkValidity()) {
                // Simulación de registro exitoso
                const successModal = new bootstrap.Modal(document.getElementById('registrationSuccessModal'));
                successModal.show();
                
                // Configurar botón de "Ir a Mi Perfil"
                document.getElementById('goToProfileBtn').addEventListener('click', function() {
                    window.location.href = 'index.html';
                });
            }
        });
    }
}

/**
 * Inicializar tooltips de Bootstrap
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Utilidad para formatear moneda
 */
function formatCurrency(amount) {
    return amount.toLocaleString('es-ES', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

/**
 * Utilidad para formatear fechas
 */
function formatDate(date) {
    if(typeof date === 'string') {
        date = new Date(date);
    }
    
    return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

/**
 * Utilidad para agregar animación de elementos al entrar en viewport
 */
function setupAnimations() {
    // Usar Intersection Observer para animar elementos al entrar en viewport
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if(animatedElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if(entry.isIntersecting) {
                    entry.target.classList.add('slide-in-up');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    }
}

/**
 * Comprobar mensajes del URL y mostrar notificaciones
 */
function checkUrlMessages() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Mensaje de cierre de sesión
    if (urlParams.get('logout') === 'true') {
        showMessage('Has cerrado sesión correctamente.', 'success');
        
        // Limpiar la URL para evitar que el mensaje se muestre después de recargar
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

/**
 * Mostrar un mensaje en la página
 */
function showMessage(message, type = 'info') {
    // Crear el contenedor para el mensaje si no existe
    let alertContainer = document.getElementById('main-alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'main-alert-container';
        alertContainer.className = 'container mt-3';
        
        // Insertar después del header y antes del primer section
        const header = document.querySelector('header');
        header.insertAdjacentElement('afterend', alertContainer);
    }
    
    // Crear el mensaje
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Mostrar el mensaje
    alertContainer.innerHTML = alertHTML;
    
    // Auto-ocultar después de 5 segundos
    setTimeout(() => {
        const alert = alertContainer.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
} 