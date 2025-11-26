// Realizar Pago - JavaScript
const PaymentFlow = {
    currentStep: 1,
    selectedApplication: null,
    selectedPaymentMethod: null,
    selectedPaymentMethodData: null,  // Datos completos del método
    selectedFile: null,
    selectedApplicationData: null,  // Datos completos de la solicitud seleccionada
    llevoRate: null,  // Tasa de conversion LLEVO a VES
    amountInLlevo: null,  // Monto original en LLEVO de la solicitud
    
    // Inicializar la aplicación
    init() {
        console.log('🚀 Inicializando flujo de pagos...');
        
        // Verificar autenticación
        if (!Auth.isAuthenticated()) {
            window.location.href = 'login.html';
            return;
        }
        
        this.setupEventListeners();
        this.loadLlevoRate();  // Cargar tasa de conversion
        this.loadApplications();
        this.setCurrentDate();
    },

    // Cargar tasa de conversion LLEVO to VES
    async loadLlevoRate() {
        try {
            const response = await fetch('/api/financing/llevo/current-rate/');
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.data && data.data.llevo_value) {
                    this.llevoRate = parseFloat(data.data.llevo_value);
                    console.log(`Tasa LLEVO cargada: 1 LLEVO = ${this.llevoRate} Bs.`);
                } else {
                    this.llevoRate = 5752.50;
                }
            } else {
                this.llevoRate = 5752.50;
            }
        } catch (error) {
            console.error("Error al cargar tasa LLEVO:", error);
            this.llevoRate = 5752.50;
        }
    },
    

    // ====================================================================
    // MEJORA 3: Funciones de upload de comprobante
    // ====================================================================
    setupFileUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('receiptFile');
        const removeBtn = document.getElementById('removeFile');
        
        if (!uploadArea || !fileInput) return;
        
        // Click en upload area
        uploadArea.addEventListener('click', () => fileInput.click());
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#007bff';
            uploadArea.style.backgroundColor = '#f8f9ff';
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.borderColor = '#dee2e6';
            uploadArea.style.backgroundColor = '';
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#dee2e6';
            uploadArea.style.backgroundColor = '';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                this.handleFileSelect({ target: fileInput });
            }
        });
        
        // Selección de archivo
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Remover archivo
        if (removeBtn) {
            removeBtn.addEventListener('click', () => this.removeFile());
        }
    },
    
    handleFileSelect(event) {
        const file = event.target.files[0];
        
        if (!file) return;
        
        // Validar tipo
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
        if (!validTypes.includes(file.type)) {
            alert('Formato no válido. Solo JPG, PNG o PDF');
            return;
        }
        
        // Validar tamaño (5MB)
        const maxSize = 5 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('Archivo muy grande. Máximo 5MB');
            return;
        }
        
        this.selectedFile = file;
        this.showFilePreview(file);
    },
    
    removeFile() {
        this.selectedFile = null;
        document.getElementById('receiptFile').value = '';
        document.getElementById('filePreview').classList.add('d-none');
        document.getElementById('uploadArea').classList.remove('d-none');
        console.log('Archivo removido');
    },

    // Configurar event listeners
    setupEventListeners() {
        // Navegación entre pasos
        document.getElementById('nextStep1').addEventListener('click', () => this.goToStep(2));
        document.getElementById('nextStep2').addEventListener('click', () => this.handleNextStep2());
        document.getElementById('nextStep3').addEventListener('click', () => this.validateAndSubmitPayment());
        
        document.getElementById('prevStep2').addEventListener('click', () => this.goToStep(1));
        document.getElementById('prevStep3').addEventListener('click', () => this.goToStep(2));
        
        // Upload de archivos
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('receiptFile');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver);
        uploadArea.addEventListener('dragleave', this.handleDragLeave);
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        
        // Actualizar resumen en tiempo real
        document.getElementById('paymentAmount').addEventListener('input', this.updateSummary.bind(this));
        document.getElementById('paymentAmount').addEventListener('input', this.updateConversionDisplay.bind(this));
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
                sessionStorage.setItem("applications", JSON.stringify(approvedApps));
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
        
        // Guardar datos completos de la solicitud
        const applications = JSON.parse(sessionStorage.getItem('applications') || '[]');
        this.selectedApplicationData = applications.find(app => app.id === appId);
        
        document.getElementById('nextStep1').disabled = false;
        
        // Actualizar resumen
        this.updateSummary();
        
        console.log('✅ Solicitud seleccionada:', appId, this.selectedApplicationData);
    },

    
    // Cargar métodos de pago
    async loadPaymentMethods() {
        try {
            console.log('📡 Cargando métodos de pago...');
            const response = await API.users.authFetch('/api/financing/payment-methods/');
            
            if (response.success) {
                console.log("🔍 Response payment-methods:", response);
                const methods = response.data.data || response.data.results || response.data;
                const activeMethods = Array.isArray(methods) ? methods.filter(m => m.id !== 6) : [];
                console.log("🔍 Methods data:", methods);
                console.log("🔍 Active methods:", activeMethods);
                this.paymentMethods = activeMethods;  // Guardar para uso posterior
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
            <div class="payment-card p-3 mb-3 ${method.name.includes("R4") ? "r4-payment-method" : ""}" data-method-id="${method.id}" onclick="PaymentFlow.selectPaymentMethod(${method.id})">
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
        
        // ===== MEJORA 1: Guardar datos completos del método =====
        // Buscar el método en el array de métodos cargados
        this.selectedPaymentMethodData = this.paymentMethods.find(m => m.id === methodId);
        
        document.getElementById('nextStep2').disabled = false;
        
        // Actualizar resumen
        this.updateSummary();
        
        console.log('✅ Método de pago seleccionado:', methodId, this.selectedPaymentMethodData);
    },
    

    // ====================================================================
    // MEJORA 1: Renderizar instrucciones de pago según método seleccionado
    // ====================================================================
    renderPaymentInstructions(method) {
        const instructionsDiv = document.getElementById('paymentInstructions');
        const contentDiv = document.getElementById('paymentInstructionsContent');
        
        if (!method || !method.accounts || method.accounts.length === 0) {
            instructionsDiv.style.display = 'none';
            return;
        }
        
        const account = method.accounts[0];  // Usar primera cuenta
        let html = '';
        
        // Renderizar según tipo de método
        if (method.payment_type === 'mobile_payment') {
            html = `
                <h6 class="mb-3">📱 Realiza tu Pago Móvil a:</h6>
                <ul class="list-unstyled">
                    <li><strong>Banco:</strong> R4 Mi Banco</li>
                    <li><strong>Teléfono:</strong> 0422 1002379</li>
                    <li><strong>RIF:</strong> J-506654547</li>
                    <li><strong>Titular:</strong> LlévateloExpress</li>
                </ul>
                <div class="alert alert-warning mt-3">
                    <small>
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <strong>Importante:</strong> Después de realizar el pago móvil, debes ingresar 
                        el número de referencia y subir la captura de pantalla del comprobante.
                    </small>
                </div>
            `;
        } else if (method.payment_type === 'bank_transfer') {
            html = `
                <h6 class="mb-3">🏦 Realiza tu Transferencia Bancaria a:</h6>
                <ul class="list-unstyled">
                    <li><strong>Banco:</strong> ${account.bank_name}</li>
                    <li><strong>Tipo de cuenta:</strong> ${account.account_type}</li>
                    <li><strong>Número de cuenta:</strong> ${account.account_number}</li>
                    <li><strong>Titular:</strong> ${account.account_holder}</li>
                    <li><strong>Moneda:</strong> ${account.currency}</li>
                </ul>
                <div class="alert alert-warning mt-3">
                    <small>
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <strong>Importante:</strong> Guarda el comprobante de la transferencia para subirlo más abajo.
                    </small>
                </div>
            `;
        } else if (method.payment_type === 'zelle') {
            html = `
                <h6 class="mb-3">💵 Envía tu Zelle a:</h6>
                <ul class="list-unstyled">
                    <li><strong>Email:</strong> ${account.account_number}</li>
                    <li><strong>Nombre del beneficiario:</strong> ${account.account_holder}</li>
                </ul>
                <div class="alert alert-warning mt-3">
                    <small>
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <strong>Importante:</strong> El pago debe realizarse desde tu cuenta personal registrada.
                    </small>
                </div>
            `;
        } else if (method.payment_type === 'cash') {
            html = `
                <h6 class="mb-3">💵 Pago en Efectivo</h6>
                <div class="alert alert-info">
                    <p><strong>Oficina principal:</strong></p>
                    <p>Dirección: [Por definir]</p>
                    <p>Horario: Lunes a Viernes 9:00 AM - 5:00 PM</p>
                </div>
                <div class="alert alert-warning mt-3">
                    <small>
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <strong>Importante:</strong> Solicita tu recibo al momento del pago.
                    </small>
                </div>
            `;
        }
        
        contentDiv.innerHTML = html;
        instructionsDiv.style.display = 'block';
        
        console.log('✅ Instrucciones de pago renderizadas para:', method.name);
    },


    // ====================================================================
    // MEJORA 2: Renderizar campos dinámicos según método seleccionado
    // ====================================================================
    renderDynamicFields(method) {
        const container = document.getElementById('dynamicFieldsContainer');
        
        if (!method) {
            container.innerHTML = '';
            return;
        }
        
        let html = '<div class="row">';
        
        // Campos según tipo de método
        if (method.payment_type === 'mobile_payment') {
            html += `
                <div class="col-md-6 mb-3">
                    <label for="referenceNumber" class="form-label">
                        Número de Referencia *
                    </label>
                    <input type="text" class="form-control" id="referenceNumber" 
                           name="reference_number" placeholder="Ej: 123456" required>
                    <small class="text-muted">Número de referencia del pago móvil</small>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="senderPhone" class="form-label">
                        Teléfono Emisor *
                    </label>
                    <input type="text" class="form-control" id="senderPhone" 
                           name="sender_phone" placeholder="Ej: 0412-1010744 o +58 412-1010744" 
                           minlength="10" maxlength="20" required>
                </div>
            `;
        } else if (method.payment_type === 'bank_transfer') {
            html += `
                <div class="col-md-6 mb-3">
                    <label for="referenceNumber" class="form-label">
                        Número de Referencia *
                    </label>
                    <input type="text" class="form-control" id="referenceNumber" 
                           name="reference_number" placeholder="Referencia bancaria" required>
                    <small class="text-muted">Referencia de la transferencia</small>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="senderBank" class="form-label">
                        Banco Emisor *
                    </label>
                    <input type="text" class="form-control" id="senderBank" 
                           name="sender_bank" placeholder="Ej: Banesco" required>
                    <small class="text-muted">Banco desde donde transferiste</small>
                </div>
            `;
        } else if (method.payment_type === 'zelle') {
            html += `
                <div class="col-md-12 mb-3">
                    <label for="senderEmail" class="form-label">
                        Email del Emisor *
                    </label>
                    <input type="email" class="form-control" id="senderEmail" 
                           name="sender_email" placeholder="tu@email.com" required>
                    <small class="text-muted">Email asociado a tu cuenta Zelle</small>
                </div>
            `;
        } else if (method.payment_type === 'cash') {
            html += `
                <div class="col-md-12 mb-3">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        El pago en efectivo no requiere campos adicionales.
                        Un recibo será generado al momento del pago en nuestras oficinas.
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        
        container.innerHTML = html;
        
        console.log('✅ Campos dinámicos renderizados para:', method.payment_type);
    },

    // Navegar a paso específico
    // ====================================================================
    // OPCIÓN 3: Interceptar flujo R4 automático antes de ir al paso 3
    // ====================================================================
    handleNextStep2() {
        console.log('🔍 Verificando tipo de método de pago seleccionado...');

        // Verificar si hay método seleccionado
        if (!this.selectedPaymentMethodData) {
            alert('Por favor selecciona un método de pago');
            return;
        }

        const paymentType = this.selectedPaymentMethodData.payment_type;
        console.log(`📋 payment_type: ${paymentType}`);

        // ===== DETECCIÓN R4 AUTOMÁTICO POR PAYMENT_TYPE =====
        if (paymentType === 'r4_mobile') {
            console.log('💰 R4 Pago Móvil Automático detectado - Abriendo modal R4');
            this.handleR4AutomaticPayment();
            return;  // No avanzar al paso 3
        }

        // ===== FLUJO NORMAL PARA TODOS LOS DEMÁS MÉTODOS =====
        // Incluye: mobile_payment (manual), bank_transfer, zelle, etc.
        console.log('📝 Método manual detectado - Continuar al paso 3');
        this.goToStep(3);
    },

    // Manejar pago R4 automático
    handleR4AutomaticPayment() {
        console.log('🏦 Iniciando flujo R4 Conecta automático...');

        // Verificar que R4PaymentModal esté disponible
        if (typeof R4PaymentModal === 'undefined') {
            console.error('❌ R4PaymentModal no está cargado');
            alert('Error: Sistema R4 no disponible. Por favor recarga la página.');
            return;
        }

        // Preparar datos para el modal R4
        const paymentData = {
            applicationId: this.selectedApplication,
            applicationNumber: this.selectedApplicationData?.application_number,
            amount: this.selectedApplicationData?.payment_amount || 0,
            productName: this.selectedApplicationData?.product?.name || 'Producto',
            customerName: this.selectedApplicationData?.customer?.full_name || 'Cliente'
        };

        console.log('📦 Datos para R4:', paymentData);

        // Crear y mostrar modal R4
        const r4Modal = new R4PaymentModal();
        r4Modal.showPaymentModal(paymentData);

        console.log('✅ Modal R4 mostrado');
    },

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
        } else if (step === 3) {
            // ===== MEJORA 1, 2 y 3: Instrucciones, campos y upload =====
            if (this.selectedPaymentMethodData) {
                this.renderPaymentInstructions(this.selectedPaymentMethodData);
                this.renderDynamicFields(this.selectedPaymentMethodData);
                this.setupFileUpload();
            }

            // Pre-cargar monto en Bs. basado en la solicitud
            if (this.selectedApplicationData && this.llevoRate) {
                const amountLLEVO = parseFloat(this.selectedApplicationData.payment_amount || 0);
                const amountVES = amountLLEVO * this.llevoRate;
                this.amountInLlevo = amountLLEVO;  // Guardar monto original en LLEVO
                document.getElementById("paymentAmount").value = amountVES.toFixed(2);
                this.updateConversionDisplay();
                console.log(`💰 Monto pre-cargado: ${amountLLEVO} LLEVO = ${amountVES.toFixed(2)} Bs.`);
            }
        }

        console.log('📍 Navegando al paso:', step);
    },
    // Validar y enviar pago
    validateAndSubmitPayment() {
        const form = document.getElementById("paymentForm");
        
        // Validar campos del formulario
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        // Validar que el comprobante esté seleccionado
        if (!this.selectedFile) {
            alert("Por favor selecciona un comprobante de pago");
            return;
        }
        
        // Enviar pago directamente
        this.submitPayment();
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
        document.getElementById('nextStep3').disabled = false;
        
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
    
    
    // Enviar pago
    async submitPayment() {
        try {
            console.log('📤 Enviando pago...');
            
            // Mostrar loading
            const submitBtn = document.getElementById("nextStep3");
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = "<i class=\"fas fa-spinner fa-spin me-1\"></i> Enviando...";
            submitBtn.disabled = true;
            
            // Preparar FormData
            const formData = new FormData();
            formData.append('application_id', this.selectedApplication);
            formData.append('payment_method_id', this.selectedPaymentMethod);
            formData.append("amount", this.amountInLlevo || document.getElementById("paymentAmount").value);
            formData.append('payment_date', document.getElementById('paymentDate').value);
            formData.append('receipt_file', this.selectedFile);
            
            
            // Agregar campos opcionales solo si existen
            const optionalFields = {
                'referenceNumber': 'reference_number',
                'transactionId': 'transaction_id',
                'senderBank': 'sender_bank',
                'senderName': 'sender_name',
                'senderPhone': 'sender_phone',
                'customerNotes': 'customer_notes'
            };
            
            for (const [fieldId, backendName] of Object.entries(optionalFields)) {
                const element = document.getElementById(fieldId);
                if (element && element.value) {
                    formData.append(backendName, element.value);
                }
            }
            
            const result = await Auth.fetch("/api/financing/submit-payment/", {
                method: "POST",
                body: formData
            });
            
            if (result.success) {
                console.log("✅ Pago enviado exitosamente:", result);
                this.showSuccessModal(result.data);
            } else {
                throw new Error(result.message || "Error al enviar el pago");
            }
        } catch (error) {
            console.error("❌ Error enviando pago:", error);
            this.showError("Error al enviar el pago: " + error.message);
            // Restaurar botón
            
            const submitBtn = document.getElementById("nextStep3");
            submitBtn.innerHTML = "🔄 Enviar Pago";
            submitBtn.disabled = false;
        }
    },
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
        
        const amount = document.getElementById("paymentAmount").value;
        // Monto
        if (amount && this.amountInLlevo) {
            const amountVES = parseFloat(amount);
            const formattedVES = this.formatNumber(amountVES);
            const formattedLLEVO = this.formatNumber(this.amountInLlevo);
            document.getElementById('summaryAmount').textContent = `${formattedLLEVO} LLEVO (≈ ${formattedVES} Bs.)`;
        } else if (amount) {
            document.getElementById('summaryAmount').textContent = `${this.formatNumber(amount)} Bs.`;
        }
        
        // Fecha
        const date = document.getElementById('paymentDate').value;
        if (date) {
            document.getElementById('summaryDate').textContent = new Date(date).toLocaleDateString('es-ES');
        }
    },
    // ===== MEJORA 4: Conversion LLEVO to VES Display =====
    updateConversionDisplay() {
        const amountInput = document.getElementById("paymentAmount");
        const conversionDiv = document.getElementById("conversionDisplay");
        
        if (!amountInput || !conversionDiv) return;
        
        const amountVES = parseFloat(amountInput.value || 0);
        
        // Mostrar el monto original en LLEVO si está disponible
        if (this.amountInLlevo && this.llevoRate && amountVES > 0) {
            conversionDiv.innerHTML = `
                <div class="alert alert-success py-2 px-3 mb-0">
                    <i class="fas fa-info-circle"></i> 
                    <strong>${this.formatNumber(this.amountInLlevo)} LLEVO = ${this.formatNumber(amountVES)} Bs.</strong>
                    <small class="text-muted d-block mt-1">
                        (Tasa: 1 LLEVO = ${this.formatNumber(this.llevoRate)} Bs.)
                    </small>
                </div>
            `;
        } else {
            conversionDiv.innerHTML = "";
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
}); /* Cache busting: 1761163160 */
