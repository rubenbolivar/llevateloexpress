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

export default FinancingRequestV2; 