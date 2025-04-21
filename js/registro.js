document.addEventListener('DOMContentLoaded', function() {
    // Elementos del formulario
    const registrationForm = document.getElementById('registrationForm');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const termsCheck = document.getElementById('termsCheck');
    
    // Inicializar validación de Bootstrap
    initializeFormValidation();
    
    // Configurar validación de contraseña en tiempo real
    setupPasswordValidation();
    
    // Configurar botones de mostrar/ocultar contraseña
    setupPasswordToggle();
    
    // Configurar modal de éxito
    setupSuccessModal();
});

/**
 * Inicializar validación del formulario
 */
function initializeFormValidation() {
    // Obtener formulario
    const form = document.getElementById('registrationForm');
    
    if(form) {
        // Prevenir envío por defecto
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            } else {
                event.preventDefault();
                showSuccessModal();
            }
            
            form.classList.add('was-validated');
        });
        
        // Validar cédula de identidad con formato venezolano
        const idNumberInput = document.getElementById('idNumber');
        if(idNumberInput) {
            idNumberInput.addEventListener('input', function() {
                const value = this.value.trim();
                const pattern = /^[VvEe]-\d{7,10}$/;
                
                if(pattern.test(value)) {
                    this.setCustomValidity('');
                } else {
                    this.setCustomValidity('Formato inválido. Ejemplo: V-12345678');
                }
            });
        }
        
        // Validar fecha de nacimiento (mayor de 18 años)
        const birthDateInput = document.getElementById('birthDate');
        if(birthDateInput) {
            birthDateInput.addEventListener('change', function() {
                const birthDate = new Date(this.value);
                const today = new Date();
                
                // Calcular edad
                let age = today.getFullYear() - birthDate.getFullYear();
                const monthDiff = today.getMonth() - birthDate.getMonth();
                
                if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
                    age--;
                }
                
                if(age < 18) {
                    this.setCustomValidity('Debes ser mayor de 18 años.');
                } else {
                    this.setCustomValidity('');
                }
            });
        }
        
        // Validar email con formato correcto
        const emailInput = document.getElementById('email');
        if(emailInput) {
            emailInput.addEventListener('input', function() {
                const value = this.value.trim();
                const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
                
                if(pattern.test(value)) {
                    this.setCustomValidity('');
                } else {
                    this.setCustomValidity('Por favor, ingresa un correo electrónico válido.');
                }
            });
        }
        
        // Validar número de teléfono con formato venezolano
        const phoneInput = document.getElementById('phone');
        if(phoneInput) {
            phoneInput.addEventListener('input', function() {
                const value = this.value.trim();
                // Formato flexible para teléfonos venezolanos
                const pattern = /^\+?58?\s?[24]\d{2}[\s-]?\d{7}$|^\+?58?\s?[45]\d{2}[\s-]?\d{7}$/;
                
                if(pattern.test(value) || value === '') {
                    this.setCustomValidity('');
                } else {
                    this.setCustomValidity('Formato inválido. Ejemplo: +58 414-1234567');
                }
            });
        }
        
        // Validar teléfono alternativo (opcional)
        const altPhoneInput = document.getElementById('altPhone');
        if(altPhoneInput) {
            altPhoneInput.addEventListener('input', function() {
                const value = this.value.trim();
                
                // Si está vacío, es válido (campo opcional)
                if(value === '') {
                    this.setCustomValidity('');
                    return;
                }
                
                // Mismo patrón que el teléfono principal
                const pattern = /^\+?58?\s?[24]\d{2}[\s-]?\d{7}$|^\+?58?\s?[45]\d{2}[\s-]?\d{7}$/;
                
                if(pattern.test(value)) {
                    this.setCustomValidity('');
                } else {
                    this.setCustomValidity('Formato inválido. Ejemplo: +58 414-1234567');
                }
            });
        }
        
        // Validar ingresos mínimos
        const incomeInput = document.getElementById('monthlyIncome');
        if(incomeInput) {
            incomeInput.addEventListener('input', function() {
                const value = parseFloat(this.value);
                
                if(value < 300) {
                    this.setCustomValidity('Los ingresos mínimos deben ser al menos $300 USD.');
                } else {
                    this.setCustomValidity('');
                }
            });
        }
    }
}

/**
 * Configurar validación de contraseña en tiempo real
 */
function setupPasswordValidation() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    
    if(password && confirmPassword) {
        // Verificar requisitos de contraseña
        password.addEventListener('input', function() {
            const value = this.value;
            
            // Verificar longitud
            const lengthValid = value.length >= 8;
            // Verificar mayúscula
            const uppercaseValid = /[A-Z]/.test(value);
            // Verificar minúscula
            const lowercaseValid = /[a-z]/.test(value);
            // Verificar número
            const numberValid = /[0-9]/.test(value);
            
            // Actualizar indicadores visuales
            updatePasswordIndicator('length-check', lengthValid);
            updatePasswordIndicator('uppercase-check', uppercaseValid);
            updatePasswordIndicator('lowercase-check', lowercaseValid);
            updatePasswordIndicator('number-check', numberValid);
            
            // Validez general de la contraseña
            if(lengthValid && uppercaseValid && lowercaseValid && numberValid) {
                this.setCustomValidity('');
            } else {
                this.setCustomValidity('La contraseña no cumple con los requisitos');
            }
            
            // Verificar coincidencia si ya hay texto en confirmPassword
            if(confirmPassword.value) {
                checkPasswordMatch();
            }
        });
        
        // Verificar que las contraseñas coincidan
        confirmPassword.addEventListener('input', checkPasswordMatch);
        
        function checkPasswordMatch() {
            if(password.value === confirmPassword.value) {
                confirmPassword.setCustomValidity('');
            } else {
                confirmPassword.setCustomValidity('Las contraseñas no coinciden');
            }
        }
    }
}

/**
 * Actualizar indicador visual de requisito de contraseña
 */
function updatePasswordIndicator(id, isValid) {
    const indicator = document.getElementById(id);
    
    if(indicator) {
        // Reemplazar icono
        const oldIcon = indicator.querySelector('i');
        const newIcon = document.createElement('i');
        
        if(isValid) {
            newIcon.className = 'fas fa-check-circle me-1';
            indicator.classList.remove('text-muted');
            indicator.classList.add('text-success');
        } else {
            newIcon.className = 'fas fa-times-circle me-1';
            indicator.classList.remove('text-success');
            indicator.classList.add('text-muted');
        }
        
        if(oldIcon) {
            indicator.replaceChild(newIcon, oldIcon);
        }
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
 * Configurar modal de registro exitoso
 */
function setupSuccessModal() {
    const goToProfileBtn = document.getElementById('goToProfileBtn');
    
    if(goToProfileBtn) {
        goToProfileBtn.addEventListener('click', function() {
            // Redireccionar a la página principal (simulación de perfil)
            window.location.href = 'index.html';
        });
    }
}

/**
 * Mostrar modal de registro exitoso
 */
function showSuccessModal() {
    const modal = new bootstrap.Modal(document.getElementById('registrationSuccessModal'));
    modal.show();
} 