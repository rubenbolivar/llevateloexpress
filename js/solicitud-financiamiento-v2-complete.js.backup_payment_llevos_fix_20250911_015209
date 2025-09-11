/**
 * SOLICITUD DE FINANCIAMIENTO V2 - ARQUITECTURA LIMPIA
 * Funcionalidad crítica del negocio - Código limpio y mantenible
 * 
 * @version 2.0.0
 * @author Claude AI Assistant
 * @date 2025-06-04
 */

class FinancingRequestV2 {
    constructor() {
        // Estado central de la aplicación
        this.state = {
            currentStep: 1,
            totalSteps: 4,
            calculationData: null,
            formData: {},
            uploadedFiles: [],
            requestId: null,
            isLoading: false,
            errors: []
        };

        // Configuración
        this.config = {
            maxFileSize: 5 * 1024 * 1024, // 5MB
            allowedFileTypes: ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'],
            validationRules: {
                employment_type: { required: true },
                monthly_income: { required: true, min: 0 }
            }
        };

        // Referencias DOM
        this.elements = {};
        
        // Bind methods
        this.init = this.init.bind(this);
        this.navigateToStep = this.navigateToStep.bind(this);
        this.submitRequest = this.submitRequest.bind(this);
    }

    /**
     * Inicialización de la aplicación
     */
    async init() {
        try {
            this.log('info', 'Inicializando FinancingRequestV2');
            
            // Verificar autenticación
            if (!this.checkAuthentication()) {
                this.redirectToLogin();
                return;
            }

            // Cachear elementos DOM
            this.cacheElements();
            
            // Configurar event listeners
            this.setupEventListeners();
            
            // Cargar datos iniciales
            await this.loadInitialData();
            
            // Renderizar estado inicial
            this.render();
            
            this.log('success', 'FinancingRequestV2 inicializado exitosamente');
            
        } catch (error) {
            this.handleError('Error en inicialización', error);
        }
    }

    /**
     * Verificar autenticación del usuario
     */
    checkAuthentication() {
        // Verificar si API está disponible
        if (typeof API === 'undefined' || !API.users) {
            this.log('error', 'API no disponible');
            return false;
        }

        // Verificar token
        const token = localStorage.getItem('access_token');
        if (!token) {
            this.log('warning', 'Usuario no autenticado');
            return false;
        }

        return true;
    }

    /**
     * Redireccionar a login
     */
    redirectToLogin() {
        const currentUrl = encodeURIComponent(window.location.href);
        window.location.href = `/login.html?redirect=${currentUrl}`;
    }

    /**
     * Cachear elementos DOM importantes
     */
    cacheElements() {
        this.elements = {
            form: document.getElementById('financingRequestForm'),
            alertContainer: document.getElementById('alertContainer'),
            submitBtn: document.getElementById('submitBtn'),
            steps: {},
            sections: {},
            fields: {}
        };

        // Cachear pasos y secciones
        for (let i = 1; i <= this.state.totalSteps; i++) {
            this.elements.steps[i] = document.getElementById(`step${i}`);
            this.elements.sections[i] = document.getElementById(`section${i}`);
        }

        // Cachear campos de formulario
        const fieldNames = [
            'employment_type', 'monthly_income', 'company_name', 'job_position',
            'work_phone', 'years_employed', 'reference1_name', 'reference1_phone',
            'reference2_name', 'reference2_phone', 'termsAccept', 'dataConsent'
        ];

        fieldNames.forEach(name => {
            const element = document.getElementById(name);
            if (element) {
                this.elements.fields[name] = element;
            }
        });

        // Cachear contenedores dinámicos
        this.elements.calculationSummary = document.getElementById('calculationSummary');
        this.elements.productDetails = document.getElementById('productDetails');
        this.elements.financingDetails = document.getElementById('financingDetails');
        this.elements.finalSummary = document.getElementById('finalSummary');
        this.elements.filesList = document.getElementById('filesList');
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Submit del formulario
        if (this.elements.form) {
            this.elements.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitRequest();
            });
        }

        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleLogout();
            });
        }

        // File upload
        const documentInput = document.getElementById('documentInput');
        const uploadZone = document.getElementById('uploadZone');
        
        if (documentInput && uploadZone) {
            documentInput.addEventListener('change', (e) => {
                this.handleFileUpload(e.target.files);
            });

            uploadZone.addEventListener('click', () => {
                documentInput.click();
            });

            // Drag & drop
            uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadZone.classList.add('drag-over');
            });

            uploadZone.addEventListener('dragleave', () => {
                uploadZone.classList.remove('drag-over');
            });

            uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('drag-over');
                this.handleFileUpload(e.dataTransfer.files);
            });
        }

        // Form field changes
        Object.values(this.elements.fields).forEach(field => {
            if (field) {
                field.addEventListener('change', () => {
                    this.updateFormData();
                    this.validateField(field);
                });
            }
        });
    }

    /**
     * Cargar datos iniciales
     */
    async loadInitialData() {
        try {
            // Obtener parámetros de URL
            const urlParams = new URLSearchParams(window.location.search);
            const calculationParam = urlParams.get('calculation');
            const requestIdParam = urlParams.get('id');

            if (requestIdParam) {
                // Cargar solicitud existente
                await this.loadExistingRequest(requestIdParam);
            } else if (calculationParam) {
                // Cargar datos de calculadora
                this.loadCalculationData(calculationParam);
            } else {
                // Sin datos - redirigir a calculadora
                this.handleMissingData();
            }

        } catch (error) {
            this.handleError('Error cargando datos iniciales', error);
        }
    }

    /**
     * Cargar datos de calculadora desde URL
     */
    loadCalculationData(calculationParam) {
        try {
            this.state.calculationData = JSON.parse(decodeURIComponent(calculationParam));
            this.log('success', 'Datos de calculadora cargados', this.state.calculationData);
        } catch (error) {
            this.log('error', 'Error parsing calculation data', error);
            this.showError('Error al cargar los datos del cálculo');
            setTimeout(() => {
                window.location.href = '/calculadora.html';
            }, 3000);
        }
    }

    /**
     * Cargar solicitud existente
     */
    async loadExistingRequest(requestId) {
        try {
            this.setLoading(true);
            
            const result = await API.users.authFetch(`/api/financing/requests/${requestId}/`);
            
            if (result.success) {
                const request = result.data;
                this.state.requestId = requestId;
                
                // Convertir datos del backend a formato de calculadora
                this.state.calculationData = this.convertBackendToCalculation(request);
                
                // Llenar formulario con datos existentes
                this.fillFormWithExistingData(request);
                
                this.log('success', 'Solicitud existente cargada', request);
            } else {
                throw new Error(result.message || 'Error al cargar la solicitud');
            }
            
        } catch (error) {
            this.handleError('Error cargando solicitud existente', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Convertir datos del backend al formato de calculadora
     */
    convertBackendToCalculation(request) {
        return {
            product: request.product_details,
            financing_plan: request.financing_plan_details,
            calculation: {
                product_price: parseFloat(request.product_price),
                down_payment_percentage: request.down_payment_percentage,
                down_payment_amount: parseFloat(request.down_payment_amount),
                financed_amount: parseFloat(request.financed_amount),
                payment_frequency: request.payment_frequency,
                number_of_payments: request.number_of_payments,
                payment_amount: parseFloat(request.payment_amount),
                total_amount: parseFloat(request.total_amount),
                interest_rate: parseFloat(request.interest_rate),
                total_interest: parseFloat(request.total_interest)
            }
        };
    }

    /**
     * Llenar formulario con datos existentes
     */
    fillFormWithExistingData(request) {
        const fieldMappings = {
            employment_type: request.employment_type,
            monthly_income: request.monthly_income,
            company_name: request.company_name,
            job_position: request.job_position,
            work_phone: request.work_phone,
            years_employed: request.years_employed,
            reference1_name: request.reference1_name,
            reference1_phone: request.reference1_phone,
            reference2_name: request.reference2_name,
            reference2_phone: request.reference2_phone
        };

        Object.entries(fieldMappings).forEach(([field, value]) => {
            if (value && this.elements.fields[field]) {
                this.elements.fields[field].value = value;
            }
        });

        // Actualizar estado del formulario
        this.updateFormData();
    }

    /**
     * Manejar datos faltantes
     */
    handleMissingData() {
        this.showError('No se encontraron datos de cálculo. Redirigiendo a la calculadora...');
        setTimeout(() => {
            window.location.href = '/calculadora.html';
        }, 3000);
    }

    /**
     * Navegación entre pasos
     */
    navigateToStep(targetStep, direction = 'next') {
        try {
            this.log('info', `Navegando al paso ${targetStep} (${direction})`);

            // Validar paso actual antes de avanzar
            if (direction === 'next' && !this.validateCurrentStep()) {
                this.log('warning', 'Validación del paso actual falló');
                return false;
            }

            // Actualizar estado
            this.state.currentStep = targetStep;

            // Renderizar nueva vista
            this.render();

            // Preservar URL
            this.updateURLParams();

            // Scroll al top
            window.scrollTo({ top: 0, behavior: 'smooth' });

            return true;

        } catch (error) {
            this.handleError('Error en navegación', error);
            return false;
        }
    }

    /**
     * Logging estructurado
     */
    log(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            component: 'FinancingRequestV2',
            message,
            data
        };

        // Console logging
        console[level] || console.log(`[${timestamp}] [${level.toUpperCase()}] ${message}`, data);

        // Aquí se puede agregar logging remoto en el futuro
    }

    /**
     * Manejo centralizado de errores
     */
    handleError(message, error) {
        this.log('error', message, {
            error: error.message,
            stack: error.stack
        });

        this.showError(`${message}: ${error.message}`);
    }

    /**
     * Mostrar mensajes de error
     */
    showError(message) {
        this.showAlert(message, 'danger');
    }

    /**
     * Mostrar mensajes de éxito
     */
    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    /**
     * Mostrar alertas
     */
    showAlert(message, type) {
        if (!this.elements.alertContainer) return;

        this.elements.alertContainer.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        // Scroll al mensaje
        this.elements.alertContainer.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });
    }

    /**
     * Control de estado de carga
     */
    setLoading(isLoading) {
        this.state.isLoading = isLoading;
        
        if (this.elements.submitBtn) {
            this.elements.submitBtn.disabled = isLoading;
            this.elements.submitBtn.innerHTML = isLoading 
                ? '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...'
                : '<i class="fas fa-paper-plane"></i> Enviar Solicitud';
        }
    }

    /**
     * Actualizar parámetros URL
     */
    updateURLParams() {
        try {
            const url = new URL(window.location);
            const params = new URLSearchParams(url.search);
            
            // Actualizar paso actual
            params.set('step', this.state.currentStep);
            
            // Construir nueva URL
            const newUrl = `${url.pathname}?${params.toString()}`;
            
            // Actualizar sin recargar
            window.history.replaceState({}, '', newUrl);
            
            this.log('debug', 'URL actualizada', newUrl);
            
        } catch (error) {
            this.log('warning', 'Error actualizando URL', error);
        }
    }

    /**
     * Renderizar estado actual
     */
    render() {
        try {
            this.renderStepIndicator();
            this.renderCurrentSection();
            this.renderStepContent();
            
        } catch (error) {
            this.handleError('Error en renderizado', error);
        }
    }

    /**
     * Renderizar indicador de pasos
     */
    renderStepIndicator() {
        for (let i = 1; i <= this.state.totalSteps; i++) {
            const stepElement = this.elements.steps[i];
            if (!stepElement) continue;

            // Limpiar clases
            stepElement.classList.remove('active', 'completed');

            // Aplicar estado
            if (i < this.state.currentStep) {
                stepElement.classList.add('completed');
            } else if (i === this.state.currentStep) {
                stepElement.classList.add('active');
            }
        }
    }

    /**
     * Renderizar sección actual
     */
    renderCurrentSection() {
        for (let i = 1; i <= this.state.totalSteps; i++) {
            const sectionElement = this.elements.sections[i];
            if (!sectionElement) continue;

            if (i === this.state.currentStep) {
                sectionElement.classList.add('active');
            } else {
                sectionElement.classList.remove('active');
            }
        }
    }

    /**
     * Renderizar contenido específico del paso
     */
    renderStepContent() {
        switch (this.state.currentStep) {
            case 1:
                this.renderCalculationSummary();
                break;
            case 4:
                this.renderFinalSummary();
                break;
        }
    }

    // ===============================
    // MÉTODOS ADICIONALES (CONTINUACIÓN)
    // ===============================

    /**
     * Continuar implementación...
     * (Los métodos restantes se implementarán en la siguiente parte)
     */
}

// Crear instancia global para compatibilidad con HTML
window.FinancingRequestV2 = new FinancingRequestV2();

// Funciones globales para compatibilidad con onclick en HTML
window.nextStep = () => {
    const current = window.FinancingRequestV2.state.currentStep;
    window.FinancingRequestV2.navigateToStep(current + 1, 'next');
};

window.prevStep = () => {
    const current = window.FinancingRequestV2.state.currentStep;
    window.FinancingRequestV2.navigateToStep(current - 1, 'prev');
};

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.FinancingRequestV2.init();
});

export default FinancingRequestV2; /**
 * SOLICITUD DE FINANCIAMIENTO V2 - PARTE 2
 * Métodos adicionales para completar la funcionalidad
 */

// MÉTODOS ADICIONALES PARA LA CLASE FinancingRequestV2

// Agregar estos métodos a la clase FinancingRequestV2:

/**
 * Actualizar datos del formulario
 */
updateFormData() {
    this.state.formData = {};
    
    Object.entries(this.elements.fields).forEach(([name, element]) => {
        if (element) {
            this.state.formData[name] = element.type === 'checkbox' 
                ? element.checked 
                : element.value;
        }
    });
    
    this.log('debug', 'Form data actualizada', this.state.formData);
}

/**
 * Validar campo individual
 */
validateField(field) {
    const name = field.name || field.id;
    const value = field.type === 'checkbox' ? field.checked : field.value;
    const rules = this.config.validationRules[name];
    
    if (!rules) return true;
    
    // Limpiar errores previos
    this.clearFieldError(field);
    
    // Validar requerido
    if (rules.required && (!value || value.toString().trim() === '')) {
        this.showFieldError(field, 'Este campo es obligatorio');
        return false;
    }
    
    // Validar valor mínimo
    if (rules.min !== undefined && parseFloat(value) < rules.min) {
        this.showFieldError(field, `El valor mínimo es ${rules.min}`);
        return false;
    }
    
    return true;
}

/**
 * Mostrar error en campo específico
 */
showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    // Buscar o crear contenedor de error
    let errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        field.parentNode.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
}

/**
 * Limpiar error de campo
 */
clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

/**
 * Validar paso actual
 */
validateCurrentStep() {
    switch (this.state.currentStep) {
        case 1:
            return this.validateStep1();
        case 2:
            return this.validateStep2();
        case 3:
            return this.validateStep3();
        case 4:
            return this.validateStep4();
        default:
            return true;
    }
}

/**
 * Validar paso 1 - Resumen
 */
validateStep1() {
    if (!this.state.calculationData) {
        this.showError('No hay datos de cálculo disponibles');
        return false;
    }
    return true;
}

/**
 * Validar paso 2 - Información Personal
 */
validateStep2() {
    this.updateFormData();
    
    const requiredFields = ['employment_type', 'monthly_income'];
    let isValid = true;
    
    requiredFields.forEach(fieldName => {
        const field = this.elements.fields[fieldName];
        if (field && !this.validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Validar paso 3 - Documentos
 */
validateStep3() {
    // Los documentos son opcionales
    return true;
}

/**
 * Validar paso 4 - Confirmación
 */
validateStep4() {
    const termsField = this.elements.fields.termsAccept;
    const consentField = this.elements.fields.dataConsent;
    
    let isValid = true;
    
    if (termsField && !termsField.checked) {
        this.showError('Debe aceptar los términos y condiciones');
        isValid = false;
    }
    
    if (consentField && !consentField.checked) {
        this.showError('Debe autorizar el tratamiento de datos personales');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Renderizar resumen de cálculo
 */
renderCalculationSummary() {
    if (!this.state.calculationData || !this.elements.calculationSummary) return;
    
    const calc = this.state.calculationData.calculation || this.state.calculationData;
    const product = this.state.calculationData.product || {};
    
    // Normalizar datos
    const productPrice = calc.product_price || product.price || 0;
    const downPaymentAmount = calc.down_payment_amount || 0;
    const downPaymentPercentage = calc.down_payment_percentage || 0;
    const paymentAmount = calc.payment_amount || 0;
    const numberOfPayments = calc.number_of_payments || 0;
    const paymentFrequency = calc.payment_frequency || 'monthly';
    
    // Renderizar resumen principal
    this.elements.calculationSummary.innerHTML = `
        <div class="row text-center">
            <div class="col-md-3">
                <h3>$${this.formatNumber(productPrice)}</h3>
                <small>Precio del Producto</small>
            </div>
            <div class="col-md-3">
                <h3>$${this.formatNumber(downPaymentAmount)}</h3>
                <small>Inicial (${downPaymentPercentage}%)</small>
            </div>
            <div class="col-md-3">
                <h3>$${this.formatNumber(paymentAmount)}</h3>
                <small>Cuota ${this.getFrequencyText(paymentFrequency)}</small>
            </div>
            <div class="col-md-3">
                <h3>${numberOfPayments}</h3>
                <small>Número de Cuotas</small>
            </div>
        </div>
    `;
    
    // Renderizar detalles del producto
    if (this.elements.productDetails) {
        this.elements.productDetails.innerHTML = `
            <p><strong>Producto:</strong> ${product.name || 'Producto Seleccionado'}</p>
            <p><strong>Categoría:</strong> ${product.category_name || 'N/A'}</p>
            <p><strong>Precio:</strong> $${this.formatNumber(productPrice)}</p>
            <p><strong>Monto a Financiar:</strong> $${this.formatNumber(calc.financed_amount || 0)}</p>
        `;
    }
    
    // Renderizar detalles del financiamiento
    if (this.elements.financingDetails) {
        const plan = this.state.calculationData.financing_plan || this.state.calculationData.mode || {};
        this.elements.financingDetails.innerHTML = `
            <p><strong>Plan:</strong> ${plan.name || 'Plan Seleccionado'}</p>
            <p><strong>Frecuencia:</strong> ${this.getFrequencyText(paymentFrequency)}</p>
            <p><strong>Plazo:</strong> ${numberOfPayments} cuotas</p>
            <p><strong>Total a Pagar:</strong> $${this.formatNumber(calc.total_amount || productPrice)}</p>
        `;
    }
}

/**
 * Renderizar resumen final
 */
renderFinalSummary() {
    if (!this.state.calculationData || !this.elements.finalSummary) return;
    
    const product = this.state.calculationData.product || {};
    const calc = this.state.calculationData.calculation || this.state.calculationData;
    
    this.updateFormData();
    
    this.elements.finalSummary.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Producto Seleccionado</h6>
                <p>${product.name || 'Producto Seleccionado'}</p>
                <p><strong>Precio:</strong> $${this.formatNumber(calc.product_price || 0)}</p>
                
                <h6 class="mt-3">Plan de Financiamiento</h6>
                <p><strong>Inicial:</strong> $${this.formatNumber(calc.down_payment_amount || 0)} (${calc.down_payment_percentage || 0}%)</p>
                <p><strong>Cuota:</strong> $${this.formatNumber(calc.payment_amount || 0)} ${this.getFrequencyText(calc.payment_frequency || 'monthly')}</p>
                <p><strong>Plazo:</strong> ${calc.number_of_payments || 0} cuotas</p>
            </div>
            <div class="col-md-6">
                <h6>Información Personal</h6>
                <p><strong>Tipo de Empleo:</strong> ${this.getEmploymentTypeText(this.state.formData.employment_type)}</p>
                <p><strong>Ingreso Mensual:</strong> $${this.formatNumber(this.state.formData.monthly_income || 0)}</p>
                
                <h6 class="mt-3">Documentos</h6>
                <p>${this.state.uploadedFiles.length} archivo(s) seleccionado(s)</p>
                
                <div class="alert alert-info mt-3">
                    <i class="fas fa-info-circle"></i>
                    Su solicitud será revisada por nuestro equipo en un plazo de 24-48 horas.
                </div>
            </div>
        </div>
    `;
}

/**
 * Manejar subida de archivos
 */
handleFileUpload(files) {
    Array.from(files).forEach(file => {
        if (this.validateFile(file)) {
            this.state.uploadedFiles.push(file);
        }
    });
    
    this.renderFilesList();
}

/**
 * Validar archivo
 */
validateFile(file) {
    // Validar tipo
    if (!this.config.allowedFileTypes.includes(file.type)) {
        this.showError(`Formato no permitido: ${file.name}`);
        return false;
    }
    
    // Validar tamaño
    if (file.size > this.config.maxFileSize) {
        this.showError(`Archivo muy grande: ${file.name} (máx. 5MB)`);
        return false;
    }
    
    return true;
}

/**
 * Renderizar lista de archivos
 */
renderFilesList() {
    if (!this.elements.filesList) return;
    
    if (this.state.uploadedFiles.length === 0) {
        this.elements.filesList.innerHTML = '';
        return;
    }
    
    this.elements.filesList.innerHTML = this.state.uploadedFiles.map((file, index) => `
        <div class="file-item">
            <div class="d-flex justify-content-between align-items-center w-100">
                <span>
                    <i class="fas fa-file"></i> ${file.name}
                    <small class="text-muted">(${this.formatFileSize(file.size)})</small>
                </span>
                <button type="button" class="btn btn-sm btn-danger" onclick="window.FinancingRequestV2.removeFile(${index})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `).join('');
}

/**
 * Remover archivo
 */
removeFile(index) {
    this.state.uploadedFiles.splice(index, 1);
    this.renderFilesList();
}

/**
 * Preparar datos de la solicitud
 */
prepareRequestData() {
    const calc = this.state.calculationData.calculation || this.state.calculationData;
    const product = this.state.calculationData.product || {};
    
    this.updateFormData();
    
    const data = {
        // Datos del producto
        product: product.id,
        financing_plan: this.getFinancingPlanByDownPayment(calc.down_payment_percentage || 35),
        
        // Datos financieros (normalizados con FinancingDataFixer)
        product_price: parseFloat(calc.product_price || 0).toFixed(2),
        down_payment_percentage: parseInt(calc.down_payment_percentage || 0),
        down_payment_amount: parseFloat(calc.down_payment_amount || 0).toFixed(2),
        financed_amount: parseFloat(calc.financed_amount || 0).toFixed(2),
        interest_rate: parseFloat(calc.interest_rate || 0).toFixed(2),
        total_interest: parseFloat(calc.total_interest || 0).toFixed(2),
        total_amount: parseFloat(calc.total_amount || 0).toFixed(2),
        payment_frequency: this.normalizePaymentFrequency(calc.payment_frequency || 'monthly'),
        number_of_payments: parseInt(calc.number_of_payments || 0),
        payment_amount: parseFloat(calc.payment_amount || 0).toFixed(2),
        
        // Datos personales
        employment_type: this.state.formData.employment_type || '',
        monthly_income: parseFloat(this.state.formData.monthly_income || 0).toFixed(2),
        company_name: this.state.formData.company_name || '',
        job_position: this.state.formData.job_position || '',
        work_phone: this.state.formData.work_phone || '',
        years_employed: parseFloat(this.state.formData.years_employed || 0),
        reference1_name: this.state.formData.reference1_name || '',
        reference1_phone: this.state.formData.reference1_phone || '',
        reference2_name: this.state.formData.reference2_name || '',
        reference2_phone: this.state.formData.reference2_phone || ''
    };
    
    return data;
}

/**
 * Mapear porcentaje inicial a plan de financiamiento
 */
getFinancingPlanByDownPayment(downPaymentPercentage) {
    const planMap = {
        35: 5, // Crédito Inmediato 35%
        45: 6, // Crédito Inmediato 45%
        55: 7, // Crédito Inmediato 55%
        60: 8  // Crédito Inmediato 60%
    };
    return planMap[downPaymentPercentage] || 5;
}

/**
 * Normalizar frecuencia de pago
 */
normalizePaymentFrequency(frequency) {
    const map = {
        'semanal': 'weekly',
        'quincenal': 'biweekly',
        'mensual': 'monthly',
        'weekly': 'weekly',
        'biweekly': 'biweekly',
        'monthly': 'monthly'
    };
    return map[frequency.toLowerCase()] || frequency;
}

/**
 * Enviar solicitud
 */
async submitRequest() {
    try {
        this.log('info', 'Iniciando envío de solicitud');
        
        // Validar paso final
        if (!this.validateCurrentStep()) {
            this.log('warning', 'Validación del paso final falló');
            return;
        }
        
        this.setLoading(true);
        
        // Preparar datos
        const requestData = this.prepareRequestData();
        this.log('info', 'Datos preparados para envío', requestData);
        
        // Enviar solicitud
        let result;
        if (this.state.requestId) {
            // Actualizar solicitud existente
            result = await API.users.authFetch(`/api/financing/requests/${this.state.requestId}/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
        } else {
            // Crear nueva solicitud
            result = await API.users.authFetch('/api/financing/requests/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
        }
        
        this.log('info', 'Respuesta del servidor', result);
        
        if (result.success) {
            const requestId = result.data.id;
            this.state.requestId = requestId;
            
            // Subir documentos si hay alguno
            if (this.state.uploadedFiles.length > 0) {
                await this.uploadDocuments(requestId);
            }
            
            // Enviar solicitud para revisión
            await this.submitForReview(requestId);
            
            // Mostrar éxito y redirigir
            this.showSuccess('¡Solicitud enviada exitosamente! Redirigiendo al dashboard...');
            setTimeout(() => {
                window.location.href = '/dashboard.html';
            }, 3000);
            
        } else {
            throw new Error(result.message || 'Error al crear la solicitud');
        }
        
    } catch (error) {
        this.handleError('Error enviando solicitud', error);
    } finally {
        this.setLoading(false);
    }
}

/**
 * Subir documentos
 */
async uploadDocuments(requestId) {
    if (this.state.uploadedFiles.length === 0) return;
    
    const formData = new FormData();
    this.state.uploadedFiles.forEach(file => {
        formData.append('documents', file);
    });
    
    const result = await API.users.authFetch(
        `/api/financing/requests/${requestId}/upload_documents/`,
        {
            method: 'POST',
            body: formData
        }
    );
    
    if (!result.success) {
        throw new Error('Error al subir documentos');
    }
}

/**
 * Enviar para revisión
 */
async submitForReview(requestId) {
    const result = await API.users.authFetch(
        `/api/financing/requests/${requestId}/submit/`,
        { method: 'POST' }
    );
    
    if (!result.success) {
        throw new Error('Error al enviar para revisión');
    }
}

/**
 * Manejar logout
 */
handleLogout() {
    if (typeof API !== 'undefined' && API.users && API.users.logout) {
        API.users.logout();
    } else {
        localStorage.removeItem('access_token');
        window.location.href = '/login.html';
    }
}

/**
 * Utilidades de formateo
 */
formatNumber(num) {
    return new Intl.NumberFormat('es-VE').format(num || 0);
}

formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

getFrequencyText(frequency) {
    const frequencies = {
        'weekly': 'Semanal',
        'biweekly': 'Quincenal',
        'monthly': 'Mensual'
    };
    return frequencies[frequency] || frequency;
}

getEmploymentTypeText(type) {
    const types = {
        'empleado_publico': 'Empleado Público',
        'empleado_privado': 'Empleado Privado',
        'independiente': 'Trabajador Independiente',
        'empresario': 'Empresario',
        'pensionado': 'Pensionado',
        'otro': 'Otro'
    };
    return types[type] || type;
} 