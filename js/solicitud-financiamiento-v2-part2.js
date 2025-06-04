/**
 * SOLICITUD DE FINANCIAMIENTO V2 - ADAPTADO PARA VPS
 * Versión adaptada para trabajar con la infraestructura existente del VPS
 */

class FinancingRequestV2 {
    constructor() {
        this.state = {
            currentStep: 1,
            formData: {},
            calculationData: null,
            uploadedFiles: [],
            requestId: null,
            isLoading: false
        };
        
        this.config = {
            // URLs exactas del VPS (confirmadas por pruebas)
            apiBase: '/api/financing',
            endpoints: {
                plans: '/api/financing/plans/',
                requests: '/api/financing/requests/',
                calculate: '/api/financing/calculate/',  // Usar el endpoint que SÍ existe
            },
            maxFileSize: 5 * 1024 * 1024,
            allowedFileTypes: ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'],
            validationRules: {
                employment_type: { required: true },
                monthly_income: { required: true, min: 1 }
            }
        };
        
        this.elements = {};
        this.csrfToken = null;
        
        this.init();
    }
    
    /**
     * Obtener token CSRF del formulario existente
     */
    getCsrfToken() {
        // El VPS ya tiene CSRF configurado, usar el token del formulario
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            this.csrfToken = metaTag.getAttribute('content');
            return this.csrfToken;
        }
        
        const hiddenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (hiddenInput) {
            this.csrfToken = hiddenInput.value;
            return this.csrfToken;
        }
        
        return null;
    }
    
    /**
     * Obtener cookie (para CSRF o autenticación)
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    /**
     * Fetch adaptado para el VPS existente
     */
    async apiRequest(url, options = {}) {
        try {
            // Configurar headers para el VPS existente
            const headers = {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                ...options.headers
            };
            
            // Agregar CSRF token si está disponible
            const csrfToken = this.getCsrfToken() || this.getCookie('csrftoken');
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }
            
            const requestOptions = {
                credentials: 'same-origin',
                ...options,
                headers
            };
            
            this.log('debug', `API Request: ${options.method || 'GET'} ${url}`);
            
            const response = await fetch(url, requestOptions);
            
            // Manejar respuestas específicas del VPS
            if (response.status === 401) {
                this.log('warning', 'Usuario no autenticado');
                this.showError('Debe iniciar sesión para continuar');
                // No redirigir automáticamente, el usuario ya está en el flujo
                return { success: false, status: 401, message: 'No autenticado' };
            }
            
            if (response.status === 403) {
                this.log('error', 'Error de permisos (CSRF o autorización)');
                return { success: false, status: 403, message: 'Sin permisos' };
            }
            
            // Parsear respuesta
            let data = null;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }
            
            return {
                success: response.ok,
                status: response.status,
                data: data,
                message: response.ok ? 'Éxito' : (data.detail || data.error || 'Error')
            };
            
        } catch (error) {
            this.log('error', 'Error en petición API', error);
            return {
                success: false,
                status: 0,
                data: null,
                message: error.message || 'Error de conexión'
            };
        }
    }
    
    /**
     * Inicializar aplicación
     */
    init() {
        this.log('info', 'Inicializando FinancingRequestV2 adaptado para VPS');
        
        // Cachear elementos del DOM
        this.cacheElements();
        
        // Configurar eventos
        this.setupEventListeners();
        
        // Cargar datos de cálculo
        this.loadCalculationData();
        
        // Verificar planes disponibles (sin requerir autenticación)
        this.loadFinancingPlans();
    }
    
    /**
     * Cachear elementos del DOM
     */
    cacheElements() {
        this.elements = {
            form: document.getElementById('financingRequestForm'),
            alertContainer: document.getElementById('alertContainer'),
            submitBtn: document.getElementById('submitBtn'),
            
            // Secciones de pasos
            section1: document.getElementById('section1'),
            section2: document.getElementById('section2'),
            section3: document.getElementById('section3'),
            section4: document.getElementById('section4'),
            
            // Indicadores de pasos
            step1: document.getElementById('step1'),
            step2: document.getElementById('step2'),
            step3: document.getElementById('step3'),
            step4: document.getElementById('step4'),
            
            // Contenedores de contenido
            calculationSummary: document.getElementById('calculationSummary'),
            productDetails: document.getElementById('productDetails'),
            financingDetails: document.getElementById('financingDetails'),
            finalSummary: document.getElementById('finalSummary'),
            
            // Subida de archivos
            uploadZone: document.getElementById('uploadZone'),
            documentInput: document.getElementById('documentInput'),
            filesList: document.getElementById('filesList'),
            
            // Campos del formulario
            fields: {
                employment_type: document.getElementById('employment_type'),
                monthly_income: document.getElementById('monthly_income'),
                company_name: document.getElementById('company_name'),
                job_position: document.getElementById('job_position'),
                work_phone: document.getElementById('work_phone'),
                years_employed: document.getElementById('years_employed'),
                reference1_name: document.getElementById('reference1_name'),
                reference1_phone: document.getElementById('reference1_phone'),
                reference2_name: document.getElementById('reference2_name'),
                reference2_phone: document.getElementById('reference2_phone'),
                termsAccept: document.getElementById('termsAccept'),
                dataConsent: document.getElementById('dataConsent')
            }
        };
    }
    
    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Formulario principal
        if (this.elements.form) {
            this.elements.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitRequest();
            });
        }
        
        // Subida de archivos
        if (this.elements.uploadZone) {
            this.elements.uploadZone.addEventListener('click', () => {
                this.elements.documentInput?.click();
            });
            
            this.elements.uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                this.elements.uploadZone.classList.add('drag-over');
            });
            
            this.elements.uploadZone.addEventListener('dragleave', () => {
                this.elements.uploadZone.classList.remove('drag-over');
            });
            
            this.elements.uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                this.elements.uploadZone.classList.remove('drag-over');
                this.handleFileUpload(e.dataTransfer.files);
            });
        }
        
        if (this.elements.documentInput) {
            this.elements.documentInput.addEventListener('change', (e) => {
                this.handleFileUpload(e.target.files);
            });
        }
        
        // Validación en tiempo real
        Object.values(this.elements.fields).forEach(field => {
            if (field) {
                field.addEventListener('blur', () => this.validateField(field));
                field.addEventListener('change', () => this.clearFieldError(field));
            }
        });
    }
    
    /**
     * Cargar planes de financiamiento (funciona sin autenticación)
     */
    async loadFinancingPlans() {
        try {
            const result = await this.apiRequest(this.config.endpoints.plans);
            
            if (result.success && result.data) {
                this.state.financingPlans = result.data;
                this.log('info', `Planes de financiamiento cargados: ${result.data.length}`);
                return result.data;
            } else {
                this.log('warning', 'No se pudieron cargar los planes de financiamiento');
                return [];
            }
        } catch (error) {
            this.log('error', 'Error cargando planes', error);
            return [];
        }
    }
    
    /**
     * Cargar datos de cálculo desde localStorage
     */
    loadCalculationData() {
        try {
            const savedData = localStorage.getItem('calculationData');
            if (savedData) {
                this.state.calculationData = JSON.parse(savedData);
                this.log('info', 'Datos de cálculo cargados desde localStorage');
                this.renderCalculationSummary();
                return;
            }
            
            // Intentar cargar desde URL params
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('product_id')) {
                this.log('info', 'Detectados parámetros de cálculo en URL');
                // Reconstruir datos básicos desde URL
                this.state.calculationData = {
                    product: { id: urlParams.get('product_id') },
                    calculation: {
                        product_price: urlParams.get('price') || 0,
                        down_payment_percentage: urlParams.get('down_payment') || 35
                    }
                };
                this.renderCalculationSummary();
            } else {
                this.log('warning', 'No se encontraron datos de cálculo - usuario puede continuar manualmente');
            }
        } catch (error) {
            this.log('error', 'Error cargando datos de cálculo', error);
        }
    }
    
    /**
     * Renderizar resumen de cálculo (adaptado para datos disponibles)
     */
    renderCalculationSummary() {
        if (!this.state.calculationData || !this.elements.calculationSummary) return;
        
        const calc = this.state.calculationData.calculation || this.state.calculationData;
        const product = this.state.calculationData.product || {};
        
        // Usar datos disponibles o valores por defecto
        const productPrice = parseFloat(calc.product_price || 0);
        const downPaymentPercentage = parseInt(calc.down_payment_percentage || 35);
        const downPaymentAmount = productPrice * (downPaymentPercentage / 100);
        const financedAmount = productPrice - downPaymentAmount;
        
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
                    <h3>$${this.formatNumber(financedAmount)}</h3>
                    <small>Monto a Financiar</small>
                </div>
                <div class="col-md-3">
                    <h3>Disponible</h3>
                    <small>Plan de Financiamiento</small>
                </div>
            </div>
        `;
        
        // Renderizar detalles si hay elementos
        if (this.elements.productDetails) {
            this.elements.productDetails.innerHTML = `
                <p><strong>Producto:</strong> ${product.name || 'Producto Seleccionado'}</p>
                <p><strong>Precio:</strong> $${this.formatNumber(productPrice)}</p>
                <p><strong>Plan:</strong> Crédito Inmediato ${downPaymentPercentage}%</p>
            `;
        }
    }
    
    /**
     * Navegación entre pasos
     */
    nextStep() {
        if (this.validateCurrentStep()) {
            if (this.state.currentStep < 4) {
                this.goToStep(this.state.currentStep + 1);
            }
        }
    }
    
    prevStep() {
        if (this.state.currentStep > 1) {
            this.goToStep(this.state.currentStep - 1);
        }
    }
    
    goToStep(step) {
        // Ocultar sección actual
        const currentSection = this.elements[`section${this.state.currentStep}`];
        if (currentSection) {
            currentSection.classList.remove('active');
        }
        
        // Actualizar indicador actual
        const currentStep = this.elements[`step${this.state.currentStep}`];
        if (currentStep) {
            currentStep.classList.remove('active');
            currentStep.classList.add('completed');
        }
        
        // Mostrar nueva sección
        const newSection = this.elements[`section${step}`];
        if (newSection) {
            newSection.classList.add('active');
        }
        
        // Actualizar indicador nuevo
        const newStep = this.elements[`step${step}`];
        if (newStep) {
            newStep.classList.add('active');
        }
        
        // Actualizar estado
        this.state.currentStep = step;
        
        // Renderizar contenido específico del paso
        if (step === 4) {
            this.renderFinalSummary();
        }
        
        this.log('info', `Navegando al paso ${step}`);
    }
    
    /**
     * Preparar datos para el VPS (formato exacto)
     */
    prepareRequestData() {
        this.updateFormData();
        
        const calc = this.state.calculationData?.calculation || {};
        const product = this.state.calculationData?.product || {};
        
        // Preparar datos en el formato que espera el VPS
        const data = {
            // Datos del producto
            product: parseInt(product.id || 1),
            financing_plan: this.getFinancingPlanByDownPayment(35), // Plan por defecto
            
            // Datos financieros (formato del VPS)
            product_price: parseFloat(calc.product_price || 4500).toFixed(2),
            down_payment_percentage: parseInt(calc.down_payment_percentage || 35),
            down_payment_amount: parseFloat(calc.down_payment_amount || 1575).toFixed(2),
            financed_amount: parseFloat(calc.financed_amount || 2925).toFixed(2),
            payment_frequency: "biweekly", // Usar formato que acepta el VPS
            number_of_payments: parseInt(calc.number_of_payments || 24),
            payment_amount: parseFloat(calc.payment_amount || 158.33).toFixed(2),
            
            // Datos personales
            employment_type: this.state.formData.employment_type || "empleado_privado",
            monthly_income: parseFloat(this.state.formData.monthly_income || 800).toFixed(2),
            company_name: this.state.formData.company_name || "",
            job_position: this.state.formData.job_position || "",
            work_phone: this.state.formData.work_phone || "",
            years_employed: parseFloat(this.state.formData.years_employed || 0),
            reference1_name: this.state.formData.reference1_name || "",
            reference1_phone: this.state.formData.reference1_phone || "",
            reference2_name: this.state.formData.reference2_name || "",
            reference2_phone: this.state.formData.reference2_phone || ""
        };
        
        this.log('debug', 'Datos preparados para VPS', data);
        return data;
    }
    
    /**
     * Enviar solicitud usando las URLs del VPS
     */
    async submitRequest() {
        try {
            this.log('info', 'Iniciando envío de solicitud al VPS');
            
            if (!this.validateCurrentStep()) {
                return;
            }
            
            this.setLoading(true);
            
            const requestData = this.prepareRequestData();
            
            // Usar endpoint exacto del VPS
            const result = await this.apiRequest(this.config.endpoints.requests, {
                method: 'POST',
                body: JSON.stringify(requestData)
            });
            
            if (result.success) {
                const requestId = result.data.id;
                this.state.requestId = requestId;
                
                this.showSuccess('¡Solicitud enviada exitosamente!');
                this.log('info', `Solicitud creada con ID: ${requestId}`);
                
                // Opcional: subir documentos si hay
                if (this.state.uploadedFiles.length > 0) {
                    await this.uploadDocuments(requestId);
                }
                
                // Redirigir al dashboard después de 3 segundos
                setTimeout(() => {
                    window.location.href = '/dashboard.html';
                }, 3000);
                
            } else {
                if (result.status === 401) {
                    this.showError('Debe iniciar sesión para enviar la solicitud. Redirigiendo...');
                    setTimeout(() => {
                        window.location.href = '/login.html';
                    }, 2000);
                } else {
                    this.showError(result.message || 'Error al enviar la solicitud');
                }
            }
            
        } catch (error) {
            this.log('error', 'Error enviando solicitud', error);
            this.showError('Error de conexión. Por favor, intente nuevamente.');
        } finally {
            this.setLoading(false);
        }
    }
    
    // Métodos de utilidad (implementación básica)
    updateFormData() {
        this.state.formData = {};
        Object.entries(this.elements.fields).forEach(([name, element]) => {
            if (element) {
                this.state.formData[name] = element.type === 'checkbox' ? element.checked : element.value;
            }
        });
    }
    
    validateCurrentStep() {
        switch (this.state.currentStep) {
            case 1: return true; // Paso de resumen siempre válido
            case 2: return this.validateStep2();
            case 3: return true; // Documentos opcionales
            case 4: return this.validateStep4();
            default: return true;
        }
    }
    
    validateStep2() {
        const requiredFields = ['employment_type', 'monthly_income'];
        let isValid = true;
        
        requiredFields.forEach(fieldName => {
            const field = this.elements.fields[fieldName];
            if (field && !field.value.trim()) {
                this.showFieldError(field, 'Este campo es obligatorio');
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    validateStep4() {
        const termsField = this.elements.fields.termsAccept;
        const consentField = this.elements.fields.dataConsent;
        
        if (termsField && !termsField.checked) {
            this.showError('Debe aceptar los términos y condiciones');
            return false;
        }
        
        if (consentField && !consentField.checked) {
            this.showError('Debe autorizar el tratamiento de datos personales');
            return false;
        }
        
        return true;
    }
    
    validateField(field) {
        this.clearFieldError(field);
        const value = field.value.trim();
        
        if (field.required && !value) {
            this.showFieldError(field, 'Este campo es obligatorio');
            return false;
        }
        
        if (field.type === 'number' && value && parseFloat(value) <= 0) {
            this.showFieldError(field, 'Debe ser un valor válido mayor a 0');
            return false;
        }
        
        return true;
    }
    
    showFieldError(field, message) {
        field.classList.add('is-invalid');
        let errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            field.parentNode.appendChild(errorElement);
        }
        errorElement.textContent = message;
    }
    
    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.remove();
        }
    }
    
    handleFileUpload(files) {
        Array.from(files).forEach(file => {
            if (this.validateFile(file)) {
                this.state.uploadedFiles.push(file);
            }
        });
        this.renderFilesList();
    }
    
    validateFile(file) {
        if (!this.config.allowedFileTypes.includes(file.type)) {
            this.showError(`Formato no permitido: ${file.name}`);
            return false;
        }
        
        if (file.size > this.config.maxFileSize) {
            this.showError(`Archivo muy grande: ${file.name} (máx. 5MB)`);
            return false;
        }
        
        return true;
    }
    
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
                    <button type="button" class="btn btn-sm btn-danger" onclick="FinancingRequestV2.removeFile(${index})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    removeFile(index) {
        this.state.uploadedFiles.splice(index, 1);
        this.renderFilesList();
    }
    
    renderFinalSummary() {
        if (!this.elements.finalSummary) return;
        
        this.updateFormData();
        
        this.elements.finalSummary.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Información del Financiamiento</h6>
                    <p><strong>Plan:</strong> Crédito Inmediato</p>
                    <p><strong>Tipo de Empleo:</strong> ${this.getEmploymentTypeText(this.state.formData.employment_type)}</p>
                    <p><strong>Ingreso Mensual:</strong> $${this.formatNumber(this.state.formData.monthly_income || 0)}</p>
                </div>
                <div class="col-md-6">
                    <h6>Documentos</h6>
                    <p>${this.state.uploadedFiles.length} archivo(s) seleccionado(s)</p>
                    
                    <div class="alert alert-info mt-3">
                        <i class="fas fa-info-circle"></i>
                        Su solicitud será procesada en un plazo de 24-48 horas.
                    </div>
                </div>
            </div>
        `;
    }
    
    // Métodos de utilidad
    getFinancingPlanByDownPayment(percentage) {
        const planMap = { 35: 5, 45: 6, 55: 7, 60: 8 };
        return planMap[percentage] || 5;
    }
    
    getEmploymentTypeText(type) {
        const types = {
            'empleado_publico': 'Empleado Público',
            'empleado_privado': 'Empleado Privado',
            'independiente': 'Trabajador Independiente',
            'empresario': 'Empresario',
            'pensionado': 'Pensionado'
        };
        return types[type] || type || 'No especificado';
    }
    
    formatNumber(number) {
        return new Intl.NumberFormat('es-PA').format(number);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    setLoading(loading) {
        this.state.isLoading = loading;
        if (this.elements.submitBtn) {
            this.elements.submitBtn.disabled = loading;
            this.elements.submitBtn.innerHTML = loading 
                ? '<i class="fas fa-spinner fa-spin"></i> Enviando...'
                : '<i class="fas fa-paper-plane"></i> Enviar Solicitud';
        }
    }
    
    showError(message) {
        this.showAlert(message, 'danger');
    }
    
    showSuccess(message) {
        this.showAlert(message, 'success');
    }
    
    showAlert(message, type) {
        if (!this.elements.alertContainer) return;
        
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        this.elements.alertContainer.innerHTML = alertHtml;
        
        // Auto-hide después de 5 segundos para mensajes de éxito
        if (type === 'success') {
            setTimeout(() => {
                const alert = this.elements.alertContainer.querySelector('.alert');
                if (alert) {
                    alert.remove();
                }
            }, 5000);
        }
    }
    
    log(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] [FinancingRequestV2-VPS] [${level.toUpperCase()}] ${message}`;
        
        if (data) {
            console[level](logMessage, data);
        } else {
            console[level](logMessage);
        }
    }
}

// Crear instancia global
window.FinancingRequestV2 = new FinancingRequestV2();

// Log de inicialización
console.info('🔧 FinancingRequestV2 adaptado para VPS inicializado correctamente'); 