/**
 * SOLICITUD DE FINANCIAMIENTO V2 - VERSIÓN CON AUTENTICACIÓN INTEGRADA
 * Compatible con llamadas directas desde HTML y sistema de autenticación existente
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
            // URLs exactas del VPS
            apiBase: '/api/financing',
            endpoints: {
                plans: '/api/financing/plans/',
                requests: '/api/financing/requests/',
                calculate: '/api/financing/calculate/',
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
     * Obtener cookie
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
     * Fetch básico para endpoints públicos (como planes)
     */
    async apiRequest(url, options = {}) {
        try {
            const headers = {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                ...options.headers
            };
            
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
            
            if (response.status === 401) {
                this.log('warning', 'Usuario no autenticado');
                this.showError('Debe iniciar sesión para continuar');
                return { success: false, status: 401, message: 'No autenticado' };
            }
            
            if (response.status === 403) {
                this.log('error', 'Error de permisos (CSRF o autorización)');
                return { success: false, status: 403, message: 'Sin permisos' };
            }
            
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
     * Fetch autenticado usando el sistema existente
     */
    async authenticatedRequest(url, options = {}) {
        try {
            // Verificar si API está disponible
            if (typeof window.API === 'undefined' || !window.API.users) {
                this.log('error', 'Sistema de autenticación no disponible');
                return { success: false, status: 500, message: 'Error del sistema' };
            }
            
            // Usar el sistema de autenticación existente
            const result = await window.API.users.authFetch(url, options);
            
            this.log('debug', `Authenticated Request: ${options.method || 'GET'} ${url}`, result);
            
            return {
                success: result.success || false,
                status: result.status || (result.success ? 200 : 500),
                data: result.data || result,
                message: result.message || (result.success ? 'Éxito' : 'Error')
            };
            
        } catch (error) {
            this.log('error', 'Error en petición autenticada', error);
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
        this.log('info', 'Inicializando FinancingRequestV2 - Versión con Autenticación Integrada');
        
        // Cachear elementos del DOM
        this.cacheElements();
        
        // Configurar eventos
        this.setupEventListeners();
        
        // Cargar datos de cálculo (CORREGIDO)
        this.loadCalculationData();
        
        // Verificar planes disponibles
        this.loadFinancingPlans();
        
        // Exponer métodos globalmente (MEJORADO)
        this.exposeGlobalMethods();
    }
    
    /**
     * MEJORADO: Exponer métodos globalmente con compatibilidad total
     */
    exposeGlobalMethods() {
        // Exponer la instancia completa
        window.FinancingRequestV2 = this;
        
        // También crear funciones globales directas
        window.nextStep = () => this.nextStep();
        window.prevStep = () => this.prevStep();
        window.submitRequest = () => this.submitRequest();
        
        // NUEVO: Agregar compatibilidad directa con la instancia
        // Esto hace que FinancingRequestV2.nextStep() funcione también
        FinancingRequestV2.nextStep = () => this.nextStep();
        FinancingRequestV2.prevStep = () => this.prevStep();
        FinancingRequestV2.submitRequest = () => this.submitRequest();
        
        this.log('info', 'Métodos expuestos globalmente con compatibilidad total');
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
        if (this.elements.form) {
            this.elements.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitRequest();
            });
        }
        
        // Configurar eventos para las nuevas zonas de upload específicas
        this.setupDocumentUploadEvents();
        
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
        
        Object.values(this.elements.fields).forEach(field => {
            if (field) {
                field.addEventListener('blur', () => this.validateField(field));
                field.addEventListener('change', () => this.clearFieldError(field));
            }
        });
    }
    
    /**
     * Configurar eventos para las nuevas zonas de upload específicas
     */
    setupDocumentUploadEvents() {
        // Buscar todas las zonas de upload específicas
        const uploadZones = document.querySelectorAll('.upload-zone-small');
        
        uploadZones.forEach(zone => {
            const documentType = zone.getAttribute('data-document-type');
            const input = zone.querySelector('.document-input');
            const button = zone.querySelector('button');
            
            if (!documentType || !input) return;
            
            // Click en la zona o botón para seleccionar archivo
            const handleClick = () => input.click();
            zone.addEventListener('click', handleClick);
            if (button) button.addEventListener('click', (e) => {
                e.stopPropagation();
                handleClick();
            });
            
            // Drag & drop
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.classList.add('drag-over');
            });
            
            zone.addEventListener('dragleave', () => {
                zone.classList.remove('drag-over');
            });
            
            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                zone.classList.remove('drag-over');
                if (e.dataTransfer.files.length > 0) {
                    this.handleSpecificDocumentUpload(e.dataTransfer.files[0], documentType, zone);
                }
            });
            
            // Cambio en input
            input.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleSpecificDocumentUpload(e.target.files[0], documentType, zone);
                }
            });
        });
    }
    
    /**
     * Manejar subida de documento específico
     */
    handleSpecificDocumentUpload(file, documentType, zone) {
        if (!this.validateFile(file)) {
            return;
        }
        
        // Almacenar archivo con su tipo específico
        const existingIndex = this.state.uploadedFiles.findIndex(f => f.documentType === documentType);
        const fileWithType = { file, documentType, name: file.name, size: file.size };
        
        if (existingIndex !== -1) {
            // Reemplazar archivo existente del mismo tipo
            this.state.uploadedFiles[existingIndex] = fileWithType;
        } else {
            // Agregar nuevo archivo
            this.state.uploadedFiles.push(fileWithType);
        }
        
        // Actualizar UI de la zona específica
        this.updateDocumentZoneUI(zone, file);
        
        this.log('info', `Documento ${documentType} subido: ${file.name}`);
    }
    
    /**
     * Actualizar UI de zona de documento específica
     */
    updateDocumentZoneUI(zone, file) {
        const uploadedDiv = zone.parentElement.querySelector('.uploaded-file');
        
        if (uploadedDiv) {
            uploadedDiv.style.display = 'flex';
            uploadedDiv.querySelector('.file-name').textContent = file.name;
            
            // Ocultar contenido de upload
            const uploadElements = zone.querySelectorAll('i, p, button');
            uploadElements.forEach(el => el.style.display = 'none');
            
            // Mostrar nombre del archivo en la zona
            zone.innerHTML = `
                <i class="fas fa-file-check fa-2x text-success mb-2"></i>
                <p class="small text-success mb-0">${file.name}</p>
                <small class="text-muted">${this.formatFileSize(file.size)}</small>
            `;
            
            // Configurar botón de eliminar
            const removeBtn = uploadedDiv.querySelector('.remove-file');
            if (removeBtn) {
                removeBtn.onclick = (e) => {
                    e.preventDefault();
                    this.removeSpecificDocument(zone);
                };
            }
        }
    }
    
    /**
     * Remover documento específico
     */
    removeSpecificDocument(zone) {
        const documentType = zone.getAttribute('data-document-type');
        
        // Remover del estado
        this.state.uploadedFiles = this.state.uploadedFiles.filter(f => f.documentType !== documentType);
        
        // Restaurar UI de la zona
        const uploadedDiv = zone.parentElement.querySelector('.uploaded-file');
        if (uploadedDiv) {
            uploadedDiv.style.display = 'none';
        }
        
        // Restaurar contenido original de la zona
        this.restoreUploadZoneUI(zone, documentType);
        
        this.log('info', `Documento ${documentType} removido`);
    }
    
    /**
     * Restaurar UI original de zona de upload
     */
    restoreUploadZoneUI(zone, documentType) {
        const icons = {
            'income_proof': 'fas fa-upload fa-2x text-muted mb-2',
            'id_document': 'fas fa-upload fa-2x text-muted mb-2',
            'address_proof': 'fas fa-upload fa-2x text-muted mb-2'
        };
        
        const colors = {
            'income_proof': 'info',
            'id_document': 'warning', 
            'address_proof': 'success'
        };
        
        zone.innerHTML = `
            <i class="${icons[documentType]}"></i>
            <p class="small text-muted mb-2">Arrastra o haz clic para subir</p>
            <input type="file" class="d-none document-input" 
                   accept=".pdf,.jpg,.jpeg,.png" data-type="${documentType}">
            <button type="button" class="btn btn-outline-${colors[documentType]} btn-sm">
                <i class="fas fa-plus"></i> Seleccionar archivo
            </button>
        `;
        
        // Reconfigurar eventos
        this.setupDocumentUploadEvents();
    }
    
    /**
     * Cargar planes de financiamiento (sin autenticación)
     */
    async loadFinancingPlans() {
        try {
            const result = await this.apiRequest(this.config.endpoints.plans);
            
            if (result.success && result.data && Array.isArray(result.data)) {
                this.state.financingPlans = result.data;
                this.log('info', `Planes de financiamiento cargados: ${result.data.length}`);
                return result.data;
            } else {
                this.log('warning', 'No se pudieron cargar los planes de financiamiento');
                this.state.financingPlans = [];
                return [];
            }
        } catch (error) {
            this.log('error', 'Error cargando planes', error);
            this.state.financingPlans = [];
            return [];
        }
    }
    
    /**
     * CORREGIDO: Cargar datos de cálculo con parseo mejorado de URL
     */
    loadCalculationData() {
        try {
            // Método 1: Desde localStorage
            const savedData = localStorage.getItem('calculationData');
            if (savedData) {
                this.state.calculationData = JSON.parse(savedData);
                this.log('info', 'Datos de cálculo cargados desde localStorage');
                this.renderCalculationSummary();
                this.validateProductData();
                return;
            }
            
            // Método 2: CORREGIDO - Desde parámetros URL
            const urlParams = new URLSearchParams(window.location.search);
            // Obtener product_id directamente del URL
            const directProductId = urlParams.get("product_id");
            if (urlParams.has('calculation')) {
                this.log('info', 'Detectado parámetro calculation en URL');
                
                try {
                    // Decodificar el parámetro calculation
                    const calculationParam = urlParams.get('calculation');
                    const calculationData = JSON.parse(decodeURIComponent(calculationParam));
                    
                    this.log('info', 'Datos de calculation parseados', calculationData);
                    
                    // DEBUG: Ver qué valores específicos tenemos disponibles
                    console.log('🔍 DEBUG - calculationData.product_id:', calculationData.product_id);
                    console.log('🔍 DEBUG - calculationData.product?.id:', calculationData.product?.id);
                    console.log('🔍 DEBUG - directProductId:', directProductId);
                    
                    // Mapear datos de la calculadora al formato V2
                    this.state.calculationData = {
                        product: {
                            id: calculationData.product_id || calculationData.product?.id || directProductId || null,
                            name: calculationData.productName || calculationData.product?.name || 'Producto Seleccionado'
                        },
                        calculation: {
                            // Datos en LLEVO desde la nueva calculadora CrediLlevo
                            product_price: calculationData.priceLlevo || calculationData.calculation?.priceLlevo || 0,
                            down_payment_percentage: 0, // No usado en CrediLlevo (inicial fija)
                            down_payment_amount: calculationData.inicialLlevo || calculationData.calculation?.inicialLlevo || 0,
                            financed_amount: calculationData.montoFinanciar || calculationData.calculation?.montoFinanciar || 0,
                            payment_frequency: 'mensual', // Fijo en CrediLlevo
                            number_of_payments: calculationData.plazoMeses || calculationData.calculation?.plazoMeses || 24,
                            payment_amount: calculationData.cuotaMensual || calculationData.calculation?.cuotaMensual || 0
                        }
                    };
                    
                    this.log('info', 'Datos de cálculo mapeados correctamente', this.state.calculationData);
                    this.renderCalculationSummary();
                    this.validateProductData();
                    return;
                    
                } catch (parseError) {
                    this.log('error', 'Error parseando datos de calculation', parseError);
                }
            }
            
            // Método 3: Desde mode=credito (fallback)
            if (urlParams.has('mode') && urlParams.get('mode') === 'credito') {
                this.log('info', 'Detectados parámetros de crédito inmediato en URL');
                
                this.state.calculationData = {
                    product: {
                        id: urlParams.get('product') || null,
                        name: urlParams.get('name') || 'Producto Seleccionado'
                    },
                    calculation: {
                        product_price: parseFloat(urlParams.get('price') || '19399'),
                        down_payment_percentage: parseInt(urlParams.get('down_payment') || '35'),
                        payment_frequency: 'monthly',
                        number_of_payments: parseInt(urlParams.get('plazo') || '24'),
                        payment_amount: parseFloat(urlParams.get('cuota') || '0')
                    }
                };
                
                // Calcular valores derivados
                const price = this.state.calculationData.calculation.product_price;
                const downPercent = this.state.calculationData.calculation.down_payment_percentage;
                this.state.calculationData.calculation.down_payment_amount = price * (downPercent / 100);
                this.state.calculationData.calculation.financed_amount = price - this.state.calculationData.calculation.down_payment_amount;
                
                this.log('info', 'Datos de cálculo reconstruidos desde URL', this.state.calculationData);
                this.renderCalculationSummary();
                this.validateProductData();
                return;
            }
            
            // Método 4: sessionStorage (backup)
            const sessionData = sessionStorage.getItem('financingData');
            if (sessionData) {
                this.state.calculationData = JSON.parse(sessionData);
                this.log('info', 'Datos de cálculo cargados desde sessionStorage');
                this.renderCalculationSummary();
                this.validateProductData();
                return;
            }
            
            // Método 5: Valores por defecto CrediLlevo
            this.log('warning', 'No se encontraron datos de cálculo - usando valores por defecto CrediLlevo');
            this.state.calculationData = {
                product: { id: null, name: 'Selecciona un producto en la calculadora' },
                calculation: {
                    product_price: 0,
                    down_payment_percentage: 0,
                    down_payment_amount: 0,
                    financed_amount: 0,
                    payment_frequency: 'mensual',
                    number_of_payments: 24,
                    payment_amount: 0
                }
            };
            
            // VALIDACIÓN CRÍTICA: Si no hay product_id válido, redirigir a calculadora
            this.validateProductData();
            
        } catch (error) {
            this.log('error', 'Error cargando datos de cálculo: ' + error.message);
            this.state.calculationData = null;
        }
    }
    
    /**
     * NUEVO: Validar que los datos del producto sean válidos
     */
    validateProductData() {
        const productId = this.state.calculationData?.product?.id;
        
        // Logging para debug
        console.log('🔍 VALIDACIÓN - product_id encontrado:', productId);
        console.log('🔍 VALIDACIÓN - datos completos:', this.state.calculationData);
        
        if (!productId || productId === null || productId === 'null') {
            this.log('error', 'VALIDACIÓN FALLIDA: No hay product_id válido. Redirigiendo a calculadora.');
            
            // Mostrar mensaje de error al usuario
            this.showError('Error: Datos de producto no válidos. Redirigiendo a la calculadora para seleccionar un producto...');
            
            // Redirigir después de 3 segundos
            setTimeout(() => {
                window.location.href = '/calculadora.html';
            }, 3000);
            
            return false;
        }
        
        // Convertir a número si es string
        const numericId = parseInt(productId);
        if (isNaN(numericId)) {
            this.log('error', `VALIDACIÓN FALLIDA: product_id no es un número válido: ${productId}`);
            this.showError('Error: ID de producto inválido. Redirigiendo a la calculadora...');
            
            setTimeout(() => {
                window.location.href = '/calculadora.html';
            }, 3000);
            
            return false;
        }
        
        // Actualizar el product_id con el valor numérico correcto
        this.state.calculationData.product.id = numericId;
        this.log('info', `✅ VALIDACIÓN EXITOSA: product_id válido: ${numericId}`);
        
        // Continuar con renderización
        this.renderCalculationSummary();
        return true;
    }
    
    /**
     * CORREGIDO: Renderizar resumen de cálculo
     */
    renderCalculationSummary() {
        if (!this.state.calculationData || !this.elements.calculationSummary) {
            this.log('warning', 'No hay datos para renderizar o elemento no encontrado');
            return;
        }
        
        const calc = this.state.calculationData.calculation || this.state.calculationData;
        const product = this.state.calculationData.product || {};
        
        // Usar datos disponibles
        const productPrice = parseFloat(calc.product_price || 0);
        const downPaymentPercentage = parseInt(calc.down_payment_percentage || 35);
        const downPaymentAmount = parseFloat(calc.down_payment_amount || (productPrice * (downPaymentPercentage / 100)));
        const financedAmount = parseFloat(calc.financed_amount || (productPrice - downPaymentAmount));
        const paymentAmount = parseFloat(calc.payment_amount || 0);
        
        this.log('info', 'Renderizando valores:', {
            productPrice,
            downPaymentAmount,
            financedAmount,
            paymentAmount
        });
        
        this.elements.calculationSummary.innerHTML = `
            <div class="row text-center">
                <div class="col-md-3">
                    <h3>${this.formatNumber(productPrice)} LLEVO</h3>
                    <small>Precio del Producto</small>
                </div>
                <div class="col-md-3">
                    <h3>${this.formatNumber(downPaymentAmount)} LLEVO</h3>
                    <small>Inicial Fija</small>
                </div>
                <div class="col-md-3">
                    <h3>${this.formatNumber(financedAmount)} LLEVO</h3>
                    <small>Monto a Financiar</small>
                </div>
                <div class="col-md-3">
                    <h3>${this.formatNumber(paymentAmount)} LLEVO</h3>
                    <small>Cuota Mensual</small>
                </div>
            </div>
        `;
        
        // Renderizar detalles si hay elementos
        if (this.elements.productDetails) {
            this.elements.productDetails.innerHTML = `
                <p><strong>Producto:</strong> ${product.name || 'Producto Seleccionado'}</p>
                <p><strong>Precio:</strong> ${this.formatNumber(productPrice)} LLEVO</p>
                <p><strong>Plan:</strong> CrediLlevo Inmediato</p>
                <p><strong>Plazo:</strong> ${calc.number_of_payments || 24} meses fijos</p>
            `;
        }
        
        this.log('info', 'Resumen de cálculo renderizado correctamente');
    }
    
    /**
     * Navegación entre pasos (CORREGIDO)
     */
    nextStep() {
        this.log('info', 'nextStep llamado');
        if (this.validateCurrentStep()) {
            if (this.state.currentStep < 4) {
                this.goToStep(this.state.currentStep + 1);
            }
        }
    }
    
    prevStep() {
        this.log('info', 'prevStep llamado');
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
     * Preparar datos para el VPS (formato exacto del serializer)
     */
    prepareRequestData() {
        this.updateFormData();
        
        const calc = this.state.calculationData?.calculation || {};
        const product = this.state.calculationData?.product || {};
        
        // DEBUG: Ver datos antes de validación
        console.log('🔍 DEBUG - product object completo:', product);
        console.log('🔍 DEBUG - product.id final:', product.id);
        
        // VALIDACIÓN CRÍTICA: Verificar que tenemos un producto válido
        if (!product.id) {
            console.error('❌ DEBUG - No hay product.id válido. Estado completo:', this.state.calculationData);
            this.showError("Error: No se ha seleccionado un producto válido. Por favor, inicia desde la calculadora.");
            throw new Error("Missing product_id");
        }
        
        // Obtener valores numéricos
        const productPrice = parseFloat(calc.product_price || 0);
        const downPaymentPercentage = parseInt(calc.down_payment_percentage || 35);
        const downPaymentAmount = parseFloat(calc.down_payment_amount || 0);
        const financedAmount = parseFloat(calc.financed_amount || 0);
        const numberOfPayments = parseInt(calc.number_of_payments || 24);
        const paymentAmount = parseFloat(calc.payment_amount || 0);
        
        // Calcular campos obligatorios que faltan
        const interestRate = 0.00; // Para crédito inmediato sin intereses
        const totalAmount = downPaymentAmount + (paymentAmount * numberOfPayments);
        const totalInterest = totalAmount - productPrice;
        
        // Preparar datos en el formato EXACTO que espera el serializer
        const data = {
            // Campos obligatorios del serializer
            product: product.id ? parseInt(product.id) : null,
            financing_plan: this.getFinancingPlanByDownPayment(),
            
            // Montos (como números, no strings)
            product_price: parseFloat(productPrice.toFixed(2)),
            down_payment_percentage: downPaymentPercentage,
            down_payment_amount: parseFloat(downPaymentAmount.toFixed(2)),
            financed_amount: parseFloat(financedAmount.toFixed(2)),
            
            // Campos que faltaban (CRÍTICO)
            interest_rate: parseFloat(interestRate.toFixed(2)),
            total_interest: parseFloat(totalInterest.toFixed(2)),
            total_amount: parseFloat(totalAmount.toFixed(2)),
            
            // Plan de pagos
            payment_frequency: "monthly", // CrediLlevo usa pagos mensuales
            number_of_payments: numberOfPayments,
            payment_amount: parseFloat(paymentAmount.toFixed(2)),
            
            // Información del cliente (campos opcionales)
            employment_type: this.state.formData.employment_type || "",
            monthly_income: parseFloat(this.state.formData.monthly_income || 0)
            
            // NOTA: Quitamos todos los campos extra que no están en el serializer:
            // company_name, job_position, work_phone, years_employed, 
            // reference1_name, reference1_phone, reference2_name, reference2_phone
        };
        
        this.log('debug', 'Datos preparados para VPS (formato serializer)', data);
        return data;
    }
    
    /**
     * CORREGIDO: Enviar solicitud usando autenticación integrada
     */
    async submitRequest() {
        try {
            this.log('info', 'Iniciando envío de solicitud con autenticación integrada');
            
            if (!this.validateCurrentStep()) {
                return;
            }
            
            this.setLoading(true);
            
            const requestData = this.prepareRequestData();
            
            // NUEVO: Usar sistema de autenticación integrado
            const result = await this.authenticatedRequest(this.config.endpoints.requests, {
                method: 'POST',
                body: JSON.stringify(requestData)
            });
            
            if (result.success) {
                const requestId = result.data.id || result.data?.data?.id;
                this.state.requestId = requestId;
                
                this.showSuccess('¡Solicitud enviada exitosamente!');
                this.log('info', `Solicitud creada con ID: ${requestId}`);
                
                // Si hay documentos, subirlos (esto automáticamente cambia estado a submitted)
                if (this.state.uploadedFiles.length > 0) {
                    await this.uploadDocuments(requestId);
                } else {
                    // Si no hay documentos, cambiar estado manualmente a submitted
                    await this.submitForReview(requestId);
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
                    this.log('error', 'Error del servidor', result);
                }
            }
            
        } catch (error) {
            this.log('error', 'Error enviando solicitud: ' + error.message);
            this.showError('Error de conexión. Por favor, intente nuevamente.');
        } finally {
            this.setLoading(false);
        }
    }
    
    // Métodos de utilidad
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
                    <button type="button" class="btn btn-sm btn-danger" onclick="window.FinancingRequestV2.removeFile(${index})">
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
                    <p><strong>Plan:</strong> CrediLlevo Inmediato</p>
                    <p><strong>Tipo de Empleo:</strong> ${this.getEmploymentTypeText(this.state.formData.employment_type)}</p>
                    <p><strong>Capacidad de Pago:</strong> ${this.formatNumber(this.state.formData.monthly_income || 0)} (demostrable)</p>
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
    getFinancingPlanByDownPayment() {
        // CORREGIDO: En CrediLlevo solo hay un plan: "CrediLlevo Inmediato" con ID 10
        // La inicial es fija por producto, no variable por porcentaje
        return 10;
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
        
        if (type === 'success') {
            setTimeout(() => {
                const alert = this.elements.alertContainer.querySelector('.alert');
                if (alert) {
                    alert.remove();
                }
            }, 5000);
        }
    }
    
    /**
     * FUNCIÓN DE LOGGING CORREGIDA
     */
    log(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] [FinancingRequestV2-AuthIntegrated] [${level.toUpperCase()}] ${message}`;
        
        const logFunctions = {
            'debug': console.debug || console.log,
            'info': console.info || console.log,
            'warning': console.warn || console.log,
            'error': console.error || console.log
        };
        
        const logFunction = logFunctions[level] || console.log;
        
        if (data) {
            logFunction.call(console, logMessage, data);
        } else {
            logFunction.call(console, logMessage);
        }
    }

    /**
     * Enviar solicitud para revisión (cambiar estado a submitted)
     */
    async submitForReview(requestId) {
        this.log('info', '📤 Enviando solicitud para revisión (cambio de estado draft → submitted)...');
        
        try {
            const result = await this.authenticatedRequest(
                `/api/financing/requests/${requestId}/submit/`,
                { method: 'POST' }
            );
            
            if (result.success) {
                this.log('info', '✅ Solicitud enviada para revisión exitosamente - Estado: submitted');
                return result.data;
            } else {
                this.log('error', '❌ Error enviando para revisión:', result);
                throw new Error('Error al enviar para revisión: ' + (result.message || 'Error desconocido'));
            }
        } catch (error) {
            this.log('error', '💥 Exception en submitForReview:', error);
            throw error;
        }
    }

    /**
     * Subir documentos después de crear la solicitud
     */
    async uploadDocuments(requestId) {
        if (this.state.uploadedFiles.length === 0) {
            this.log('info', 'No hay documentos para subir');
            return;
        }
        
        // Verificación proactiva de autenticación
        if (typeof window.API === 'undefined' || !window.API.users || !window.API.users.isAuthenticated()) {
            this.log('error', 'Usuario no autenticado antes del upload');
            throw new Error('Usuario no autenticado. Por favor, inicie sesión nuevamente.');
        }
        
        this.log('info', `📤 Iniciando upload de ${this.state.uploadedFiles.length} documentos para solicitud ${requestId}...`);
        
        try {
            const formData = new FormData();
            
            // Usar tipos de documentos específicos de las zonas de upload
            this.state.uploadedFiles.forEach((fileData, index) => {
                let fieldName;
                let actualFile;
                
                if (fileData.documentType) {
                    // Nuevo sistema con tipos específicos
                    fieldName = fileData.documentType;
                    actualFile = fileData.file;
                    this.log('info', `📎 Archivo ${index + 1}: ${fileData.name} → ${fieldName} (específico)`);
                } else {
                    // Sistema legacy - detectar por nombre
                    actualFile = fileData;
                    const fileName = fileData.name.toLowerCase();
                    
                    if (fileName.includes('ingreso') || fileName.includes('nomina') || fileName.includes('salario')) {
                        fieldName = 'income_proof';
                    } else if (fileName.includes('cedula') || fileName.includes('identidad') || fileName.includes('id')) {
                        fieldName = 'id_document';
                    } else if (fileName.includes('direccion') || fileName.includes('domicilio') || fileName.includes('residencia')) {
                        fieldName = 'address_proof';
                    } else {
                        // Por defecto, asignar según el orden
                        switch (index) {
                            case 0: fieldName = 'income_proof'; break;
                            case 1: fieldName = 'id_document'; break;
                            case 2: fieldName = 'address_proof'; break;
                            default: fieldName = 'income_proof'; break;
                        }
                    }
                    this.log('info', `📎 Archivo ${index + 1}: ${fileData.name} → ${fieldName} (detectado)`);
                }
                
                formData.append(fieldName, actualFile);
            });
            
            this.log('info', `🚀 Enviando FormData al endpoint: /api/financing/requests/${requestId}/upload_documents/`);
            
            const result = await this.authenticatedRequest(
                `/api/financing/requests/${requestId}/upload_documents/`,
                {
                    method: 'POST',
                    body: formData
                }
            );
            
            if (result.success) {
                this.log('info', '✅ Documentos subidos exitosamente');
                // Limpiar archivos subidos del estado
                this.state.uploadedFiles = [];
                
                // CRUCIAL: Después de subir documentos, enviar para revisión (cambiar estado a submitted)
                try {
                    this.log('info', '📤 Enviando solicitud para revisión después del upload...');
                    await this.submitForReview(requestId);
                    this.log('info', '✅ Solicitud enviada para revisión - Estado cambiado a "submitted"');
                } catch (submitError) {
                    this.log('warning', '⚠️ Documentos subidos pero error al cambiar estado:', submitError);
                    // No lanzar error aquí - los documentos ya se subieron exitosamente
                }
                
                return result.data;
            } else {
                // Manejo mejorado de errores específicos
                let errorMessage = 'Error desconocido';
                
                if (result.message) {
                    errorMessage = result.message;
                } else if (result.data && result.data.error) {
                    errorMessage = result.data.error;
                } else if (result.status === 401) {
                    errorMessage = 'Sesión expirada. Por favor, inicie sesión nuevamente.';
                } else if (result.status === 403) {
                    errorMessage = 'No tiene permisos para subir documentos a esta solicitud.';
                } else if (result.status === 400) {
                    errorMessage = 'Error en los archivos enviados. Verifique el formato y tamaño.';
                } else if (result.status >= 500) {
                    errorMessage = 'Error interno del servidor. Intente nuevamente.';
                }
                
                this.log('error', '❌ Error subiendo documentos:', {
                    status: result.status,
                    message: errorMessage,
                    debug: result.debug || 'No debug info'
                });
                
                throw new Error(errorMessage);
            }
        } catch (error) {
            this.log('error', '💥 Exception en uploadDocuments:', error);
            
            // Re-lanzar con mensaje más claro para el usuario
            if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
                throw new Error('Error de conexión. Verifique su conexión a internet.');
            } else {
                throw error;
            }
        }
    }
}

// Función para inicializar cuando el DOM esté listo y API esté disponible
function initializeFinancingRequestV2() {
    // Verificar que API esté disponible
    if (typeof window.API === 'undefined') {
        console.warn('⏳ API no disponible aún, reintentando en 100ms...');
        setTimeout(initializeFinancingRequestV2, 100);
        return;
    }
    
    // Crear instancia global
    window.FinancingRequestV2 = new FinancingRequestV2();
    console.info('🎯 FinancingRequestV2 - Versión con Autenticación Integrada inicializada correctamente');
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeFinancingRequestV2);
} else {
    // DOM ya está cargado
    initializeFinancingRequestV2();
} 