document.addEventListener('DOMContentLoaded', function() {
    // Inicializar elementos de la calculadora
    initCalculator();
    
    // Configurar eventos
    setupCalculatorEvents();
    
    // Inicializar sliders
    initializeRangeSliders();
    
    // Configurar tooltips para explicaciones
    setupTooltips();
});

/**
 * Inicializar la calculadora y sus valores predeterminados
 */
function initCalculator() {
    // Obtener elementos del DOM
    const planSelector = document.getElementById('financingPlan');
    const priceInput = document.getElementById('vehiclePrice');
    const initialPaymentInput = document.getElementById('initialPayment');
    const termInput = document.getElementById('financingTerm');
    const resultContainer = document.getElementById('resultContainer');
    
    // Establecer valores predeterminados
    if (priceInput) priceInput.value = 15000;
    if (initialPaymentInput) initialPaymentInput.value = 5000;
    if (termInput) termInput.value = 36;
    
    // Ocultar resultados inicialmente
    if (resultContainer) {
        resultContainer.style.display = 'none';
    }
    
    // Actualizar textos de valores iniciales
    updatePriceText();
    updateInitialPaymentText();
    updateTermText();
}

/**
 * Configurar eventos de la calculadora
 */
function setupCalculatorEvents() {
    // Elementos principales
    const calculateBtn = document.getElementById('calculateBtn');
    const resetBtn = document.getElementById('resetBtn');
    const planSelector = document.getElementById('financingPlan');
    
    // Botón calcular
    if (calculateBtn) {
        calculateBtn.addEventListener('click', function() {
            calculateFinancing();
        });
    }
    
    // Botón reiniciar
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            resetCalculator();
        });
    }
    
    // Cambio de plan
    if (planSelector) {
        planSelector.addEventListener('change', function() {
            updatePlanInfo();
        });
    }
    
    // Actualizar información del plan seleccionado inicialmente
    updatePlanInfo();
}

/**
 * Inicializar sliders con rangos y pasos apropiados
 */
function initializeRangeSliders() {
    // Configurar slider de precio
    const priceSlider = document.getElementById('vehiclePriceRange');
    const priceInput = document.getElementById('vehiclePrice');
    
    if (priceSlider && priceInput) {
        // Sincronizar slider con input
        priceSlider.value = priceInput.value;
        
        // Eventos
        priceSlider.addEventListener('input', function() {
            priceInput.value = this.value;
            updatePriceText();
            updateInitialPaymentConstraints();
        });
        
        priceInput.addEventListener('input', function() {
            priceSlider.value = this.value;
            updatePriceText();
            updateInitialPaymentConstraints();
        });
    }
    
    // Configurar slider de inicial
    const initialSlider = document.getElementById('initialPaymentRange');
    const initialInput = document.getElementById('initialPayment');
    
    if (initialSlider && initialInput) {
        // Sincronizar slider con input
        initialSlider.value = initialInput.value;
        
        // Eventos
        initialSlider.addEventListener('input', function() {
            initialInput.value = this.value;
            updateInitialPaymentText();
        });
        
        initialInput.addEventListener('input', function() {
            initialSlider.value = this.value;
            updateInitialPaymentText();
        });
    }
    
    // Configurar slider de plazo
    const termSlider = document.getElementById('financingTermRange');
    const termInput = document.getElementById('financingTerm');
    
    if (termSlider && termInput) {
        // Sincronizar slider con input
        termSlider.value = termInput.value;
        
        // Eventos
        termSlider.addEventListener('input', function() {
            termInput.value = this.value;
            updateTermText();
        });
        
        termInput.addEventListener('input', function() {
            termSlider.value = this.value;
            updateTermText();
        });
    }
}

/**
 * Actualizar texto de precio del vehículo
 */
function updatePriceText() {
    const priceText = document.getElementById('vehiclePriceText');
    const priceInput = document.getElementById('vehiclePrice');
    
    if (priceText && priceInput) {
        priceText.textContent = formatCurrency(parseFloat(priceInput.value));
    }
}

/**
 * Actualizar texto de pago inicial
 */
function updateInitialPaymentText() {
    const initialText = document.getElementById('initialPaymentText');
    const initialInput = document.getElementById('initialPayment');
    
    if (initialText && initialInput) {
        initialText.textContent = formatCurrency(parseFloat(initialInput.value));
    }
}

/**
 * Actualizar texto de plazo
 */
function updateTermText() {
    const termText = document.getElementById('financingTermText');
    const termInput = document.getElementById('financingTerm');
    
    if (termText && termInput) {
        const months = parseInt(termInput.value);
        const years = Math.floor(months / 12);
        const remainingMonths = months % 12;
        
        let termString = '';
        
        if (years > 0) {
            termString += years + ' año' + (years > 1 ? 's' : '');
        }
        
        if (remainingMonths > 0) {
            if (termString) termString += ' y ';
            termString += remainingMonths + ' mes' + (remainingMonths > 1 ? 'es' : '');
        }
        
        termText.textContent = termString;
    }
}

/**
 * Actualizar restricciones de pago inicial basado en el precio
 */
function updateInitialPaymentConstraints() {
    const priceInput = document.getElementById('vehiclePrice');
    const initialInput = document.getElementById('initialPayment');
    const initialSlider = document.getElementById('initialPaymentRange');
    
    if (priceInput && initialInput && initialSlider) {
        const price = parseFloat(priceInput.value);
        const maxInitial = price * 0.7; // Máximo 70% del precio
        
        // Actualizar atributos del slider
        initialSlider.max = maxInitial;
        initialInput.max = maxInitial;
        
        // Verificar si el valor actual excede el nuevo máximo
        if (parseFloat(initialInput.value) > maxInitial) {
            initialInput.value = maxInitial;
            initialSlider.value = maxInitial;
            updateInitialPaymentText();
        }
    }
}

/**
 * Actualizar información del plan de financiamiento
 */
function updatePlanInfo() {
    const planSelector = document.getElementById('financingPlan');
    const planInfo = document.getElementById('planInfo');
    
    if (planSelector && planInfo) {
        const selectedPlan = planSelector.value;
        
        if (selectedPlan === 'plan50') {
            planInfo.innerHTML = `
                <div class="alert alert-info">
                    <h5><i class="fas fa-info-circle me-2"></i>Plan 50-50</h5>
                    <p>Con este plan, pagas el 50% como inicial y el otro 50% financiado en cuotas mensuales.</p>
                    <ul>
                        <li>Tasa de interés preferencial del 15% anual</li>
                        <li>Plazos desde 12 hasta 36 meses</li>
                        <li>Aprobación rápida en 24 horas</li>
                    </ul>
                </div>
            `;
            
            // Ajustar slider y valor de inicial para que sea 50% del precio
            const priceInput = document.getElementById('vehiclePrice');
            const initialInput = document.getElementById('initialPayment');
            const initialSlider = document.getElementById('initialPaymentRange');
            
            if (priceInput && initialInput && initialSlider) {
                const price = parseFloat(priceInput.value);
                const fiftyPercent = price * 0.5;
                
                initialInput.value = fiftyPercent;
                initialSlider.value = fiftyPercent;
                updateInitialPaymentText();
            }
            
        } else if (selectedPlan === 'plan70') {
            planInfo.innerHTML = `
                <div class="alert alert-info">
                    <h5><i class="fas fa-info-circle me-2"></i>Plan 70-30</h5>
                    <p>Con este plan, pagas el 30% como inicial y el otro 70% financiado en cuotas mensuales.</p>
                    <ul>
                        <li>Tasa de interés anual del 18%</li>
                        <li>Plazos desde 24 hasta 60 meses</li>
                        <li>Incluye seguro de desempleo</li>
                    </ul>
                </div>
            `;
            
            // Ajustar slider y valor de inicial para que sea 30% del precio
            const priceInput = document.getElementById('vehiclePrice');
            const initialInput = document.getElementById('initialPayment');
            const initialSlider = document.getElementById('initialPaymentRange');
            
            if (priceInput && initialInput && initialSlider) {
                const price = parseFloat(priceInput.value);
                const thirtyPercent = price * 0.3;
                
                initialInput.value = thirtyPercent;
                initialSlider.value = thirtyPercent;
                updateInitialPaymentText();
            }
        }
    }
}

/**
 * Calcular financiamiento
 */
function calculateFinancing() {
    // Obtener valores
    const planSelector = document.getElementById('financingPlan');
    const priceInput = document.getElementById('vehiclePrice');
    const initialInput = document.getElementById('initialPayment');
    const termInput = document.getElementById('financingTerm');
    
    if (!planSelector || !priceInput || !initialInput || !termInput) {
        return;
    }
    
    const selectedPlan = planSelector.value;
    const price = parseFloat(priceInput.value);
    const initialPayment = parseFloat(initialInput.value);
    const term = parseInt(termInput.value);
    
    // Validaciones
    if (isNaN(price) || isNaN(initialPayment) || isNaN(term)) {
        showError('Por favor, ingresa valores numéricos válidos.');
        return;
    }
    
    if (initialPayment >= price) {
        showError('El pago inicial no puede ser mayor o igual al precio del vehículo.');
        return;
    }
    
    // Definir tasa según el plan
    let annualRate;
    if (selectedPlan === 'plan50') {
        annualRate = 0.15; // 15% anual
    } else {
        annualRate = 0.18; // 18% anual
    }
    
    // Convertir tasa anual a mensual
    const monthlyRate = annualRate / 12;
    
    // Calcular monto a financiar
    const amountToFinance = price - initialPayment;
    
    // Calcular cuota mensual
    // Fórmula: M = P * [r(1+r)^n] / [(1+r)^n-1]
    // Donde:
    // M = Pago mensual
    // P = Monto del préstamo
    // r = Tasa de interés mensual
    // n = Número de pagos (plazo en meses)
    
    const monthlyPayment = amountToFinance * 
        (monthlyRate * Math.pow(1 + monthlyRate, term)) / 
        (Math.pow(1 + monthlyRate, term) - 1);
    
    // Calcular costo total
    const totalCost = initialPayment + (monthlyPayment * term);
    
    // Calcular intereses pagados
    const interestPaid = totalCost - price;
    
    // Calcular fecha de adjudicación (simulada)
    const today = new Date();
    const adjudicationDate = new Date(today);
    
    // Fecha de adjudicación: +3 meses para Plan 50-50, +2 meses para Plan 70-30
    if (selectedPlan === 'plan50') {
        adjudicationDate.setMonth(today.getMonth() + 3);
    } else {
        adjudicationDate.setMonth(today.getMonth() + 2);
    }
    
    // Mostrar resultados
    displayResults({
        monthlyPayment,
        amountToFinance,
        totalCost,
        interestPaid,
        adjudicationDate,
        term,
        initialPayment,
        annualRate
    });
}

/**
 * Mostrar error
 */
function showError(message) {
    const errorAlert = document.getElementById('calculatorError');
    
    if (errorAlert) {
        errorAlert.textContent = message;
        errorAlert.style.display = 'block';
        
        // Ocultar después de 5 segundos
        setTimeout(() => {
            errorAlert.style.display = 'none';
        }, 5000);
    }
}

/**
 * Mostrar resultados del cálculo
 */
function displayResults(results) {
    const resultContainer = document.getElementById('resultContainer');
    const monthlyPaymentValue = document.getElementById('monthlyPaymentValue');
    const totalAmountValue = document.getElementById('totalAmountValue');
    const financedAmountValue = document.getElementById('financedAmountValue');
    const interestPaidValue = document.getElementById('interestPaidValue');
    const adjudicationDateValue = document.getElementById('adjudicationDateValue');
    const interestRateValue = document.getElementById('interestRateValue');
    
    if (!resultContainer) return;
    
    // Mostrar contenedor de resultados
    resultContainer.style.display = 'block';
    
    // Actualizar valores
    if (monthlyPaymentValue) {
        monthlyPaymentValue.textContent = formatCurrency(results.monthlyPayment);
    }
    
    if (totalAmountValue) {
        totalAmountValue.textContent = formatCurrency(results.totalCost);
    }
    
    if (financedAmountValue) {
        financedAmountValue.textContent = formatCurrency(results.amountToFinance);
    }
    
    if (interestPaidValue) {
        interestPaidValue.textContent = formatCurrency(results.interestPaid);
    }
    
    if (adjudicationDateValue) {
        adjudicationDateValue.textContent = formatDate(results.adjudicationDate);
    }
    
    if (interestRateValue) {
        interestRateValue.textContent = (results.annualRate * 100).toFixed(2) + '% anual';
    }
    
    // Generar tabla de amortización
    generateAmortizationTable(results);
    
    // Scroll suave hacia los resultados
    resultContainer.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Generar tabla de amortización
 */
function generateAmortizationTable(results) {
    const tableContainer = document.getElementById('amortizationTableBody');
    
    if (!tableContainer) return;
    
    // Limpiar tabla existente
    tableContainer.innerHTML = '';
    
    // Valores iniciales
    let remainingBalance = results.amountToFinance;
    const monthlyRate = results.annualRate / 12;
    
    // Generar filas para cada mes
    for (let month = 1; month <= results.term; month++) {
        // Calcular interés para este mes
        const interestPayment = remainingBalance * monthlyRate;
        
        // Calcular abono a capital
        const principalPayment = results.monthlyPayment - interestPayment;
        
        // Actualizar saldo restante
        remainingBalance -= principalPayment;
        
        // Crear fila
        const row = document.createElement('tr');
        
        // Contenido de la fila
        row.innerHTML = `
            <td>${month}</td>
            <td>${formatCurrency(results.monthlyPayment)}</td>
            <td>${formatCurrency(principalPayment)}</td>
            <td>${formatCurrency(interestPayment)}</td>
            <td>${formatCurrency(Math.max(0, remainingBalance))}</td>
        `;
        
        // Añadir fila a la tabla
        tableContainer.appendChild(row);
        
        // Para evitar tablas muy largas, mostrar solo los primeros 12 meses y el último
        if (month === 12 && results.term > 24) {
            const skipRow = document.createElement('tr');
            skipRow.innerHTML = `
                <td colspan="5" class="text-center">
                    <i class="fas fa-ellipsis-h"></i> Se omiten ${results.term - 13} pagos
                </td>
            `;
            tableContainer.appendChild(skipRow);
            month = results.term - 1;
        }
    }
}

/**
 * Reiniciar calculadora
 */
function resetCalculator() {
    // Obtener elementos
    const priceInput = document.getElementById('vehiclePrice');
    const priceSlider = document.getElementById('vehiclePriceRange');
    const initialInput = document.getElementById('initialPayment');
    const initialSlider = document.getElementById('initialPaymentRange');
    const termInput = document.getElementById('financingTerm');
    const termSlider = document.getElementById('financingTermRange');
    const resultContainer = document.getElementById('resultContainer');
    
    // Restablecer valores
    if (priceInput && priceSlider) {
        priceInput.value = 15000;
        priceSlider.value = 15000;
    }
    
    if (initialInput && initialSlider) {
        initialInput.value = 5000;
        initialSlider.value = 5000;
    }
    
    if (termInput && termSlider) {
        termInput.value = 36;
        termSlider.value = 36;
    }
    
    // Actualizar textos
    updatePriceText();
    updateInitialPaymentText();
    updateTermText();
    
    // Ocultar resultados
    if (resultContainer) {
        resultContainer.style.display = 'none';
    }
    
    // Actualizar información del plan
    updatePlanInfo();
}

/**
 * Configurar tooltips para información adicional
 */
function setupTooltips() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
}

/**
 * Formatear moneda a USD
 */
function formatCurrency(value) {
    return '$' + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

/**
 * Formatear fecha
 */
function formatDate(date) {
    const options = { day: 'numeric', month: 'long', year: 'numeric' };
    return date.toLocaleDateString('es-VE', options);
} 