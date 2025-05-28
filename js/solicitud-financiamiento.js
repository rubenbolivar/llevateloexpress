import { Auth } from './auth.js';
import { API } from './api.js';

// Módulo de Solicitud de Financiamiento
const FinancingRequest = {
    currentStep: 1,
    totalSteps: 4,
    calculationData: null,
    selectedFiles: [],
    requestId: null,

    // Inicialización
    async init() {
        // Verificar autenticación
        if (!Auth.isAuthenticated()) {
            window.location.href = '/login.html?redirect=solicitud-financiamiento';
            return;
        }

        // Configurar eventos
        this.setupEventListeners();
        
        // Cargar datos de la calculadora desde URL
        this.loadCalculationData();
        
        // Actualizar UI de autenticación
        Auth.updateAuthUI();
        
        // Renderizar paso inicial
        this.renderCurrentStep();
    },

    // Configurar event listeners
    setupEventListeners() {
        // Logout
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                Auth.logoutUser();
            });
        }

        // Upload de documentos
        const uploadZone = document.getElementById('uploadZone');
        const documentInput = document.getElementById('documentInput');

        if (uploadZone && documentInput) {
            // Click para seleccionar archivo
            uploadZone.addEventListener('click', () => documentInput.click());

            // Drag and drop
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
                this.handleFiles(e.dataTransfer.files);
            });

            // File input change
            documentInput.addEventListener('change', (e) => {
                this.handleFiles(e.target.files);
            });
        }

        // Submit del formulario
        const form = document.getElementById('financingRequestForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitRequest();
            });
        }
    },

    // Cargar datos de la calculadora desde URL
    loadCalculationData() {
        const urlParams = new URLSearchParams(window.location.search);
        const calculationParam = urlParams.get('calculation');
        const requestIdParam = urlParams.get('id');

        if (requestIdParam) {
            // Cargar solicitud existente
            this.requestId = requestIdParam;
            this.loadExistingRequest();
        } else if (calculationParam) {
            // Datos nuevos desde calculadora
            try {
                this.calculationData = JSON.parse(decodeURIComponent(calculationParam));
                this.renderCalculationSummary();
            } catch (error) {
                console.error('Error parsing calculation data:', error);
                this.showError('Error al cargar los datos del cálculo');
                setTimeout(() => {
                    window.location.href = '/calculadora.html';
                }, 3000);
            }
        } else {
            // Sin datos, redirigir a calculadora
            this.showError('No se encontraron datos de cálculo. Redirigiendo...');
            setTimeout(() => {
                window.location.href = '/calculadora.html';
            }, 3000);
        }
    },

    // Cargar solicitud existente
    async loadExistingRequest() {
        try {
            const result = await Auth.fetch(`/api/financing/requests/${this.requestId}/`);
            if (result.success) {
                const request = result.data;
                this.calculationData = {
                    product: request.product,
                    financing_plan: request.financing_plan,
                    calculation: {
                        product_price: request.product_price,
                        down_payment_percentage: request.down_payment_percentage,
                        down_payment_amount: request.down_payment_amount,
                        financed_amount: request.financed_amount,
                        payment_frequency: request.payment_frequency,
                        number_of_payments: request.number_of_payments,
                        payment_amount: request.payment_amount,
                        total_amount: request.total_amount
                    }
                };

                // Llenar formulario con datos existentes
                this.fillFormWithExistingData(request);
                this.renderCalculationSummary();
            } else {
                throw new Error(result.message || 'Error al cargar la solicitud');
            }
        } catch (error) {
            console.error('Error loading existing request:', error);
            this.showError('Error al cargar la solicitud existente');
        }
    },

    // Llenar formulario con datos existentes
    fillFormWithExistingData(request) {
        // Información laboral
        if (request.employment_type) {
            document.getElementById('employment_type').value = request.employment_type;
        }
        if (request.monthly_income) {
            document.getElementById('monthly_income').value = request.monthly_income;
        }

        // Otros campos si están disponibles en el modelo
        // TODO: Agregar más campos según se expanda el modelo
    },

    // Renderizar resumen del cálculo
    renderCalculationSummary() {
        if (!this.calculationData) return;

        const { product, financing_plan, calculation } = this.calculationData;

        // Resumen principal
        const summaryContainer = document.getElementById('calculationSummary');
        summaryContainer.innerHTML = `
            <div class="row text-center">
                <div class="col-md-3">
                    <h3>$${this.formatNumber(calculation.product_price)}</h3>
                    <small>Precio del Producto</small>
                </div>
                <div class="col-md-3">
                    <h3>$${this.formatNumber(calculation.down_payment_amount)}</h3>
                    <small>Inicial (${calculation.down_payment_percentage}%)</small>
                </div>
                <div class="col-md-3">
                    <h3>$${this.formatNumber(calculation.payment_amount)}</h3>
                    <small>Cuota ${this.getFrequencyText(calculation.payment_frequency)}</small>
                </div>
                <div class="col-md-3">
                    <h3>${calculation.number_of_payments}</h3>
                    <small>Número de Cuotas</small>
                </div>
            </div>
        `;

        // Detalles del producto
        const productContainer = document.getElementById('productDetails');
        productContainer.innerHTML = `
            <p><strong>Producto:</strong> ${product?.name || 'Producto Seleccionado'}</p>
            <p><strong>Categoría:</strong> ${product?.category?.name || 'N/A'}</p>
            <p><strong>Precio:</strong> $${this.formatNumber(calculation.product_price)}</p>
            <p><strong>Monto a Financiar:</strong> $${this.formatNumber(calculation.financed_amount)}</p>
        `;

        // Detalles del financiamiento
        const financingContainer = document.getElementById('financingDetails');
        financingContainer.innerHTML = `
            <p><strong>Plan:</strong> ${financing_plan?.name || 'Plan Seleccionado'}</p>
            <p><strong>Frecuencia:</strong> ${this.getFrequencyText(calculation.payment_frequency)}</p>
            <p><strong>Plazo:</strong> ${calculation.number_of_payments} cuotas</p>
            <p><strong>Total a Pagar:</strong> $${this.formatNumber(calculation.total_amount)}</p>
        `;
    },

    // Navegación entre pasos
    nextStep() {
        if (this.currentStep < this.totalSteps) {
            // Validar paso actual antes de continuar
            if (this.validateCurrentStep()) {
                this.currentStep++;
                this.renderCurrentStep();
            }
        }
    },

    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.renderCurrentStep();
        }
    },

    // Renderizar paso actual
    renderCurrentStep() {
        // Actualizar indicador de pasos
        for (let i = 1; i <= this.totalSteps; i++) {
            const step = document.getElementById(`step${i}`);
            const section = document.getElementById(`section${i}`);
            
            if (i < this.currentStep) {
                step.classList.add('completed');
                step.classList.remove('active');
            } else if (i === this.currentStep) {
                step.classList.add('active');
                step.classList.remove('completed');
            } else {
                step.classList.remove('active', 'completed');
            }

            // Mostrar/ocultar secciones
            if (i === this.currentStep) {
                section.classList.add('active');
            } else {
                section.classList.remove('active');
            }
        }

        // Renderizar contenido específico del paso
        switch (this.currentStep) {
            case 1:
                this.renderCalculationSummary();
                break;
            case 4:
                this.renderFinalSummary();
                break;
        }

        // Scroll al top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    // Validar paso actual
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

    // Validar información personal
    validatePersonalInfo() {
        const employmentType = document.getElementById('employment_type').value;
        const monthlyIncome = document.getElementById('monthly_income').value;

        if (!employmentType) {
            this.showError('Por favor seleccione el tipo de empleo');
            return false;
        }

        if (!monthlyIncome || parseFloat(monthlyIncome) <= 0) {
            this.showError('Por favor ingrese un ingreso mensual válido');
            return false;
        }

        return true;
    },

    // Validar paso final
    validateFinalStep() {
        const termsAccept = document.getElementById('termsAccept').checked;
        const dataConsent = document.getElementById('dataConsent').checked;

        if (!termsAccept) {
            this.showError('Debe aceptar los términos y condiciones');
            return false;
        }

        if (!dataConsent) {
            this.showError('Debe autorizar el tratamiento de datos personales');
            return false;
        }

        return true;
    },

    // Renderizar resumen final
    renderFinalSummary() {
        if (!this.calculationData) return;

        const { product, calculation } = this.calculationData;
        const employmentType = document.getElementById('employment_type').value;
        const monthlyIncome = document.getElementById('monthly_income').value;

        const summaryContainer = document.getElementById('finalSummary');
        summaryContainer.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Producto Seleccionado</h6>
                    <p>${product?.name || 'Producto Seleccionado'}</p>
                    <p><strong>Precio:</strong> $${this.formatNumber(calculation.product_price)}</p>
                    
                    <h6 class="mt-3">Plan de Financiamiento</h6>
                    <p><strong>Inicial:</strong> $${this.formatNumber(calculation.down_payment_amount)} (${calculation.down_payment_percentage}%)</p>
                    <p><strong>Cuota:</strong> $${this.formatNumber(calculation.payment_amount)} ${this.getFrequencyText(calculation.payment_frequency)}</p>
                    <p><strong>Plazo:</strong> ${calculation.number_of_payments} cuotas</p>
                </div>
                <div class="col-md-6">
                    <h6>Información Personal</h6>
                    <p><strong>Tipo de Empleo:</strong> ${this.getEmploymentTypeText(employmentType)}</p>
                    <p><strong>Ingreso Mensual:</strong> $${this.formatNumber(monthlyIncome)}</p>
                    
                    <h6 class="mt-3">Documentos</h6>
                    <p>${this.selectedFiles.length} archivo(s) seleccionado(s)</p>
                    
                    <div class="alert alert-info mt-3">
                        <i class="fas fa-info-circle"></i>
                        Su solicitud será revisada por nuestro equipo en un plazo de 24-48 horas.
                    </div>
                </div>
            </div>
        `;
    },

    // Manejar archivos seleccionados
    handleFiles(files) {
        const validTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
        const maxSize = 5 * 1024 * 1024; // 5MB
        
        for (let file of files) {
            if (!validTypes.includes(file.type)) {
                this.showError(`Formato no permitido: ${file.name}`);
                continue;
            }
            
            if (file.size > maxSize) {
                this.showError(`Archivo muy grande: ${file.name} (máx. 5MB)`);
                continue;
            }
            
            this.selectedFiles.push(file);
        }
        
        this.renderFilesList();
    },

    // Renderizar lista de archivos
    renderFilesList() {
        const container = document.getElementById('filesList');
        
        if (this.selectedFiles.length === 0) {
            container.innerHTML = '';
            return;
        }
        
        container.innerHTML = this.selectedFiles.map((file, index) => `
            <div class="file-item">
                <div class="d-flex justify-content-between align-items-center w-100">
                    <span>
                        <i class="fas fa-file"></i> ${file.name}
                        <small class="text-muted">(${this.formatFileSize(file.size)})</small>
                    </span>
                    <button type="button" class="btn btn-sm btn-danger" onclick="FinancingRequest.removeFile(${index})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `).join('');
    },

    // Remover archivo
    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.renderFilesList();
    },

    // Enviar solicitud
    async submitRequest() {
        if (!this.validateCurrentStep()) {
            return;
        }

        const submitBtn = document.getElementById('submitBtn');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...';

        try {
            // Preparar datos de la solicitud
            const requestData = this.prepareRequestData();

            let result;
            if (this.requestId) {
                // Actualizar solicitud existente
                result = await Auth.fetch(`/api/financing/requests/${this.requestId}/`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestData)
                });
            } else {
                // Crear nueva solicitud
                result = await Auth.fetch('/api/financing/requests/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestData)
                });
            }

            if (result.success) {
                const requestId = result.data.id;
                
                // Subir documentos si hay alguno
                if (this.selectedFiles.length > 0) {
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
            console.error('Error submitting request:', error);
            this.showError(error.message || 'Error al enviar la solicitud');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Solicitud';
        }
    },

    // Preparar datos de la solicitud
    prepareRequestData() {
        const { product, financing_plan, calculation } = this.calculationData;

        return {
            product: product?.id,
            financing_plan: financing_plan?.id,
            product_price: calculation.product_price,
            down_payment_percentage: calculation.down_payment_percentage,
            down_payment_amount: calculation.down_payment_amount,
            financed_amount: calculation.financed_amount,
            interest_rate: financing_plan?.interest_rate || 0,
            total_interest: calculation.total_amount - calculation.financed_amount,
            total_amount: calculation.total_amount,
            payment_frequency: calculation.payment_frequency,
            number_of_payments: calculation.number_of_payments,
            payment_amount: calculation.payment_amount,
            employment_type: document.getElementById('employment_type').value,
            monthly_income: parseFloat(document.getElementById('monthly_income').value)
        };
    },

    // Subir documentos
    async uploadDocuments(requestId) {
        if (this.selectedFiles.length === 0) return;

        const formData = new FormData();
        this.selectedFiles.forEach(file => {
            formData.append('documents', file);
        });

        const result = await Auth.fetch(
            `/api/financing/requests/${requestId}/upload_documents/`,
            {
                method: 'POST',
                body: formData
            }
        );

        if (!result.success) {
            throw new Error('Error al subir documentos');
        }
    },

    // Enviar para revisión
    async submitForReview(requestId) {
        const result = await Auth.fetch(
            `/api/financing/requests/${requestId}/submit/`,
            { method: 'POST' }
        );

        if (!result.success) {
            throw new Error('Error al enviar para revisión');
        }
    },

    // Utilidades
    formatNumber(num) {
        return new Intl.NumberFormat('es-VE').format(num);
    },

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    },

    getFrequencyText(frequency) {
        const frequencies = {
            'weekly': 'Semanal',
            'biweekly': 'Quincenal',
            'monthly': 'Mensual'
        };
        return frequencies[frequency] || frequency;
    },

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
    },

    // Mostrar mensajes
    showError(message) {
        this.showAlert(message, 'danger');
    },

    showSuccess(message) {
        this.showAlert(message, 'success');
    },

    showAlert(message, type) {
        const container = document.getElementById('alertContainer');
        container.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Scroll al mensaje
        container.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
};

// Hacer disponible globalmente para los onclick en HTML
window.FinancingRequest = FinancingRequest;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    FinancingRequest.init();
});

export { FinancingRequest }; 