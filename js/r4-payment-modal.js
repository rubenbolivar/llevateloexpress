// Sistema de Modal de Pago R4 Real
class R4PaymentModal {
    constructor() {
        this.config = window.R4Config || {};
    }

    // Crear y mostrar modal de pago R4
    showPaymentModal(paymentData) {
        const { applicationId, amount, productName, customerName } = paymentData;
        
        // Crear HTML del modal
        const modalHtml = this.createModalHTML(paymentData);
        
        // Remover modal existente si existe
        const existingModal = document.getElementById('r4PaymentModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Agregar modal al DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Mostrar modal con Bootstrap
        const modal = new bootstrap.Modal(document.getElementById('r4PaymentModal'));
        modal.show();
        
        // Configurar eventos
        this.setupModalEvents(modal, paymentData);
        
        return modal;
    }

    createModalHTML(paymentData) {
        const { applicationId, amount, productName } = paymentData;
        const phoneFormatted = this.config.commercePhone || '0422 1002379';
        
        return `
            <div class="modal fade" id="r4PaymentModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white;">
                            <h5 class="modal-title">
                                <i class="fas fa-mobile-alt me-2"></i>
                                ${this.config.ui?.modalTitle || '💰 Pago Móvil R4'}
                                <span class="badge bg-warning text-dark ms-2">PRINCIPAL</span>
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="card bg-light h-100">
                                        <div class="card-header bg-success text-white">
                                            <h6 class="mb-0"><i class="fas fa-info-circle me-1"></i> Datos del Pago</h6>
                                        </div>
                                        <div class="card-body">
                                            <p><strong>Solicitud:</strong> #${applicationId}</p>
                                            <p><strong>Producto:</strong> ${productName || 'Financiamiento'}</p>
                                            <p><strong>Monto a Pagar:</strong> <span class="h5 text-success">$${this.formatAmount(amount)}</span></p>
                                            <p><strong>Concepto:</strong> LlévateloExpress-${applicationId}</p>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="card bg-success text-white h-100">
                                        <div class="card-header">
                                            <h6 class="mb-0"><i class="fas fa-university me-1"></i> Datos del Beneficiario</h6>
                                        </div>
                                        <div class="card-body">
                                            <p><strong>Teléfono:</strong> <span class="h5">${phoneFormatted}</span></p>
                                            <p><strong>Banco:</strong> ${this.config.commerceBank || 'Mi Banco'}</p>
                                            <p><strong>Beneficiario:</strong> ${this.config.commerceName || 'LlévateloExpress'}</p>
                                            <p><strong>RIF:</strong> J-506654547</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="alert alert-info mt-3">
                                <h6><i class="fas fa-mobile-alt me-1"></i> Instrucciones de Pago:</h6>
                                <ol class="mb-0">
                                    <li>Abre tu app bancaria</li>
                                    <li>Selecciona "Pago Móvil"</li>
                                    <li>Ingresa el teléfono: <strong>${phoneFormatted}</strong></li>
                                    <li>Monto exacto: <strong>$${this.formatAmount(amount)}</strong></li>
                                    <li>Concepto: <strong>LlévateloExpress-${applicationId}</strong></li>
                                    <li>Confirma el pago</li>
                                </ol>
                            </div>
                            
                            <div class="alert alert-success">
                                <h6><i class="fas fa-magic me-1"></i> Procesamiento Automático:</h6>
                                <p class="mb-0">Tu pago será <strong>detectado y procesado automáticamente</strong> por nuestro sistema R4. 
                                Recibirás confirmación inmediata una vez completado.</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-1"></i> Cerrar
                            </button>
                            <button type="button" class="btn btn-success" id="markAsPaidBtn">
                                <i class="fas fa-check me-1"></i> Ya Realicé el Pago
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    setupModalEvents(modal, paymentData) {
        const markAsPaidBtn = document.getElementById('markAsPaidBtn');
        if (markAsPaidBtn) {
            markAsPaidBtn.addEventListener('click', () => {
                this.handlePaymentConfirmation(modal, paymentData);
            });
        }
    }

    handlePaymentConfirmation(modal, paymentData) {
        // Mostrar mensaje de confirmación
        const alertHtml = `
            <div class="alert alert-warning alert-dismissible fade show" role="alert">
                <h6><i class="fas fa-clock me-1"></i> Pago en Proceso</h6>
                <p class="mb-0">Tu pago está siendo verificado por el sistema R4. 
                Recibirás confirmación automática en unos minutos.</p>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Insertar alerta en dashboard
        const dashboardContainer = document.querySelector('.container');
        if (dashboardContainer) {
            dashboardContainer.insertAdjacentHTML('afterbegin', alertHtml);
        }
        
        // Cerrar modal
        modal.hide();
        
        // Opcional: recargar dashboard después de un tiempo
        setTimeout(() => {
            if (window.Dashboard && typeof window.Dashboard.loadDashboardData === 'function') {
                window.Dashboard.loadDashboardData();
            }
        }, 5000);
    }

    formatAmount(amount) {
        return parseFloat(amount).toLocaleString('es-VE', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
}

// Crear instancia global
window.R4PaymentModal = new R4PaymentModal();

// Crear función compatible con código existente
window.R4PaymentButton = {
    createPaymentButton: function(container, config) {
        if (!container) return;
        
        const buttonHtml = `
            <button class="btn r4-payment-button" data-application-id="${config.applicationId}">
                <i class="fas fa-mobile-alt me-1"></i> Pago Móvil R4
            </button>
        `;
        
        container.innerHTML = buttonHtml;
        
        const button = container.querySelector('.r4-payment-button');
        if (button) {
            button.addEventListener('click', () => {
                window.R4PaymentModal.showPaymentModal({
                    applicationId: config.applicationId,
                    amount: config.amount,
                    productName: config.productName || 'Financiamiento'
                });
            });
        }
    }
};