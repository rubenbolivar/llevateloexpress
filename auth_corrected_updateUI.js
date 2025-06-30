/**
 * Actualiza los elementos de UI según el estado de autenticación
 */
async function updateAuthUI() {
    const authenticated = isAuthenticated();
    
    // Actualizar botones de autenticación en la barra de navegación
    const authButtonsContainer = document.getElementById('auth-buttons');
    if (authButtonsContainer) {
        if (authenticated) {
            // Usuario autenticado: Obtener nombre del perfil
            let userName = localStorage.getItem('user_display_name') || 'Usuario';
            
            // Si no tenemos el nombre guardado, obtenerlo del perfil
            if (userName === 'Usuario' || \!localStorage.getItem('user_display_name')) {
                try {
                    const profileResult = await getUserProfile();
                    if (profileResult.success && profileResult.data.user) {
                        const { first_name, last_name } = profileResult.data.user;
                        if (first_name || last_name) {
                            userName = `${first_name || ''} ${last_name || ''}`.trim();
                            localStorage.setItem('user_display_name', userName);
                        }
                    }
                } catch (error) {
                    console.log('No se pudo obtener el perfil del usuario');
                    userName = localStorage.getItem('user_email') || 'Usuario';
                }
            }
            
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
    
    // Actualizar otros contenedores con atributos data-auth
    const authContainers = document.querySelectorAll('[data-auth-container]');
    if (authContainers.length > 0) {
        authContainers.forEach(container => {
            // Comprobar si el contenedor es para usuarios autenticados o no autenticados
            const forAuthenticated = container.getAttribute('data-auth-container') === 'authenticated';
            
            // Mostrar u ocultar según corresponda
            if ((forAuthenticated && authenticated) || (\!forAuthenticated && \!authenticated)) {
                container.style.display = '';
            } else {
                container.style.display = 'none';
            }
        });
    }
    
    // Si hay elementos que muestran el email del usuario
    if (authenticated) {
        const userName = await getUserDisplayName();
        const emailElements = document.querySelectorAll('[data-auth-email]');
        emailElements.forEach(element => {
            element.textContent = userName || 'Usuario';
        });
    }
}

// Función auxiliar para obtener el nombre del usuario
async function getUserDisplayName() {
    try {
        const savedName = localStorage.getItem('user_display_name');
        if (savedName && savedName \!== 'Usuario') {
            return savedName;
        }
        
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
        
        return localStorage.getItem('user_email') || 'Usuario';
    } catch (error) {
        return localStorage.getItem('user_email') || 'Usuario';
    }
}
