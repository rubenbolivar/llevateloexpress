/**
 * Gestión de Perfil de Usuario - LlévateloExpress
 * 
 * Este módulo maneja todas las operaciones del perfil de usuario:
 * - Carga de datos del perfil
 * - Actualización de información personal
 * - Validación de formularios
 * - Cálculo de completitud del perfil
 */

// Variables globales
let currentProfile = null;

// Elementos del DOM (se inicializan cuando el DOM esté listo)
let profileForm;
let loadingOverlay;
let successToast;
let errorToast;

/**
 * Carga los datos del perfil del usuario
 */
async function loadProfile() {
    try {
        showLoading(true, 'Cargando perfil...');
        
        // Verificar que Auth.fetch existe
        if (!Auth || !Auth.fetch) {
            throw new Error('Auth.fetch no está disponible');
        }
        
        const result = await Auth.fetch('/api/users/profile/');
        
        if (result.success && result.data) {
            currentProfile = result.data;
            populateForm(result.data);
            updateProfileSummary(result.data);
            calculateProfileCompleteness(result.data);
        } else {
            console.error('Error cargando perfil:', result);
            showError('Error al cargar los datos del perfil: ' + (result.message || 'Error desconocido'));
        }
    } catch (error) {
        console.error('Error en loadProfile:', error);
        showError('Error de conexión al cargar el perfil: ' + error.message);
    } finally {
        showLoading(false);
    }
}

/**
 * Llena el formulario con los datos del perfil
 */
function populateForm(profileData) {
    const { user } = profileData;
    
    // Datos del usuario
    document.getElementById('firstName').value = user.first_name || '';
    document.getElementById('lastName').value = user.last_name || '';
    document.getElementById('email').value = user.email || '';
    
    // Datos del customer
    document.getElementById('phone').value = profileData.phone || '';
    document.getElementById('address').value = profileData.address || '';
    document.getElementById('identityDocument').value = profileData.identity_document || '';
    document.getElementById('dateOfBirth').value = profileData.date_of_birth || '';
    document.getElementById('occupation').value = profileData.occupation || '';
    document.getElementById('monthlyIncome').value = profileData.monthly_income || '';
}

/**
 * Actualiza el resumen del perfil en la barra lateral
 */
function updateProfileSummary(profileData) {
    const { user } = profileData;
    
    // Nombre completo
    const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'Usuario';
    document.getElementById('profileName').textContent = fullName;
    document.getElementById('profileEmail').textContent = user.email || '';
    
    // Estado de verificación
    const verificationBadge = document.getElementById('verificationStatus');
    if (profileData.verified) {
        verificationBadge.textContent = 'Verificado';
        verificationBadge.className = 'badge bg-success';
    } else {
        verificationBadge.textContent = 'No Verificado';
        verificationBadge.className = 'badge bg-secondary';
    }
    
    // Actualizar email en navbar
    const navbarEmail = document.getElementById('userEmail');
    if (navbarEmail) {
        navbarEmail.textContent = user.email || 'Usuario';
    }
}

/**
 * Calcula y muestra el porcentaje de completitud del perfil
 */
function calculateProfileCompleteness(profileData) {
    const { user } = profileData;
    
    const requiredFields = [
        { field: user.first_name, name: 'Nombre', element: 'firstName' },
        { field: user.last_name, name: 'Apellido', element: 'lastName' },
        { field: profileData.phone, name: 'Teléfono', element: 'phone' },
        { field: profileData.identity_document, name: 'Documento de identidad', element: 'identityDocument' }
    ];
    
    const optionalFields = [
        { field: profileData.address, name: 'Dirección' },
        { field: profileData.date_of_birth, name: 'Fecha de nacimiento' },
        { field: profileData.occupation, name: 'Ocupación' },
        { field: profileData.monthly_income, name: 'Ingresos mensuales' }
    ];
    
    // Calcular campos completados
    const completedRequired = requiredFields.filter(item => item.field && item.field.trim() !== '').length;
    const completedOptional = optionalFields.filter(item => item.field && item.field.toString().trim() !== '').length;
    
    const totalFields = requiredFields.length + optionalFields.length;
    const completedFields = completedRequired + completedOptional;
    const completeness = Math.round((completedFields / totalFields) * 100);
    
    // Actualizar UI
    document.getElementById('profileCompleteness').textContent = `${completeness}%`;
    
    // Actualizar lista de campos requeridos
    const requiredFieldsList = document.getElementById('requiredFields');
    requiredFieldsList.innerHTML = '';
    
    requiredFields.forEach(item => {
        const isCompleted = item.field && item.field.trim() !== '';
        const li = document.createElement('li');
        li.innerHTML = `
            <i class="fas fa-circle ${isCompleted ? 'text-success' : 'text-danger'} me-2"></i>
            ${item.name}
        `;
        requiredFieldsList.appendChild(li);
    });
}

/**
 * Guarda los cambios del perfil
 */
async function saveProfile(formData) {
    try {
        showLoading(true, 'Guardando cambios...');
        
        // Preparar datos para enviar
        const profileData = {
            user: {
                first_name: formData.get('firstName'),
                last_name: formData.get('lastName')
            },
            phone: formData.get('phone'),
            address: formData.get('address'),
            identity_document: formData.get('identityDocument'),
            date_of_birth: formData.get('dateOfBirth') || null,
            occupation: formData.get('occupation'),
            monthly_income: formData.get('monthlyIncome') || null
        };
        
        // Enviar actualización
        const result = await Auth.fetch('/api/users/profile/', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
        
        if (result.success) {
            currentProfile = result.data;
            updateProfileSummary(result.data);
            calculateProfileCompleteness(result.data);
            showSuccess('Perfil actualizado correctamente');
        } else {
            console.error('Error guardando perfil:', result);
            showError('Error al guardar los cambios del perfil');
        }
    } catch (error) {
        console.error('Error en saveProfile:', error);
        showError('Error de conexión al guardar el perfil');
    } finally {
        showLoading(false);
    }
}

/**
 * Valida los campos requeridos del formulario
 */
function validateForm(formData) {
    const errors = [];
    
    if (!formData.get('firstName')?.trim()) {
        errors.push('El nombre es requerido');
    }
    
    if (!formData.get('lastName')?.trim()) {
        errors.push('El apellido es requerido');
    }
    
    if (!formData.get('phone')?.trim()) {
        errors.push('El teléfono es requerido');
    }
    
    if (!formData.get('identityDocument')?.trim()) {
        errors.push('El documento de identidad es requerido');
    }
    
    // Validar formato de teléfono (básico)
    const phone = formData.get('phone')?.trim();
    if (phone && !/^[\d\s\-\+\(\)]+$/.test(phone)) {
        errors.push('El formato del teléfono no es válido');
    }
    
    // Validar ingresos mensuales si se proporciona
    const income = formData.get('monthlyIncome');
    if (income && (isNaN(income) || parseFloat(income) < 0)) {
        errors.push('Los ingresos mensuales deben ser un número válido');
    }
    
    return errors;
}

/**
 * Muestra/oculta el overlay de carga
 */
function showLoading(show, message = 'Cargando...') {
    if (!loadingOverlay) {
        console.error('loadingOverlay no encontrado');
        return;
    }
    
    // Actualizar texto del loading
    const loadingText = document.getElementById('loadingText');
    if (loadingText) {
        loadingText.textContent = message;
    }
    
    if (show) {
        loadingOverlay.style.display = 'flex';
        loadingOverlay.style.visibility = 'visible';
    } else {
        loadingOverlay.style.display = 'none';
        loadingOverlay.style.visibility = 'hidden';
    }
}

/**
 * Muestra un mensaje de éxito
 */
function showSuccess(message) {
    console.log('SUCCESS:', message);
    const toastBody = document.querySelector('#successToast .toast-body');
    if (toastBody) {
        toastBody.textContent = message;
    }
    if (successToast) {
        successToast.show();
    } else {
        alert('Éxito: ' + message);
    }
}

/**
 * Muestra un mensaje de error
 */
function showError(message) {
    console.error('ERROR:', message);
    const toastBody = document.querySelector('#errorToast .toast-body');
    if (toastBody) {
        toastBody.textContent = message;
    }
    if (errorToast) {
        errorToast.show();
    } else {
        alert('Error: ' + message);
    }
}

/**
 * Configura los event listeners
 */
function setupEventListeners() {
    // Manejar envío del formulario
    if (profileForm) {
        profileForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(profileForm);
            
            // Validar formulario
            const errors = validateForm(formData);
            if (errors.length > 0) {
                showError(errors.join('. '));
                return;
            }
            
            // Guardar perfil
            await saveProfile(formData);
        });
    }
    
    // Manejar logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
                Auth.logout();
            }
        });
    }
}

// Inicializar página cuando se carga el DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado, inicializando perfil...');
    
    // Inicializar elementos del DOM
    profileForm = document.getElementById('profileForm');
    loadingOverlay = document.querySelector('.loading');
    
    // Verificar elementos críticos
    if (!profileForm) {
        console.error('profileForm no encontrado');
        return;
    }
    if (!loadingOverlay) {
        console.error('loadingOverlay no encontrado');
        return;
    }
    
    // Inicializar toasts
    const successToastElement = document.getElementById('successToast');
    const errorToastElement = document.getElementById('errorToast');
    
    if (successToastElement) {
        successToast = new bootstrap.Toast(successToastElement);
    }
    if (errorToastElement) {
        errorToast = new bootstrap.Toast(errorToastElement);
    }
    
    // Verificar autenticación
    if (!Auth || !Auth.isAuthenticated()) {
        console.log('Usuario no autenticado, redirigiendo...');
        window.location.href = '/login.html';
        return;
    }
    
    console.log('Todos los elementos inicializados, configurando event listeners...');
    // Configurar event listeners
    setupEventListeners();
    
    console.log('Obteniendo token CSRF...');
    // Obtener token CSRF antes de cargar perfil
    Auth.fetchCsrfToken().then(() => {
        console.log('Token CSRF obtenido, cargando perfil...');
        loadProfile();
    }).catch(error => {
        console.error('Error obteniendo token CSRF:', error);
        showError('Error de configuración. Por favor recarga la página.');
    });
});

// Exponer funciones globalmente para uso desde HTML
window.ProfileManager = {
    loadProfile,
    saveProfile,
    showSuccess,
    showError
};