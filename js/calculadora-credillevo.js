/**
 * Calculadora CrediLlevo - Sistema Único
 * Adaptada para el nuevo sistema de financiamiento único con LLEVO tokens
 */

const CalculadoraCrediLlevo = {
    // Estado actual
    currentProduct: null,
    currentCalculation: null,
    llevoRate: null,
    
    // URLs de la API
    API_BASE: '/api',
    
    /**
     * Inicializar la calculadora
     */
    async init() {
        console.log('Inicializando Calculadora CrediLlevo...');
        
        try {
            // Cargar tasa LLEVO actual
            await this.loadLlevoRate();
            
            // Configurar event listeners
            this.setupEventListeners();
            
            // Cargar productos
            await this.loadProducts();
            
            console.log('Calculadora CrediLlevo inicializada correctamente');
        } catch (error) {
            console.error('Error inicializando calculadora:', error);
            this.showError('Error al inicializar la calculadora');
        }
    },
    
    /**
     * Cargar tasa LLEVO actual
     */
    async loadLlevoRate() {
        try {
            console.log('Cargando tasa LLEVO desde API...');
            const response = await fetch('/api/financing/llevo/current-rate/');
            
            if (response.ok) {
                const result = await response.json();
                console.log('Respuesta completa del API:', result);
                
                if (result.success && result.data) {
                    // La estructura correcta según el backend
                    const llevoValue = result.data.llevo_value;
                    
                    if (llevoValue && !isNaN(llevoValue) && llevoValue > 0) {
                        this.llevoRate = parseFloat(llevoValue);
                        console.log('Tasa LLEVO cargada exitosamente:', this.llevoRate, 'VES por LLEVO');
                    } else {
                        throw new Error('Valor LLEVO no válido en la respuesta');
                    }
                } else {
                    throw new Error('Respuesta de API no exitosa: ' + (result.error || 'Unknown error'));
                }
            } else {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            
        } catch (error) {
            console.error('Error cargando tasa LLEVO:', error);
            // Usar tasa por defecto basada en la imagen del admin (4,159.50)
            this.llevoRate = 4159.50;
            console.log('Usando tasa por defecto:', this.llevoRate, 'VES por LLEVO');
        }
        
        // Mostrar cotización en la interfaz
        this.displayLlevoRate();
    },
    
    /**
     * Mostrar cotización LLEVO
     */
    displayLlevoRate() {
        const rateElement = document.getElementById('llevoRate');
        const currentRateElement = document.getElementById('currentRate');
        
        if (rateElement && currentRateElement) {
            // Verificar que la tasa es válida
            if (this.llevoRate && !isNaN(this.llevoRate) && this.llevoRate > 0) {
                currentRateElement.textContent = `1 LLEVO = ${this.formatNumber(this.llevoRate)} VES`;
                rateElement.className = 'alert alert-warning mb-4'; // Amarillo para cotización
            } else {
                // Fallback si no hay tasa válida
                currentRateElement.textContent = 'Cotización no disponible';
                rateElement.className = 'alert alert-secondary mb-4'; // Gris para error
            }
            rateElement.style.display = 'block';
        }
    },
    
    /**
     * Cargar productos del catálogo
     */
    async loadProducts() {
        try {
            let allProducts = [];
            let page = 1;
            let hasMore = true;

            // Intentar desde el endpoint específico de calculadora (sin paginación)
            let response = await fetch(`${this.API_BASE}/products/calculadora-products/`);

            if (response.ok) {
                // Endpoint de calculadora devuelve todos los productos sin paginación
                const data = await response.json();
                allProducts = Array.isArray(data) ? data : (data.results || data.products || []);
                console.log(`Endpoint calculadora: ${allProducts.length} productos cargados`);
            } else {
                // Fallback: cargar todas las páginas del endpoint general
                console.log('Usando endpoint general con paginación');

                while (hasMore) {
                    const paginatedResponse = await fetch(`${this.API_BASE}/products/products/?page=${page}&page_size=100`);

                    if (!paginatedResponse.ok) {
                        throw new Error('Error al cargar productos');
                    }

                    const data = await paginatedResponse.json();
                    const products = data.results || [];

                    if (products.length > 0) {
                        allProducts = allProducts.concat(products);
                        hasMore = data.next !== null && data.next !== undefined;
                        page++;
                        console.log(`Página ${page - 1}: ${products.length} productos, total acumulado: ${allProducts.length}`);
                    } else {
                        hasMore = false;
                    }
                }
            }

            if (allProducts.length > 0) {
                // Filtrar solo productos con price_llevo e inicial_llevos
                const validProducts = allProducts.filter(product =>
                    product.price_llevo && product.price_llevo > 0 &&
                    product.inicial_llevos && product.inicial_llevos > 0
                );

                if (validProducts.length > 0) {
                    console.log(`✅ ${validProducts.length} productos válidos cargados para calculadora (de ${allProducts.length} totales)`);
                    this.populateProductSelectors(validProducts);
                } else {
                    console.log('⚠️ No se encontraron productos con price_llevo e inicial_llevos configurados');
                    this.loadSampleProducts();
                }
            } else {
                // Usar productos de ejemplo si no hay datos
                console.log('⚠️ No se encontraron productos, usando ejemplos');
                this.loadSampleProducts();
            }

        } catch (error) {
            console.error('❌ Error cargando productos:', error);
            // Cargar productos de ejemplo en caso de error
            this.loadSampleProducts();
        }
    },
    
    /**
     * Cargar productos de ejemplo
     */
    loadSampleProducts() {
        const sampleProducts = [
            {
                id: 1,
                name: 'DK150',
                brand: 'Haojue',
                category_name: 'Motocicletas',
                price_llevo: 181,
                inicial_llevos: 30
            },
            {
                id: 2,
                name: 'DL160',
                brand: 'Haojue',
                category_name: 'Motocicletas',
                price_llevo: 215,
                inicial_llevos: 40
            },
            {
                id: 3,
                name: 'HJ150-8',
                brand: 'Haojue',
                category_name: 'Motocicletas',
                price_llevo: 192,
                inicial_llevos: 25
            },
            {
                id: 4,
                name: 'DR 650',
                brand: 'Suzuki',
                category_name: 'Motocicletas',
                price_llevo: 480,
                inicial_llevos: 100
            }
        ];
        
        this.populateProductSelectors(sampleProducts);
        console.log('Productos de ejemplo cargados');
    },
    
    /**
     * Poblar selectores de productos
     */
    populateProductSelectors(products) {
        const vehicleTypeSelect = document.getElementById('vehicleType');
        const vehicleModelSelect = document.getElementById('vehicleModel');
        
        if (!vehicleTypeSelect || !vehicleModelSelect) return;
        
        // Verificar si hay un producto preseleccionado en la URL
        const urlParams = new URLSearchParams(window.location.search);
        const preselectedModelId = urlParams.get('modelo');
        
        // Agrupar productos por categoría
        const categories = {};
        products.forEach(product => {
            if (!categories[product.category_name]) {
                categories[product.category_name] = [];
            }
            categories[product.category_name].push(product);
        });
        
        // Limpiar y poblar selector de categorías
        vehicleTypeSelect.innerHTML = '';
        Object.keys(categories).forEach(categoryName => {
            const option = document.createElement('option');
            option.value = categoryName.toLowerCase();
            option.textContent = categoryName;
            vehicleTypeSelect.appendChild(option);
        });
        
        // Buscar producto preseleccionado si hay parámetro en URL
        let preselectedProduct = null;
        if (preselectedModelId) {
            for (const categoryProducts of Object.values(categories)) {
                preselectedProduct = categoryProducts.find(p => p.id.toString() === preselectedModelId);
                if (preselectedProduct) break;
            }
        }
        
        // Seleccionar categoría apropiada
        if (preselectedProduct) {
            // Seleccionar categoría del producto preseleccionado
            vehicleTypeSelect.value = preselectedProduct.category_name.toLowerCase();
            this.updateProductModels(categories);
            
            // Preseleccionar el modelo después de un pequeño delay
            setTimeout(() => {
                const vehicleModelSelect = document.getElementById('vehicleModel');
                if (vehicleModelSelect) {
                    vehicleModelSelect.value = preselectedProduct.id.toString();
                    // Disparar evento change para actualizar cálculos
                    vehicleModelSelect.dispatchEvent(new Event('change'));
                    console.log(`Producto preseleccionado: ${preselectedProduct.name} (ID: ${preselectedProduct.id})`);
                }
            }, 100);
        } else if (Object.keys(categories).length > 0) {
            // Seleccionar primera categoría si no hay preselección
            vehicleTypeSelect.value = Object.keys(categories)[0].toLowerCase();
            this.updateProductModels(categories);
        }
    },
    
    /**
     * Actualizar modelos según la categoría seleccionada
     */
    updateProductModels(categories = null) {
        const vehicleTypeSelect = document.getElementById('vehicleType');
        const vehicleModelSelect = document.getElementById('vehicleModel');
        
        if (!vehicleTypeSelect || !vehicleModelSelect) return;
        
        const selectedCategory = vehicleTypeSelect.value;
        
        // Limpiar selector de modelos
        vehicleModelSelect.innerHTML = '<option value="" disabled selected>Selecciona un modelo</option>';
        
        if (categories) {
            // Usar categorías pasadas como parámetro
            const categoryKey = Object.keys(categories).find(key => key.toLowerCase() === selectedCategory);
            if (categoryKey) {
                categories[categoryKey].forEach(product => {
                    this.addProductOption(vehicleModelSelect, product);
                });
            }
        } else {
            // Recargar productos si no se pasan categorías
            this.loadProducts();
        }
    },
    
    /**
     * Agregar opción de producto al selector
     */
    addProductOption(select, product) {
        const option = document.createElement('option');
        option.value = product.id;
        option.textContent = `${product.brand || ''} ${product.name}`.trim();

        // Guardar datos del producto
        option.dataset.productId = product.id;
        option.dataset.productName = product.name;
        option.dataset.brand = product.brand || '';
        option.dataset.priceLlevo = product.price_llevo || 0;
        option.dataset.inicialLlevos = product.inicial_llevos || 0;
        option.dataset.cuotaMensualLlevos = product.cuota_mensual_llevos || 0;

        // Guardar datos del plan de financiamiento
        option.dataset.financingPlanName = product.financing_plan_name || 'CrediLlevo Inmediato';
        option.dataset.financingPlanSlug = product.financing_plan_slug || 'credillevo-inmediato';
        option.dataset.termMonths = product.financing_term_months || 24;

        select.appendChild(option);
    },
    
    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Cambio de tipo de producto
        const vehicleTypeSelect = document.getElementById('vehicleType');
        if (vehicleTypeSelect) {
            vehicleTypeSelect.addEventListener('change', () => {
                this.updateProductModels();
            });
        }
        
        // Cambio de modelo
        const vehicleModelSelect = document.getElementById('vehicleModel');
        if (vehicleModelSelect) {
            vehicleModelSelect.addEventListener('change', () => {
                this.updateSelectedProduct();
                this.calculateAutomatically();
            });
        }
        
        
        // Botón calcular
        const calculateBtn = document.getElementById('calculateBtn');
        if (calculateBtn) {
            calculateBtn.addEventListener('click', () => {
                this.calculate();
            });
        }
        
        // Botones de acción
        this.setupActionButtons();
    },
    
    /**
     * Configurar botones de acción
     */
    setupActionButtons() {
        const saveBtn = document.getElementById('saveSimulationBtn');
        const applyBtn = document.getElementById('applyNowBtn');
        const shareBtn = document.getElementById('shareBtn');
        
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveSimulation());
        }
        
        if (applyBtn) {
            applyBtn.addEventListener('click', () => this.requestFinancing());
        }
        
        if (shareBtn) {
            shareBtn.addEventListener('click', () => this.shareCalculation());
        }
    },
    
    /**
     * Actualizar producto seleccionado
     */
    updateSelectedProduct() {
        const vehicleModelSelect = document.getElementById('vehicleModel');
        if (!vehicleModelSelect || !vehicleModelSelect.value) {
            this.currentProduct = null;
            return;
        }

        const selectedOption = vehicleModelSelect.options[vehicleModelSelect.selectedIndex];
        this.currentProduct = {
            id: parseInt(selectedOption.dataset.productId),
            name: selectedOption.dataset.productName,
            brand: selectedOption.dataset.brand,
            price_llevo: parseInt(selectedOption.dataset.priceLlevo) || 0,
            inicial_llevos: parseInt(selectedOption.dataset.inicialLlevos) || 0,
            cuota_mensual_llevos: parseInt(selectedOption.dataset.cuotaMensualLlevos) || 0,
            financing_details: {
                plan_name: selectedOption.dataset.financingPlanName || 'CrediLlevo Inmediato',
                plan_slug: selectedOption.dataset.financingPlanSlug || 'credillevo-inmediato',
                term_months: parseInt(selectedOption.dataset.termMonths) || 24
            }
        };

        console.log('Producto seleccionado:', this.currentProduct);

        // Actualizar textos del plan en la interfaz
        this.updatePlanTexts(this.currentProduct.financing_details);
    },


    /**
     * Actualizar textos del plan en la interfaz
     */
    updatePlanTexts(financingDetails) {
        const planName = financingDetails.plan_name || 'CrediLlevo Inmediato';
        const termMonths = financingDetails.term_months || 24;

        // Actualizar título del plan en el header izquierdo
        this.updateElementText('selectedPlanTitle', planName);

        // Actualizar texto informativo
        this.updateElementText('planInfoText', `${termMonths} meses • Inicial fija por producto • Pagos en LLEVO`);

        // Actualizar título del plan en el header derecho
        this.updateElementText('planTitleHeader', planName);

        // Actualizar plazo en características del plan
        this.updateElementText('planTermText', `${termMonths} meses`);

        console.log('✨ Textos del plan actualizados:', { planName, termMonths });
    },


    /**
     * Calcular automáticamente cuando se selecciona un producto
     */
    calculateAutomatically() {
        if (this.currentProduct && this.currentProduct.price_llevo > 0) {
            this.calculate();
        } else {
            this.hideResults();
        }
    },
    
    /**
     * Calcular financiamiento CrediLlevo
     */
    calculate() {
        try {
            // Validar datos
            if (!this.validateForm()) return;
            
            // Calcular con producto seleccionado
            if (this.currentProduct) {
                this.calculateWithProduct();
            } else {
                this.showError('Por favor selecciona un producto');
            }
            
        } catch (error) {
            console.error('Error en cálculo:', error);
            this.showError('Error al calcular el financiamiento');
        }
    },
    
    /**
     * Calcular con producto seleccionado
     */
    calculateWithProduct() {
        const product = this.currentProduct;
        
        // Verificar que el producto tenga inicial configurada
        if (!product.inicial_llevos || product.inicial_llevos <= 0) {
            this.showError('Este producto no tiene inicial configurada. Contacta al administrador.');
            return;
        }

        // Obtener plan de financiamiento (plazo dinámico)
        const termMonths = product.financing_details?.term_months || 24;
        const planName = product.financing_details?.plan_name || 'CrediLlevo Inmediato';

        console.log('📋 Plan de financiamiento:', {
            planName,
            termMonths,
            financing_details: product.financing_details
        });

        // Calcular datos CrediLlevo
        const priceLlevo = product.price_llevo;
        const inicialLlevo = product.inicial_llevos;
        const montoFinanciar = priceLlevo - inicialLlevo;

        // Usar cuota manual si está configurada, sino calcular automáticamente
        let cuotaMensual;
        if (product.cuota_mensual_llevos && product.cuota_mensual_llevos > 0) {
            cuotaMensual = product.cuota_mensual_llevos;
            console.log('Usando cuota mensual manual:', cuotaMensual, 'LLEVO');
        } else {
            cuotaMensual = Math.round(montoFinanciar / termMonths); // Plazo dinámico según plan
            console.log(`Calculando cuota mensual automáticamente para ${termMonths} meses:`, cuotaMensual, 'LLEVO');
        }

        // Calcular fechas
        const hoy = new Date();
        const primeraCuota = new Date(hoy);
        primeraCuota.setMonth(primeraCuota.getMonth() + 1);

        this.currentCalculation = {
            product_id: product.id, // AGREGADO: ID del producto para solicitud
            productName: `${product.brand} ${product.name}`.trim(),
            priceLlevo: priceLlevo,
            inicialLlevo: inicialLlevo,
            montoFinanciar: montoFinanciar,
            cuotaMensual: cuotaMensual,
            plazoMeses: termMonths, // Plazo dinámico
            planName: planName, // Nombre del plan
            primeraCuota: this.formatDate(primeraCuota),
            llevoRate: this.llevoRate
        };
        
        this.displayResults();
    },
    
    
    /**
     * Mostrar resultados
     */
    displayResults() {
        if (!this.currentCalculation) return;

        const calc = this.currentCalculation;
        const resultsDiv = document.getElementById('credilleloResults');

        if (!resultsDiv) return;

        // Actualizar valores
        this.updateElementText('productName', calc.productName);
        this.updateElementText('productPriceLlevo', `${this.formatNumber(calc.priceLlevo)} LLEVO`);
        this.updateElementText('inicialLlevo', `${this.formatNumber(calc.inicialLlevo)} LLEVO`);
        this.updateElementText('montoFinanciar', `${this.formatNumber(calc.montoFinanciar)} LLEVO`);
        this.updateElementText('cuotaMensual', `${this.formatNumber(calc.cuotaMensual)} LLEVO`);
        this.updateElementText('primeraCuota', calc.primeraCuota);

        // Actualizar nombre del plan y plazo
        this.updateElementText('planName', calc.planName || 'CrediLlevo Inmediato');
        this.updateElementText('plazoMeses', `${calc.plazoMeses} meses`);

        // Mostrar resultados
        resultsDiv.style.display = 'block';
    },
    
    
    /**
     * Ocultar resultados
     */
    hideResults() {
        const resultsDiv = document.getElementById('credilleloResults');
        if (resultsDiv) {
            resultsDiv.style.display = 'none';
        }
    },
    
    /**
     * Validar formulario
     */
    validateForm() {
        // Validar producto seleccionado
        if (!this.currentProduct) {
            this.showError('Por favor selecciona un producto');
            return false;
        }
        
        return true;
    },
    
    /**
     * Guardar simulación
     */
    async saveSimulation() {
        if (!this.currentCalculation) {
            this.showError('Primero debes realizar un cálculo');
            return;
        }
        
        // Aquí se implementaría la lógica para guardar
        this.showSuccess('Simulación guardada (funcionalidad en desarrollo)');
    },
    
    /**
     * Solicitar financiamiento
     */
    async requestFinancing() {
        if (!this.currentCalculation) {
            this.showError('Primero debes realizar un cálculo');
            return;
        }
        
        // Redirigir a página de solicitud
        const params = new URLSearchParams({
            product_id: this.currentProduct.id,
            calculation: JSON.stringify(this.currentCalculation)
        });
        
        window.location.href = `solicitud-financiamiento.html?${params.toString()}`;
    },
    
    /**
     * Compartir cálculo
     */
    shareCalculation() {
        if (!this.currentCalculation) {
            this.showError('Primero debes realizar un cálculo');
            return;
        }
        
        // Crear URL para compartir
        const params = new URLSearchParams({
            product_id: this.currentProduct.id
        });
        
        const shareUrl = `${window.location.origin}/calculadora.html?${params.toString()}`;
        
        // Copiar al portapapeles
        navigator.clipboard.writeText(shareUrl).then(() => {
            this.showSuccess('Enlace copiado al portapapeles');
        }).catch(() => {
            this.showError('No se pudo copiar el enlace');
        });
    },
    
    /**
     * Utilidades
     */
    updateElementText(elementId, text) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = text;
        }
    },
    
    formatNumber(number) {
        return new Intl.NumberFormat('es-VE').format(number);
    },
    
    formatDate(date) {
        return date.toLocaleDateString('es-VE');
    },
    
    showError(message) {
        console.error(message);
        // Crear toast de error
        this.showToast(message, 'error');
    },
    
    showSuccess(message) {
        console.log(message);
        // Crear toast de éxito
        this.showToast(message, 'success');
    },
    
    showWarning(message) {
        console.warn(message);
        // Crear toast de advertencia
        this.showToast(message, 'warning');
    },
    
    showToast(message, type) {
        // Implementación simple de toast
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'warning'} position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'warning'} me-2"></i>
            ${message}
            <button type="button" class="btn-close float-end" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove después de 5 segundos
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    CalculadoraCrediLlevo.init();
});

// Exportar para uso global
window.CalculadoraCrediLlevo = CalculadoraCrediLlevo;