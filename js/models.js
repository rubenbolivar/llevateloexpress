/**
 * models.js - Definición de modelos para integración con futuro backend Django
 * 
 * Este archivo contiene la estructura de datos que se utilizará para la integración
 * con el futuro panel administrativo de Django.
 */

// Definición de categorías - Esto servirá como referencia para el modelo Django Category
const PRODUCT_CATEGORIES = [
    {
        id: 'motocicletas',
        name: 'Motocicleta',
        slug: 'motocicletas',
        description: 'Motocicletas de diferentes cilindradas y estilos',
        icon: 'fa-motorcycle'
    },
    {
        id: 'vehiculos',
        name: 'Vehículo',
        slug: 'vehiculos',
        description: 'Automóviles, camionetas y vehículos de pasajeros',
        icon: 'fa-car'
    },
    {
        id: 'maquinaria',
        name: 'Maquinaria Agrícola',
        slug: 'maquinaria',
        description: 'Tractores y maquinaria para el sector agrícola',
        icon: 'fa-tractor'
    },
    {
        id: 'camiones',
        name: 'Camión',
        slug: 'camiones',
        description: 'Camiones de carga, transporte y distribución',
        icon: 'fa-truck'
    },
    {
        id: 'equipos',
        name: 'Maquinaria y Equipos',
        slug: 'equipos',
        description: 'Equipamiento especializado para la industria y el comercio',
        icon: 'fa-industry'
    }
];

// Función para obtener todas las categorías
function getCategories() {
    return PRODUCT_CATEGORIES;
}

// Función para obtener una categoría por su ID
function getCategoryById(categoryId) {
    return PRODUCT_CATEGORIES.find(category => category.id === categoryId);
}

// Función para obtener el nombre legible de una categoría
function getCategoryName(categoryId) {
    const category = getCategoryById(categoryId);
    return category ? category.name : categoryId;
}

// Esquema de modelo de Producto para integración con Django
const PRODUCT_SCHEMA = {
    id: 'ID numérico único',
    name: 'Nombre del producto',
    category: 'ID de categoría (foreign key a Category)',
    brand: 'Marca del producto',
    price: 'Precio en dólares',
    image: 'URL de la imagen principal',
    description: 'Descripción detallada',
    features: 'Array de características destacadas',
    specs: {
        general: 'Especificaciones generales (array de objetos {label, value})',
        engine: 'Especificaciones del motor (array de objetos {label, value})',
        comfort: 'Especificaciones de confort (array de objetos {label, value})',
        safety: 'Especificaciones de seguridad (array de objetos {label, value})'
    },
    stock: 'Cantidad disponible',
    featured: 'Destacado en página de inicio (boolean)'
};

// Exportar funciones y constantes para su uso en otros archivos
window.models = {
    categories: PRODUCT_CATEGORIES,
    getCategories,
    getCategoryById,
    getCategoryName,
    PRODUCT_SCHEMA
}; 