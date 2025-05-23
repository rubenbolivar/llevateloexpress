/**
 * API Client para LlévateloExpress
 * 
 * Este módulo es responsable de todas las comunicaciones con la API del backend.
 * Para autenticación utiliza el módulo Auth.
 */

const API_BASE_URL = '/api';

// Objeto principal de la API
const API = {
    // Productos
    products: {
        // Obtener lista de categorías
        async getCategories() {
            try {
                const response = await fetch(`${API_BASE_URL}/products/categories/`);
                const data = await response.json();
                
                if (response.ok) {
                    return { success: true, data };
                } else {
                    return { error: true, data, status: response.status };
                }
            } catch (error) {
                console.error('Error al obtener categorías:', error);
                return { error: true, message: 'Error de conexión' };
            }
        },
        
        // Obtener lista de productos (con paginación y filtros)
        async getProducts(page = 1, filters = {}) {
            try {
                // Construir URL con parámetros
                let url = `${API_BASE_URL}/products/products/?page=${page}`;
                
                // Añadir filtros a la URL si existen
                Object.keys(filters).forEach(key => {
                    if (filters[key]) {
                        url += `&${key}=${encodeURIComponent(filters[key])}`;
                    }
                });
                
                const response = await fetch(url);
                const data = await response.json();
                
                if (response.ok) {
                    return { success: true, data };
                } else {
                    return { error: true, data, status: response.status };
                }
            } catch (error) {
                console.error('Error al obtener productos:', error);
                return { error: true, message: 'Error de conexión' };
            }
        },
        
        // Obtener detalle de un producto
        async getProductDetail(productId) {
            try {
                const response = await fetch(`${API_BASE_URL}/products/products/${productId}/`);
                const data = await response.json();
                
                if (response.ok) {
                    return { success: true, data };
                } else {
                    return { error: true, data, status: response.status };
                }
            } catch (error) {
                console.error('Error al obtener detalle del producto:', error);
                return { error: true, message: 'Error de conexión' };
            }
        },
        
        // Obtener productos destacados
        async getFeaturedProducts() {
            try {
                const response = await fetch(`${API_BASE_URL}/products/featured-products/`);
                const data = await response.json();
                
                if (response.ok) {
                    return { success: true, data };
                } else {
                    return { error: true, data, status: response.status };
                }
            } catch (error) {
                console.error('Error al obtener productos destacados:', error);
                return { error: true, message: 'Error de conexión' };
            }
        }
    },
    
    // Financiamiento
    financing: {
        // Obtener planes de financiamiento
        async getPlans() {
            try {
                const response = await fetch(`${API_BASE_URL}/financing/plans/`);
                const data = await response.json();
                
                if (response.ok) {
                    return { success: true, data };
                } else {
                    return { error: true, data, status: response.status };
                }
            } catch (error) {
                console.error('Error al obtener planes:', error);
                return { error: true, message: 'Error de conexión' };
            }
        },
        
        // Simular financiamiento
        async simulateFinancing(simulationData) {
            try {
                const response = await fetch(`${API_BASE_URL}/financing/simulate/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(simulationData)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    return { success: true, data };
                } else {
                    return { error: true, data, status: response.status };
                }
            } catch (error) {
                console.error('Error al simular financiamiento:', error);
                return { error: true, message: 'Error de conexión' };
            }
        },
        
        // Guardar simulación (requiere autenticación)
        async saveSimulation(simulationData) {
            return await Auth.fetch(`${API_BASE_URL}/financing/save-simulation/`, {
                method: 'POST',
                body: JSON.stringify(simulationData)
            });
        }
    },
    
    // Solicitudes
    applications: {
        // Obtener lista de solicitudes del usuario (requiere autenticación)
        async getApplications() {
            return await Auth.fetch(`${API_BASE_URL}/users/applications/`);
        },
        
        // Crear nueva solicitud (requiere autenticación)
        async createApplication(applicationData) {
            return await Auth.fetch(`${API_BASE_URL}/users/applications/create/`, {
                method: 'POST',
                body: JSON.stringify(applicationData)
            });
        },
        
        // Obtener detalle de una solicitud (requiere autenticación)
        async getApplicationDetail(applicationId) {
            return await Auth.fetch(`${API_BASE_URL}/users/applications/${applicationId}/`);
        }
    },
    
    // Métodos de utilidad
    utils: {
        // Exportación para compatibilidad con código anterior
        isAuthenticated: function() {
            return Auth.isAuthenticated();
        },
        
        logout: function() {
            Auth.logout();
        }
    }
};

// Actualizar UI según estado de autenticación al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Actualizar elementos de la interfaz según la autenticación
    const isAuthenticated = Auth.isAuthenticated();
    const authButtonsContainer = document.querySelector('header .d-flex');
    
    if (authButtonsContainer) {
        if (isAuthenticated) {
            // Usuario autenticado: Mostrar "Mi Perfil" y "Cerrar Sesión"
            authButtonsContainer.innerHTML = `
                <a href="#" class="btn btn-outline-primary me-2">Mi Perfil</a>
                <button id="logoutBtn" class="btn btn-primary">Cerrar Sesión</button>
            `;
            
            // Añadir evento de logout
            const logoutBtn = document.getElementById('logoutBtn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', function() {
                    Auth.logout();
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
}); 