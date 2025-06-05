document.addEventListener('DOMContentLoaded', function() {
    // Inicializar comparador de planes
    initPlanComparison();
    
    // Configurar animaciones de entrada
    setupAnimations();
    
    // Configurar modales de información
    setupInfoModals();
    
    // Configurar FAQ (Preguntas frecuentes)
    setupFAQAccordion();
});

/**
 * Inicializar comparador de planes
 */
function initPlanComparison() {
    const comparisonToggle = document.getElementById('comparisonToggle');
    const comparisonTable = document.getElementById('planComparisonTable');
    
    if (comparisonToggle && comparisonTable) {
        comparisonToggle.addEventListener('click', function() {
            // Alternar visibilidad de la tabla
            if (comparisonTable.style.display === 'none' || !comparisonTable.style.display) {
                comparisonTable.style.display = 'block';
                comparisonToggle.textContent = 'Ocultar comparativa';
                
                // Scroll suave hacia la tabla
                comparisonTable.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                comparisonTable.style.display = 'none';
                comparisonToggle.textContent = 'Comparar planes';
            }
        });
    }
    
    // Inicialmente ocultar la tabla
    if (comparisonTable) {
        comparisonTable.style.display = 'none';
    }
}

/**
 * Configurar animaciones de entrada
 */
function setupAnimations() {
    // Elementos que se animarán
    const elements = document.querySelectorAll('.plan-card, .testimonial-card, .faq-item');
    
    // Observer para detectar cuándo los elementos son visibles
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    // Observar cada elemento
    elements.forEach(element => {
        observer.observe(element);
    });
}

/**
 * Configurar modales de información detallada
 */
function setupInfoModals() {
    // Botones de más información
    const infoButtons = document.querySelectorAll('.plan-info-btn');
    
    infoButtons.forEach(button => {
        button.addEventListener('click', function() {
            const planId = this.dataset.plan;
            showPlanDetails(planId);
        });
    });
}

/**
 * Mostrar detalles del plan en un modal
 */
function showPlanDetails(planId) {
    // Definir información detallada para cada plan
    const planDetails = {
        'plan5050': {
            title: 'Plan 50-50: Detalles Completos',
            description: 'El Plan 50-50 es ideal para quienes buscan un término medio entre pago inicial y financiamiento. Con este plan, pagas la mitad del valor del vehículo como inicial y financias el resto en cómodas cuotas mensuales.',
            requirements: [
                'Edad entre 18 y 65 años',
                'Ingresos mínimos de $500 mensuales',
                'Historial crediticio verificable',
                'Documentos de identidad vigentes'
            ],
            benefits: [
                'Tasa de interés preferencial del 15% anual',
                'Plazos flexibles de 12 a 36 meses',
                'Aprobación rápida en 24 horas',
                'Sin penalización por pago anticipado',
                'Incluye seguro contra robo y accidentes'
            ],
            adjudication: 'Con el Plan 50-50, la adjudicación de tu vehículo se realiza en un plazo aproximado de 3 meses desde la aprobación del financiamiento. Este periodo puede variar según la demanda y disponibilidad del modelo seleccionado.',
            examples: [
                {
                    vehicle: 'Toyota Corolla 2023',
                    price: 25000,
                    initial: 12500,
                    term: 24,
                    monthly: 615.72
                },
                {
                    vehicle: 'Honda CBR 650R',
                    price: 12000,
                    initial: 6000,
                    term: 18,
                    monthly: 388.52
                }
            ]
        },
        'plan7030': {
            title: 'Plan 70-30: Detalles Completos',
            description: 'El Plan 70-30 es perfecto para quienes prefieren un pago inicial menor. Con este plan, solo necesitas el 30% del valor del vehículo como entrada y financias el 70% restante en plazos extendidos.',
            requirements: [
                'Edad entre 21 y 65 años',
                'Ingresos mínimos de $800 mensuales',
                'Historial crediticio favorable',
                'Documentos de identidad y residencia vigentes',
                'Fiador en caso de no cumplir con todos los requisitos'
            ],
            benefits: [
                'Tasa de interés competitiva del 18% anual',
                'Plazos extendidos de 24 a 60 meses',
                'Seguro de desempleo incluido por 6 meses',
                'Posibilidad de refinanciamiento después de 12 pagos puntuales',
                'Mantenimiento básico incluido por 1 año'
            ],
            adjudication: 'Con el Plan 70-30, la adjudicación de tu vehículo se realiza en un plazo aproximado de 2 meses desde la aprobación del financiamiento, siendo ligeramente más rápido que el Plan 50-50.',
            examples: [
                {
                    vehicle: 'Nissan Sentra 2023',
                    price: 22000,
                    initial: 6600,
                    term: 48,
                    monthly: 435.27
                },
                {
                    vehicle: 'Yamaha MT-07',
                    price: 9500,
                    initial: 2850,
                    term: 36,
                    monthly: 238.94
                }
            ]
        },
        'planEspecial': {
            title: 'Plan Agrícola: Detalles Completos',
            description: 'El Plan Agrícola está diseñado específicamente para maquinaria y equipos agrícolas, con condiciones especiales que se adaptan a los ciclos de producción y las necesidades específicas del sector agrícola.',
            requirements: [
                'Ser propietario o arrendatario de terrenos agrícolas',
                'Experiencia demostrable en el sector agrícola',
                'Ingresos mínimos proporcionales al financiamiento solicitado',
                'Plan de negocio o proyección de uso de la maquinaria',
                'Documentación legal completa'
            ],
            benefits: [
                'Tasa de interés especial del 16.5% anual',
                'Pagos adaptados a los ciclos de cosecha',
                'Plazos de 24 a 72 meses',
                'Inclusión de capacitación en el uso del equipo',
                'Servicio técnico prioritario',
                'Posibilidad de subsidios gubernamentales'
            ],
            adjudication: 'Con el Plan Agrícola, la adjudicación de tu maquinaria se realiza en un plazo de 1 a 3 meses, dependiendo de la complejidad del equipo y si requiere importación específica.',
            examples: [
                {
                    vehicle: 'Tractor John Deere 5075E',
                    price: 45000,
                    initial: 13500,
                    term: 60,
                    monthly: 763.65
                },
                {
                    vehicle: 'Sistema de Riego Automatizado',
                    price: 18000,
                    initial: 5400,
                    term: 36,
                    monthly: 452.67
                }
            ]
        }
    };
    
    // Obtener información del plan seleccionado
    const planInfo = planDetails[planId];
    
    if (!planInfo) return;
    
    // Crear contenido del modal
    let modalContent = `
        <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">${planInfo.title}</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
            <div class="plan-description mb-4">
                <h6 class="border-bottom pb-2 mb-3"><i class="fas fa-info-circle me-2"></i>Descripción</h6>
                <p>${planInfo.description}</p>
            </div>
            
            <div class="plan-requirements mb-4">
                <h6 class="border-bottom pb-2 mb-3"><i class="fas fa-clipboard-check me-2"></i>Requisitos</h6>
                <ul class="list-group list-group-flush">
                    ${planInfo.requirements.map(req => `<li class="list-group-item"><i class="fas fa-check-circle text-success me-2"></i>${req}</li>`).join('')}
                </ul>
            </div>
            
            <div class="plan-benefits mb-4">
                <h6 class="border-bottom pb-2 mb-3"><i class="fas fa-gift me-2"></i>Beneficios</h6>
                <ul class="list-group list-group-flush">
                    ${planInfo.benefits.map(benefit => `<li class="list-group-item"><i class="fas fa-star text-warning me-2"></i>${benefit}</li>`).join('')}
                </ul>
            </div>
            
            <div class="plan-adjudication mb-4">
                <h6 class="border-bottom pb-2 mb-3"><i class="fas fa-calendar-check me-2"></i>Tiempo de Adjudicación</h6>
                <p>${planInfo.adjudication}</p>
            </div>
            
            <div class="plan-examples">
                <h6 class="border-bottom pb-2 mb-3"><i class="fas fa-calculator me-2"></i>Ejemplos de Financiamiento</h6>
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead class="table-light">
                            <tr>
                                <th>Vehículo/Equipo</th>
                                <th>Precio</th>
                                <th>Inicial</th>
                                <th>Plazo</th>
                                <th>Cuota Mensual</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${planInfo.examples.map(example => `
                                <tr>
                                    <td>${example.vehicle}</td>
                                    <td>$${example.price.toLocaleString()}</td>
                                    <td>$${example.initial.toLocaleString()}</td>
                                    <td>${example.term} meses</td>
                                    <td>$${example.monthly.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            <a href="calculadora.html" class="btn btn-primary">Ir a Calculadora</a>
        </div>
    `;
    
    // Crear modal dinámicamente
    const modalEl = document.createElement('div');
    modalEl.className = 'modal fade';
    modalEl.id = 'planDetailModal';
    modalEl.setAttribute('tabindex', '-1');
    modalEl.setAttribute('aria-labelledby', 'planDetailModalLabel');
    modalEl.setAttribute('aria-hidden', 'true');
    
    modalEl.innerHTML = `
        <div class="modal-dialog modal-lg modal-dialog-scrollable">
            <div class="modal-content">
                ${modalContent}
            </div>
        </div>
    `;
    
    // Añadir modal al DOM
    document.body.appendChild(modalEl);
    
    // Inicializar y mostrar modal
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
    
    // Eliminar modal del DOM cuando se cierre
    modalEl.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modalEl);
    });
}

/**
 * Configurar acordeón de preguntas frecuentes
 */
function setupFAQAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const header = item.querySelector('.faq-header');
        
        if (header) {
            header.addEventListener('click', function() {
                // Contraer todos los demás
                faqItems.forEach(otherItem => {
                    if (otherItem !== item && otherItem.classList.contains('active')) {
                        otherItem.classList.remove('active');
                        const otherContent = otherItem.querySelector('.faq-content');
                        if (otherContent) {
                            otherContent.style.maxHeight = null;
                        }
                    }
                });
                
                // Alternar el actual
                item.classList.toggle('active');
                
                const content = item.querySelector('.faq-content');
                if (content) {
                    if (item.classList.contains('active')) {
                        content.style.maxHeight = content.scrollHeight + 'px';
                    } else {
                        content.style.maxHeight = null;
                    }
                }
            });
        }
    });
} 