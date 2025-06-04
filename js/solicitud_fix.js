/**
 * FIX SOLICITUD DE FINANCIAMIENTO
 * Solución independiente que no requiere autenticación
 */

const SolicitudFix = {
    currentStep: 1,
    totalSteps: 4,
    calculationData: null,

    init() {
        console.log('🔧 SolicitudFix inicializando...');
        
        // Cargar datos inmediatamente
        this.loadAndRenderData();
        
        // Configurar navegación de pasos
        this.setupStepNavigation();
        
        // También intentar cada segundo por si el módulo original se carga después
        const interval = setInterval(() => {
            if (window.FinancingRequest && window.FinancingRequest.calculationData) {
                console.log('✅ FinancingRequest ya tiene datos');
                clearInterval(interval);
            } else {
                this.loadAndRenderData();
            }
        }, 1000);
        
        // Parar después de 10 intentos
        setTimeout(() => clearInterval(interval), 10000);
    },

    setupStepNavigation() {
        // Crear un FinancingRequest mock para compatibilidad
        if (!window.FinancingRequest) {
            window.FinancingRequest = {
                currentStep: 1,
                totalSteps: 4,
                calculationData: null,
                
                nextStep: () => this.nextStep(),
                prevStep: () => this.prevStep(),
                renderCurrentStep: () => this.renderCurrentStep(),
                validateCurrentStep: () => this.validateCurrentStep(),
                submitRequest: () => this.submitRequest()
            };
            console.log('✅ FinancingRequest mock creado');
        }
    },

    nextStep() {
        console.log(`🔄 nextStep() llamado - paso actual: ${this.currentStep}`);
        
        if (this.currentStep < this.totalSteps) {
            // Validar paso actual antes de continuar
            if (this.validateCurrentStep()) {
                this.currentStep++;
                this.renderCurrentStep();
                console.log(`✅ Avanzado al paso ${this.currentStep}`);
            } else {
                console.log('❌ Validación del paso falló');
            }
        }
    },

    prevStep() {
        console.log(`🔄 prevStep() llamado - paso actual: ${this.currentStep}`);
        
        if (this.currentStep > 1) {
            this.currentStep--;
            this.renderCurrentStep();
            console.log(`✅ Retrocedido al paso ${this.currentStep}`);
        }
    },

    validateCurrentStep() {
        switch (this.currentStep) {
            case 1:
                return this.calculationData !== null;
            case 2:
                return this.validatePersonalInfo();
            case 3:
                return true; // Documentos son opcionales
            case 4:
                return this.validateFinalStep();
            default:
                return true;
        }
    },

    validatePersonalInfo() {
        const employmentType = document.getElementById('employment_type');
        const monthlyIncome = document.getElementById('monthly_income');

        if (employmentType && !employmentType.value) {
            this.showError('Por favor seleccione el tipo de empleo');
            return false;
        }

        if (monthlyIncome && (!monthlyIncome.value || parseFloat(monthlyIncome.value) <= 0)) {
            this.showError('Por favor ingrese un ingreso mensual válido');
            return false;
        }

        return true;
    },

    validateFinalStep() {
        const termsAccept = document.getElementById('termsAccept');
        const dataConsent = document.getElementById('dataConsent');

        if (termsAccept && !termsAccept.checked) {
            this.showError('Debe aceptar los términos y condiciones');
            return false;
        }

        if (dataConsent && !dataConsent.checked) {
            this.showError('Debe autorizar el tratamiento de datos personales');
            return false;
        }

        return true;
    },

    renderCurrentStep() {
        console.log(`🎨 Renderizando paso ${this.currentStep}`);
        
        // Actualizar indicador de pasos
        for (let i = 1; i <= this.totalSteps; i++) {
            const step = document.getElementById(`step${i}`);
            const section = document.getElementById(`section${i}`);
            
            if (step) {
                if (i < this.currentStep) {
                    step.classList.add('completed');
                    step.classList.remove('active');
                } else if (i === this.currentStep) {
                    step.classList.add('active');
                    step.classList.remove('completed');
                } else {
                    step.classList.remove('active', 'completed');
                }
            }

            // Mostrar/ocultar secciones
            if (section) {
                if (i === this.currentStep) {
                    section.classList.add('active');
                    section.style.display = 'block';
                } else {
                    section.classList.remove('active');
                    section.style.display = 'none';
                }
            }
        }

        // Scroll al top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    async submitRequest() {
        console.log('📤 submitRequest() llamado');
        
        if (!this.validateCurrentStep()) {
            return;
        }

        // Simular envío de solicitud
        this.showSuccess('¡Solicitud enviada exitosamente! (Simulación)');
        
        // En implementación real, aquí iría la llamada API
        console.log('📊 Datos a enviar:', this.calculationData);
    },

    showError(message) {
        console.error('❌', message);
        alert(message); // Temporal - se puede mejorar con toast notifications
    },

    showSuccess(message) {
        console.log('✅', message);
        alert(message); // Temporal - se puede mejorar con toast notifications
    },
    
    loadAndRenderData() {
        const urlParams = new URLSearchParams(window.location.search);
        const calculationParam = urlParams.get('calculation');
        const modeParam = urlParams.get('mode');
        
        if (!calculationParam) {
            console.log('❌ No hay parámetro calculation');
            return;
        }
        
        try {
            // Intentar parsing directo primero
            let calculationData;
            try {
                calculationData = JSON.parse(calculationParam);
                console.log('✅ Parsing directo exitoso');
            } catch (e) {
                // Si falla, intentar con decodeURIComponent
                calculationData = JSON.parse(decodeURIComponent(calculationParam));
                console.log('✅ Parsing con decode exitoso');
            }
            
            console.log('📊 Datos cargados:', calculationData);
            
            // Guardar datos localmente
            this.calculationData = calculationData;
            
            // Renderizar directamente
            this.renderCalculationSummary(calculationData);
            
            // Si existe FinancingRequest, asignar los datos también
            if (window.FinancingRequest && window.FinancingRequest !== this) {
                window.FinancingRequest.calculationData = calculationData;
                console.log('✅ Datos asignados a FinancingRequest original');
            }
            
        } catch (error) {
            console.error('❌ Error en loadAndRenderData:', error);
        }
    },
    
    renderCalculationSummary(calculationData) {
        console.log('🎨 Renderizando resumen...');
        
        // Normalizar datos de diferentes fuentes
        const calc = calculationData.calculation || calculationData;
        const product = calculationData.product || {};
        const mode = calculationData.mode || {};
        
        // Mapear campos con diferentes nombres
        const productPrice = calc.vehicle_value || calc.product_price || product.price || 0;
        const downPaymentAmount = calc.down_payment_amount || 0;
        const downPaymentPercentage = calc.down_payment_percentage || 0;
        const paymentAmount = calc.payment_amount || calc.monthly_payment || 0;
        const numberOfPayments = calc.number_of_payments || calc.term_months || 0;
        const financedAmount = calc.financed_amount || (productPrice - downPaymentAmount);
        const totalAmount = calc.total_cost || calc.total_amount || productPrice;
        const paymentFrequency = calc.payment_frequency || 'monthly';
        
        // Función para formatear números
        const formatNumber = (num) => new Intl.NumberFormat('es-VE').format(num);
        const formatCurrency = (amount) => `$${formatNumber(amount)}`;
        const getFrequencyText = (freq) => {
            const frequencies = {
                'weekly': 'Semanal',
                'biweekly': 'Quincenal',
                'monthly': 'Mensual'
            };
            return frequencies[freq] || freq;
        };
        
        // Resumen principal
        const summaryContainer = document.getElementById('calculationSummary');
        if (summaryContainer) {
            summaryContainer.innerHTML = `
                <div class="row text-center">
                    <div class="col-md-3">
                        <h3>${formatCurrency(productPrice)}</h3>
                        <small>Precio del Producto</small>
                    </div>
                    <div class="col-md-3">
                        <h3>${formatCurrency(downPaymentAmount)}</h3>
                        <small>Inicial (${downPaymentPercentage}%)</small>
                    </div>
                    <div class="col-md-3">
                        <h3>${formatCurrency(paymentAmount)}</h3>
                        <small>Cuota ${getFrequencyText(paymentFrequency)}</small>
                    </div>
                    <div class="col-md-3">
                        <h3>${numberOfPayments}</h3>
                        <small>Número de Cuotas</small>
                    </div>
                </div>
            `;
            console.log('✅ Resumen principal renderizado');
        }
        
        // Detalles del producto
        const productContainer = document.getElementById('productDetails');
        if (productContainer) {
            productContainer.innerHTML = `
                <p><strong>Producto:</strong> ${product.name || 'Producto Seleccionado'}</p>
                <p><strong>Marca:</strong> ${product.brand || 'N/A'}</p>
                <p><strong>Categoría:</strong> ${product.category || 'N/A'}</p>
                <p><strong>Precio:</strong> ${formatCurrency(productPrice)}</p>
                <p><strong>Monto a Financiar:</strong> ${formatCurrency(financedAmount)}</p>
            `;
            console.log('✅ Detalles del producto renderizados');
        }
        
        // Detalles del financiamiento
        const financingContainer = document.getElementById('financingDetails');
        if (financingContainer) {
            financingContainer.innerHTML = `
                <p><strong>Modalidad:</strong> ${mode.name || 'Crédito Inmediato'}</p>
                <p><strong>Inicial:</strong> ${formatCurrency(downPaymentAmount)} (${downPaymentPercentage}%)</p>
                <p><strong>Monto Financiado:</strong> ${formatCurrency(financedAmount)}</p>
                <p><strong>Frecuencia:</strong> ${getFrequencyText(paymentFrequency)}</p>
                <p><strong>Plazo:</strong> ${numberOfPayments} cuotas</p>
                <p><strong>Cuota:</strong> ${formatCurrency(paymentAmount)}</p>
                <p><strong>Total a Pagar:</strong> ${formatCurrency(totalAmount)}</p>
            `;
            console.log('✅ Detalles del financiamiento renderizados');
        }
        
        console.log('🎉 Renderizado completo exitoso');
    }
};

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => SolicitudFix.init());
} else {
    SolicitudFix.init();
}

// Hacer disponible globalmente para debugging
window.SolicitudFix = SolicitudFix; 