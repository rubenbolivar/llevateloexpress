// Dashboard Module

// Variable global para la tasa LLEVO actual
let currentLlevoRate = 4186.05;

// Función para obtener la tasa LLEVO actual
async function getCurrentLlevoRate() {
    try {
        const response = await fetch('/api/financing/llevo/current-rate/');
        if (!response.ok) {
            throw new Error('Error al obtener tasa LLEVO');
        }
        const data = await response.json();
        return data.data.llevo_value || 4186.05;
    } catch (error) {
        console.error('Error obteniendo tasa LLEVO:', error);
        return 4186.05;
    }
}

const Dashboard = {
    currentRequestId: null,
    selectedFiles: [],
    pendingPayments: [],  // Pagos pendientes para polling
    pollingInterval: null,  // Intervalo de polling
    POLLING_INTERVAL_MS: 15000,  // 15 segundos

    // Inicialización
    async init() {
        // Verificar autenticación
        if (!API.users.isAuthenticated()) {
            window.location.href = '/login.html?redirect=dashboard';
            return;
        }

        // Configurar eventos
        this.setupEventListeners();
        
        // Cargar datos del dashboard
        // Cargar tasa LLEVO actual
        currentLlevoRate = await getCurrentLlevoRate();
        // Mostrar tasa en el cuadro informativo
        const tasaElement = document.getElementById("tasaLlevoHoy");
        if (tasaElement) {
            tasaElement.textContent = this.formatNumber(currentLlevoRate) + " Bs = 1 LLEVO";
        }
        await this.loadDashboardData();
        
        // Actualizar UI de autenticación
        updateAuthUI();
        
        // Configurar mensaje de bienvenida
        this.setWelcomeMessage();
        
        // Iniciar polling de pagos pendientes
        this.startPaymentPolling();
        
        // Verificar si hay pago R4 pendiente que ya fue procesado
        this.checkPendingR4Payment();
    },

    // Configurar event listeners
    setupEventListeners() {
        // Logout
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                API.users.logout();
            });
        }

        // Upload modal
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');
        const uploadBtn = document.getElementById('uploadBtn');

        if (uploadZone && fileInput) {
            // Click para seleccionar archivo
            uploadZone.addEventListener('click', () => fileInput.click());

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
            fileInput.addEventListener('change', (e) => {
                this.handleFiles(e.target.files);
            });
        }

        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this.uploadDocuments());
        }
    },

    // Establecer mensaje de bienvenida
    setWelcomeMessage() {
        const userEmail = localStorage.getItem('userEmail');
        const welcomeMessage = document.getElementById('welcomeMessage');
        const userEmailSpan = document.getElementById('userEmail');
        
        if (userEmail) {
            const userName = userEmail.split('@')[0];
            if (welcomeMessage) {
                welcomeMessage.textContent = `¡Bienvenido, ${userName}!`;
            }
            if (userEmailSpan) {
                userEmailSpan.textContent = userEmail;
            }
        }
    },

    // Cargar datos del dashboard
    async loadDashboardData() {
        try {
            console.log('🔍 Iniciando carga de datos del dashboard...');
            // Mostrar loading
            this.showLoading();

            // Cargar solicitudes del usuario
            console.log('📡 Llamando a /api/financing/my-requests/...');
            const requestsResult = await API.users.authFetch('/api/financing/my-requests/');
            console.log('📊 Resultado de solicitudes:', requestsResult);
            
            if (requestsResult.success) {
                // Manejar respuesta paginada: los datos están en .results
                const requestsData = requestsResult.data.results || requestsResult.data;
                console.log('✅ Datos de solicitudes obtenidos:', requestsData.length, 'solicitudes');
                console.log('📋 Estructura de datos:', {
                    'Es array': Array.isArray(requestsData),
                    'Cantidad': requestsData.length,
                    'Primer elemento': requestsData[0]?.application_number
                });
                this.renderRequests(requestsData);
                this.updateStats(requestsData);
            } else {
                console.error('❌ Error en respuesta de solicitudes:', requestsResult);
                this.showError(`Error al cargar solicitudes: ${requestsResult.message || 'Error desconocido'}`);
            }

            // Cargar calendario de pagos
            console.log('📡 Llamando a /api/financing/payment-schedule/...');
            const scheduleResult = await API.users.authFetch('/api/financing/payment-schedule/');
            console.log('📅 Resultado de calendario:', scheduleResult);
            
            if (scheduleResult.success) {
                // Manejar respuesta paginada: los datos están en .results
                const scheduleData = scheduleResult.data.results || scheduleResult.data;
                console.log('📅 Datos de calendario procesados:', {
                    'Es array': Array.isArray(scheduleData),
                    'Cantidad': scheduleData.length || 0
                });

                // Renderizar pago inicial (de las solicitudes aprobadas/activas)
                const requestsData = requestsResult.data.results || requestsResult.data;
                this.renderInitialPayments(requestsData);

                this.renderPaymentSchedule(scheduleData);
                
                // Cargar pagos verificados para estadísticas
                const paymentsResult = await API.users.authFetch('/api/financing/my-payments/');
                const paymentsData = paymentsResult.success ? (paymentsResult.data.data || paymentsResult.data) : [];
                console.log('💰 Pagos cargados para estadísticas:', paymentsData.length);
                
                this.updateFinancialStats(requestsData, scheduleData, paymentsData);
            } else {
                console.warn('⚠️ Error en calendario de pagos:', scheduleResult);
            }

        } catch (error) {
            console.error('💥 Error crítico cargando dashboard:', error);
            this.showError('Error al cargar los datos del dashboard');
        } finally {
            this.hideLoading();
        }
    },

    // Renderizar solicitudes
    renderRequests(requests) {
        const tableBody = document.getElementById('requestsTableBody');
        const noRequestsMessage = document.getElementById('noRequestsMessage');
        const requestsTable = document.getElementById('requestsTable');

        if (!requests || requests.length === 0) {
            requestsTable.style.display = 'none';
            noRequestsMessage.style.display = 'block';
            return;
        }

        requestsTable.style.display = 'table';
        noRequestsMessage.style.display = 'none';

        tableBody.innerHTML = requests.map(request => {
            const statusBadge = this.getStatusBadge(request.status);
            const actions = this.getActionButtons(request);
            
            return `
                <tr>
                    <td>${request.application_number || request.id}</td>
                    <td>${request.product_name || 'N/A'}</td>
                    <td>${this.formatNumber(request.product_price || 0)} LLEVO</td>
                    <td>${statusBadge}</td>
                    <td>${this.formatDate(request.created_at)}</td>
                    <td>${actions}</td>
                </tr>
            `;
        }).join('');

        // Inicializar botones R4 para solicitudes aprobadas
        this.initializeR4PaymentButtons(requests);
    },

    // Actualizar estadísticas
    updateStats(requests) {
        // Solicitudes activas (enviadas, en revisión, aprobadas)
        const activeRequests = requests.filter(r => 
            ['submitted', 'under_review', 'approved', 'active'].includes(r.status)
        ).length;
        document.getElementById('activeRequests').textContent = activeRequests;

        // Para el total pagado y saldo pendiente, necesitamos más datos del backend
        // Por ahora mostraremos estadísticas básicas
        // Total pagado se calculara abajo
        
        // Mostrar número de solicitudes en borrador como "pendiente"
        const draftRequests = requests.filter(r => r.status === 'draft').length;
        document.getElementById('pendingBalance').textContent = `${draftRequests} borradores`;

        // Habilitar botón de pago si hay solicitudes activas o aprobadas
        const payableRequests = requests.filter(r => 
            ['approved', 'active'].includes(r.status)
        );
        const makePaymentBtn = document.getElementById('makePaymentBtn');
        if (makePaymentBtn) {
            makePaymentBtn.disabled = payableRequests.length === 0;
            
            // Actualizar text del botón para indicar R4 con estilo destacado
            if (payableRequests.length > 0) {
                makePaymentBtn.innerHTML = `
                    <i class="fas fa-mobile-alt"></i> Pago Móvil R4
                    <span class="r4-payment-badge" style="margin-left: 8px;">PRINCIPAL</span>
                `;
                makePaymentBtn.className = 'btn r4-payment-button';
            }
            
            // Agregar event listener si no existe
            if (!makePaymentBtn.hasAttribute('data-listener')) {
                makePaymentBtn.addEventListener('click', () => {
                    if (payableRequests.length === 1) {
                        // Si solo hay una solicitud, ir directo a pagar con R4
                        const request = payableRequests[0];
                        if (typeof window.R4PaymentButton !== 'undefined') {
                            // Iniciar pago R4 directamente
                            this.initiateQuickR4Payment(request);
                        } else {
                            window.location.href = `realizar-pago.html?request=${request.id}`;
                        }
                    } else {
                        // Si hay múltiples, ir a la página de pagos
                        window.location.href = 'realizar-pago.html';
                    }
                });
                makePaymentBtn.setAttribute('data-listener', 'true');
            }
        }
    },

    // Renderizar calendario de pagos con nuevas reglas de ventanas

    // Actualizar estadísticas financieras (Total Pagado y Saldo Pendiente)
    updateFinancialStats(requests, scheduleData, paymentsData) {
        let totalPaid = 0;
        let pendingBalance = 0;
        
        // Obtener IDs de solicitudes activas para filtrar pagos
        const activeRequestIds = requests
            .filter(req => ['approved', 'active', 'in_payment'].includes(req.status))
            .map(req => req.application_number);
        
        console.log('📋 Solicitudes activas:', activeRequestIds);
        
        // Calcular total pagado SOLO de solicitudes activas
        if (paymentsData && Array.isArray(paymentsData)) {
            console.log('💰 Procesando pagos para Total Pagado:');
            paymentsData.forEach(payment => {
                // Solo contar pagos de solicitudes activas
                if (payment.status_code === 'verified' && activeRequestIds.includes(payment.application_number)) {
                    if (payment.payment_type_code === 'initial') {
                        // El pago inicial tiene amount en LLEVO (amount_llevos puede ser null)
                        const monto = payment.amount || 0;
                        console.log('  Inicial:', {id: payment.id, app: payment.application_number, amount: payment.amount, usando: monto});
                        totalPaid += parseFloat(monto);
                    } else if (payment.payment_type_code === 'installment') {
                        const monto = payment.amount_llevos || 0;
                        console.log('  Cuota:', {id: payment.id, app: payment.application_number, amount_llevos: payment.amount_llevos, usando: monto});
                        totalPaid += parseFloat(monto);
                    }
                }
            });
            console.log('  Total calculado:', totalPaid);
        }
        
        // Calcular saldo pendiente: inicial no pagada + cuotas pendientes
        requests.forEach(req => {
            if (['approved', 'active', 'in_payment'].includes(req.status)) {
                // Sumar pago inicial si no está pagado
                if (!req.initial_payment_completed) {
                    pendingBalance += parseFloat(req.down_payment_llevos || 0);
                }
            }
        });
        
        // Sumar cuotas pendientes del calendario
        if (scheduleData && Array.isArray(scheduleData)) {
            scheduleData.forEach(cuota => {
                // El calendario solo devuelve cuotas pendientes (is_paid=False)
                const monto = parseFloat(cuota.amount_llevos) || parseFloat(cuota.amount_llevo) || parseFloat(cuota.amount) || 0;
                pendingBalance += monto;
            });
        }
        
        // Actualizar UI
        const totalPaidEl = document.getElementById('totalPaid');
        const pendingBalanceEl = document.getElementById('pendingBalance');
        
        if (totalPaidEl) {
            totalPaidEl.textContent = this.formatNumber(totalPaid) + ' LLEVO';
        }
        if (pendingBalanceEl) {
            pendingBalanceEl.textContent = this.formatNumber(pendingBalance) + ' LLEVO';
        }
        
        console.log('📊 Estadísticas actualizadas:', {totalPaid, pendingBalance, payments: paymentsData?.length || 0});
    },

    renderPaymentSchedule(schedule) {
        const container = document.getElementById('paymentSchedule');
        const noPaymentsMessage = document.getElementById('noPaymentsMessage');

        if (!schedule || schedule.length === 0) {
            container.style.display = 'none';
            noPaymentsMessage.style.display = 'block';
            return;
        }

        container.style.display = 'block';
        noPaymentsMessage.style.display = 'none';

        // Proximo pago (pendiente o en ventana)
        const nextPayment = schedule.find(p => p.status === 'pending' || p.status === 'in_window');
        if (nextPayment) {
            const amountLlevo = nextPayment.amount_llevos || nextPayment.amount_llevo || nextPayment.amount;
            document.getElementById('nextPaymentAmount').textContent =
                `${this.formatNumber(amountLlevo)} LLEVO`;
            document.getElementById('nextPaymentDate').textContent =
                nextPayment.window_status || this.formatDate(nextPayment.due_date);
        }

        // Renderizar lista completa de pagos
        container.innerHTML = schedule.map((payment, index) => {
            const statusClass = this.getPaymentStatusClass(payment);
            const statusText = this.getPaymentStatusText(payment);
            const amountLlevo = payment.amount_llevos || payment.amount_llevo || payment.amount;
            const amountVes = payment.amount_ves || 0;
            const isNextPayment = (index === 0 && (payment.status === 'pending' || payment.status === 'in_window'));

            // Determinar si mostrar alerta de penalizacion
            const showPenalty = payment.status === 'overdue' && !payment.penalty_applied;

            // Formatear fechas de ventana
            let windowInfo = '';
            if (payment.payment_window_start && payment.payment_window_end) {
                windowInfo = `Del ${this.formatDate(payment.payment_window_start)} al ${this.formatDate(payment.payment_window_end)}`;
            }

            // Solo mostrar "Paga hoy" con monto en Bs para la cuota mas inmediata
            let payTodayInfo = '';
            if (isNextPayment && amountVes > 0) {
                payTodayInfo = `<div class="mt-2 p-2 bg-success bg-opacity-10 rounded"><small class="text-success fw-bold"><i class="fas fa-bolt me-1"></i>Paga hoy: ${this.formatNumber(amountVes)} Bs</small></div>`;
            }

            return `
                <div class="card mb-2 payment-card ${statusClass}">
                    <div class="card-body p-3">
                        <div class="row align-items-center">
                            <div class="col-md-5">
                                <h6 class="mb-1 fw-bold">Cuota ${payment.payment_number}</h6>
                                ${payment.application_number ? '<small class="text-muted d-block"><i class="fas fa-file-alt me-1"></i>' + payment.application_number + '</small>' : ''}
                                <small class="text-muted d-block">
                                    <i class="fas fa-calendar-alt me-1"></i>
                                    ${windowInfo || 'Vence: ' + this.formatDate(payment.due_date)}
                                </small>
                                ${payment.window_status ? '<small class="text-info d-block"><i class="fas fa-clock me-1"></i>' + payment.window_status + '</small>' : ''}
                            </div>
                            <div class="col-md-3 text-center">
                                <h5 class="mb-0 text-primary">${this.formatNumber(amountLlevo)} LLEVO</h5>
                                ${payTodayInfo}
                            </div>
                            <div class="col-md-4 text-end">
                                <span class="badge ${this.getStatusBadgeClass(payment.status)}">${statusText}</span>
                                ${showPenalty ? '<br><small class="text-danger"><i class="fas fa-exclamation-triangle"></i> +$10 USD</small>' : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    },

    // Renderizar seccion de pagos iniciales
    renderInitialPayments(requests) {
        const section = document.getElementById('initialPaymentSection');
        const content = document.getElementById('initialPaymentContent');

        if (!section || !content) return;

        // Filtrar solicitudes que requieren pago inicial (aprobadas o en proceso de pago)
        const pendingInitial = requests.filter(r =>
            (r.status === 'approved' || r.status === 'in_payment') &&
            !r.initial_payment_completed
        );

        if (pendingInitial.length === 0) {
            section.style.display = 'none';
            return;
        }

        section.style.display = 'block';

        content.innerHTML = pendingInitial.map(request => {
            const initialAmount = request.down_payment_llevos || request.down_payment_amount || 0;
            const initialAmountVes = initialAmount * currentLlevoRate;
            const productName = request.product_name || request.product?.name || 'Producto';
            const planName = request.financing_plan_name || request.financing_plan?.name || 'Plan';

            return `
                <div class="d-flex justify-content-between align-items-center mb-2 p-2 bg-light rounded">
                    <div>
                        <strong>${productName}</strong>
                        <br><small class="text-muted">${planName} - Solicitud ${request.application_number}</small>
                    </div>
                    <div class="text-end">
                        <h5 class="mb-0 text-warning">${this.formatNumber(initialAmount)} LLEVO</h5>
                        <small class="text-success fw-bold">Paga hoy: ${this.formatNumber(initialAmountVes)} Bs</small>
                    </div>
                </div>
            `;
        }).join('');
    },

    // Clase CSS para badge de estado
    getStatusBadgeClass(status) {
        const classMap = {
            'paid': 'bg-success',
            'overdue': 'bg-danger',
            'in_window': 'bg-warning text-dark',
            'pending': 'bg-secondary'
        };
        return classMap[status] || 'bg-secondary';
    },


    // Obtener badge de estado
    getStatusBadge(status) {
        const statusMap = {
            'draft': { class: 'draft', text: 'Borrador' },
            'submitted': { class: 'submitted', text: 'Enviada' },
            'under_review': { class: 'under-review', text: 'En Revisión' },
            'documents_required': { class: 'submitted', text: 'Docs Requeridos' },
            'approved': { class: 'approved', text: 'Aprobada' },
            'rejected': { class: 'rejected', text: 'Rechazada' },
            'active': { class: 'active', text: 'Activa' },
            'completed': { class: 'completed', text: 'Completada' }
        };

        const statusInfo = statusMap[status] || { class: 'draft', text: status };
        return `<span class="status-badge status-${statusInfo.class}">${statusInfo.text}</span>`;
    },

    // Obtener botones de acción según estado
    getActionButtons(request) {
        const buttons = [];
        
        // Ver detalles siempre disponible
        buttons.push(`
            <button class="btn btn-sm btn-info" onclick="Dashboard.viewDetails(${request.id})">
                <i class="fas fa-eye"></i>
            </button>
        `);

        // Acciones según estado
        switch (request.status) {
            case 'draft':
                buttons.push(`
                    <button class="btn btn-sm btn-primary" onclick="Dashboard.completeRequest(${request.id})">
                        Completar
                    </button>
                `);
                break;
            case 'documents_required':
                buttons.push(`
                    <button class="btn btn-sm btn-warning" onclick="Dashboard.showUploadModal(${request.id})">
                        <i class="fas fa-upload"></i> Subir Docs
                    </button>
                `);
                break;
            case 'approved':
            case 'active':
                // ====================================================================
                // MODIFICACIÓN: Habilitar pagos manuales (2025-10-21)
                // Se agrega botón principal para pagos con comprobante
                // R4 queda deshabilitado temporalmente hasta completar integración
                // ====================================================================
                
                // Botón PRINCIPAL: Pagar con comprobante (métodos manuales)
                buttons.push(`
                    <button class="btn btn-sm btn-success" 
                            onclick="window.location.href='realizar-pago.html?request=${request.id}'" 
                            title="Pagar con transferencia, pago móvil, zelle u otros métodos">
                        <i class="fas fa-file-invoice-dollar"></i> Pagar
                    </button>
                `);
                
        }

        return buttons.join(' ');
    },

    // Ver detalles de solicitud
    async viewDetails(requestId) {
        try {
            const result = await API.users.authFetch(`/api/financing/requests/${requestId}/`);
            if (result.success) {
                this.showDetailsModal(result.data);
            }
        } catch (error) {
            console.error('Error al cargar detalles:', error);
            this.showError('Error al cargar los detalles de la solicitud');
        }
    },

    // Mostrar modal de detalles
    showDetailsModal(request) {
        const content = document.getElementById('detailsContent');
        
        
        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Información del Producto</h6>
                    <p><strong>N° Solicitud:</strong> ${request.application_number || request.id}</p>
                    <p><!-- <strong>Producto:</strong> ${request.product_name || 'N/A'} --></p>
                    <p><strong>Precio:</strong> ${this.formatNumber(request.product_price || 0)} LLEVO</p>
                </div>
                <div class="col-md-6">
                    <h6>Información del Financiamiento</h6>
                    <p><strong>Estado:</strong> ${request.status_display || request.status}</p>
                    <p><strong>Frecuencia de Pago:</strong> ${request.payment_frequency === 'monthly' ? 'Mensual' : (request.payment_frequency || 'N/A')}</p>
                    <p><strong>Monto de Cuota:</strong> ${this.formatNumber(request.payment_amount || 0)} LLEVO</p>
                </div>
            </div>
            
            ${request.status === 'approved' ? `
            <hr>
            <div class="row">
                <div class="col-12">
                    <h6 class="text-success"><i class="fas fa-credit-card me-2"></i>Opciones de Pago</h6>
                    
                    <!-- Pago Inicial -->
                    <div class="card mb-3">
                        <div class="card-header bg-primary text-white">
                            <h6 class="mb-0"><i class="fas fa-play me-2"></i>Pago Inicial</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <p class="mb-1"><strong>Monto:</strong> ${this.formatNumber((request.down_payment_amount || request.product_price * 0.2))} LLEVO</p>
                                    <p class="mb-1"><strong>Equivalente:</strong> ${this.formatNumber((request.down_payment_amount || request.product_price * 0.2) * currentLlevoRate)} VES</p>
                                    <small class="text-muted">Tasa actual: ${this.formatNumber(currentLlevoRate)} VES/LLEVO</small>
                                </div>
                                <div class="col-md-4 d-flex align-items-center">
                                    <button class="btn btn-success btn-sm w-100" onclick="showR4Modal(${request.id}, 'Inicial-${request.id}', ${(request.down_payment_amount || request.product_price * 0.2) * currentLlevoRate})">
                                        <i class="fas fa-mobile-alt me-1"></i> Pagar Inicial R4
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Cuotas Mensuales -->
                    <div class="card">
                        <div class="card-header bg-info text-white">
                            <h6 class="mb-0"><i class="fas fa-calendar-alt me-2"></i>Cuotas Mensuales</h6>
                        </div>
                        <div class="card-body">
                            <p><strong>Monto por cuota:</strong> ${this.formatNumber(request.payment_amount || 0)} LLEVO (${this.formatNumber((request.payment_amount || 0) * currentLlevoRate)} VES)</p>
                            <p class="text-info"><i class="fas fa-info-circle me-1"></i>Las cuotas mensuales se activan después del pago inicial</p>
                        </div>
                    </div>
                </div>
            </div>
            ` : ''}
            
            <hr>
            <div class="row">
                <div class="col-md-6">
                    <h6>Estado de la Solicitud</h6>
                    <p>${this.getStatusBadge(request.status)}</p>
                    <p><strong>Fecha de Solicitud:</strong> ${this.formatDate(request.created_at)}</p>
                </div>
                <div class="col-md-6">
                    <h6>Cliente</h6>
                    <p><strong>Nombre:</strong> ${request.customer_name || 'N/A'}</p>
                    <p><strong>Imagen del Producto:</strong></p>
                    ${request.product_image ? `<img src="${request.product_image}" alt="${request.product_name}" style="max-width: 150px; height: auto;">` : 'Sin imagen'}
                </div>
            </div>
        `;

        const modal = new bootstrap.Modal(document.getElementById('detailsModal'));
        modal.show();
    },

    // Mostrar modal de subida de documentos
    showUploadModal(requestId) {
        this.currentRequestId = requestId;
        this.selectedFiles = [];
        document.getElementById('fileList').innerHTML = '';
        document.getElementById('fileInput').value = '';
        document.getElementById('uploadBtn').disabled = true;
        
        const modal = new bootstrap.Modal(document.getElementById('uploadModal'));
        modal.show();
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
        
        this.renderFileList();
    },

    // Renderizar lista de archivos
    renderFileList() {
        const fileList = document.getElementById('fileList');
        const uploadBtn = document.getElementById('uploadBtn');
        
        if (this.selectedFiles.length === 0) {
            fileList.innerHTML = '';
            uploadBtn.disabled = true;
            return;
        }
        
        uploadBtn.disabled = false;
        
        fileList.innerHTML = this.selectedFiles.map((file, index) => `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span>
                    <i class="fas fa-file"></i> ${file.name}
                    <small class="text-muted">(${this.formatFileSize(file.size)})</small>
                </span>
                <button class="btn btn-sm btn-danger" onclick="Dashboard.removeFile(${index})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    },

    // Remover archivo de la lista
    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.renderFileList();
    },

    // Subir documentos
    async uploadDocuments() {
        if (!this.currentRequestId || this.selectedFiles.length === 0) return;
        
        const uploadBtn = document.getElementById('uploadBtn');
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Subiendo...';
        
        try {
            const formData = new FormData();
            this.selectedFiles.forEach(file => {
                formData.append('documents', file);
            });
            
            const result = await API.users.authFetch(
                `/api/financing/requests/${this.currentRequestId}/upload_documents/`,
                {
                    method: 'POST',
                    body: formData
                }
            );
            
            if (result.success) {
                this.showSuccess('Documentos subidos exitosamente');
                bootstrap.Modal.getInstance(document.getElementById('uploadModal')).hide();
                await this.loadDashboardData(); // Recargar datos
            } else {
                this.showError(result.message || 'Error al subir documentos');
            }
        } catch (error) {
            console.error('Error al subir documentos:', error);
            this.showError('Error al subir los documentos');
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = 'Subir Documentos';
        }
    },

    // Utilidades
    formatNumber(num) {
        return new Intl.NumberFormat('es-VE').format(num);
    },

    formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateString).toLocaleDateString('es-VE', options);
    },

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    },

    getPaymentStatusClass(payment) {
        const statusMap = {
            'paid': 'payment-paid',
            'overdue': 'payment-overdue',
            'in_window': 'payment-in-window',
            'pending': 'payment-upcoming'
        };
        return statusMap[payment.status] || 'payment-upcoming';
    },

    getPaymentStatusText(payment) {
        // Usar status_display del backend si existe
        if (payment.status_display) {
            return payment.status_display;
        }
        const statusMap = {
            'paid': 'Pagado',
            'overdue': 'Vencido',
            'in_window': 'En ventana de pago',
            'pending': 'Pendiente'
        };
        const text = statusMap[payment.status] || 'Pendiente';
        if (payment.status === 'overdue' && payment.days_overdue > 0) {
            return `${text} (${payment.days_overdue} dias)`;
        }
        return text;
    },

    // Mostrar/ocultar loading
    showLoading() {
        // Implementar spinner de carga
    },

    hideLoading() {
        // Ocultar spinner
    },

    // Mostrar mensajes
    showError(message) {
        // Implementar notificación de error
        console.error(message);
        alert(message); // Temporal
    },

    showSuccess(message) {
        // Implementar notificación de éxito
        console.log(message);
        alert(message); // Temporal
    },

    // Iniciar pago R4 rápido desde el botón de acciones rápidas
    initiateQuickR4Payment(request) {
        try {
            if (typeof window.R4PaymentButton === 'undefined') {
                console.warn('⚠️ R4PaymentButton no disponible, redirigiendo...');
                window.location.href = `realizar-pago.html?request=${request.id}`;
                return;
            }

            // Crear modal temporal para el pago R4
            const modalHtml = `
                <div class="modal fade" id="quickR4PaymentModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white;">
                                <h5 class="modal-title">
                                    <i class="fas fa-mobile-alt"></i> 
                                    Pago Móvil R4
                                    <span class="r4-payment-badge" style="background: rgba(255,255,255,0.3); color: white;">PRINCIPAL</span>
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="text-center mb-3">
                                    <h6>Solicitud: ${request.application_number || request.id}</h6>
                                    <p class="text-muted">${request.product_name}</p>
                                    <h4 class="text-success">${this.formatNumber(request.payment_amount || 0)} LLEVO</h4>
                                    <small class="text-muted">Pago R4: ${this.formatNumber(request.payment_amount_ves || 0)} VES</small>
                                </div>
                                <div id="quickR4ButtonContainer" class="text-center">
                                    <!-- Botón R4 se generará aquí -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Agregar modal al DOM si no existe
            let existingModal = document.getElementById('quickR4PaymentModal');
            if (existingModal) {
                existingModal.remove();
            }
            document.body.insertAdjacentHTML('beforeend', modalHtml);

            // Mostrar modal
            const modal = new bootstrap.Modal(document.getElementById('quickR4PaymentModal'));
            modal.show();

            // Configurar botón R4 en el modal con estilo destacado
            const buttonConfig = {
                applicationId: request.id,
                amount: request.payment_amount_ves || request.payment_amount || request.product_price,
                currency: 'VES',
                size: 'large',
                variant: 'success',
                cssClass: 'r4-payment-button', // Estilo destacado
                showBadge: true,
                onSuccess: (paymentData) => {
                    console.log('✅ Pago R4 rápido exitoso:', paymentData);
                    modal.hide();
                    this.showSuccess('¡Pago procesado exitosamente!');
                    this.loadDashboardData(); // Recargar datos
                },
                onError: (error) => {
                    console.error('❌ Error en pago R4 rápido:', error);
                    this.showError('Error procesando el pago: ' + error.message);
                }
            };

            // Crear botón R4 en el modal
            const container = document.getElementById('quickR4ButtonContainer');
            window.R4PaymentButton.createPaymentButton(container, buttonConfig);

        } catch (error) {
            console.error('Error iniciando pago R4 rápido:', error);
            window.location.href = `realizar-pago.html?request=${request.id}`;
        }
    },

    // Inicializar botones R4 para solicitudes aprobadas
    initializeR4PaymentButtons(requests) {
        // Verificar si R4PaymentButton está disponible
        if (typeof window.R4PaymentButton === 'undefined') {
            console.warn('⚠️ R4PaymentButton no está disponible');
            return;
        }

        // Filtrar solicitudes aprobadas/activas
        const approvedRequests = requests.filter(request => 
            ['approved', 'active'].includes(request.status)
        );

        // Crear botón R4 para cada solicitud aprobada
        approvedRequests.forEach(request => {
            const containerId = `r4-payment-container-${request.id}`;
            const container = document.getElementById(containerId);
            
            if (container) {
                try {
                    // Configuración del botón R4 con estilos destacados
                    const buttonConfig = {
                        applicationId: request.id,
                        amount: request.payment_amount_ves || request.payment_amount || request.product_price,
                        currency: 'VES', // R4 opera en bolívares
                        size: 'small',
                        variant: 'success',
                        cssClass: 'r4-payment-button', // Clase CSS especial
                        showBadge: true, // Mostrar badge "R4"
                        onSuccess: (paymentData) => {
                            console.log('✅ Pago R4 exitoso:', paymentData);
                            this.showSuccess('¡Pago procesado exitosamente!');
                            this.loadDashboardData(); // Recargar datos
                        },
                        onError: (error) => {
                            console.error('❌ Error en pago R4:', error);
                            this.showError('Error procesando el pago: ' + error.message);
                        }
                    };

                    // Crear botón R4 con estilo destacado
                    window.R4PaymentButton.createPaymentButton(container, buttonConfig);
                    
                    // Agregar badge R4 al contenedor
                    const r4Badge = document.createElement('span');
                    r4Badge.className = 'r4-payment-badge';
                    r4Badge.textContent = 'R4';
                    r4Badge.title = 'Pago Móvil R4 - Método Principal';
                    container.appendChild(r4Badge);
                    
                } catch (error) {
                    console.error('Error creando botón R4:', error);
                    // Fallback al botón tradicional con estilo R4
                    container.innerHTML = `
                        <button class="btn btn-sm r4-payment-button" onclick="window.location.href='/realizar-pago.html?request=${request.id}'">
                            <i class="fas fa-mobile-alt"></i> Pago Móvil
                        </button>
                        <span class="r4-payment-badge">R4</span>
                    `;
                }
            }
        });
    },

    // Funciones pendientes de implementar
    async completeRequest(requestId) {
        // TODO: Implementar completar solicitud borrador
        window.location.href = `/solicitud-financiamiento.html?id=${requestId}`;
    },


    // ========== SISTEMA DE POLLING PARA PAGOS PENDIENTES ==========
    
    // Iniciar polling de pagos pendientes
    startPaymentPolling() {
        // Si ya hay un polling activo, no iniciar otro
        if (this.pollingInterval) {
            console.log("⏱️ Polling ya activo");
            return;
        }
        
        console.log("🔄 Iniciando polling de pagos pendientes cada " + (this.POLLING_INTERVAL_MS/1000) + "s");
        
        // Ejecutar inmediatamente la primera vez
        this.checkPendingPayments();
        
        // Configurar intervalo
        this.pollingInterval = setInterval(() => {
            this.checkPendingPayments();
        }, this.POLLING_INTERVAL_MS);
    },
    
    // Detener polling
    stopPaymentPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
            console.log("⏹️ Polling detenido");
        }
    },
    
    
    // Verificar si hay un pago R4 pendiente que fue procesado
    async checkPendingR4Payment() {
        const pendingR4 = localStorage.getItem('pending_r4_payment');
        if (!pendingR4) return;
        
        try {
            const pending = JSON.parse(pendingR4);
            const ageMinutes = (Date.now() - pending.timestamp) / 1000 / 60;
            
            // Si el pago pendiente tiene mas de 30 minutos, ignorarlo
            if (ageMinutes > 30) {
                localStorage.removeItem('pending_r4_payment');
                return;
            }
            
            console.log('Verificando pago R4 pendiente:', pending);
            
            // Buscar pagos recientes de esta solicitud
            const response = await API.users.authFetch('/api/financing/my-payments/?application=' + pending.applicationId);
            if (!response.success) return;
            
            const payments = response.data || [];
            
            // Buscar un pago verificado reciente con el mismo monto
            const verifiedPayment = payments.find(p => {
                const isVerified = p.status_code === 'verified';
                const isR4 = p.payment_method === 'r4_automatic';
                const sameAmount = Math.abs(parseFloat(p.amount_llevos || 0) - parseFloat(pending.amount)) < 0.1;
                return isVerified && isR4 && sameAmount;
            });
            
            if (verifiedPayment) {
                console.log('Pago R4 verificado encontrado:', verifiedPayment);
                this.showPaymentConfirmedNotification(verifiedPayment);
                localStorage.removeItem('pending_r4_payment');
                // Recargar datos del dashboard
                await this.loadDashboardData();
            } else {
                console.log('Pago R4 aun no verificado, continuando polling...');
            }
        } catch (e) {
            console.error('Error verificando pago R4:', e);
        }
    },

    // Verificar estado de pagos pendientes
    async checkPendingPayments() {
        try {
            const response = await API.users.authFetch("/api/financing/my-payments/?status=pending");
            
            if (!response.success) {
                console.warn("⚠️ Error consultando pagos pendientes");
                return;
            }
            
            const currentPendingPayments = response.data || [];
            console.log(`🔍 Pagos pendientes: ${currentPendingPayments.length}`);
            
            // Si no hay pagos pendientes, detener polling
            if (currentPendingPayments.length === 0 && this.pendingPayments.length === 0) {
                console.log("✅ No hay pagos pendientes - deteniendo polling");
                this.stopPaymentPolling();
                return;
            }
            
            // Verificar si algún pago que estaba pendiente ya fue verificado
            if (this.pendingPayments.length > 0) {
                const currentIds = currentPendingPayments.map(p => p.id);
                
                for (const prevPayment of this.pendingPayments) {
                    // Si el pago ya no está en pendientes, fue verificado o rechazado
                    if (!currentIds.includes(prevPayment.id)) {
                        // Consultar el estado actual del pago
                        const statusResponse = await API.users.authFetch(`/api/financing/my-payments/`);
                        if (statusResponse.success) {
                            const allPayments = statusResponse.data || [];
                            const updatedPayment = allPayments.find(p => p.id === prevPayment.id);
                            
                            if (updatedPayment) {
                                if (updatedPayment.status_code === "verified") {
                                    console.log(`✅ Pago ${prevPayment.id} VERIFICADO!`);
                                    this.showPaymentConfirmedNotification(updatedPayment);
                                    // Recargar dashboard para mostrar cambios
                                    await this.loadDashboardData();
                                } else if (updatedPayment.status_code === "rejected") {
                                    console.log(`❌ Pago ${prevPayment.id} RECHAZADO`);
                                    this.showPaymentRejectedNotification(updatedPayment);
                                }
                            }
                        }
                    }
                }
            }
            
            // Actualizar lista de pagos pendientes
            this.pendingPayments = currentPendingPayments;
            
            // Si no hay más pagos pendientes, detener polling
            if (currentPendingPayments.length === 0) {
                console.log("✅ Todos los pagos procesados - deteniendo polling");
                this.stopPaymentPolling();
            }
            
        } catch (error) {
            console.error("❌ Error en polling de pagos:", error);
        }
    },
    
    // Mostrar notificación de pago confirmado
    showPaymentConfirmedNotification(payment) {
        // Crear toast de éxito
        const toastHtml = `
            <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 9999;">
                <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header bg-success text-white">
                        <i class="fas fa-check-circle me-2"></i>
                        <strong class="me-auto">¡Pago Confirmado!</strong>
                        <small>Ahora</small>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body">
                        <p class="mb-1"><strong>Solicitud:</strong> ${payment.application_number}</p>
                        <p class="mb-1"><strong>Monto:</strong> ${payment.amount} ${payment.currency}</p>
                        <p class="mb-0 text-success"><i class="fas fa-check me-1"></i>Tu pago ha sido verificado exitosamente.</p>
                    </div>
                </div>
            </div>
        `;
        
        // Remover toast anterior si existe
        const existingToast = document.querySelector(".toast-container");
        if (existingToast) existingToast.remove();
        
        // Agregar nuevo toast
        document.body.insertAdjacentHTML("beforeend", toastHtml);
        
        // Reproducir sonido de éxito (opcional)
        this.playNotificationSound("success");
        
        // Auto-cerrar después de 10 segundos
        setTimeout(() => {
            const toast = document.querySelector(".toast-container");
            if (toast) toast.remove();
        }, 10000);
    },
    
    // Mostrar notificación de pago rechazado
    showPaymentRejectedNotification(payment) {
        const toastHtml = `
            <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 9999;">
                <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header bg-danger text-white">
                        <i class="fas fa-times-circle me-2"></i>
                        <strong class="me-auto">Pago No Verificado</strong>
                        <small>Ahora</small>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body">
                        <p class="mb-1"><strong>Solicitud:</strong> ${payment.application_number}</p>
                        <p class="mb-0 text-danger"><i class="fas fa-exclamation-triangle me-1"></i>Por favor contacta a soporte.</p>
                    </div>
                </div>
            </div>
        `;
        
        const existingToast = document.querySelector(".toast-container");
        if (existingToast) existingToast.remove();
        
        document.body.insertAdjacentHTML("beforeend", toastHtml);
        this.playNotificationSound("error");
        
        setTimeout(() => {
            const toast = document.querySelector(".toast-container");
            if (toast) toast.remove();
        }, 15000);
    },
    
    // Reproducir sonido de notificación
    playNotificationSound(type) {
        try {
            // Usar Web Audio API para un sonido simple
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            if (type === "success") {
                oscillator.frequency.value = 800;
                oscillator.type = "sine";
            } else {
                oscillator.frequency.value = 400;
                oscillator.type = "square";
            }
            
            gainNode.gain.value = 0.1;
            oscillator.start();
            
            setTimeout(() => {
                oscillator.stop();
            }, 200);
        } catch (e) {
            // Silenciar errores de audio
        }
    },
    async makePayment(requestId) {
        // TODO: Implementar proceso de pago
        window.location.href = `/realizar-pago.html?request=${requestId}`;
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    Dashboard.init();
});

// Exportar para uso global
window.Dashboard = Dashboard; 
    // === PUNTO DE INSERCION PARA FUNCIONES DE PAGO ===
