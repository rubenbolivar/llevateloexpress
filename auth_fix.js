/**
 * Corrección para mostrar nombre del usuario en lugar de email
 */

// Función mejorada para obtener el nombre del usuario
async function getUserDisplayName() {
    try {
        // Primero intentar obtener desde localStorage
        const savedName = localStorage.getItem('user_display_name');
        if (savedName && savedName \!== 'Usuario') {
            return savedName;
        }
        
        // Si no está guardado, obtener del perfil
        const profileResult = await getUserProfile();
        if (profileResult.success && profileResult.data.user) {
            const { first_name, last_name } = profileResult.data.user;
            if (first_name || last_name) {
                const fullName = `${first_name || ''} ${last_name || ''}`.trim();
                if (fullName) {
                    localStorage.setItem('user_display_name', fullName);
                    return fullName;
                }
            }
        }
        
        // Fallback al email
        return localStorage.getItem('user_email') || 'Usuario';
    } catch (error) {
        console.log('Error obteniendo nombre del usuario, usando email como fallback');
        return localStorage.getItem('user_email') || 'Usuario';
    }
}

// Nueva función updateAuthUI mejorada
async function updateAuthUIImproved() {
    const authenticated = isAuthenticated();
    
    // Actualizar botones de autenticación en la barra de navegación
    const authButtonsContainer = document.getElementById('auth-buttons');
    if (authButtonsContainer) {
        if (authenticated) {
            // Usuario autenticado: Obtener nombre del perfil y mostrar Mi Dashboard y Cerrar Sesión
            const userName = await getUserDisplayName();
            
            authButtonsContainer.innerHTML = `
                <a href=/dashboard.html class=btn btn-outline-primary me-2>
                    <i class=fas fa-user-circle></i> Mi Dashboard
                </a>
                <span class=me-3 text-muted>Hola, ${userName}</span>
                <button id=logoutBtn class=btn btn-outline-danger>Cerrar Sesión</button>
            `;
            
            // Añadir evento de logout
            const logoutBtn = document.getElementById('logoutBtn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    logoutUser();
                });
            }
        } else {
            // Usuario no autenticado: Mostrar Registrarse e Iniciar Sesión
            authButtonsContainer.innerHTML = `
                <a href=registro.html class=btn btn-outline-primary me-2>Registrarse</a>
                <a href=login.html class=btn btn-primary>Iniciar Sesión</a>
            `;
        }
    }
    
    // Resto de la funcionalidad original...
    const authContainers = document.querySelectorAll('[data-auth-container]');
    if (authContainers.length > 0) {
        authContainers.forEach(container => {
            const forAuthenticated = container.getAttribute('data-auth-container') === 'authenticated';
            if ((forAuthenticated && authenticated) || (\!forAuthenticated && \!authenticated)) {
                container.style.display = '';
            } else {
                container.style.display = 'none';
            }
        });
    }
    
    if (authenticated) {
        const userName = await getUserDisplayName();
        const emailElements = document.querySelectorAll('[data-auth-email]');
        emailElements.forEach(element => {
            element.textContent = userName || 'Usuario';
        });
    }
}
