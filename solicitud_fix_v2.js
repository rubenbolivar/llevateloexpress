/**
 * FIX SOLICITUD DE FINANCIAMIENTO V2
 * Versión mejorada con persistencia de datos
 */

const SolicitudFixV2 = {
    currentStep: 1,
    totalSteps: 4,
    calculationData: null,

    init() {
        console.log('🔧 SolicitudFixV2 inicializando...');
        
        // Cargar datos con persistencia
        this.loadAndRenderDataWithPersistence();
        
        // Configurar navegación de pasos
        this.setupStepNavigation();
        
        // Interceptar envío del formulario
        this.setupFormSubmission();
        
        // Guardar datos periódicamente
        this.setupDataPersistence();
    },

    loadAndRenderDataWithPersistence() {
        const urlParams = new URLSearchParams(window.location.search);
        const calculationParam = urlParams.get('calculation');
        
        // Intentar cargar de URL primero
        if (calculationParam) {
            this.loadFromURL(calculationParam);
        } 
        // Si no hay en URL, intentar cargar de localStorage
        else {
            this.loadFromStorage();
        }
    },

    loadFromURL(calculationParam) {
        try {
            let calculationData;
            try {
                calculationData = JSON.parse(calculationParam);
                console.log('✅ Parsing directo exitoso');
            } catch (e) {
                calculationData = JSON.parse(decodeURIComponent(calculationParam));
                console.log('✅ Parsing con decode exitoso');
            }
            
            console.log('📊 Datos cargados desde URL:', calculationData);
            this.calculationData = calculationData;
            
            // Guardar en localStorage para persistencia
            localStorage.setItem('financing_calculation_data', JSON.stringify(calculationData));
            localStorage.setItem('financing_data_timestamp', Date.now().toString());
            
            this.renderCalculationSummary(calculationData);
            this.setupStepNavigation();
            
        } catch (error) {
            console.error('❌ Error cargando desde URL:', error);
            this.loadFromStorage();
        }
    },

    loadFromStorage() {
        try {
            const storedData = localStorage.getItem('financing_calculation_data');
            const timestamp = localStorage.getItem('financing_data_timestamp');
            
            // Verificar que los datos no sean muy antiguos (1 hora)
            const oneHour = 60 * 60 * 1000;
            const isRecent = timestamp && (Date.now() - parseInt(timestamp)) < oneHour;
            
            if (storedData && isRecent) {
                this.calculationData = JSON.parse(storedData);
                console.log('✅ Datos recuperados desde localStorage');
                this.renderCalculationSummary(this.calculationData);
                this.setupStepNavigation();
            } else {
                console.log('❌ No hay datos válidos en storage');
                this.showDataLostError();
            }
        } catch (error) {
            console.error('❌ Error cargando desde storage:', error);
            this.showDataLostError();
        }
    },

    showDataLostError() {
        const summaryContainer = document.getElementById('calculationSummary');
        if (summaryContainer) {
            summaryContainer.innerHTML = `
                <div class="alert alert-warning text-center">
                    <h5>⚠️ Datos de cálculo no encontrados</h5>
                    <p>Parece que se perdieron los datos del cálculo.</p>
                    <a href="/calculadora.html" class="btn btn-primary">
                        🔄 Volver al Calculador
                    </a>
                </div>
            `;
        }
    },

    setupDataPersistence() {
        // Guardar datos cada vez que cambie algo importante
        const saveData = () => {
            if (this.calculationData) {
                localStorage.setItem('financing_calculation_data', JSON.stringify(this.calculationData));
                localStorage.setItem('financing_data_timestamp', Date.now().toString());
            }
        };

        // Guardar cuando el usuario interactúe con el formulario
        document.addEventListener('input', saveData);
        document.addEventListener('change', saveData);
    },

    setupFormSubmission() {
        // Interceptar el envío del formulario
        const form = document.getElementById('financingRequestForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                console.log('📤 Envío interceptado');
                this.handleFormSubmission();
            });
        }

        // También interceptar clicks en botones de envío
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('📤 Envío por botón interceptado');
                this.handleFormSubmission();
            });
        }
    },

    async handleFormSubmission() {
        console.log('📤 Procesando envío de solicitud...');
        
        if (!this.validateCurrentStep()) {
            return;
        }

        // Mostrar loading
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...';
        }

        try {
            // Simular envío exitoso
            await this.simulateSubmission();
            
            // Mostrar éxito sin redirigir
            this.showSuccessMessage();
            
        } catch (error) {
            console.error('❌ Error en envío:', error);
            this.showError('Error al enviar la solicitud: ' + error.message);
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Solicitud';
            }
        }
    },

    async simulateSubmission() {
        // Simular llamada API
        return new Promise((resolve) => {
            setTimeout(() => {
                console.log('✅ Solicitud enviada (simulación)');
                resolve();
            }, 2000);
        });
    },

    showSuccessMessage() {
        // Mostrar mensaje de éxito sin perder los datos
        const alertContainer = document.getElementById('alertContainer') || document.body;
        const successHTML = `
            <div class="alert alert-success alert-dismissible fade show mt-3" role="alert">
                <h5 class="alert-heading">🎉 ¡Solicitud Enviada Exitosamente!</h5>
                <p>Su solicitud de financiamiento ha sido recibida y será procesada en las próximas 24-48 horas.</p>
                <p class="mb-0">Recibirá una notificación por email con el estado de su solicitud.</p>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('afterbegin', successHTML);
        alertContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    },

    setupStepNavigation() {
        // Crear mock igual que la versión anterior
        if (!window.FinancingRequest) {
            window.FinancingRequest = {
                currentStep: 1,
                totalSteps: 4,
                calculationData: this.calculationData,
                
                nextStep: () => this.nextStep(),
                prevStep: () => this.prevStep(),
                renderCurrentStep: () => this.renderCurrentStep(),
                validateCurrentStep: () => this.validateCurrentStep(),
                submitRequest: () => this.handleFormSubmission()
            };
            console.log('✅ FinancingRequest mock V2 creado');
        } else {
            // Si existe, asegurar que tenga los datos
            window.FinancingRequest.calculationData = this.calculationData;
        }
    },

    nextStep() {
        console.log(`🔄 nextStep() llamado - paso actual: ${this.currentStep}`);
        
        if (this.currentStep < this.totalSteps) {
            if (this.validateCurrentStep()) {
                this.currentStep++;
                this.renderCurrentStep();
                console.log(`✅ Avanzado al paso ${this.currentStep}`);
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
                return true; // Documentos opcionales
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

        window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    renderCalculationSummary(calculationData) {
        console.log('🎨 Renderizando resumen...');
        
        const calc = calculationData.calculation || calculationData;
        const product = calculationData.product || {};
        const mode = calculationData.mode || {};
        
        const productPrice = calc.vehicle_value || calc.product_price || product.price || 0;
        const downPaymentAmount = calc.down_payment_amount || 0;
        const downPaymentPercentage = calc.down_payment_percentage || 0;
        const paymentAmount = calc.payment_amount || calc.monthly_payment || 0;
        const numberOfPayments = calc.number_of_payments || calc.term_months || 0;
        const financedAmount = calc.financed_amount || (productPrice - downPaymentAmount);
        const totalAmount = calc.total_cost || calc.total_amount || productPrice;
        const paymentFrequency = calc.payment_frequency || 'monthly';
        
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
    },

    showError(message) {
        console.error('❌', message);
        alert(message);
    }
};

// Inicializar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => SolicitudFixV2.init());
} else {
    SolicitudFixV2.init();
}

// Disponible globalmente
window.SolicitudFixV2 = SolicitudFixV2; 