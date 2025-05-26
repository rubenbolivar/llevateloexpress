import { Auth } from './auth.js';

// Dashboard Module
const Dashboard = {
    currentRequestId: null,
    selectedFiles: [],

    // Inicialización
    async init() {
        // Verificar autenticación
        if (!Auth.isAuthenticated()) {
            window.location.href = '/login.html?redirect=dashboard';
            return;
        }

        // Configurar eventos
        this.setupEventListeners();
        
        // Cargar datos del dashboard
        await this.loadDashboardData();
        
        // Actualizar UI de autenticación
        Auth.updateAuthUI();
        
        // Configurar mensaje de bienvenida
        this.setWelcomeMessage();
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
            // Mostrar loading
            this.showLoading();

            // Cargar solicitudes del usuario
            const requestsResult = await Auth.fetch('/api/financing/my-requests/');
            if (requestsResult.success) {
                this.renderRequests(requestsResult.data);
                this.updateStats(requestsResult.data);
            }

            // Cargar calendario de pagos
            const scheduleResult = await Auth.fetch('/api/financing/payment-schedule/');
            if (scheduleResult.success) {
                this.renderPaymentSchedule(scheduleResult.data);
            }

        } catch (error) {
            console.error('Error cargando dashboard:', error);
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
                    <td>${request.id}</td>
                    <td>${request.product?.name || 'N/A'}</td>
                    <td>$${this.formatNumber(request.total_amount)}</td>
                    <td>${statusBadge}</td>
                    <td>${this.formatDate(request.created_at)}</td>
                    <td>${actions}</td>
                </tr>
            `;
        }).join('');
    },

    // Actualizar estadísticas
    updateStats(requests) {
        // Solicitudes activas
        const activeRequests = requests.filter(r => 
            ['submitted', 'under_review', 'approved', 'active'].includes(r.status)
        ).length;
        document.getElementById('activeRequests').textContent = activeRequests;

        // Total pagado
        const totalPaid = requests.reduce((sum, r) => 
            sum + parseFloat(r.total_paid || 0), 0
        );
        document.getElementById('totalPaid').textContent = `$${this.formatNumber(totalPaid)}`;

        // Saldo pendiente
        const pendingBalance = requests
            .filter(r => r.status === 'active')
            .reduce((sum, r) => sum + (parseFloat(r.total_amount) - parseFloat(r.total_paid || 0)), 0);
        document.getElementById('pendingBalance').textContent = `$${this.formatNumber(pendingBalance)}`;

        // Habilitar botón de pago si hay saldo pendiente
        if (pendingBalance > 0) {
            document.getElementById('makePaymentBtn').disabled = false;
        }
    },

    // Renderizar calendario de pagos
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

        // Próximo pago
        const nextPayment = schedule.find(p => p.status === 'pending');
        if (nextPayment) {
            document.getElementById('nextPaymentAmount').textContent = 
                `$${this.formatNumber(nextPayment.amount)}`;
            document.getElementById('nextPaymentDate').textContent = 
                this.formatDate(nextPayment.due_date);
        }

        // Renderizar lista de pagos
        container.innerHTML = schedule.slice(0, 5).map(payment => {
            const statusClass = this.getPaymentStatusClass(payment);
            const statusText = this.getPaymentStatusText(payment);
            
            return `
                <div class="card mb-2 ${statusClass}">
                    <div class="card-body p-3">
                        <div class="row align-items-center">
                            <div class="col">
                                <h6 class="mb-0">Cuota ${payment.installment_number}</h6>
                                <small class="text-muted">Vence: ${this.formatDate(payment.due_date)}</small>
                            </div>
                            <div class="col-auto">
                                <h6 class="mb-0">$${this.formatNumber(payment.amount)}</h6>
                                <small>${statusText}</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
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
            case 'active':
                buttons.push(`
                    <button class="btn btn-sm btn-success" onclick="Dashboard.makePayment(${request.id})">
                        <i class="fas fa-credit-card"></i> Pagar
                    </button>
                `);
                break;
        }

        return buttons.join(' ');
    },

    // Ver detalles de solicitud
    async viewDetails(requestId) {
        try {
            const result = await Auth.fetch(`/api/financing/requests/${requestId}/`);
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
                    <p><strong>Producto:</strong> ${request.product?.name || 'N/A'}</p>
                    <p><strong>Precio:</strong> $${this.formatNumber(request.product?.price || 0)}</p>
                </div>
                <div class="col-md-6">
                    <h6>Información del Financiamiento</h6>
                    <p><strong>Plan:</strong> ${request.financing_plan?.name || 'N/A'}</p>
                    <p><strong>Monto Total:</strong> $${this.formatNumber(request.total_amount)}</p>
                    <p><strong>Cuotas:</strong> ${request.term_months} meses</p>
                    <p><strong>Cuota Mensual:</strong> $${this.formatNumber(request.monthly_payment)}</p>
                </div>
            </div>
            <hr>
            <div class="row">
                <div class="col-md-6">
                    <h6>Estado de la Solicitud</h6>
                    <p>${this.getStatusBadge(request.status)}</p>
                    <p><strong>Fecha de Solicitud:</strong> ${this.formatDate(request.created_at)}</p>
                </div>
                <div class="col-md-6">
                    <h6>Pagos</h6>
                    <p><strong>Total Pagado:</strong> $${this.formatNumber(request.total_paid || 0)}</p>
                    <p><strong>Saldo Pendiente:</strong> $${this.formatNumber(request.total_amount - (request.total_paid || 0))}</p>
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
            
            const result = await Auth.fetch(
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
        if (payment.status === 'paid') return 'payment-paid';
        if (payment.days_overdue > 0) return 'payment-overdue';
        return 'payment-upcoming';
    },

    getPaymentStatusText(payment) {
        if (payment.status === 'paid') return 'Pagado';
        if (payment.days_overdue > 0) return `Vencido (${payment.days_overdue} días)`;
        return 'Pendiente';
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

    // Funciones pendientes de implementar
    async completeRequest(requestId) {
        // TODO: Implementar completar solicitud borrador
        window.location.href = `/solicitud-financiamiento.html?id=${requestId}`;
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