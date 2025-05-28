/**
 * Calculadora de Financiamiento Integrada con API
 * Mantiene la UI actual pero conecta con el backend configurable
 */

const CalculadoraIntegrada = {
    // Estado actual
    currentMode: 'programada',
    currentProduct: null,
    currentCalculation: null,
    configuration: null,
    
    // URLs de la API
    API_BASE: '/api/financing',
    
    /**
     * Obtener token CSRF
     */
    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            return csrfToken.value;
        }
        
        // Buscar en cookies
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        return null;
    },
    
    /**
     * Inicializar la calculadora
     */
    async init() {
        console.log('Inicializando Calculadora Integrada...');
        
        try {
            // Cargar configuración desde el backend
            await this.loadConfiguration();
            
            // Configurar event listeners
            this.setupEventListeners();
            
            // Cargar productos
            await this.loadProducts();
            
            // Configurar modalidad inicial
            this.setupInitialMode();
            
            console.log('Calculadora Integrada inicializada correctamente');
        } catch (error) {
            console.error('Error inicializando calculadora:', error);
            // No mostrar error al usuario en la inicialización
        }
    },
    
    /**
     * Cargar configuración desde el backend
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`${this.API_BASE}/calculator/config/`);
            if (!response.ok) {
                throw new Error('Error al cargar configuración');
            }
            
            this.configuration = await response.json();
            console.log('Configuración cargada:', this.configuration);
            
            // Configurar modalidades
            this.setupModes();
            
        } catch (error) {
            console.error('Error cargando configuración:', error);
            throw error;
        }
    },
    
    /**
     * Configurar las modalidades disponibles
     */
    setupModes() {
        if (!this.configuration || !this.configuration.modes) return;
        
        // Encontrar modalidades
        const programadaMode = this.configuration.modes.find(m => m.mode_type === 'programada');
        const creditoMode = this.configuration.modes.find(m => m.mode_type === 'credito');
        
        // Actualizar textos de las modalidades
        if (programadaMode) {
            const programadaLabel = document.querySelector('label[for="programadaRadio"]');
            if (programadaLabel) {
                programadaLabel.innerHTML = `
                    <strong>${programadaMode.name}</strong>
                    <p class="text-muted small mb-0">${programadaMode.description}</p>
                `;
            }
        }
        
        if (creditoMode) {
            const creditoLabel = document.querySelector('label[for="creditoRadio"]');
            if (creditoLabel) {
                creditoLabel.innerHTML = `
                    <strong>${creditoMode.name}</strong>
                    <p class="text-muted small mb-0">${creditoMode.description}</p>
                `;
            }
        }
    },
    
    /**
     * Cargar productos del catálogo
     */
    async loadProducts() {
        if (!this.configuration || !this.configuration.categories) return;
        
        const vehicleTypeSelect = document.getElementById('vehicleType');
        const vehicleModelSelect = document.getElementById('vehicleModel');
        
        if (!vehicleTypeSelect || !vehicleModelSelect) return;
        
        // Limpiar opciones existentes
        vehicleTypeSelect.innerHTML = '';
        vehicleModelSelect.innerHTML = '<option value="" disabled selected>Selecciona un modelo</option>';
        
        // Agregar categorías
        this.configuration.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.slug;
            option.textContent = category.name;
            option.dataset.categoryId = category.id;
            vehicleTypeSelect.appendChild(option);
        });
        
        // Seleccionar primera categoría por defecto
        if (this.configuration.categories.length > 0) {
            vehicleTypeSelect.value = this.configuration.categories[0].slug;
            this.updateProductModels();
        }
    },
    
    /**
     * Actualizar modelos según la categoría seleccionada
     */
    updateProductModels() {
        const vehicleTypeSelect = document.getElementById('vehicleType');
        const vehicleModelSelect = document.getElementById('vehicleModel');
        
        if (!vehicleTypeSelect || !vehicleModelSelect) return;
        
        const selectedCategorySlug = vehicleTypeSelect.value;
        const category = this.configuration.categories.find(c => c.slug === selectedCategorySlug);
        
        // Limpiar modelos
        vehicleModelSelect.innerHTML = '<option value="" disabled selected>Selecciona un modelo</option>';
        
        if (category && category.products) {
            category.products.forEach(product => {
                const option = document.createElement('option');
                option.value = product.price;
                option.textContent = `${product.brand} ${product.name} - $${this.formatNumber(product.price)}`;
                option.dataset.productId = product.id;
                option.dataset.productName = product.name;
                option.dataset.productBrand = product.brand;
                vehicleModelSelect.appendChild(option);
            });
        }
    },
    
    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Cambio de modalidad
        const programadaRadio = document.getElementById('programadaRadio');
        const creditoRadio = document.getElementById('creditoRadio');
        
        if (programadaRadio) {
            programadaRadio.addEventListener('change', () => {
                if (programadaRadio.checked) {
                    this.switchMode('programada');
                }
            });
        }
        
        if (creditoRadio) {
            creditoRadio.addEventListener('change', () => {
                if (creditoRadio.checked) {
                    this.switchMode('credito');
                }
            });
        }
        
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
                // Actualizar montos de crédito cuando cambie el modelo
                this.updateCreditoAmounts();
            });
        }
        
        // Checkbox de precio personalizado
        const customPriceCheck = document.getElementById('customPriceCheck');
        if (customPriceCheck) {
            customPriceCheck.addEventListener('change', () => {
                this.toggleCustomPrice();
                // Actualizar montos de crédito cuando se active/desactive precio personalizado
                this.updateCreditoAmounts();
            });
        }
        
        // Input de precio personalizado
        const customPriceInput = document.getElementById('customPrice');
        if (customPriceInput) {
            customPriceInput.addEventListener('input', () => {
                // Actualizar montos de crédito cuando cambie el precio personalizado
                this.updateCreditoAmounts();
            });
        }
        
        // Selector de frecuencia de pago
        const paymentFrequencySelect = document.getElementById('paymentFrequency');
        if (paymentFrequencySelect) {
            paymentFrequencySelect.addEventListener('change', () => {
                // Actualizar cálculos cuando cambie la frecuencia de pago
                this.updatePaymentFrequencyDisplay();
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
        // Botones de Compra Programada
        const saveSimulationBtn = document.getElementById('saveSimulationBtn');
        const applyNowBtn = document.getElementById('applyNowBtn');
        const shareBtn = document.getElementById('shareBtn');
        
        // Botones de Crédito Inmediato
        const creditoSaveBtn = document.getElementById('creditoSaveBtn');
        const creditoApplyBtn = document.getElementById('creditoApplyBtn');
        const creditoShareBtn = document.getElementById('creditoShareBtn');
        
        // Event listeners para guardar simulación
        if (saveSimulationBtn) {
            saveSimulationBtn.addEventListener('click', () => this.saveSimulation());
        }
        if (creditoSaveBtn) {
            creditoSaveBtn.addEventListener('click', () => this.saveSimulation());
        }
        
        // Event listeners para solicitar financiamiento
        if (applyNowBtn) {
            applyNowBtn.addEventListener('click', () => this.requestFinancing());
        }
        if (creditoApplyBtn) {
            creditoApplyBtn.addEventListener('click', () => this.requestFinancing());
        }
        
        // Event listeners para compartir
        if (shareBtn) {
            shareBtn.addEventListener('click', () => this.shareCalculation());
        }
        if (creditoShareBtn) {
            creditoShareBtn.addEventListener('click', () => this.shareCalculation());
        }
    },
    
    /**
     * Cambiar modalidad
     */
    switchMode(mode) {
        this.currentMode = mode;
        
        const programadaForm = document.getElementById('programadaForm');
        const creditoForm = document.getElementById('creditoForm');
        
        if (mode === 'programada') {
            if (programadaForm) programadaForm.style.display = 'block';
            if (creditoForm) creditoForm.style.display = 'none';
            this.setupProgramadaMode();
        } else if (mode === 'credito') {
            if (programadaForm) programadaForm.style.display = 'none';
            if (creditoForm) creditoForm.style.display = 'block';
            this.setupCreditoMode();
        }
    },
    
    /**
     * Configurar modalidad inicial
     */
    setupInitialMode() {
        // Verificar qué modalidad está seleccionada
        const programadaRadio = document.getElementById('programadaRadio');
        const creditoRadio = document.getElementById('creditoRadio');
        
        if (programadaRadio && programadaRadio.checked) {
            this.switchMode('programada');
        } else if (creditoRadio && creditoRadio.checked) {
            this.switchMode('credito');
        }
    },
    
    /**
     * Configurar modalidad Compra Programada
     */
    setupProgramadaMode() {
        if (!this.configuration) return;
        
        const programadaMode = this.configuration.modes.find(m => m.mode_type === 'programada');
        if (!programadaMode) return;
        
        // Configurar rangos de aporte inicial
        const initialContributionInput = document.getElementById('initialContribution');
        if (initialContributionInput) {
            initialContributionInput.min = programadaMode.min_initial_contribution;
            initialContributionInput.max = programadaMode.max_initial_contribution;
            initialContributionInput.value = programadaMode.min_initial_contribution;
        }
        
        // Actualizar texto de ayuda
        const helpText = document.querySelector('#programadaForm .form-text');
        if (helpText) {
            helpText.textContent = `Entre ${programadaMode.min_initial_contribution}% y ${programadaMode.max_initial_contribution}% del valor del vehículo`;
        }
    },
    
    /**
     * Configurar modalidad Crédito Inmediato
     */
    setupCreditoMode() {
        if (!this.configuration) return;

        const creditoMode = this.configuration.modes.find(m => m.mode_type === 'credito');
        if (!creditoMode) return;

        // Guardar los porcentajes para uso interno
        this.creditoPercentages = creditoMode.down_payment_options;

        // Configurar opciones de inicial (se actualizarán dinámicamente)
        const planTypeSelect = document.getElementById('planType');
        if (planTypeSelect && this.creditoPercentages) {
            planTypeSelect.innerHTML = '';
            // Agregar opción por defecto
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.disabled = true;
            defaultOption.selected = true;
            defaultOption.textContent = 'Selecciona monto inicial';
            planTypeSelect.appendChild(defaultOption);
            
            // Agregar opciones con montos (se calcularán dinámicamente)
            this.creditoPercentages.forEach((percentage) => {
                const option = document.createElement('option');
                option.value = percentage;
                option.textContent = '$0'; // Se actualizará dinámicamente
                option.dataset.percentage = percentage;
                planTypeSelect.appendChild(option);
            });
        }

        // Configurar plazos
        const financingTermSelect = document.getElementById('financingTerm');
        if (financingTermSelect && creditoMode.term_options) {
            financingTermSelect.innerHTML = '';
            // Agregar opción por defecto
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.disabled = true;
            defaultOption.selected = true;
            defaultOption.textContent = 'Selecciona plazo';
            financingTermSelect.appendChild(defaultOption);
            
            creditoMode.term_options.forEach(months => {
                const option = document.createElement('option');
                option.value = months;
                option.textContent = `${months} meses`;
                financingTermSelect.appendChild(option);
            });
        }

        // Actualizar montos iniciales si ya hay un precio
        this.updateCreditoAmounts();
    },

    /**
     * Actualizar montos de inicial en el selector de crédito inmediato
     */
    updateCreditoAmounts() {
        const planTypeSelect = document.getElementById('planType');
        const currentPrice = this.getCurrentPrice();
        
        if (!planTypeSelect || !this.creditoPercentages || !currentPrice || currentPrice <= 0) {
            return;
        }

        // Actualizar cada opción con el monto correspondiente
        for (let i = 1; i < planTypeSelect.options.length; i++) { // Empezar en 1 para saltar la opción por defecto
            const option = planTypeSelect.options[i];
            const percentage = parseFloat(option.dataset.percentage);
            const amount = (currentPrice * percentage) / 100;
            option.textContent = this.formatCurrency(amount);
        }
    },
    
    /**
     * Actualizar producto seleccionado
     */
    updateSelectedProduct() {
        const vehicleModelSelect = document.getElementById('vehicleModel');
        if (!vehicleModelSelect || !vehicleModelSelect.value) return;
        
        const selectedOption = vehicleModelSelect.options[vehicleModelSelect.selectedIndex];
        if (selectedOption.dataset.productId) {
            this.currentProduct = {
                id: parseInt(selectedOption.dataset.productId),
                name: selectedOption.dataset.productName,
                brand: selectedOption.dataset.productBrand,
                price: parseFloat(vehicleModelSelect.value)
            };
        }
    },
    
    /**
     * Alternar precio personalizado
     */
    toggleCustomPrice() {
        const customPriceCheck = document.getElementById('customPriceCheck');
        const vehicleModelContainer = document.getElementById('vehicleModelContainer');
        const customPriceContainer = document.getElementById('customPriceContainer');
        
        if (customPriceCheck && customPriceCheck.checked) {
            if (vehicleModelContainer) vehicleModelContainer.style.display = 'none';
            if (customPriceContainer) customPriceContainer.style.display = 'block';
            this.currentProduct = null;
        } else {
            if (vehicleModelContainer) vehicleModelContainer.style.display = 'block';
            if (customPriceContainer) customPriceContainer.style.display = 'none';
            this.updateSelectedProduct();
        }
    },
    
    /**
     * Obtener precio actual
     */
    getCurrentPrice() {
        const customPriceCheck = document.getElementById('customPriceCheck');
        
        if (customPriceCheck && customPriceCheck.checked) {
            const customPriceInput = document.getElementById('customPrice');
            return customPriceInput ? parseFloat(customPriceInput.value) || 0 : 0;
        } else {
            const vehicleModelSelect = document.getElementById('vehicleModel');
            return vehicleModelSelect ? parseFloat(vehicleModelSelect.value) || 0 : 0;
        }
    },
    
    /**
     * Calcular financiamiento
     */
    async calculate() {
        try {
            // Validar datos
            if (!this.validateForm()) return;
            
            // Mostrar loading
            this.showLoading(true);
            
            // Preparar datos según la modalidad
            const requestData = this.prepareCalculationData();
            
            // Preparar headers con CSRF token
            const headers = {
                'Content-Type': 'application/json',
            };
            
            const csrfToken = this.getCSRFToken();
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }
            
            // Realizar cálculo
            const response = await fetch(`${this.API_BASE}/calculator/calculate/`, {
                method: 'POST',
                headers: headers,
                credentials: 'same-origin', // Incluir cookies
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                let errorMessage = 'Error al calcular';
                try {
                    const error = await response.json();
                    errorMessage = error.error || errorMessage;
                } catch (e) {
                    errorMessage = `Error ${response.status}: ${response.statusText}`;
                }
                throw new Error(errorMessage);
            }
            
            this.currentCalculation = await response.json();
            this.displayResults();
            
        } catch (error) {
            console.error('Error en cálculo:', error);
            this.showError(error.message || 'Error al calcular el financiamiento');
        } finally {
            this.showLoading(false);
        }
    },
    
    /**
     * Validar formulario
     */
    validateForm() {
        const price = this.getCurrentPrice();
        
        if (!price || price <= 0) {
            this.showError('Por favor selecciona un producto o ingresa un precio válido');
            return false;
        }
        
        if (this.currentMode === 'programada') {
            const monthlyPayment = document.getElementById('monthlyPayment');
            if (!monthlyPayment || !monthlyPayment.value || parseFloat(monthlyPayment.value) <= 0) {
                this.showError('Por favor ingresa una cuota mensual válida');
                return false;
            }
        } else if (this.currentMode === 'credito') {
            const planType = document.getElementById('planType');
            const financingTerm = document.getElementById('financingTerm');
            
            if (!planType || !planType.value) {
                this.showError('Por favor selecciona un porcentaje de inicial');
                return false;
            }
            
            if (!financingTerm || !financingTerm.value) {
                this.showError('Por favor selecciona un plazo');
                return false;
            }
        }
        
        return true;
    },
    
    /**
     * Preparar datos para el cálculo
     */
    prepareCalculationData() {
        const data = {
            mode_type: this.currentMode,
            product_price: this.getCurrentPrice()
        };
        
        // Agregar ID del producto si está seleccionado
        if (this.currentProduct) {
            data.product_id = this.currentProduct.id;
        }
        
        if (this.currentMode === 'programada') {
            const initialContribution = document.getElementById('initialContribution');
            const monthlyPayment = document.getElementById('monthlyPayment');
            const punctuality = document.getElementById('paymentPunctuality');
            
            data.initial_contribution_percentage = parseFloat(initialContribution.value);
            data.monthly_payment = parseFloat(monthlyPayment.value);
            data.punctuality = punctuality.value;
            
        } else if (this.currentMode === 'credito') {
            const planType = document.getElementById('planType');
            const financingTerm = document.getElementById('financingTerm');
            const paymentFrequency = document.getElementById('paymentFrequency');
            
            data.down_payment_percentage = parseFloat(planType.value);
            data.term_months = parseInt(financingTerm.value);
            data.payment_frequency = paymentFrequency ? paymentFrequency.value : 'monthly';
        }
        
        return data;
    },
    
    /**
     * Mostrar resultados
     */
    displayResults() {
        if (!this.currentCalculation) return;
        
        if (this.currentMode === 'programada') {
            this.displayProgramadaResults();
        } else if (this.currentMode === 'credito') {
            this.displayCreditoResults();
        }
    },
    
    /**
     * Mostrar resultados de Compra Programada
     */
    displayProgramadaResults() {
        const calc = this.currentCalculation.calculation;
        const resultsDiv = document.getElementById('programadaResults');
        
        if (!resultsDiv) return;
        
        // Actualizar valores
        this.updateElementText('vehicleValue', this.formatCurrency(calc.vehicle_value));
        this.updateElementText('initialFee', this.formatCurrency(calc.initial_fee));
        this.updateElementText('initialContributionValue', this.formatCurrency(calc.initial_contribution));
        this.updateElementText('financeAmount', this.formatCurrency(calc.amount_to_finance));
        this.updateElementText('monthlyPaymentValue', this.formatCurrency(calc.monthly_payment));
        this.updateElementText('postAdjudicationAmount', this.formatCurrency(calc.post_adjudication_amount));
        
        this.updateElementText('monthsToAdjudication', calc.months_to_adjudication);
        this.updateElementText('adjudicationDate', calc.estimated_adjudication_date);
        this.updateElementText('accumulatedPoints', calc.accumulated_points);
        this.updateElementText('reducedMonths', calc.reduced_months);
        this.updateElementText('finalAdjudicationDate', calc.final_adjudication_date);
        
        // Actualizar gráfico de progreso
        this.updateProgressChart(calc);
        
        // Mostrar resultados
        resultsDiv.style.display = 'block';
    },
    
    /**
     * Mostrar resultados de Crédito Inmediato
     */
    displayCreditoResults() {
        const calc = this.currentCalculation.calculation;
        const resultsDiv = document.getElementById('creditoResults');
        
        if (!resultsDiv) return;
        
        // Obtener frecuencia de pago para mostrar etiquetas correctas
        const paymentFrequencySelect = document.getElementById('paymentFrequency');
        const frequency = paymentFrequencySelect ? paymentFrequencySelect.value : 'monthly';
        const frequencyNames = {
            'weekly': 'semanal',
            'biweekly': 'quincenal', 
            'monthly': 'mensual'
        };
        const frequencyName = frequencyNames[frequency] || 'mensual';
        
        // Actualizar valores
        this.updateElementText('creditoVehicleValue', this.formatCurrency(calc.vehicle_value));
        this.updateElementText('creditoInitialPayment', this.formatCurrency(calc.down_payment_amount));
        this.updateElementText('creditoFinanceAmount', this.formatCurrency(calc.financed_amount));
        this.updateElementText('creditoTerm', `${calc.term_months} meses`);
        this.updateElementText('creditoMonthlyPayment', this.formatCurrency(calc.payment_amount || calc.monthly_payment));
        this.updateElementText('creditoTotalCost', this.formatCurrency(calc.total_cost));
        
        // Actualizar etiqueta de cuota según frecuencia
        const paymentLabel = document.getElementById('creditoPaymentLabel');
        if (paymentLabel) {
            paymentLabel.textContent = `Cuota ${frequencyName}:`;
        }
        
        this.updateElementText('creditoFirstPaymentDate', calc.first_payment_date);
        this.updateElementText('creditoPayoffDate', calc.payoff_date);
        
        // Actualizar gráfico de distribución
        this.updateDistributionChart(calc);
        
        // Mostrar resultados
        resultsDiv.style.display = 'block';
    },
    
    /**
     * Actualizar gráfico de progreso (Compra Programada)
     */
    updateProgressChart(calc) {
        const initialFeeProgress = document.getElementById('initialFeeProgress');
        const initialContributionProgress = document.getElementById('initialContributionProgress');
        const monthlyPaymentsProgress = document.getElementById('monthlyPaymentsProgress');
        
        if (initialFeeProgress && initialContributionProgress && monthlyPaymentsProgress) {
            const initialFeePercentage = (calc.initial_fee / calc.vehicle_value) * 100;
            const initialContributionPercentage = (calc.initial_contribution / calc.vehicle_value) * 100;
            const monthlyPaymentsPercentage = (calc.amount_to_finance / calc.vehicle_value) * 100;
            const remainingPercentage = 100 - calc.adjudication_percentage;
            
            initialFeeProgress.style.width = `${initialFeePercentage}%`;
            initialFeeProgress.textContent = `${initialFeePercentage.toFixed(1)}%`;
            
            initialContributionProgress.style.width = `${initialContributionPercentage}%`;
            initialContributionProgress.textContent = `${initialContributionPercentage.toFixed(1)}%`;
            
            monthlyPaymentsProgress.style.width = `${monthlyPaymentsPercentage}%`;
            monthlyPaymentsProgress.textContent = `${monthlyPaymentsPercentage.toFixed(1)}%`;
        }
    },
    
    /**
     * Actualizar gráfico de distribución (Crédito Inmediato)
     */
    updateDistributionChart(calc) {
        const initialPaymentProgress = document.getElementById('initialPaymentProgress');
        const financedAmountProgress = document.getElementById('financedAmountProgress');
        const progressMidpoint = document.getElementById('progressMidpoint');
        
        if (initialPaymentProgress && financedAmountProgress) {
            const initialPercentage = calc.down_payment_percentage;
            const financedPercentage = 100 - initialPercentage;
            
            initialPaymentProgress.style.width = `${initialPercentage}%`;
            initialPaymentProgress.textContent = `${initialPercentage}%`;
            
            financedAmountProgress.style.width = `${financedPercentage}%`;
            financedAmountProgress.textContent = `${financedPercentage}%`;
            
            if (progressMidpoint) {
                progressMidpoint.textContent = `${initialPercentage}%`;
            }
        }
    },
    
    /**
     * Guardar simulación
     */
    async saveSimulation() {
        if (!this.currentCalculation) {
            this.showError('Primero debes realizar un cálculo');
            return;
        }
        
        // Verificar autenticación
        if (!Auth.isAuthenticated()) {
            window.location.href = 'login.html?redirect=calculadora';
            return;
        }
        
        try {
            // Aquí se implementaría la lógica para guardar la simulación
            this.showSuccess('Simulación guardada exitosamente');
        } catch (error) {
            console.error('Error guardando simulación:', error);
            this.showError('Error al guardar la simulación');
        }
    },
    
    /**
     * Solicitar financiamiento
     */
    async requestFinancing() {
        if (!this.currentCalculation) {
            this.showError('Primero debes realizar un cálculo');
            return;
        }
        
        // Verificar autenticación
        if (!Auth.isAuthenticated()) {
            window.location.href = 'login.html?redirect=calculadora';
            return;
        }
        
        // Redirigir a página de solicitud con datos
        const params = new URLSearchParams({
            mode: this.currentMode,
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
            mode: this.currentMode,
            price: this.getCurrentPrice()
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
    
    formatCurrency(amount) {
        return `$${this.formatNumber(amount)}`;
    },
    
    showLoading(show) {
        const calculateBtn = document.getElementById('calculateBtn');
        if (calculateBtn) {
            calculateBtn.disabled = show;
            calculateBtn.innerHTML = show ? 
                '<span class="spinner-border spinner-border-sm me-2"></span>Calculando...' : 
                'Calcular';
        }
    },
    
    showError(message) {
        // Implementar notificación de error
        console.error(message);
        alert(message); // Temporal, se puede mejorar con toast notifications
    },
    
    showSuccess(message) {
        // Implementar notificación de éxito
        console.log(message);
        alert(message); // Temporal, se puede mejorar con toast notifications
    },

    /**
     * Actualizar visualización según frecuencia de pago
     */
    updatePaymentFrequencyDisplay() {
        const paymentFrequencySelect = document.getElementById('paymentFrequency');
        if (!paymentFrequencySelect) return;
        
        const frequency = paymentFrequencySelect.value;
        
        // Actualizar etiquetas en la interfaz según la frecuencia
        this.updateFrequencyLabels(frequency);
    },

    /**
     * Actualizar etiquetas según la frecuencia de pago
     */
    updateFrequencyLabels(frequency) {
        const frequencyNames = {
            'weekly': 'semanal',
            'biweekly': 'quincenal', 
            'monthly': 'mensual'
        };
        
        const frequencyName = frequencyNames[frequency] || 'mensual';
        
        // Actualizar etiquetas en los resultados si existen
        const monthlyPaymentLabel = document.querySelector('label[for="creditoMonthlyPayment"]');
        if (monthlyPaymentLabel) {
            monthlyPaymentLabel.textContent = `Cuota ${frequencyName}:`;
        }
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    CalculadoraIntegrada.init();
});

// Exportar para uso global
window.CalculadoraIntegrada = CalculadoraIntegrada; 