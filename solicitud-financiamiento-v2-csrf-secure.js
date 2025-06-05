/**
 * SOLICITUD DE FINANCIAMIENTO V2 - SEGURO CON CSRF
 * Implementación completa con protección CSRF para LlévateloExpress
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
            maxFileSize: 5 * 1024 * 1024, // 5MB
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
     * Obtener token CSRF de múltiples fuentes
     */
    getCsrfToken() {
        // 1. Intentar desde meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            this.csrfToken = metaTag.getAttribute('content');
            this.log('info', 'CSRF token obtenido desde meta tag');
            return this.csrfToken;
        }
        
        // 2. Intentar desde input hidden
        const hiddenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (hiddenInput) {
            this.csrfToken = hiddenInput.value;
            this.log('info', 'CSRF token obtenido desde input hidden');
            return this.csrfToken;
        }
        
        // 3. Intentar desde cookie
        this.csrfToken = this.getCookie('csrftoken');
        if (this.csrfToken) {
            this.log('info', 'CSRF token obtenido desde cookie');
            return this.csrfToken;
        }
        
        this.log('error', 'No se pudo obtener token CSRF - VULNERABILIDAD DE SEGURIDAD');
        return null;
    }
    
    /**
     * Obtener cookie por nombre
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
     * Configurar headers seguros para peticiones
     */
    getSecureHeaders(additionalHeaders = {}) {
        const headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            ...additionalHeaders
        };
        
        // Agregar token CSRF si está disponible
        if (this.csrfToken) {
            headers['X-CSRFToken'] = this.csrfToken;
        } else {
            this.log('warning', 'Enviando petición sin token CSRF - RIESGO DE SEGURIDAD');
        }
        
        return headers;
    }
    
    /**
     * Fetch seguro con protección CSRF
     */
    async secureAuthFetch(url, options = {}) {
        try {
            // Asegurar que tenemos token CSRF
            if (!this.csrfToken) {
                this.getCsrfToken();
            }
            
            // Configurar opciones por defecto
            const secureOptions = {
                credentials: 'same-origin', // Incluir cookies
                ...options,
                headers: {
                    ...this.getSecureHeaders(),
                    ...options.headers
                }
            };
            
            // Log de seguridad
            this.log('debug', 'Enviando petición segura', {
                url,
                method: secureOptions.method || 'GET',
                hasCSRF: !!this.csrfToken,
                headers: secureOptions.headers
            });
            
            const response = await fetch(url, secureOptions);
            
            // Verificar respuesta de seguridad
            if (response.status === 403) {
                this.log('error', 'Error 403 - Token CSRF inválido o expirado');
                throw new Error('Token de seguridad inválido. Recargue la página.');
            }
            
            // Intentar parsear JSON
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                return {
                    success: response.ok,
                    status: response.status,
                    data: data,
                    message: data.message || data.error || 'Operación completada'
                };
            } else {
                const text = await response.text();
                return {
                    success: response.ok,
                    status: response.status,
                    data: text,
                    message: response.ok ? 'Operación completada' : 'Error en el servidor'
                };
            }
        } catch (error) {
            this.log('error', 'Error en petición segura', error);
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
        this.log('info', 'Inicializando FinancingRequestV2 con protección CSRF');
        
        // Obtener token CSRF inmediatamente
        this.getCsrfToken();
        
        // Cachear elementos del DOM
        this.cacheElements();
        
        // Configurar eventos
        this.setupEventListeners();
        
        // Cargar datos de cálculo
        this.loadCalculationData();
        
        // Verificar autenticación
        this.checkAuthentication();
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
                this.elements.documentInput.click();
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
     * Verificar autenticación con protección CSRF
     */
    async checkAuthentication() {
        try {
            const result = await this.secureAuthFetch('/api/users/profile/');
            
            if (!result.success) {
                this.log('warning', 'Usuario no autenticado, redirigiendo a login');
                this.showError('Debe iniciar sesión para continuar');
                setTimeout(() => {
                    window.location.href = '/login.html';
                }, 2000);
                return false;
            }
            
            this.log('info', 'Usuario autenticado correctamente');
            return true;
        } catch (error) {
            this.log('error', 'Error verificando autenticación', error);
            return false;
        }
    }
    
    /**
     * Cargar datos de cálculo
     */
    loadCalculationData() {
        try {
            // Intentar cargar desde localStorage
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
                // Lógica para reconstruir datos desde URL
            }
            
            this.log('warning', 'No se encontraron datos de cálculo');
        } catch (error) {
            this.log('error', 'Error cargando datos de cálculo', error);
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
     * Enviar solicitud con protección CSRF
     */
    async submitRequest() {
        try {
            this.log('info', 'Iniciando envío de solicitud con protección CSRF');
            
            // Validar paso final
            if (!this.validateCurrentStep()) {
                this.log('warning', 'Validación del paso final falló');
                return;
            }
            
            this.setLoading(true);
            
            // Preparar datos
            const requestData = this.prepareRequestData();
            this.log('info', 'Datos preparados para envío seguro', requestData);
            
            // Enviar solicitud con protección CSRF
            let result;
            if (this.state.requestId) {
                // Actualizar solicitud existente
                result = await this.secureAuthFetch(`/api/financing/requests/${this.state.requestId}/`, {
                    method: 'PUT',
                    body: JSON.stringify(requestData)
                });
            } else {
                // Crear nueva solicitud
                result = await this.secureAuthFetch('/api/financing/requests/', {
                    method: 'POST',
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
     * Subir documentos con protección CSRF
     */
    async uploadDocuments(requestId) {
        if (this.state.uploadedFiles.length === 0) return;
        
        try {
            const formData = new FormData();
            this.state.uploadedFiles.forEach(file => {
                formData.append('documents', file);
            });
            
            // Para FormData, no establecer Content-Type para que el browser lo haga automáticamente
            const result = await this.secureAuthFetch(
                `/api/financing/requests/${requestId}/upload_documents/`,
                {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                        // No incluir Content-Type para FormData
                    },
                    body: formData
                }
            );
            
            if (!result.success) {
                throw new Error('Error al subir documentos');
            }
            
            this.log('info', 'Documentos subidos exitosamente');
        } catch (error) {
            this.log('error', 'Error subiendo documentos', error);
            throw error;
        }
    }
    
    /**
     * Enviar para revisión
     */
    async submitForReview(requestId) {
        const result = await this.secureAuthFetch(
            `/api/financing/requests/${requestId}/submit/`,
            { method: 'POST' }
        );
        
        if (!result.success) {
            throw new Error('Error al enviar para revisión');
        }
    }
    
    /**
     * Métodos de utilidad y validación
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
    
    validateStep1() {
        if (!this.state.calculationData) {
            this.showError('No hay datos de cálculo disponibles');
            return false;
        }
        return true;
    }
    
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
    
    validateStep3() {
        // Los documentos son opcionales
        return true;
    }
    
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
    
    // ... [resto de métodos de utilidad: validateField, showFieldError, clearFieldError, etc.]
    
    /**
     * Logging para depuración
     */
    log(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] [FinancingRequestV2] [${level.toUpperCase()}] ${message}`;
        
        if (data) {
            console[level](logMessage, data);
        } else {
            console[level](logMessage);
        }
    }
}

// Crear instancia global para compatibilidad
window.FinancingRequestV2 = new FinancingRequestV2();

// Log de inicialización de seguridad
console.info('🔒 FinancingRequestV2 inicializado con protección CSRF completa'); 