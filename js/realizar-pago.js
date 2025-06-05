// Realizar Pago - JavaScript
const PaymentFlow = {
    currentStep: 1,
    selectedApplication: null,
    selectedPaymentMethod: null,
    selectedFile: null,
    
    // Inicializar la aplicación
    init() {
        console.log('🚀 Inicializando flujo de pagos...');
        
        // Verificar autenticación
        if (!Auth.isAuthenticated()) {
            window.location.href = 'login.html';
            return;
        }
        
        this.setupEventListeners();
        this.loadApplications();
        this.setCurrentDate();
    },
    
    // Configurar event listeners
    setupEventListeners() {
        // Navegación entre pasos
        document.getElementById('nextStep1').addEventListener('click', () => this.goToStep(2));
        document.getElementById('nextStep2').addEventListener('click', () => this.goToStep(3));
        document.getElementById('nextStep3').addEventListener('click', () => this.validateAndGoToStep(4));
        
        document.getElementById('prevStep2').addEventListener('click', () => this.goToStep(1));
        document.getElementById('prevStep3').addEventListener('click', () => this.goToStep(2));
        document.getElementById('prevStep4').addEventListener('click', () => this.goToStep(3));
        
        // Upload de archivos
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('receiptFile');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver);
        uploadArea.addEventListener('dragleave', this.handleDragLeave);
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        document.getElementById('removeFile').addEventListener('click', this.removeFile.bind(this));
        
        // Envío del formulario
        document.getElementById('submitPayment').addEventListener('click', this.submitPayment.bind(this));
        
        // Actualizar resumen en tiempo real
        document.getElementById('paymentAmount').addEventListener('input', this.updateSummary.bind(this));
        document.getElementById('paymentDate').addEventListener('change', this.updateSummary.bind(this));
    },
    
    // Establecer fecha actual
    setCurrentDate() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('paymentDate').value = today;
    },
    
    // Cargar solicitudes del usuario
    async loadApplications() {
        try {
            console.log('📡 Cargando solicitudes del usuario...');
            const response = await API.users.authFetch('/api/financing/my-requests/');
            
            if (response.success) {
                const applications = response.data.results || response.data;
                const approvedApps = applications.filter(app => app.status === 'approved' || app.status === 'active');
                this.renderApplications(approvedApps);
            } else {
                this.showError('Error al cargar solicitudes: ' + response.message);
            }
        } catch (error) {
            console.error('❌ Error cargando solicitudes:', error);
            this.showError('Error de conexión al cargar solicitudes');
        }
    },
    
    // Renderizar solicitudes
    renderApplications(applications) {
        const container = document.getElementById('applicationsContainer');
        
        if (applications.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                    <h5>No tienes solicitudes aprobadas</h5>
                    <p class="text-muted">Solo puedes realizar pagos para solicitudes aprobadas.</p>
                    <a href="dashboard.html" class="btn btn-primary">Ir al Dashboard</a>
                </div>
            `;
            return;
        }
        
        container.innerHTML = applications.map(app => `
            <div class="payment-card p-3 mb-3" data-app-id="${app.id}" onclick="PaymentFlow.selectApplication(${app.id})">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h6 class="mb-1">
                            <i class="fas fa-file-invoice text-primary me-2"></i>
                            ${app.application_number || `Solicitud #${app.id}`}
                        </h6>
                        <p class="mb-1"><strong>Producto:</strong> ${app.product_name || 'N/A'}</p>
                        <p class="mb-1"><strong>Cuota mensual:</strong> $${this.formatNumber(app.payment_amount || 0)}</p>
                        <span class="badge bg-${this.getStatusColor(app.status)}">${app.status_display || app.status}</span>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="selectedApplication" 
                                   id="app_${app.id}" value="${app.id}">
                            <label class="form-check-label" for="app_${app.id}">
                                Seleccionar
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    },
    
    // Seleccionar solicitud
    selectApplication(appId) {
        // Remover selección anterior
        document.querySelectorAll('.payment-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Seleccionar nueva
        const selectedCard = document.querySelector(`[data-app-id="${appId}"]`);
        selectedCard.classList.add('selected');
        
        const radio = document.getElementById(`app_${appId}`);
        radio.checked = true;
        
        this.selectedApplication = appId;
        document.getElementById('nextStep1').disabled = false;
        
        // Actualizar resumen
        this.updateSummary();
        
        console.log('✅ Solicitud seleccionada:', appId);
    },
    
    // Cargar métodos de pago
    async loadPaymentMethods() {
        try {
            console.log('📡 Cargando métodos de pago...');
            const response = await API.users.authFetch('/api/financing/payment-methods/');
            
            if (response.success) {
                const methods = response.data.results || response.data;
                const activeMethods = methods.filter(method => method.is_active);
                this.renderPaymentMethods(activeMethods);
            } else {
                this.showError('Error al cargar métodos de pago: ' + response.message);
            }
        } catch (error) {
            console.error('❌ Error cargando métodos de pago:', error);
            this.showError('Error de conexión al cargar métodos de pago');
        }
    },
    
    // Renderizar métodos de pago
    renderPaymentMethods(methods) {
        const container = document.getElementById('paymentMethodsContainer');
        
        container.innerHTML = methods.map(method => `
            <div class="payment-card p-3 mb-3" data-method-id="${method.id}" onclick="PaymentFlow.selectPaymentMethod(${method.id})">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h6 class="mb-1">
                            <i class="fas fa-${this.getPaymentIcon(method.payment_type)} text-primary me-2"></i>
                            ${method.name}
                        </h6>
                        <p class="mb-1 text-muted">${method.description}</p>
                        ${method.instructions ? `<small class="text-info">${method.instructions}</small>` : ''}
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="selectedMethod" 
                                   id="method_${method.id}" value="${method.id}">
                            <label class="form-check-label" for="method_${method.id}">
                                Seleccionar
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    },
    
    // Seleccionar método de pago
    selectPaymentMethod(methodId) {
        // Remover selección anterior
        document.querySelectorAll('.payment-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Seleccionar nuevo
        const selectedCard = document.querySelector(`[data-method-id="${methodId}"]`);
        selectedCard.classList.add('selected');
        
        const radio = document.getElementById(`method_${methodId}`);
        radio.checked = true;
        
        this.selectedPaymentMethod = methodId;
        document.getElementById('nextStep2').disabled = false;
        
        // Actualizar resumen
        this.updateSummary();
        
        console.log('✅ Método de pago seleccionado:', methodId);
    },
    
    // Navegar a paso específico
    async goToStep(step) {
        // Ocultar paso actual
        document.getElementById(`step-${this.currentStep}`).classList.add('d-none');
        
        // Actualizar indicadores
        document.getElementById(`step${this.currentStep}`).classList.remove('active');
        document.getElementById(`step${this.currentStep}`).classList.add('completed');
        
        if (this.currentStep < step) {
            document.getElementById(`line${this.currentStep}`).classList.add('completed');
        }
        
        // Mostrar nuevo paso
        this.currentStep = step;
        document.getElementById(`step-${step}`).classList.remove('d-none');
        document.getElementById(`step${step}`).classList.add('active');
        
        // Cargar datos específicos del paso
        if (step === 2) {
            await this.loadPaymentMethods();
        }
        
        console.log('📍 Navegando al paso:', step);
    },
    
    // Validar y ir al paso 4
    validateAndGoToStep(step) {
        const form = document.getElementById('paymentForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        this.goToStep(step);
    },
    
    // Manejar drag over
    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    },
    
    // Manejar drag leave
    handleDragLeave(e) {
        e.currentTarget.classList.remove('dragover');
    },
    
    // Manejar drop
    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    },
    
    // Manejar selección de archivo
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.handleFile(file);
        }
    },
    
    // Procesar archivo
    handleFile(file) {
        // Validar tipo de archivo
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('Tipo de archivo no permitido. Solo se aceptan JPG, PNG y PDF.');
            return;
        }
        
        // Validar tamaño (5MB)
        if (file.size > 5 * 1024 * 1024) {
            this.showError('El archivo es demasiado grande. Máximo 5MB.');
            return;
        }
        
        this.selectedFile = file;
        this.showFilePreview(file);
        document.getElementById('submitPayment').disabled = false;
        
        console.log('✅ Archivo seleccionado:', file.name);
    },
    
    // Mostrar preview del archivo
    showFilePreview(file) {
        const preview = document.getElementById('filePreview');
        const previewImage = document.getElementById('previewImage');
        const previewPdf = document.getElementById('previewPdf');
        const fileName = document.getElementById('fileName');
        
        preview.classList.remove('d-none');
        
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';
                previewPdf.classList.add('d-none');
            };
            reader.readAsDataURL(file);
        } else if (file.type === 'application/pdf') {
            previewImage.style.display = 'none';
            previewPdf.classList.remove('d-none');
            fileName.textContent = file.name;
        }
    },
    
    // Remover archivo
    removeFile() {
        this.selectedFile = null;
        document.getElementById('filePreview').classList.add('d-none');
        document.getElementById('receiptFile').value = '';
        document.getElementById('submitPayment').disabled = true;
        
        console.log('🗑️ Archivo removido');
    },
    
    // Enviar pago
    async submitPayment() {
        try {
            console.log('📤 Enviando pago...');
            
            // Mostrar loading
            const submitBtn = document.getElementById('submitPayment');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Enviando...';
            submitBtn.disabled = true;
            
            // Preparar FormData
            const formData = new FormData();
            formData.append('application_id', this.selectedApplication);
            formData.append('payment_method_id', this.selectedPaymentMethod);
            formData.append('amount', document.getElementById('paymentAmount').value);
            formData.append('payment_date', document.getElementById('paymentDate').value);
            formData.append('reference_number', document.getElementById('referenceNumber').value);
            formData.append('transaction_id', document.getElementById('transactionId').value);
            formData.append('sender_bank', document.getElementById('senderBank').value);
            formData.append('sender_name', document.getElementById('senderName').value);
            formData.append('customer_notes', document.getElementById('customerNotes').value);
            formData.append('receipt_file', this.selectedFile);
            
            // Enviar al servidor
            const response = await fetch('/api/financing/submit-payment/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${Auth.getToken()}`,
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                console.log('✅ Pago enviado exitosamente:', result);
                this.showSuccessModal(result.data);
            } else {
                throw new Error(result.message || 'Error al enviar el pago');
            }
            
        } catch (error) {
            console.error('❌ Error enviando pago:', error);
            this.showError('Error al enviar el pago: ' + error.message);
            
            // Restaurar botón
            const submitBtn = document.getElementById('submitPayment');
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    },
    
    // Mostrar modal de éxito
    showSuccessModal(paymentData) {
        document.getElementById('paymentReference').textContent = paymentData.reference_number || paymentData.id;
        const modal = new bootstrap.Modal(document.getElementById('successModal'));
        modal.show();
    },
    
    // Actualizar resumen
    updateSummary() {
        // Solicitud
        if (this.selectedApplication) {
            const appCard = document.querySelector(`[data-app-id="${this.selectedApplication}"]`);
            const appNumber = appCard.querySelector('h6').textContent.trim();
            document.getElementById('summaryApplication').textContent = appNumber;
        }
        
        // Método de pago
        if (this.selectedPaymentMethod) {
            const methodCard = document.querySelector(`[data-method-id="${this.selectedPaymentMethod}"]`);
            const methodName = methodCard.querySelector('h6').textContent.trim();
            document.getElementById('summaryMethod').textContent = methodName;
        }
        
        // Monto
        const amount = document.getElementById('paymentAmount').value;
        if (amount) {
            document.getElementById('summaryAmount').textContent = `$${this.formatNumber(amount)}`;
        }
        
        // Fecha
        const date = document.getElementById('paymentDate').value;
        if (date) {
            document.getElementById('summaryDate').textContent = new Date(date).toLocaleDateString('es-ES');
        }
    },
    
    // Obtener CSRF token
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    },
    
    // Obtener icono para tipo de pago
    getPaymentIcon(type) {
        const icons = {
            'bank_transfer': 'university',
            'mobile_payment': 'mobile-alt',
            'zelle': 'dollar-sign',
            'binance': 'bitcoin',
            'cash': 'money-bill',
            'check': 'money-check',
            'other': 'credit-card'
        };
        return icons[type] || 'credit-card';
    },
    
    // Obtener color para estado
    getStatusColor(status) {
        const colors = {
            'approved': 'success',
            'active': 'primary',
            'submitted': 'warning',
            'under_review': 'info'
        };
        return colors[status] || 'secondary';
    },
    
    // Formatear números
    formatNumber(num) {
        return parseFloat(num).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    },
    
    // Mostrar error
    showError(message) {
        // Crear toast de error
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-danger border-0 position-fixed top-0 end-0 m-3';
        toast.style.zIndex = '9999';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remover después de que se oculte
        toast.addEventListener('hidden.bs.toast', () => {
            document.body.removeChild(toast);
        });
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    PaymentFlow.init();
}); 