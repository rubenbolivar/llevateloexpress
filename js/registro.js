/**
 * Registro.js - Controlador para la página de registro
 * Utiliza el módulo Auth para gestionar el registro de usuarios
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del formulario
    const registrationForm = document.getElementById('registrationForm');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const submitButton = registrationForm ? registrationForm.querySelector('button[type="submit"]') : null;
    const alertContainer = document.getElementById('alert-container');
    
    // Inicializar validaciones
    initializeFormValidation();
    setupPasswordValidation();
    setupPasswordToggle();
    setupSuccessModal();
    
    /**
     * Inicializa la validación del formulario
     */
    function initializeFormValidation() {
        if (!registrationForm) return;
        
        // Manejar envío del formulario
        registrationForm.addEventListener('submit', handleRegistrationSubmit);
        
        // Validar formato de cédula
        const idNumberInput = document.getElementById('idNumber');
        if (idNumberInput) {
            idNumberInput.addEventListener('input', function() {
                const value = this.value.trim();
                const pattern = /^[VvEe]-\d{7,10}$/;
                
                if (pattern.test(value)) {
                    this.setCustomValidity('');
                } else {
                    this.setCustomValidity('Formato inválido. Ejemplo: V-12345678');
                }
            });
        }
        
        // Validar email con formato correcto
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.addEventListener('input', function() {
                const value = this.value.trim();
                const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
                
                if (pattern.test(value)) {
                    this.setCustomValidity('');
                } else {
                    this.setCustomValidity('Por favor, ingresa un correo electrónico válido.');
                }
            });
        }
        
        // Validar número de teléfono
        const phoneInput = document.getElementById('phone');
        if (phoneInput) {
            phoneInput.addEventListener('input', function() {
                const value = this.value.trim();
                
                // VALIDACIÓN ORIGINAL PRESERVADA: Formato internacional estándar
                // Acepta códigos de país de 1-4 dígitos seguidos de 7-12 dígitos
                const originalPattern = /^\+[1-9]\d{0,3}\s?\d{7,12}$/;
                
                if (originalPattern.test(value) || value === '') {
                    // EXTENSIÓN: Verificación adicional para números específicos que puedan fallar
                    if (value !== '' && !isPhoneValidForRegistration(value)) {
                        this.setCustomValidity('Número no válido para registro. Contacta soporte si persiste el problema.');
                    } else {
                        this.setCustomValidity('');
                    }
                } else {
                    this.setCustomValidity('Formato inválido. Ejemplo: +52 5539794679, +58 4141234567');
                }
            });
        }
    }
    
    /**
     * Validación adicional específica para números que podrían tener problemas
     * Esta función NO reemplaza la validación original, solo la complementa
     * ACEPTA NÚMEROS DE CUALQUIER PAÍS
     */
    function isPhoneValidForRegistration(phone) {
        // Si es un número de Venezuela, usar validación original (siempre válido)
        if (phone.startsWith('+58')) {
            return true;
        }
        
        // Para cualquier número internacional
        const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
        const numberPart = cleanPhone.slice(1);
        
        // Verificaciones básicas según estándar ITU-T E.164
        if (!/^\d+$/.test(numberPart)) {
            return false; // Solo dígitos después del +
        }
        
        if (numberPart.length < 7 || numberPart.length > 15) {
            return false; // Longitud válida internacional
        }
        
        // El primer dígito no puede ser 0 (estándar internacional)
        if (numberPart.charAt(0) === '0') {
            return false;
        }
        
        // Validación por rangos de códigos de país válidos
        const countryCode = getCountryCodeFromNumber(numberPart);
        
        if (countryCode && isValidCountryCode(countryCode)) {
            return true;
        }
        
        return false;
    }
    
    /**
     * Extrae el código de país de un número
     */
    function getCountryCodeFromNumber(numberPart) {
        // Códigos de país pueden ser de 1-4 dígitos
        for (let i = 1; i <= 4 && i <= numberPart.length; i++) {
            const potentialCode = numberPart.substring(0, i);
            if (isValidCountryCode(potentialCode)) {
                return potentialCode;
            }
        }
        return null;
    }
    
    /**
     * Verifica si un código es un código de país válido
     * Basado en la lista oficial ITU-T E.164
     */
    function isValidCountryCode(code) {
        // Códigos de país de 1 dígito (Zona 1: NANP)
        if (code === '1') return true;
        
        // Códigos de país de 2 dígitos
        const twoDigitCodes = [
            '20', '27', '30', '31', '32', '33', '34', '36', '39', '40', '41', 
            '43', '44', '45', '46', '47', '48', '49', '51', '52', '53', '54', 
            '55', '56', '57', '58', '60', '61', '62', '63', '64', '65', '66', 
            '81', '82', '84', '86', '90', '91', '92', '93', '94', '95', '98'
        ];
        if (twoDigitCodes.includes(code)) return true;
        
        // Códigos de país de 3 dígitos
        const threeDigitCodes = [
            '212', '213', '216', '218', '220', '221', '222', '223', '224', '225',
            '226', '227', '228', '229', '230', '231', '232', '233', '234', '235',
            '236', '237', '238', '239', '240', '241', '242', '243', '244', '245',
            '246', '247', '248', '249', '250', '251', '252', '253', '254', '255',
            '256', '257', '258', '260', '261', '262', '263', '264', '265', '266',
            '267', '268', '269', '290', '291', '297', '298', '299', '350', '351',
            '352', '353', '354', '355', '356', '357', '358', '359', '370', '371',
            '372', '373', '374', '375', '376', '377', '378', '380', '381', '382',
            '383', '385', '386', '387', '389', '420', '421', '423', '500', '501',
            '502', '503', '504', '505', '506', '507', '508', '509', '590', '591',
            '592', '593', '594', '595', '596', '597', '598', '599', '670', '672',
            '673', '674', '675', '676', '677', '678', '679', '680', '681', '682',
            '683', '684', '685', '686', '687', '688', '689', '690', '691', '692'
        ];
        if (threeDigitCodes.includes(code)) return true;
        
        // Códigos de país de 4 dígitos (pocos casos especiales)
        const fourDigitCodes = ['1242', '1246', '1264', '1268', '1284', '1340', '1345', '1441', '1473', '1649', '1664', '1670', '1671', '1684', '1721', '1758', '1767', '1784', '1787', '1809', '1829', '1849', '1868', '1869', '1876', '1939'];
        if (fourDigitCodes.includes(code)) return true;
        
        return false;
    }
    
    /**
     * Configura la validación de contraseña en tiempo real
     */
    function setupPasswordValidation() {
        if (!passwordInput || !confirmPasswordInput) return;
        
        // Verificar requisitos de contraseña en tiempo real
        passwordInput.addEventListener('input', function() {
            const value = this.value;
            
            // Verificar criterios
            const lengthValid = value.length >= 8;
            const uppercaseValid = /[A-Z]/.test(value);
            const lowercaseValid = /[a-z]/.test(value);
            const numberValid = /[0-9]/.test(value);
            
            // Actualizar indicadores visuales
            updatePasswordIndicator('length-check', lengthValid);
            updatePasswordIndicator('uppercase-check', uppercaseValid);
            updatePasswordIndicator('lowercase-check', lowercaseValid);
            updatePasswordIndicator('number-check', numberValid);
            
            // Validar contraseña completa
            if (lengthValid && uppercaseValid && lowercaseValid && numberValid) {
                this.setCustomValidity('');
            } else {
                this.setCustomValidity('La contraseña no cumple con los requisitos');
            }
            
            // Verificar confirmación si ya hay texto
            if (confirmPasswordInput.value) {
                checkPasswordMatch();
            }
        });
        
        // Verificar que las contraseñas coinciden
        confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    }
    
    /**
     * Verifica si las contraseñas coinciden
     */
    function checkPasswordMatch() {
        if (passwordInput.value === confirmPasswordInput.value) {
            confirmPasswordInput.setCustomValidity('');
        } else {
            confirmPasswordInput.setCustomValidity('Las contraseñas no coinciden');
        }
    }
    
    /**
     * Actualiza el indicador visual de requisito de contraseña
     */
    function updatePasswordIndicator(id, isValid) {
        const indicator = document.getElementById(id);
        if (!indicator) return;
        
        // Obtener o crear icono
        let icon = indicator.querySelector('i');
        if (!icon) {
            icon = document.createElement('i');
            indicator.prepend(icon);
        }
        
        // Actualizar clase del icono y del indicador
        if (isValid) {
            icon.className = 'fas fa-check-circle me-1';
            indicator.classList.remove('text-muted');
            indicator.classList.add('text-success');
        } else {
            icon.className = 'fas fa-times-circle me-1';
            indicator.classList.remove('text-success');
            indicator.classList.add('text-muted');
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
     * Configura el modal de registro exitoso
     */
    function setupSuccessModal() {
        const modal = document.getElementById('registrationSuccessModal');
        if (!modal) return;
        
        const goToProfileBtn = document.getElementById('goToProfileBtn');
        if (goToProfileBtn) {
            goToProfileBtn.addEventListener('click', function() {
                window.location.href = 'index.html';
            });
        }
    }
    
    /**
     * Muestra el modal de registro exitoso
     */
    function showSuccessModal(email) {
        const modal = new bootstrap.Modal(document.getElementById('registrationSuccessModal'));
        
        // Configurar redirección al hacer clic en el botón del modal
        const goToProfileBtn = document.getElementById('goToProfileBtn');
        if (goToProfileBtn) {
            goToProfileBtn.textContent = 'Iniciar Sesión';
            goToProfileBtn.onclick = function() {
                window.location.href = 'login.html?registered=true&email=' + encodeURIComponent(email);
            };
        }
        
        modal.show();
    }
    
    /**
     * Maneja el envío del formulario de registro
     */
    async function handleRegistrationSubmit(event) {
        event.preventDefault();
        
        // Validar formulario
        if (!registrationForm.checkValidity()) {
            registrationForm.classList.add('was-validated');
            return;
        }
        
        // Mostrar indicador de carga
        const originalBtnText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...';
        
        try {
            // Recopilar datos para el registro
            const userData = {
                email: document.getElementById('email').value,
                password: document.getElementById('password').value,
                password2: document.getElementById('confirmPassword').value,
                first_name: document.getElementById('firstName').value,
                last_name: document.getElementById('lastName').value,
                phone: document.getElementById('phone').value,
                identity_document: document.getElementById('idNumber').value
            };
            
            // Realizar registro
            const result = await Auth.register(userData);
            
            if (result.success) {
                // Registro exitoso
                console.log('Registro exitoso:', result.data);
                
                // Mostrar modal de éxito - Evitar que la página se redirija antes de mostrarlo
                setTimeout(() => {
                    showSuccessModal(userData.email);
                }, 500);
                
                // Evitar que el evento DOMContentLoaded de auth.js redirija automáticamente
                // al detectar un token válido en localStorage
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
            } else {
                // Error en registro
                showErrorMessage(getErrorMessage(result));
            }
        } catch (error) {
            console.error('Error durante el registro:', error);
            showErrorMessage('Error de conexión. Por favor, intente de nuevo más tarde.');
        } finally {
            // Restaurar botón
            submitButton.disabled = false;
            submitButton.innerHTML = originalBtnText;
        }
    }
    
    /**
     * Muestra un mensaje de error
     */
    function showErrorMessage(message) {
        if (!alertContainer) {
            console.warn('No se encontró contenedor de alertas');
            return;
        }
        
        alertContainer.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
            </div>
        `;
        
        // Scroll hacia el mensaje de error
        alertContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
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
        
        return result.message || 'Error desconocido';
    }
}); 