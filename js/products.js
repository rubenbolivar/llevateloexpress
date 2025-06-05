// Sistema de productos dinámico - Consume API de Django REST Framework
// Versión 2.0 - Migración de datos estáticos a API dinámica

// Variables globales para almacenar datos de la API
window.products = [];
window.categories = [];
let isDataLoaded = false;

// Configuración de la API
const PRODUCTS_API_BASE_URL = '/api/products';
const API_ENDPOINTS = {
    categories: `${PRODUCTS_API_BASE_URL}/categories/`,
    products: `${PRODUCTS_API_BASE_URL}/products/`,
    productDetail: (id) => `${PRODUCTS_API_BASE_URL}/products/${id}/`
};

// Función para cargar categorías desde la API
async function loadCategories() {
    try {
        console.log('[products-dynamic.js] Cargando categorías desde API...');
        const response = await fetch(API_ENDPOINTS.categories);
        
        if (!response.ok) {
            throw new Error(`Error al cargar categorías: ${response.status}`);
        }
        
        const data = await response.json();
        window.categories = data.results || data;
        console.log('[products-dynamic.js] Categorías cargadas:', window.categories.length);
        return window.categories;
    } catch (error) {
        console.error('[products-dynamic.js] Error cargando categorías:', error);
        return [];
    }
}

// Función para cargar productos desde la API (TODAS las páginas)
async function loadProducts() {
    try {
        console.log('[products-dynamic.js] Cargando productos desde API...');
        
        let allProducts = [];
        let currentUrl = API_ENDPOINTS.products;
        let pageCount = 0;
        
        // Cargar todas las páginas paginadas
        while (currentUrl) {
            pageCount++;
            console.log(`[products-dynamic.js] Cargando página ${pageCount}: ${currentUrl}`);
            
            const response = await fetch(currentUrl);
            
            if (!response.ok) {
                throw new Error(`Error al cargar productos página ${pageCount}: ${response.status}`);
            }
            
            const data = await response.json();
            const pageProducts = data.results || data;
            
            // Agregar productos de esta página al array total
            allProducts = allProducts.concat(pageProducts);
            console.log(`[products-dynamic.js] Página ${pageCount} cargada: ${pageProducts.length} productos`);
            
            // Verificar si hay siguiente página
            currentUrl = data.next;
        }
        
        console.log(`[products-dynamic.js] Total de páginas cargadas: ${pageCount}`);
        console.log(`[products-dynamic.js] Total de productos obtenidos: ${allProducts.length}`);
        
        // Transformar todos los datos de la API al formato esperado por el frontend
        window.products = allProducts.map(transformProductFromAPI);
        console.log('[products-dynamic.js] Productos cargados y transformados:', window.products.length);
        return window.products;
    } catch (error) {
        console.error('[products-dynamic.js] Error cargando productos:', error);
        return [];
    }
}

// Función para transformar un producto de la API al formato del frontend
function transformProductFromAPI(apiProduct) {
    console.log('🔄 [TRANSFORM] Iniciando transformación para:', apiProduct.name);
    console.log('🔄 [TRANSFORM] Datos crudos de API:', {
        specs_general: apiProduct.specs_general ? apiProduct.specs_general.substring(0, 100) + '...' : 'null',
        specs_engine: apiProduct.specs_engine ? apiProduct.specs_engine.substring(0, 100) + '...' : 'null',
        features: apiProduct.features ? apiProduct.features.substring(0, 100) + '...' : 'null'
    });
    
    // Parsear especificaciones técnicas desde los campos separados de la API
    let specs = {};
    
    // Procesar specs_general
    if (apiProduct.specs_general) {
        try {
            console.log('🔄 [TRANSFORM] Parseando specs_general...');
            console.log('🔄 [TRANSFORM] specs_general tipo:', typeof apiProduct.specs_general);
            console.log('🔄 [TRANSFORM] specs_general raw:', apiProduct.specs_general.substring(0, 200));
            
            specs.general = typeof apiProduct.specs_general === 'string' ? 
                JSON.parse(apiProduct.specs_general) : apiProduct.specs_general;
                
            console.log('✅ [TRANSFORM] specs_general parseado:', specs.general?.length || 0, 'items');
            console.log('✅ [TRANSFORM] Primer item specs_general:', specs.general?.[0]);
        } catch (e) {
            console.error('❌ [TRANSFORM] Error parseando specs_general:', e);
            console.error('❌ [TRANSFORM] Datos problemáticos:', apiProduct.specs_general);
            specs.general = [];
        }
    } else {
        console.log('⚠️ [TRANSFORM] specs_general no disponible');
        specs.general = [];
    }
    
    // Procesar specs_engine
    if (apiProduct.specs_engine) {
        try {
            console.log('🔄 [TRANSFORM] Parseando specs_engine...');
            specs.engine = typeof apiProduct.specs_engine === 'string' ? 
                JSON.parse(apiProduct.specs_engine) : apiProduct.specs_engine;
            console.log('✅ [TRANSFORM] specs_engine parseado:', specs.engine?.length || 0, 'items');
        } catch (e) {
            console.error('❌ [TRANSFORM] Error parseando specs_engine:', e);
            specs.engine = [];
        }
    } else {
        specs.engine = [];
    }
    
    // Procesar specs_comfort
    if (apiProduct.specs_comfort) {
        try {
            console.log('🔄 [TRANSFORM] Parseando specs_comfort...');
            specs.comfort = typeof apiProduct.specs_comfort === 'string' ? 
                JSON.parse(apiProduct.specs_comfort) : apiProduct.specs_comfort;
            console.log('✅ [TRANSFORM] specs_comfort parseado:', specs.comfort?.length || 0, 'items');
        } catch (e) {
            console.error('❌ [TRANSFORM] Error parseando specs_comfort:', e);
            specs.comfort = [];
        }
    } else {
        specs.comfort = [];
    }
    
    // Procesar specs_safety
    if (apiProduct.specs_safety) {
        try {
            console.log('🔄 [TRANSFORM] Parseando specs_safety...');
            specs.safety = typeof apiProduct.specs_safety === 'string' ? 
                JSON.parse(apiProduct.specs_safety) : apiProduct.specs_safety;
            console.log('✅ [TRANSFORM] specs_safety parseado:', specs.safety?.length || 0, 'items');
        } catch (e) {
            console.error('❌ [TRANSFORM] Error parseando specs_safety:', e);
            specs.safety = [];
        }
    } else {
        specs.safety = [];
    }
    
    // Parsear características si vienen como string JSON
    let features = [];
    if (typeof apiProduct.features === 'string') {
        try {
            console.log('🔄 [TRANSFORM] Parseando features...');
            features = JSON.parse(apiProduct.features);
            console.log('✅ [TRANSFORM] features parseado:', features?.length || 0, 'items');
        } catch (e) {
            console.error('❌ [TRANSFORM] Error parseando features:', e);
            features = [];
        }
    } else if (Array.isArray(apiProduct.features)) {
        features = apiProduct.features;
    }
    
    // Manejar URLs de imagen - ahora todas están en media/products/
    let imageUrl = apiProduct.image || 'img/products/default.jpg';
    
    // Si la imagen viene del API con ruta relativa products/filename.jpg
    if (imageUrl.startsWith('products/')) {
        imageUrl = `media/${imageUrl}`;
    }
    
    // Si ya tiene el prefijo media/, mantenerla
    if (imageUrl.startsWith('media/products/')) {
        // Ya está correcta
    }
    
    // Si viene con dominio completo, hacer relativa
    if (imageUrl.startsWith('https://llevateloexpress.com/')) {
        imageUrl = imageUrl.replace('https://llevateloexpress.com/', '');
    }
    
    // Log final de debugging
    console.log(`🎯 [TRANSFORM] RESULTADO FINAL para ${apiProduct.name}:`);
    console.log(`   - specs.general: ${specs.general?.length || 0} items`);
    console.log(`   - specs.engine: ${specs.engine?.length || 0} items`);
    console.log(`   - specs.comfort: ${specs.comfort?.length || 0} items`);
    console.log(`   - specs.safety: ${specs.safety?.length || 0} items`);
    console.log(`   - features: ${features.length} items`);
    
    return {
        id: apiProduct.id,
        name: apiProduct.name,
        category: apiProduct.category_name || apiProduct.category || 'motocicletas',
        brand: apiProduct.brand,
        price: parseFloat(apiProduct.price) || 0,
        image: imageUrl,
        description: apiProduct.description || '',
        features: features,
        specs: specs,
        stock: parseInt(apiProduct.stock) || 0,
        featured: apiProduct.featured || false
    };
}

// Función para cargar detalle completo de un producto
async function loadProductDetail(productId) {
    try {
        console.log('[products-dynamic.js] Cargando detalle del producto:', productId);
        const response = await fetch(API_ENDPOINTS.productDetail(productId));
        
        if (!response.ok) {
            throw new Error(`Error al cargar producto ${productId}: ${response.status}`);
        }
        
        const apiProduct = await response.json();
        return transformProductFromAPI(apiProduct);
    } catch (error) {
        console.error('[products-dynamic.js] Error cargando detalle del producto:', error);
        return null;
    }
}

// Función principal para inicializar datos
async function initializeData() {
    if (isDataLoaded) {
        console.log('[products-dynamic.js] Datos ya cargados');
        return true;
    }
    
    try {
        console.log('[products-dynamic.js] Inicializando datos desde API...');
        
        // Cargar categorías y productos en paralelo
        const [categories, products] = await Promise.all([
            loadCategories(),
            loadProducts()
        ]);
        
        if (products.length > 0) {
            isDataLoaded = true;
            console.log('[products-dynamic.js] Datos inicializados correctamente');
            
            // Disparar evento personalizado para notificar que los datos están listos
            const event = new CustomEvent('productsLoaded', {
                detail: { products: window.products, categories: window.categories }
            });
            document.dispatchEvent(event);
            
            return true;
        } else {
            throw new Error('No se pudieron cargar productos');
        }
    } catch (error) {
        console.error('[products-dynamic.js] Error inicializando datos:', error);
        return false;
    }
}

// Función para obtener productos por categoría
function getProductsByCategory(categoryName) {
    return window.products.filter(product => 
        product.category.toLowerCase() === categoryName.toLowerCase()
    );
}

// Función para obtener productos destacados
function getFeaturedProducts() {
    return window.products.filter(product => product.featured);
}

// Función para buscar productos
function searchProducts(query) {
    const searchTerm = query.toLowerCase();
    return window.products.filter(product => 
        product.name.toLowerCase().includes(searchTerm) ||
        product.brand.toLowerCase().includes(searchTerm) ||
        product.description.toLowerCase().includes(searchTerm)
    );
}

// Función para filtrar productos por precio
function getProductsByPriceRange(minPrice, maxPrice) {
    return window.products.filter(product => 
        product.price >= minPrice && product.price <= maxPrice
    );
}

// Función para obtener un producto por ID
function getProductById(productId) {
    const id = parseInt(productId);
    return window.products.find(product => product.id === id);
}

// === FUNCIONES DEL FRONTEND ORIGINAL ===

// Crear tarjeta de producto (manteniendo funcionalidad original)
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'col-md-6 col-lg-4 mb-4';
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    
    // Determinar imagen con fallback mejorado
    let imageUrl = product.image;
    if (!imageUrl || imageUrl === 'img/products/default.jpg') {
        imageUrl = 'img/products/default.jpg';
    }
    
    card.innerHTML = `
        <div class="card product-card h-100">
            <div class="position-relative">
                <img src="${imageUrl}" 
                     class="card-img-top product-image" 
                     alt="${product.name}" 
                     loading="lazy"
                     style="height: 200px; object-fit: cover; background-color: #f8f9fa;"
                     onerror="this.src='img/products/default.jpg'; this.onerror=null;">
                ${product.featured ? '<span class="badge bg-primary position-absolute top-0 end-0 m-2">Destacado</span>' : ''}
                ${product.stock <= 3 && product.stock > 0 ? '<span class="badge bg-warning position-absolute top-0 start-0 m-2">Pocas unidades</span>' : ''}
                ${product.stock === 0 ? '<span class="badge bg-danger position-absolute top-0 start-0 m-2">Agotado</span>' : ''}
            </div>
            
            <div class="card-body d-flex flex-column">
                <div class="mb-2">
                    <small class="text-muted">${product.brand}</small>
                    <h5 class="card-title">${product.name}</h5>
                </div>
                
                <p class="card-text text-muted flex-grow-1">${product.description.substring(0, 100)}${product.description.length > 100 ? '...' : ''}</p>
                
                <div class="product-features mb-3">
                    ${product.features && product.features.length > 0 ? 
                        product.features.slice(0, 3).map(feature => 
                            `<small class="d-block text-success">• ${feature}</small>`
                        ).join('') :
                        '<small class="text-muted">Características no disponibles</small>'
                    }
                </div>
                
                <div class="mt-auto">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div>
                            <h4 class="text-primary mb-0">$${product.price.toLocaleString()}</h4>
                            <small class="text-muted">Stock: ${product.stock} unidades</small>
                        </div>
                        <span class="badge bg-secondary">${getCategoryName(product.category)}</span>
                    </div>
                    
                    <div class="btn-group w-100" role="group">
                        <a href="detalle-producto.html?id=${product.id}" class="btn btn-outline-primary">
                            <i class="fas fa-eye"></i> Ver detalles
                        </a>
                        <button class="btn btn-primary" onclick="addToCart(${product.id})" ${product.stock === 0 ? 'disabled' : ''}>
                            <i class="fas fa-cart-plus"></i> ${product.stock === 0 ? 'Agotado' : 'Agregar'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Animación de entrada suave
    setTimeout(() => {
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
    }, Math.random() * 200); // Efecto escalonado
    
    return card;
}

// Obtener nombre de categoría (manteniendo funcionalidad original)
function getCategoryName(category) {
    const categoryMap = {
        'motocicletas': 'Motocicletas',
        'repuestos': 'Repuestos',
        'accesorios': 'Accesorios',
        'cascos': 'Cascos',
        'lubricantes': 'Lubricantes'
    };
    return categoryMap[category] || category;
}

// Configurar filtros (manteniendo funcionalidad original)
function setupFilters() {
    console.log('[products-dynamic.js] Configurando filtros');
    
    // Filtro por categoría
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            filterProducts('category', this.value);
        });
    }
    
    // Filtro por marca
    const brandFilter = document.getElementById('brand-filter');
    if (brandFilter) {
        brandFilter.addEventListener('change', function() {
            filterProducts('brand', this.value);
        });
    }
    
    // Filtro por precio
    const priceFilter = document.getElementById('price-filter');
    if (priceFilter) {
        priceFilter.addEventListener('change', function() {
            filterProducts('price', this.value);
        });
    }
    
    // Barra de búsqueda
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterProducts('search', this.value);
        });
    }
    
    // Ordenamiento
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            sortProducts(this.value);
        });
    }
    
    // Botón de limpiar filtros
    const clearFilters = document.getElementById('clear-filters');
    if (clearFilters) {
        clearFilters.addEventListener('click', function() {
            clearAllFilters();
        });
    }
}

// Filtrar productos (manteniendo funcionalidad original)
function filterProducts(filterType, filterValue) {
    console.log('[products-dynamic.js] Filtrando por:', filterType, filterValue);
    
    let filteredProducts = [...window.products];
    
    // Aplicar filtros activos
    const categoryFilter = document.getElementById('category-filter');
    const brandFilter = document.getElementById('brand-filter');
    const priceFilter = document.getElementById('price-filter');
    const searchInput = document.getElementById('search-input');
    
    // Filtro por categoría
    if (categoryFilter && categoryFilter.value) {
        filteredProducts = filteredProducts.filter(product => 
            product.category === categoryFilter.value
        );
    }
    
    // Filtro por marca
    if (brandFilter && brandFilter.value) {
        filteredProducts = filteredProducts.filter(product => 
            product.brand === brandFilter.value
        );
    }
    
    // Filtro por precio
    if (priceFilter && priceFilter.value) {
        const [min, max] = priceFilter.value.split('-').map(Number);
        filteredProducts = filteredProducts.filter(product => 
            product.price >= min && (max ? product.price <= max : true)
        );
    }
    
    // Filtro por búsqueda
    if (searchInput && searchInput.value.trim()) {
        const searchTerm = searchInput.value.toLowerCase();
        filteredProducts = filteredProducts.filter(product => 
            product.name.toLowerCase().includes(searchTerm) ||
            product.brand.toLowerCase().includes(searchTerm) ||
            product.description.toLowerCase().includes(searchTerm)
        );
    }
    
    displayProducts(filteredProducts);
}

// Mostrar productos en el DOM
function displayProducts(products) {
    const container = document.getElementById('products-container');
    if (!container) return;
    
    // Fade out contenido actual
    container.style.opacity = '0.5';
    container.style.transition = 'opacity 0.2s ease';
    
    setTimeout(() => {
        container.innerHTML = '';
        
        if (products.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-4">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h4>No se encontraron productos</h4>
                    <p class="text-muted">Intenta con otros criterios de búsqueda</p>
                </div>
            `;
        } else {
            products.forEach((product, index) => {
                const productCard = createProductCard(product);
                // Añadir delay escalonado para animación
                productCard.style.animationDelay = `${index * 0.1}s`;
                container.appendChild(productCard);
            });
        }
        
        // Fade in nuevo contenido
        container.style.opacity = '1';
        
        // Actualizar contador
        const counter = document.getElementById('products-counter');
        if (counter) {
            counter.textContent = `${products.length} producto${products.length !== 1 ? 's' : ''} encontrado${products.length !== 1 ? 's' : ''}`;
        }
    }, 150);
}

// Ordenar productos
function sortProducts(sortBy) {
    let sortedProducts = [...window.products];
    
    switch (sortBy) {
        case 'name-asc':
            sortedProducts.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'name-desc':
            sortedProducts.sort((a, b) => b.name.localeCompare(a.name));
            break;
        case 'price-asc':
            sortedProducts.sort((a, b) => a.price - b.price);
            break;
        case 'price-desc':
            sortedProducts.sort((a, b) => b.price - a.price);
            break;
        case 'brand':
            sortedProducts.sort((a, b) => a.brand.localeCompare(b.brand));
            break;
        default:
            sortedProducts = [...window.products];
    }
    
    displayProducts(sortedProducts);
}

// Limpiar todos los filtros
function clearAllFilters() {
    const filters = ['category-filter', 'brand-filter', 'price-filter', 'search-input'];
    filters.forEach(filterId => {
        const element = document.getElementById(filterId);
        if (element) element.value = '';
    });
    
    displayProducts(window.products);
}

// Agregar al carrito (mantener funcionalidad existente)
function addToCart(productId) {
    console.log('[products-dynamic.js] Agregando al carrito:', productId);
    // Aquí iría la lógica del carrito
    alert(`Producto ${productId} agregado al carrito`);
}

// === INICIALIZACIÓN ===

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', async function() {
    console.log('[products-dynamic.js] DOM cargado, inicializando...');
    
    // Mostrar indicador de carga mejorado
    const container = document.getElementById('products-container') || document.getElementById('featured-products-container');
    if (container) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="d-flex flex-column align-items-center">
                    <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Cargando productos...</span>
                    </div>
                    <h5 class="text-muted mb-2">Cargando productos</h5>
                    <p class="text-muted small mb-0">Obteniendo información desde el servidor...</p>
                    <div class="progress mt-3" style="width: 200px; height: 4px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 100%"></div>
                    </div>
                </div>
            </div>
        `;
        // Aplicar fade in suave al indicador
        container.style.opacity = '0';
        container.style.transition = 'opacity 0.3s ease';
        setTimeout(() => {
            container.style.opacity = '1';
        }, 100);
    }
    
    // Inicializar datos
    const success = await initializeData();
    
    if (success) {
        console.log('[products-dynamic.js] Datos cargados exitosamente');
        
        // Cargar productos destacados en la página principal
        const featuredContainer = document.getElementById('featured-products-container');
        if (featuredContainer) {
            console.log('[products-dynamic.js] Cargando productos destacados');
            const featuredProducts = getFeaturedProducts();
            
            // Transición suave para productos destacados
            featuredContainer.style.opacity = '0.5';
            setTimeout(() => {
                featuredContainer.innerHTML = '';
                
                featuredProducts.forEach((product, index) => {
                    const productCard = createProductCard(product);
                    productCard.style.animationDelay = `${index * 0.1}s`;
                    featuredContainer.appendChild(productCard);
                });
                
                featuredContainer.style.opacity = '1';
            }, 200);
        }
        
        // Cargar todos los productos en la página de catálogo
        const productsContainer = document.getElementById('products-container');
        if (productsContainer) {
            console.log('[products-dynamic.js] Cargando catálogo completo');
            displayProducts(window.products);
        }
        
        // Configurar filtros
        setupFilters();
        
    } else {
        console.error('[products-dynamic.js] Error cargando datos');
        if (container) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                        <h4>Error cargando productos</h4>
                        <p class="mb-3">No se pudieron cargar los productos desde el servidor</p>
                        <button class="btn btn-primary" onclick="location.reload()">
                            <i class="fas fa-refresh me-2"></i>Recargar página
                        </button>
                    </div>
                </div>
            `;
        }
    }
});

// Exponer funciones para uso externo
window.ProductsAPI = {
    initializeData,
    loadProducts,
    loadCategories,
    loadProductDetail,
    getProductById,
    getFeaturedProducts,
    getProductsByCategory,
    searchProducts,
    getProductsByPriceRange,
    isDataLoaded: () => isDataLoaded
};

console.log('[products-dynamic.js] Script cargado - API de productos dinámicos lista'); 