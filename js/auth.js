/**
 * auth.js - Módulo para gestionar la autenticación en toda la aplicación
 * Este archivo proporciona funciones para gestionar el estado de autenticación y actualizar la UI en consecuencia
 */

document.addEventListener('DOMContentLoaded', function() {
    // Verificar si el usuario está autenticado al cargar la página
    updateAuthUI();
});

/**
 * Actualiza la interfaz de usuario basada en el estado de autenticación
 */
function updateAuthUI() {
    const isLoggedIn = API && API.users && API.users.isAuthenticated();
    const authContainer = document.querySelector('.collapse .d-flex');
    
    if (!authContainer) return;
    
    if (isLoggedIn) {
        // Usuario autenticado, mostrar menú de usuario
        getUserProfile()
            .then(profile => {
                const userName = profile && profile.user ? 
                    (profile.user.first_name || profile.user.username) : 
                    'Usuario';
                
                authContainer.innerHTML = `
                    <div class="dropdown">
                        <button class="btn btn-primary dropdown-toggle" type="button" id="userMenuButton" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-user-circle me-1"></i> ${userName}
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userMenuButton">
                            <li><a class="dropdown-item" href="#"><i class="fas fa-user me-2"></i>Mi Perfil</a></li>
                            <li><a class="dropdown-item" href="#"><i class="fas fa-file-alt me-2"></i>Mis Solicitudes</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="#" onclick="logout(); return false;"><i class="fas fa-sign-out-alt me-2"></i>Cerrar Sesión</a></li>
                        </ul>
                    </div>
                `;
            })
            .catch(error => {
                console.error('Error al obtener perfil de usuario:', error);
                // Mostrar un menú genérico en caso de error
                authContainer.innerHTML = `
                    <div class="dropdown">
                        <button class="btn btn-primary dropdown-toggle" type="button" id="userMenuButton" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-user-circle me-1"></i> Usuario
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userMenuButton">
                            <li><a class="dropdown-item" href="#" onclick="logout(); return false;"><i class="fas fa-sign-out-alt me-2"></i>Cerrar Sesión</a></li>
                        </ul>
                    </div>
                `;
            });
    } else {
        // Usuario no autenticado, mostrar botones de login/registro
        authContainer.innerHTML = `
            <a href="registro.html" class="btn btn-outline-primary me-2">Registrarse</a>
            <a href="login.html" class="btn btn-primary">Iniciar Sesión</a>
        `;
    }
}

/**
 * Obtiene el perfil del usuario autenticado
 * @returns {Promise} Promesa que resuelve al perfil de usuario
 */
async function getUserProfile() {
    try {
        return await API.users.getProfile();
    } catch (error) {
        console.error('Error obteniendo perfil:', error);
        throw error;
    }
}

/**
 * Cierra la sesión del usuario
 */
function logout() {
    if (API && API.users) {
        API.users.logout();
        updateAuthUI();
        
        // Mostrar mensaje de cierre de sesión exitoso
        const message = 'Has cerrado sesión exitosamente';
        
        // Si estamos en una página con un contenedor de alertas, mostrar ahí
        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            alertContainer.innerHTML = `
                <div class="alert alert-success alert-dismissible fade show" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
                </div>
            `;
        } else {
            // Alternativa: crear un toast o alguna notificación flotante
            alert(message);
        }
        
        // Redirigir a la página principal
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1500);
    }
} 