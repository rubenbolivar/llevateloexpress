/**
 * SOLICITUD DE FINANCIAMIENTO V2 - PARTE 2
 * Métodos adicionales para completar la funcionalidad
 */

// MÉTODOS ADICIONALES PARA LA CLASE FinancingRequestV2

// Agregar estos métodos a la clase FinancingRequestV2:

/**
 * Actualizar datos del formulario
 */
updateFormData() {
    this.state.formData = {};
    
    Object.entries(this.elements.fields).forEach(([name, element]) => {
        if (element) {
            this.state.formData[name] = element.type === 'checkbox' 
                ? element.checked 
                : element.value;
        }
    });
    
    this.log('debug', 'Form data actualizada', this.state.formData);
}

/**
 * Validar campo individual
 */
validateField(field) {
    const name = field.name || field.id;
    const value = field.type === 'checkbox' ? field.checked : field.value;
    const rules = this.config.validationRules[name];
    
    if (!rules) return true;
    
    // Limpiar errores previos
    this.clearFieldError(field);
    
    // Validar requerido
    if (rules.required && (!value || value.toString().trim() === '')) {
        this.showFieldError(field, 'Este campo es obligatorio');
        return false;
    }
    
    // Validar valor mínimo
    if (rules.min !== undefined && parseFloat(value) < rules.min) {
        this.showFieldError(field, `El valor mínimo es ${rules.min}`);
        return false;
    }
    
    return true;
}

/**
 * Mostrar error en campo específico
 */
showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    // Buscar o crear contenedor de error
    let errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        field.parentNode.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
}

/**
 * Limpiar error de campo
 */
clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

/**
 * Validar paso actual
 */
validateCurrentStep() {
    switch (this.state.currentStep) {
        case 1:
            return this.validateStep1();
        case 2:
            return this.validateStep2();
        case 3:
            return this.validateStep3();
        case 4:
            return this.validateStep4();
        default:
            return true;
    }
}

/**
 * Validar paso 1 - Resumen
 */
validateStep1() {
    if (!this.state.calculationData) {
        this.showError('No hay datos de cálculo disponibles');
        return false;
    }
    return true;
}

/**
 * Validar paso 2 - Información Personal
 */
validateStep2() {
    this.updateFormData();
    
    const requiredFields = ['employment_type', 'monthly_income'];
    let isValid = true;
    
    requiredFields.forEach(fieldName => {
        const field = this.elements.fields[fieldName];
        if (field && !this.validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Validar paso 3 - Documentos
 */
validateStep3() {
    // Los documentos son opcionales
    return true;
}

/**
 * Validar paso 4 - Confirmación
 */
validateStep4() {
    const termsField = this.elements.fields.termsAccept;
    const consentField = this.elements.fields.dataConsent;
    
    let isValid = true;
    
    if (termsField && !termsField.checked) {
        this.showError('Debe aceptar los términos y condiciones');
        isValid = false;
    }
    
    if (consentField && !consentField.checked) {
        this.showError('Debe autorizar el tratamiento de datos personales');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Renderizar resumen de cálculo
 */
renderCalculationSummary() {
    if (!this.state.calculationData || !this.elements.calculationSummary) return;
    
    const calc = this.state.calculationData.calculation || this.state.calculationData;
    const product = this.state.calculationData.product || {};
    
    // Normalizar datos
    const productPrice = calc.product_price || product.price || 0;
    const downPaymentAmount = calc.down_payment_amount || 0;
    const downPaymentPercentage = calc.down_payment_percentage || 0;
    const paymentAmount = calc.payment_amount || 0;
    const numberOfPayments = calc.number_of_payments || 0;
    const paymentFrequency = calc.payment_frequency || 'monthly';
    
    // Renderizar resumen principal
