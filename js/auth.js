/**
 * Sistema de Autenticación para LlévateloExpress
 * 
 * Este módulo maneja todas las operaciones relacionadas con autenticación:
 * - Login/Logout
 * - Registro de usuarios
 * - Gestión de tokens JWT
 * - Protección CSRF
 */

// Configuración base
// const API_BASE_URL = "/api"; // Ya declarado en api-fixed.js

// --------------------------------------
// FUNCIONES AUXILIARES DE AUTENTICACIÓN
// --------------------------------------

/**
 * Obtiene el token CSRF de las cookies del navegador
 * @returns {string|null} El token CSRF o null si no existe
 */
function getCsrfToken() {
    const name = 'csrftoken=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');
    
    for (let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i].trim();
        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
    return null;
}

/**
 * Realiza una solicitud para obtener una cookie CSRF fresca
 * @returns {Promise<boolean>} True si se obtuvo el token, false en caso contrario
 */
async function fetchCsrfToken() {
    try {
        console.log('Solicitando token CSRF...');
        const response = await fetch(`${API_BASE_URL}/users/csrf-token/`, {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            console.log('Token CSRF obtenido correctamente');
            return true;
        } else {
            console.error('Error al obtener token CSRF:', response.status);
            return false;
        }
    } catch (error) {
        console.error('Error al solicitar token CSRF:', error);
        return false;
    }
}

/**
 * Realiza una solicitud autenticada con tokens JWT
 * @param {string} url URL a la que realizar la petición
 * @param {Object} options Opciones de fetch adicionales
 * @returns {Promise<Object>} Respuesta procesada
 */
async function authenticatedFetch(url, options = {}) {
    // Obtener token de acceso
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
        return { error: true, message: 'No autenticado' };
    }
    
    // Configurar headers autenticados
    const authOptions = {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    };
    
    try {
        // Realizar petición
        let response = await fetch(url, authOptions);
        
        // Si es error 401 (Unauthorized), intentar refrescar token
        if (response.status === 401) {
            const refreshSuccess = await refreshAccessToken();
            
            if (refreshSuccess) {
                // Actualizar token en headers y reintentar
                authOptions.headers.Authorization = `Bearer ${localStorage.getItem('access_token')}`;
                response = await fetch(url, authOptions);
            } else {
                // Si no se pudo refrescar, cerrar sesión
                logoutUser();
                return { error: true, message: 'Sesión expirada' };
            }
        }
        
        // Procesar respuesta
        let data;
        try {
            data = await response.json();
        } catch {
            data = {};
        }
        
        if (response.ok) {
            return { success: true, data };
        } else {
            return { error: true, data, status: response.status };
        }
    } catch (error) {
        console.error('Error en petición autenticada:', error);
        return { error: true, message: 'Error de conexión' };
    }
}

/**
 * Refresca el token de acceso usando el token de refresco
 * @returns {Promise<boolean>} True si el refresco fue exitoso
 */
async function refreshAccessToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return false;
    
    try {
        console.log('Intentando refrescar token de acceso...');
        const response = await fetch(`${API_BASE_URL}/users/token/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            console.log('Token refrescado correctamente');
            return true;
        } else {
            console.error('Error al refrescar token:', response.status);
            return false;
        }
    } catch (error) {
        console.error('Error durante el refresco de token:', error);
        return false;
    }
}

// ------------------------------------
// FUNCIONES PRINCIPALES DE AUTENTICACIÓN
// ------------------------------------

/**
 * Inicia sesión de usuario
 * @param {string} email Email del usuario
 * @param {string} password Contraseña del usuario
 * @returns {Promise<Object>} Resultado del inicio de sesión
 */
async function loginUser(email, password) {
    // Validación básica de parámetros
    if (!email || typeof email !== 'string') {
        return {
            error: true,
            data: { username: ["Campo requerido"] },
            status: 400
        };
    }
    
    if (!password || typeof password !== 'string') {
        return {
            error: true,
            data: { password: ["Campo requerido"] },
            status: 400
        };
    }
    
    try {
        // Asegurar que tenemos token CSRF
        await fetchCsrfToken();
        
        console.log(`Iniciando sesión para: ${email}`);
        
        // Realizar petición de login
        const response = await fetch(`${API_BASE_URL}/users/token/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            credentials: 'include',
            body: JSON.stringify({ username: email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Guardar tokens en localStorage
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            
            // También guardar email para identificación rápida
            localStorage.setItem('user_email', email);
            
            console.log('Inicio de sesión exitoso');
            return { success: true };
        } else {
            console.error('Error en inicio de sesión:', data);
            return { error: true, data, status: response.status };
        }
    } catch (error) {
        console.error('Error durante login:', error);
        return { error: true, message: 'Error de conexión' };
    }
}

/**
 * Registra un nuevo usuario
 * @param {Object} userData Datos del usuario a registrar
 * @returns {Promise<Object>} Resultado del registro
 */
async function registerUser(userData) {
    // Validación básica
    if (!userData || !userData.email || !userData.password || !userData.password2) {
        return {
            error: true,
            data: { detail: "Faltan campos requeridos" },
            status: 400
        };
    }
    
    try {
        // Asegurar que tenemos token CSRF
        await fetchCsrfToken();
        
        console.log('Registrando nuevo usuario:', {
            ...userData,
            password: '[REDACTED]',
            password2: '[REDACTED]'
        });
        
        // Asegurar que username y email coinciden (requerido por backend)
        userData.username = userData.email;
        
        // Realizar petición de registro
        const response = await fetch(`${API_BASE_URL}/users/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            credentials: 'include',
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            console.log('Registro exitoso:', data);
            return { success: true, data };
        } else {
            console.error('Error en registro:', data);
            return { error: true, data, status: response.status };
        }
    } catch (error) {
        console.error('Error durante registro:', error);
        return { error: true, message: 'Error de conexión' };
    }
}

/**
 * Cierra la sesión del usuario
 */
function logoutUser() {
    // Limpiar tokens del localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_email');
    
    // Limpiar cookie CSRF (para prevenir cualquier problema de autenticación)
    document.cookie = "csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    
    console.log('Sesión cerrada correctamente');
    
    // Actualizar la UI inmediatamente antes de redireccionar
    updateAuthUI();
    
    // Redireccionar a la página principal con un parámetro para mostrar mensaje
    window.location.href = 'index.html?logout=true';
}

/**
 * Verifica si el usuario está autenticado
 * @returns {boolean} True si el usuario está autenticado
 */
function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

/**
 * Obtiene el perfil del usuario actual
 * @returns {Promise<Object>} Datos del perfil o error
 */
async function getUserProfile() {
    return await authenticatedFetch(`${API_BASE_URL}/users/profile/`);
}

/**
 * Actualiza los elementos de UI según el estado de autenticación
 */
function updateAuthUI() {
    const authenticated = isAuthenticated();
    
    // Actualizar botones de autenticación en la barra de navegación
    const authButtonsContainer = document.getElementById('auth-buttons');
    if (authButtonsContainer) {
        if (authenticated) {
            // Usuario autenticado: Mostrar "Mi Dashboard" y "Cerrar Sesión"
            const userEmail = localStorage.getItem('user_email') || 'Usuario';
            authButtonsContainer.innerHTML = `
                <a href="/dashboard.html" class="btn btn-outline-primary me-2">
                    <i class="fas fa-user-circle"></i> Mi Dashboard
                </a>
                <span class="me-3 text-muted">${userEmail}</span>
                <button id="logoutBtn" class="btn btn-outline-danger">Cerrar Sesión</button>
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
            // Usuario no autenticado: Mostrar "Registrarse" e "Iniciar Sesión"
            authButtonsContainer.innerHTML = `
                <a href="registro.html" class="btn btn-outline-primary me-2">Registrarse</a>
                <a href="login.html" class="btn btn-primary">Iniciar Sesión</a>
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
            if ((forAuthenticated && authenticated) || (!forAuthenticated && !authenticated)) {
                container.style.display = '';
            } else {
                container.style.display = 'none';
            }
        });
    }
    
    // Si hay elementos que muestran el email del usuario
    if (authenticated) {
        const userEmail = localStorage.getItem('user_email');
        const emailElements = document.querySelectorAll('[data-auth-email]');
        emailElements.forEach(element => {
            element.textContent = userEmail || 'Usuario';
        });
    }
}

// Inicializar sistema de autenticación al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Obtener token CSRF
    fetchCsrfToken().then(() => {
        // Actualizar UI según estado de autenticación
        updateAuthUI();
        
        // Solo redirigir si el usuario ya ha iniciado sesión anteriormente
        // y está intentando acceder a páginas de login/registro
        if (isAuthenticated()) {
            const currentPage = window.location.pathname.split('/').pop();
            
            // Si la página actual es login o registro Y el usuario tiene una sesión previa válida
            if ((currentPage === 'login.html' || currentPage === 'registro.html') && 
                localStorage.getItem('user_email')) {
                
                console.log('Usuario ya autenticado, redirigiendo...');
                window.location.href = 'index.html';
            }
        }
    });
});

// Exportar funciones públicas
window.Auth = {
    login: loginUser,
    loginUser: loginUser, // Alias para compatibilidad
    register: registerUser,
    registerUser: registerUser, // Alias para compatibilidad
    logout: logoutUser,
    logoutUser: logoutUser, // Alias para compatibilidad
    isAuthenticated,
    getProfile: getUserProfile,
    fetch: authenticatedFetch,
    fetchCsrfToken: fetchCsrfToken,
    getCsrfToken: getCsrfToken,
    updateAuthUI: updateAuthUI,
    refreshAccessToken: refreshAccessToken
};

// Exportar como módulo ES6 también
// export const Auth = window.Auth; 
// Actualizar UI automáticamente cuando se carga la página
document.addEventListener("DOMContentLoaded", function() {
    updateAuthUI();
});
