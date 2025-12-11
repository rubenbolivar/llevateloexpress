// Sistema de Modal de Pago R4 - Versión Actualizada LLEVO
// Actualizado: 3 Dic 2025 - Sistema dual LLEVO/Bolívares
class R4PaymentModal {
    constructor() {
        this.config = window.R4Config || {};
        this.llevoRate = null;
        this.amountInLlevos = null;
        this.amountInBs = null;
    }

    // Cargar tasa LLEVO actual
    async loadLlevoRate() {
        try {
            const response = await fetch('/api/financing/llevo/current-rate/');
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.data && data.data.llevo_value) {
                    this.llevoRate = parseFloat(data.data.llevo_value);
                    console.log(`✅ Tasa LLEVO cargada: 1 LLEVO = Bs. ${this.formatNumber(this.llevoRate)}`);
                    return this.llevoRate;
                }
            }
            // Fallback: usar tasa por defecto
            this.llevoRate = 7080.00;
            console.warn(`⚠️ Usando tasa LLEVO por defecto: ${this.llevoRate}`);
            return this.llevoRate;
        } catch (error) {
            console.error('❌ Error cargando tasa LLEVO:', error);
            this.llevoRate = 7080.00;
            return this.llevoRate;
        }
    }

    // Crear y mostrar modal de pago R4
    async showPaymentModal(paymentData) {
        const { applicationId, amount, productName, customerName } = paymentData;

        console.log('📦 Datos recibidos en modal R4:', paymentData);

        // Cargar tasa LLEVO actual
        await this.loadLlevoRate();

        // El amount viene en LLEVOS desde el sistema
        this.amountInLlevos = parseFloat(amount);

        // Calcular equivalente en Bs
        this.amountInBs = this.amountInLlevos * this.llevoRate;

        console.log(`💰 Conversión: ${this.amountInLlevos} LLEVOS × ${this.llevoRate} = Bs. ${this.formatNumber(this.amountInBs)}`);

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
        const modal = new bootstrap.Modal(document.getElementById('r4PaymentModal'), {
            backdrop: 'static',  // No cerrar al hacer clic fuera
            keyboard: true       // Permitir cerrar con ESC
        });
        modal.show();

        // Configurar eventos
        this.setupModalEvents(modal, paymentData);

        return modal;
    }

    createModalHTML(paymentData) {
        const { applicationId, applicationNumber, productName } = paymentData;
        const phoneFormatted = this.config.commercePhone || '0422-1002379';

        return `
            <div class="modal fade" id="r4PaymentModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-lg modal-dialog-centered">
                    <div class="modal-content">
                        <!-- Header -->
                        <div class="modal-header" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white;">
                            <h5 class="modal-title">
                                <i class="fas fa-mobile-alt me-2"></i>
                                Pago Móvil R4 Automático
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Cerrar"></button>
                        </div>

                        <!-- Body -->
                        <div class="modal-body">
                            <!-- Información de la Solicitud -->
                            <div class="alert alert-primary border-primary">
                                <div class="row align-items-center">
                                    <div class="col-md-8">
                                        <h6 class="mb-1">
                                            <i class="fas fa-file-alt me-2"></i>
                                            Solicitud #${applicationNumber || applicationId}
                                        </h6>
                                        <p class="mb-0 text-muted">${productName || 'Financiamiento de vehículo'}</p>
                                    </div>
                                    <div class="col-md-4 text-end">
                                        <span class="badge bg-success" style="font-size: 0.9rem; padding: 8px 12px;">
                                            <i class="fas fa-check-circle me-1"></i> Aprobada
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <!-- Monto a Pagar (DESTACADO) -->
                            <div class="card mb-3" style="border: 2px solid #28a745;">
                                <div class="card-body text-center py-4">
                                    <h6 class="text-muted mb-2">
                                        <i class="fas fa-coins me-1"></i> Monto a Pagar
                                    </h6>
                                    <div class="display-4 text-primary fw-bold mb-2">
                                        ${this.formatNumber(this.amountInLlevos)} LLEVO
                                    </div>
                                    <div class="h5 text-success mb-0">
                                        = Bs. ${this.formatNumber(this.amountInBs)}
                                    </div>
                                    <small class="text-muted d-block mt-2">
                                        <i class="fas fa-info-circle me-1"></i>
                                        Tasa: 1 LLEVO = Bs. ${this.formatNumber(this.llevoRate)}
                                    </small>
                                </div>
                            </div>

                            <!-- Instrucciones de Pago -->
                            <div class="card bg-light mb-3">
                                <div class="card-header bg-success text-white">
                                    <h6 class="mb-0">
                                        <i class="fas fa-mobile-alt me-2"></i>
                                        Instrucciones de Pago Móvil
                                    </h6>
                                </div>
                                <div class="card-body">
                                    <ol class="mb-0 ps-3">
                                        <li class="mb-2">Abre tu app bancaria</li>
                                        <li class="mb-2">Selecciona <strong>"Pago Móvil"</strong></li>
                                        <li class="mb-2">Ingresa el teléfono del beneficiario:
                                            <div class="alert alert-warning py-2 px-3 mt-1 mb-0">
                                                <strong style="font-size: 1.1rem;">${phoneFormatted}</strong>
                                            </div>
                                        </li>
                                        <li class="mb-2">Ingresa el monto EXACTO en Bolívares:
                                            <div class="alert alert-danger py-2 px-3 mt-1 mb-0">
                                                <strong style="font-size: 1.2rem;">Bs. ${this.formatNumber(this.amountInBs)}</strong>
                                            </div>
                                        </li>
                                        <li class="mb-2">Concepto: <code>LlévateloExpress-${applicationNumber || applicationId}</code></li>
                                        <li class="mb-0">Confirma el pago en tu banco</li>
                                    </ol>
                                </div>
                            </div>

                            <!-- Datos del Beneficiario -->
                            <div class="card mb-3">
                                <div class="card-header bg-info text-white">
                                    <h6 class="mb-0">
                                        <i class="fas fa-university me-2"></i>
                                        Datos del Beneficiario
                                    </h6>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <p class="mb-2"><strong>Beneficiario:</strong><br>${this.config.commerceName || 'LlévateloExpress C.A.'}</p>
                                            <p class="mb-2"><strong>Teléfono:</strong><br><span class="text-primary fs-5">${phoneFormatted}</span></p>
                                        </div>
                                        <div class="col-md-6">
                                            <p class="mb-2"><strong>Banco:</strong><br>${this.config.commerceBank || 'Mi Banco'}</p>
                                            <p class="mb-0"><strong>RIF:</strong><br>J-506654547</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Procesamiento Automático -->
                            <div class="alert alert-success mb-0">
                                <h6>
                                    <i class="fas fa-bolt me-2"></i>
                                    Procesamiento Automático
                                </h6>
                                <p class="mb-0">
                                    Tu pago será <strong>detectado y procesado automáticamente</strong>
                                    por nuestro sistema R4 Conecta. No necesitas subir comprobante.
                                    <br><br>
                                    <i class="fas fa-check-circle text-success me-1"></i>
                                    Recibirás confirmación inmediata una vez que el banco procese tu pago.
                                </p>
                            </div>
                        </div>

                        <!-- Footer -->
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-1"></i> Cerrar
                            </button>
                            <button type="button" class="btn btn-primary" id="r4ConfirmPaymentBtn">
                                <i class="fas fa-check me-1"></i> Ya Realicé el Pago
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    setupModalEvents(modal, paymentData) {
        // Botón de confirmación
        const confirmBtn = document.getElementById('r4ConfirmPaymentBtn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                this.handlePaymentConfirmation(modal, paymentData);
            });
        }

        // Event listener cuando el modal se cierra
        const modalElement = document.getElementById('r4PaymentModal');
        modalElement.addEventListener('hidden.bs.modal', () => {
            console.log('ℹ️ Modal R4 cerrado');
            modalElement.remove();  // Limpiar del DOM
        });
    }

    handlePaymentConfirmation(modal, paymentData) {
        console.log('✅ Usuario confirmó pago realizado');

        // Mostrar mensaje de confirmación
        const confirmMessage = `
            <div class="alert alert-success">
                <h5 class="alert-heading">
                    <i class="fas fa-check-circle me-2"></i>
                    ¡Pago en Proceso!
                </h5>
                <p class="mb-0">
                    Tu pago está siendo verificado automáticamente por nuestro sistema.
                    <br><br>
                    <strong>Te notificaremos cuando sea confirmado.</strong>
                    <br><br>
                    Puedes revisar el estado en tu dashboard.
                </p>
            </div>
        `;

        // Reemplazar contenido del modal
        const modalBody = document.querySelector('#r4PaymentModal .modal-body');
        modalBody.innerHTML = confirmMessage;

        // Cambiar footer
        const modalFooter = document.querySelector('#r4PaymentModal .modal-footer');
        modalFooter.innerHTML = `
            <button type="button" class="btn btn-primary" onclick="window.location.href='dashboard.html'">
                <i class="fas fa-tachometer-alt me-1"></i> Ir al Dashboard
            </button>
        `;

        // Auto-cerrar después de 3 segundos y redirigir
        setTimeout(() => {
            modal.hide();
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 500);
        }, 3000);
    }

    // Formatear números con separadores de miles
    formatNumber(number) {
        return new Intl.NumberFormat('es-VE', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(number);
    }
}

// Exportar clase globalmente
window.R4PaymentModal = R4PaymentModal;
console.log('✅ R4PaymentModal cargado correctamente (versión LLEVO actualizada)');
