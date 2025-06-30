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

// Elementos del DOM
const profileForm = document.getElementById('profileForm');
const loadingOverlay = document.querySelector('.loading');
const successToast = new bootstrap.Toast(document.getElementById('successToast'));
const errorToast = new bootstrap.Toast(document.getElementById('errorToast'));

/**
 * Carga los datos del perfil del usuario
 */
async function loadProfile() {
    try {
        showLoading(true);
        
        const result = await Auth.fetch('/api/users/profile/');
        
        if (result.success && result.data) {
            currentProfile = result.data;
            populateForm(result.data);
            updateProfileSummary(result.data);
            calculateProfileCompleteness(result.data);
        } else {
            console.error('Error cargando perfil:', result);
            showError('Error al cargar los datos del perfil');
        }
    } catch (error) {
        console.error('Error en loadProfile:', error);
        showError('Error de conexión al cargar el perfil');
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
        showLoading(true);
        
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
function showLoading(show) {
    if (show) {
        loadingOverlay.classList.add('show');
    } else {
        loadingOverlay.classList.remove('show');
    }
}

/**
 * Muestra un mensaje de éxito
 */
function showSuccess(message) {
    const toastBody = document.querySelector('#successToast .toast-body');
    toastBody.textContent = message;
    successToast.show();
}

/**
 * Muestra un mensaje de error
 */
function showError(message) {
    const toastBody = document.querySelector('#errorToast .toast-body');
    toastBody.textContent = message;
    errorToast.show();
}

/**
 * Maneja el envío del formulario
 */
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

/**
 * Maneja el logout desde la página de perfil
 */
document.getElementById('logoutBtn').addEventListener('click', function(e) {
    e.preventDefault();
    if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
        Auth.logout();
    }
});

// Inicializar página cuando se carga el DOM
document.addEventListener('DOMContentLoaded', function() {
    // Verificar autenticación
    if (!Auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return;
    }
    
    // Cargar datos del perfil
    loadProfile();
});

// Exponer funciones globalmente para uso desde HTML
window.ProfileManager = {
    loadProfile,
    saveProfile,
    showSuccess,
    showError
};