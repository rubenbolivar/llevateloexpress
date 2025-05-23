/**
 * API.js - Módulo para gestionar las comunicaciones con la API del backend de LlévateloExpress
 * Este archivo proporciona funciones para obtener datos de productos, categorías y otros recursos del backend.
 */

// Configuración base para las peticiones a la API
const API_BASE_URL = '/api';

// Objeto principal de la API
const API = {
    // Registra errores en la consola y opcionalmente muestra un mensaje al usuario
    handleError: function(error, showUserMessage = true) {
        console.error('Error en la petición a la API:', error);
        
        // Si el error ya tiene un formato estructurado, devolverlo directamente
        if (error && (error.status || error.data)) {
            return error;
        }
        
        if (showUserMessage) {
            // Determinar un mensaje amigable para el usuario basado en el error
            let userMessage = 'Ocurrió un error al cargar los datos. Por favor, intenta nuevamente.';
            
            if (error.status === 404) {
                userMessage = 'El recurso solicitado no existe.';
            } else if (error.status === 401 || error.status === 403) {
                userMessage = 'No tienes permiso para acceder a este recurso. Por favor inicia sesión.';
            } else if (error.status === 500) {
                userMessage = 'Error del servidor. Por favor, intenta más tarde.';
            }
            
            // Si estamos en una página con un contenedor de alertas, mostrar ahí
            const alertContainer = document.getElementById('alert-container');
            if (alertContainer) {
                alertContainer.innerHTML = `
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        ${userMessage}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
                    </div>
                `;
            }
        }
        
        // Devolver un objeto de error estructurado
        return {
            status: error.status || 500,
            message: error.message || 'Error desconocido',
            data: error.data || null
        };
    },

    // Productos
    products: {
        // Obtener todos los productos
        getAll: async function() {
            try {
                const response = await fetch(`${API_BASE_URL}/products/products/`);
                if (!response.ok) throw response;
                return await response.json();
            } catch (error) {
                return API.handleError(error);
            }
        },
        
        // Obtener un producto por su ID
        getById: async function(productId) {
            try {
                const response = await fetch(`${API_BASE_URL}/products/products/${productId}/`);
                if (!response.ok) throw response;
                return await response.json();
            } catch (error) {
                return API.handleError(error);
            }
        },
        
        // Obtener productos por categoría
        getByCategory: async function(categorySlug) {
            try {
                const response = await fetch(`${API_BASE_URL}/products/products-by-category/${categorySlug}/`);
                if (!response.ok) throw response;
                return await response.json();
            } catch (error) {
                return API.handleError(error);
            }
        },
        
        // Obtener productos destacados
        getFeatured: async function() {
            try {
                const response = await fetch(`${API_BASE_URL}/products/featured-products/`);
                if (!response.ok) throw response;
                return await response.json();
            } catch (error) {
                return API.handleError(error);
            }
        }
    },
    
    // Categorías
    categories: {
        // Obtener todas las categorías
        getAll: async function() {
            try {
                const response = await fetch(`${API_BASE_URL}/products/categories/`);
                if (!response.ok) throw response;
                return await response.json();
            } catch (error) {
                return API.handleError(error);
            }
        },
        
        // Obtener una categoría por su ID
        getById: async function(categoryId) {
            try {
                const response = await fetch(`${API_BASE_URL}/products/categories/${categoryId}/`);
                if (!response.ok) throw response;
                return await response.json();
            } catch (error) {
                return API.handleError(error);
            }
        }
    },

    // Planes de financiamiento
    financing: {
        // Obtener todos los planes de financiamiento
        getPlans: async function() {
            try {
                const response = await fetch(`${API_BASE_URL}/financing/plans/`);
                if (!response.ok) throw response;
                return await response.json();
            } catch (error) {
                return API.handleError(error);
            }
        }
    },

    // Usuarios y autenticación
    users: {
        // Registrar un nuevo usuario
        register: async function(userData) {
            try {
                const response = await fetch(`${API_BASE_URL}/users/register/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(userData)
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw { status: response.status, data: errorData };
                }
                
                return await response.json();
            } catch (error) {
                return API.handleError(error);
            }
        },
        
        // Iniciar sesión
        login: async function(credentials) {
            try {
                console.log("Iniciando login con credenciales:", JSON.stringify(credentials));
                
                // Asegurarnos de que las credenciales incluyan username o email
                const loginData = {...credentials};
                
                // Algunos backends esperan 'email' en lugar de 'username'
                // Intentemos enviar ambos para mayor compatibilidad
                if (loginData.username && !loginData.email && loginData.username.includes('@')) {
                    loginData.email = loginData.username;
                }
                
                console.log("Datos de login enviados:", JSON.stringify(loginData));
                
                const response = await fetch(`${API_BASE_URL}/users/token/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(loginData)
                });
                
                console.log("Respuesta del servidor:", response.status, response.statusText);
                
                // Capturar la respuesta incluso si no es exitosa para manejar errores
                const data = await response.json().catch(err => {
                    console.error("Error al parsear respuesta JSON:", err);
                    return {};
                });
                
                console.log("Datos de respuesta:", data);
                
                if (!response.ok) {
                    return {
                        status: response.status,
                        data: data,
                        error: true,
                        message: data.detail || 'Error al iniciar sesión'
                    };
                }
                
                // Guardar tokens en localStorage
                localStorage.setItem('accessToken', data.access);
                localStorage.setItem('refreshToken', data.refresh);
                
                return data;
            } catch (error) {
                console.error("Error en API.users.login:", error);
                return {
                    status: error.status || 500,
                    data: error.data || null,
                    error: true,
                    message: error.message || 'Error de conexión al iniciar sesión'
                };
            }
        },
        
        // Cerrar sesión
        logout: function() {
            // Eliminar tokens del localStorage
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            return true;
        },
        
        // Obtener perfil del usuario
        getProfile: async function() {
            try {
                const token = localStorage.getItem('accessToken');
                
                if (!token) {
                    throw { status: 401, message: 'No autenticado' };
                }
                
                const response = await fetch(`${API_BASE_URL}/users/profile/`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (!response.ok) throw response;
                
                return await response.json();
            } catch (error) {
                return API.handleError(error);
            }
        },
        
        // Actualizar perfil de usuario
        updateProfile: async function(profileData) {
            try {
                const token = localStorage.getItem('accessToken');
                
                if (!token) {
                    throw { status: 401, message: 'No autenticado' };
                }
                
                const response = await fetch(`${API_BASE_URL}/users/profile/`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(profileData)
                });
                
                if (!response.ok) throw response;
                
                return await response.json();
            } catch (error) {
                return API.handleError(error);
            }
        },
        
        // Verificar si el usuario está autenticado
        isAuthenticated: function() {
            return localStorage.getItem('accessToken') !== null;
        }
    }
};

// Exportar el objeto API para uso en otros archivos
window.API = API; 