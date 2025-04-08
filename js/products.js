// Datos de productos
const products = [
    {
        id: 1,
        name: "Voge Rally 300",
        category: "motocicletas",
        brand: "Voge",
        price: 4500,
        image: "img/products/300.jpg",
        description: "La Voge Rally 300 es una motocicleta de aventura ligera que combina versatilidad y rendimiento. Perfecta para quienes buscan una moto capaz tanto en ciudad como en caminos de tierra.",
        features: [
            "Motor monocilíndrico de 292cc refrigerado por líquido",
            "Potencia máxima de 29 HP a 8500 rpm",
            "Transmisión de 6 velocidades",
            "Frenos de disco con ABS desconectable",
            "Suspensión invertida ajustable",
            "Panel de instrumentos TFT a color",
            "Iluminación full LED",
            "Capacidad de tanque: 16 litros"
        ],
        stock: 8,
        featured: true
    },
    {
        id: 2,
        name: "Voge 525 DSX",
        category: "motocicletas",
        brand: "Voge",
        price: 6800,
        image: "img/products/525dsx.jpg",
        description: "La Voge 525 DSX es una motocicleta trail de media cilindrada que ofrece excelentes prestaciones para aventuras on/off-road. Su diseño moderno y equipamiento premium la hacen destacar en su segmento.",
        features: [
            "Motor bicilíndrico en línea de 494cc",
            "Potencia de 46.2 HP a 8500 rpm",
            "Transmisión de 6 velocidades",
            "Sistema de frenos ABS Bosch de doble canal",
            "Suspensión KYB totalmente ajustable",
            "Pantalla TFT de 7 pulgadas",
            "Modos de conducción",
            "Control de tracción"
        ],
        stock: 5,
        featured: true
    },
    {
        id: 3,
        name: "Voge AC 525 X",
        category: "motocicletas",
        brand: "Voge",
        price: 7200,
        image: "img/products/ac525.jpg",
        description: "La Voge AC 525 X representa la evolución en el segmento adventure touring. Con su diseño sofisticado y tecnología avanzada, ofrece el equilibrio perfecto entre confort y capacidad todoterreno.",
        features: [
            "Motor bicilíndrico de 494cc refrigerado por líquido",
            "48 HP de potencia máxima",
            "Transmisión de 6 velocidades con embrague anti-rebote",
            "Sistema de frenos ABS Bosch con modo off-road",
            "Suspensión KYB con recorrido extendido",
            "Pantalla TFT con conectividad bluetooth",
            "Control de crucero",
            "Protectores de motor y manos incluidos"
        ],
        stock: 6,
        featured: true
    },
    {
        id: 4,
        name: "Suzuki DR 650",
        category: "motocicletas",
        brand: "Suzuki",
        price: 8500,
        image: "img/products/dr650.jpg",
        description: "La legendaria Suzuki DR 650 es sinónimo de confiabilidad y versatilidad. Una moto dual-purpose que ha probado su valor tanto en largas travesías como en el uso diario.",
        features: [
            "Motor monocilíndrico SOHC de 644cc refrigerado por aire",
            "Potencia de 46 HP",
            "Transmisión de 5 velocidades",
            "Freno de disco delantero y trasero",
            "Suspensión de largo recorrido",
            "Altura de asiento ajustable",
            "Peso en seco de 166 kg",
            "Tanque de combustible de 13 litros"
        ],
        stock: 4,
        featured: true
    },
    {
        id: 5,
        name: "Suzuki GN 125",
        category: "motocicletas",
        brand: "Suzuki",
        price: 2200,
        image: "img/products/gn125.jpg",
        description: "La Suzuki GN 125 es una motocicleta clásica ideal para principiantes y uso urbano. Su diseño atemporal, bajo consumo y fácil mantenimiento la han convertido en un referente de su categoría.",
        features: [
            "Motor monocilíndrico de 124cc refrigerado por aire",
            "Potencia de 12.5 HP a 9500 rpm",
            "Transmisión de 5 velocidades",
            "Freno de disco delantero y tambor trasero",
            "Arranque eléctrico y por patada",
            "Consumo aproximado de 2.2L/100km",
            "Peso en orden de marcha: 113 kg",
            "Capacidad de tanque: 10.5 litros"
        ],
        stock: 12,
        featured: true
    },
    {
        id: 6,
        name: "Voge SR4",
        category: "motocicletas",
        brand: "Voge",
        price: 5500,
        image: "img/products/sr4.jpg",
        description: "La Voge SR4 es una motocicleta deportiva que combina estilo y rendimiento. Su diseño moderno y tecnología avanzada la convierten en una opción atractiva para los amantes de las motos deportivas.",
        features: [
            "Motor bicilíndrico en línea de 350cc",
            "Potencia de 42.5 HP a 9000 rpm",
            "Transmisión de 6 velocidades",
            "Sistema de frenos ABS de doble canal",
            "Suspensión invertida ajustable",
            "Pantalla TFT a color",
            "Iluminación full LED",
            "Modos de conducción seleccionables"
        ],
        stock: 7,
        featured: true
    },
    {
        id: 7,
        name: "Suzuki V-Strom 250",
        category: "motocicletas",
        brand: "Suzuki",
        price: 5800,
        image: "img/products/vstrom.jpg",
        description: "La Suzuki V-Strom 250 es una aventurera ligera que hereda el ADN de la familia V-Strom. Perfecta para iniciarse en el mundo adventure, ofrece comodidad y versatilidad en un paquete accesible.",
        features: [
            "Motor bicilíndrico paralelo de 248cc",
            "Potencia de 25 HP a 8000 rpm",
            "Transmisión de 6 velocidades",
            "Sistema ABS de serie",
            "Suspensión telescópica delantera",
            "Panel LCD multifunción",
            "Parabrisas ajustable",
            "Capacidad de tanque: 17.3 litros"
        ],
        stock: 9,
        featured: true
    }
];

// Cargar productos destacados en la página principal
document.addEventListener('DOMContentLoaded', function() {
    const featuredContainer = document.getElementById('featured-products-container');
    
    if(featuredContainer) {
        // Filtrar productos destacados
        const featuredProducts = products.filter(product => product.featured);
        
        // Generar HTML para cada producto
        featuredProducts.forEach(product => {
            const productCard = createProductCard(product);
            featuredContainer.appendChild(productCard);
        });
        
        // Configurar filtros
        setupFilters();
    }
});

// Crear tarjeta de producto
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'col-md-4 mb-4 product-card';
    card.dataset.category = product.category;
    card.dataset.brand = product.brand;
    card.dataset.price = product.price;
    
    card.innerHTML = `
        <div class="card h-100 border-0 shadow-sm">
            <div class="position-relative">
                <img src="${product.image || 'img/products/placeholder.jpg'}" class="card-img-top" alt="${product.name}" style="height: 200px; object-fit: cover;">
                <div class="position-absolute top-0 start-0 m-3">
                    <span class="badge bg-primary">${getCategoryName(product.category)}</span>
                </div>
            </div>
            <div class="card-body d-flex flex-column">
                <h5 class="card-title">${product.name}</h5>
                <p class="card-text text-muted small mb-0">Marca: ${product.brand}</p>
                <p class="card-text text-primary fw-bold mt-2 mb-3">$${product.price.toLocaleString()}</p>
                <p class="card-text">${product.description.slice(0, 80)}...</p>
                <div class="mt-auto d-flex justify-content-between">
                    <a href="detalle-producto.html?id=${product.id}" class="btn btn-outline-secondary btn-sm">
                        <i class="fas fa-eye me-1"></i>Ver detalles
                    </a>
                    <a href="calculadora.html?modelo=${product.id}" class="btn btn-primary btn-sm">
                        <i class="fas fa-calculator me-1"></i>Financiar
                    </a>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

// Obtener nombre legible de categoría
function getCategoryName(category) {
    const categories = {
        'motocicletas': 'Motocicleta',
        'vehiculos': 'Vehículo',
        'maquinaria': 'Maquinaria'
    };
    
    return categories[category] || category;
}

// Configurar filtros
function setupFilters() {
    // Filtro de categoría
    const categoryFilter = document.getElementById('categoryFilter');
    if(categoryFilter) {
        const categoryMenu = categoryFilter.nextElementSibling;
        const categoryOptions = categoryMenu.querySelectorAll('.dropdown-item');
        
        categoryOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                const selectedCategory = this.textContent.toLowerCase();
                filterProducts('category', selectedCategory);
                categoryFilter.textContent = this.textContent;
            });
        });
    }
    
    // Filtro de marca
    const brandFilter = document.getElementById('brandFilter');
    if(brandFilter) {
        const brandMenu = brandFilter.nextElementSibling;
        const brandOptions = brandMenu.querySelectorAll('.dropdown-item');
        
        brandOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                const selectedBrand = this.textContent;
                filterProducts('brand', selectedBrand);
                brandFilter.textContent = this.textContent;
            });
        });
    }
    
    // Filtro de precio
    const priceFilter = document.getElementById('priceFilter');
    if(priceFilter) {
        const priceMenu = priceFilter.nextElementSibling;
        const priceOptions = priceMenu.querySelectorAll('.dropdown-item');
        
        priceOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                const selectedPrice = this.textContent;
                
                const container = document.getElementById('featured-products-container');
                const cards = Array.from(container.querySelectorAll('.product-card'));
                
                if(selectedPrice === 'Menor precio') {
                    cards.sort((a, b) => parseInt(a.dataset.price) - parseInt(b.dataset.price));
                } else {
                    cards.sort((a, b) => parseInt(b.dataset.price) - parseInt(a.dataset.price));
                }
                
                container.innerHTML = '';
                cards.forEach(card => container.appendChild(card));
                
                priceFilter.textContent = this.textContent;
            });
        });
    }
}

// Filtrar productos
function filterProducts(filterType, filterValue) {
    const container = document.getElementById('featured-products-container');
    const cards = container.querySelectorAll('.product-card');
    
    cards.forEach(card => {
        if(filterValue === 'todos' || filterValue === 'todas') {
            card.style.display = 'block';
        } else {
            if(filterType === 'category') {
                const category = card.dataset.category;
                
                if(filterValue === 'motocicletas' && category === 'motocicletas') {
                    card.style.display = 'block';
                } else if(filterValue === 'vehículos' && category === 'vehiculos') {
                    card.style.display = 'block';
                } else if(filterValue === 'maquinaria' && category === 'maquinaria') {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            } else if(filterType === 'brand') {
                const brand = card.dataset.brand;
                card.style.display = (brand === filterValue) ? 'block' : 'none';
            }
        }
    });
} 