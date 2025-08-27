/**
 * R4 Payment Button Component
 * Botón de pago móvil R4 integrado al dashboard existente
 */

const R4PaymentButton = {
    
    // Crear botón de pago R4 para una solicitud específica
    createPaymentButton(application) {
        const buttonContainer = document.createElement("div");
        buttonContainer.className = "r4-payment-container mt-3";
        
        buttonContainer.innerHTML = `
            <div class="card border-success">
                <div class="card-header bg-success text-white">
                    <h6 class="mb-0">
                        <i class="fas fa-mobile-alt me-2"></i>
                        Pago Móvil R4 - Método Principal
                    </h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <p class="mb-2">
                                <strong>Pago instantáneo y seguro</strong><br>
                                <small class="text-muted">
                                    Conectado directamente con R4 Conecta para confirmación automática
                                </small>
                            </p>
                            <div class="payment-amounts">
                                <div class="row">
                                    <div class="col-6">
                                        <label class="form-label">Monto a Pagar:</label>
                                        <input type="number" 
                                               id="r4Amount${application.id}" 
                                               class="form-control" 
                                               placeholder="Ingresa el monto"
                                               min="5" 
                                               step="0.01">
                                    </div>
                                    <div class="col-6">
                                        <label class="form-label">Tipo de Pago:</label>
                                        <select id="r4PaymentType${application.id}" class="form-select">
                                            <option value="installment">Cuota Mensual</option>
                                            <option value="initial">Pago Inicial</option>
                                            <option value="partial">Pago Parcial</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="row mt-2">
                                    <div class="col-12">
                                        <label class="form-label">Notas (Opcional):</label>
                                        <input type="text" 
                                               id="r4Notes${application.id}" 
                                               class="form-control" 
                                               placeholder="Ej: Pago cuota #3, adelanto, etc.">
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 text-center">
                            <button class="btn btn-success btn-lg w-100 r4-pay-btn" 
                                    data-app-id="${application.id}"
                                    onclick="R4PaymentButton.initiatePayment(${application.id})">
                                <i class="fas fa-mobile-alt me-2"></i>
                                Pagar con R4
                            </button>
                            <small class="text-muted d-block mt-2">
                                Confirmación automática en segundos
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        return buttonContainer;
    },
    
    // Iniciar proceso de pago R4
    async initiatePayment(applicationId) {
        try {
            // Obtener datos del formulario
            const amount = document.getElementById(`r4Amount${applicationId}`).value;
            const paymentType = document.getElementById(`r4PaymentType${applicationId}`).value;
            const notes = document.getElementById(`r4Notes${applicationId}`).value;
            
            // Validaciones
            if (\!amount || parseFloat(amount) <= 0) {
                this.showError("Por favor ingresa un monto válido mayor a 0");
                return;
            }
            
            if (parseFloat(amount) < 5) {
                this.showError("El monto mínimo para pago móvil R4 es .00");
                return;
            }
            
            // Deshabilitar botón durante el proceso
            const button = document.querySelector(`[data-app-id="${applicationId}"]`);
            const originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>Procesando...`;
            
            // Llamar API para iniciar pago R4
            const response = await API.users.authFetch("/api/payments/r4/initiate-payment/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    financing_request_id: applicationId,
                    amount: amount,
                    payment_type: paymentType,
                    customer_notes: notes
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showPaymentInstructions(result);
                
                // Limpiar formulario
                document.getElementById(`r4Amount${applicationId}`).value = "";
                document.getElementById(`r4Notes${applicationId}`).value = "";
                
                // Iniciar monitoreo del pago
                this.startPaymentMonitoring(result.payment_id);
                
            } else {
                this.showError(result.error || "Error al iniciar el pago R4");
            }
            
        } catch (error) {
            console.error("Error en pago R4:", error);
            this.showError("Error de conexión. Por favor intenta nuevamente.");
        } finally {
            // Rehabilitar botón
            const button = document.querySelector(`[data-app-id="${applicationId}"]`);
            button.disabled = false;
            button.innerHTML = originalText;
        }
    },
    
    // Mostrar instrucciones de pago R4
    showPaymentInstructions(paymentData) {
        const modal = document.createElement("div");
        modal.className = "modal fade";
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-mobile-alt me-2"></i>
                            Pago Móvil R4 Iniciado
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-success">
                            <strong>¡Pago iniciado exitosamente\!</strong><br>
                            Referencia: <code>${paymentData.reference}</code>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <h6>📱 Instrucciones de Pago:</h6>
                                <ol class="list-group list-group-numbered">
                                    <li class="list-group-item border-0 ps-0">${paymentData.instructions.step1}</li>
                                    <li class="list-group-item border-0 ps-0">${paymentData.instructions.step2}</li>
                                    <li class="list-group-item border-0 ps-0">${paymentData.instructions.step3}</li>
                                    <li class="list-group-item border-0 ps-0">${paymentData.instructions.step4}</li>
                                </ol>
                            </div>
                            <div class="col-md-6">
                                <h6>💳 Datos de Pago:</h6>
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <p class="mb-1"><strong>Teléfono:</strong> ${paymentData.r4_info.phone}</p>
                                        <p class="mb-1"><strong>Beneficiario:</strong> ${paymentData.r4_info.name}</p>
                                        <p class="mb-1"><strong>RIF:</strong> ${paymentData.r4_info.rif}</p>
                                        <p class="mb-0"><strong>Referencia:</strong> <code>${paymentData.reference}</code></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="alert alert-info mt-3">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>El pago se confirmará automáticamente</strong> una vez que R4 procese la transacción. 
                            Recibirás una notificación cuando se complete.
                        </div>
                        
                        <div id="paymentStatus${paymentData.payment_id}" class="mt-3">
                            <div class="d-flex align-items-center">
                                <div class="spinner-border spinner-border-sm text-primary me-2"></div>
                                <span>Esperando confirmación de R4...</span>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        <button type="button" class="btn btn-primary" onclick="window.location.reload()">
                            Actualizar Dashboard
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Limpiar modal cuando se cierre
        modal.addEventListener("hidden.bs.modal", () => {
            document.body.removeChild(modal);
        });
    },
    
    // Monitorear estado del pago
    async startPaymentMonitoring(paymentId) {
        let attempts = 0;
        const maxAttempts = 20; // 10 minutos máximo
        
        const checkStatus = async () => {
            try {
                const response = await API.users.authFetch(`/api/payments/r4/payment-status/${paymentId}/`);
                const status = await response.json();
                
                if (status.success) {
                    const statusElement = document.getElementById(`paymentStatus${paymentId}`);
                    
                    if (status.r4_status === "confirmed") {
                        if (statusElement) {
                            statusElement.innerHTML = `
                                <div class="alert alert-success">
                                    <i class="fas fa-check-circle me-2"></i>
                                    <strong>¡Pago confirmado por R4\!</strong>
                                </div>
                            `;
                        }
                        
                        // Mostrar notificación de éxito
                        this.showSuccessNotification("Pago confirmado exitosamente por R4");
                        return; // Detener monitoreo
                        
                    } else if (status.r4_status === "rejected") {
                        if (statusElement) {
                            statusElement.innerHTML = `
                                <div class="alert alert-danger">
                                    <i class="fas fa-times-circle me-2"></i>
                                    <strong>Pago rechazado</strong>
                                </div>
                            `;
                        }
                        return; // Detener monitoreo
                    }
                }
                
                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(checkStatus, 30000); // Revisar cada 30 segundos
                } else {
                    // Timeout - mostrar mensaje de estado manual
                    const statusElement = document.getElementById(`paymentStatus${paymentId}`);
                    if (statusElement) {
                        statusElement.innerHTML = `
                            <div class="alert alert-warning">
                                <i class="fas fa-clock me-2"></i>
                                El pago está siendo procesado. Te notificaremos cuando se confirme.
                            </div>
                        `;
                    }
                }
                
            } catch (error) {
                console.error("Error monitoring payment:", error);
            }
        };
        
        // Iniciar monitoreo después de 10 segundos
        setTimeout(checkStatus, 10000);
    },
    
    // Mostrar notificación de éxito
    showSuccessNotification(message) {
        const notification = document.createElement("div");
        notification.className = "alert alert-success alert-dismissible position-fixed";
        notification.style.cssText = "top: 20px; right: 20px; z-index: 9999; min-width: 300px;";
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove después de 5 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    },
    
    // Mostrar mensaje de error
    showError(message) {
        const alert = document.createElement("div");
        alert.className = "alert alert-danger alert-dismissible";
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insertar antes del primer botón R4
        const firstButton = document.querySelector(".r4-payment-container");
        if (firstButton) {
            firstButton.parentNode.insertBefore(alert, firstButton);
            
            // Auto-remove después de 5 segundos
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 5000);
        }
    }
};
