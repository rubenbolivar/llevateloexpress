// FIX FRONTEND - Conversión automática de datos problemáticos
// Este script se ejecuta antes del envío para normalizar los datos

const FinancingDataFixer = {
    // Mapeo de frecuencias de pago
    paymentFrequencyMap: {
        'semanal': 'weekly',
        'quincenal': 'biweekly', 
        'mensual': 'monthly',
        'weekly': 'weekly',
        'biweekly': 'biweekly',
        'monthly': 'monthly'
    },

    // Mapeo de tipos de empleo
    employmentTypeMap: {
        'empleado_publico': 'empleado_publico',
        'empleado_privado': 'empleado_privado', 
        'independiente': 'independiente',
        'empresario': 'empresario',
        'pensionado': 'pensionado',
        'otro': 'otro'
    },

    /**
     * Normaliza los datos antes del envío al backend
     * @param {Object} data - Datos del formulario
     * @returns {Object} - Datos normalizados
     */
    normalizeData(data) {
        const normalized = { ...data };

        // Fix 1: Normalizar payment_frequency
        if (normalized.payment_frequency) {
            const freq = normalized.payment_frequency.toLowerCase();
            normalized.payment_frequency = this.paymentFrequencyMap[freq] || normalized.payment_frequency;
        }

        // Fix 2: Redondear payment_amount a 2 decimales
        if (normalized.payment_amount) {
            normalized.payment_amount = parseFloat(normalized.payment_amount).toFixed(2);
        }

        // Fix 3: Redondear todos los montos a 2 decimales
        const moneyFields = [
            'product_price', 'down_payment_amount', 'financed_amount', 
            'total_interest', 'total_amount', 'monthly_income'
        ];
        
        moneyFields.forEach(field => {
            if (normalized[field]) {
                normalized[field] = parseFloat(normalized[field]).toFixed(2);
            }
        });

        // Fix 4: Validar employment_type
        if (normalized.employment_type) {
            normalized.employment_type = this.employmentTypeMap[normalized.employment_type] || normalized.employment_type;
        }

        // Fix 5: Convertir números enteros
        const intFields = ['product', 'financing_plan', 'number_of_payments', 'down_payment_percentage'];
        intFields.forEach(field => {
            if (normalized[field]) {
                normalized[field] = parseInt(normalized[field]);
            }
        });

        return normalized;
    },

    /**
     * Valida que los datos estén en el formato correcto
     * @param {Object} data - Datos normalizados
     * @returns {Object} - {isValid: boolean, errors: string[]}
     */
    validateData(data) {
        const errors = [];

        // Validar payment_frequency
        const validFrequencies = ['weekly', 'biweekly', 'monthly'];
        if (data.payment_frequency && !validFrequencies.includes(data.payment_frequency)) {
            errors.push(`Frecuencia de pago inválida: ${data.payment_frequency}`);
        }

        // Validar employment_type
        const validEmploymentTypes = ['empleado_publico', 'empleado_privado', 'independiente', 'empresario', 'pensionado', 'otro'];
        if (data.employment_type && !validEmploymentTypes.includes(data.employment_type)) {
            errors.push(`Tipo de empleo inválido: ${data.employment_type}`);
        }

        // Validar que los montos tengan máximo 2 decimales
        const moneyFields = ['payment_amount', 'product_price', 'down_payment_amount'];
        moneyFields.forEach(field => {
            if (data[field]) {
                const value = data[field].toString();
                const decimals = value.split('.')[1];
                if (decimals && decimals.length > 2) {
                    errors.push(`${field} tiene más de 2 decimales: ${value}`);
                }
            }
        });

        return {
            isValid: errors.length === 0,
            errors: errors
        };
    },

    /**
     * Procesa y valida los datos antes del envío
     * @param {Object} rawData - Datos sin procesar
     * @returns {Object} - {success: boolean, data: Object, errors: string[]}
     */
    processForSubmission(rawData) {
        try {
            // Paso 1: Normalizar datos
            const normalized = this.normalizeData(rawData);
            
            // Paso 2: Validar datos
            const validation = this.validateData(normalized);
            
            if (!validation.isValid) {
                return {
                    success: false,
                    data: null,
                    errors: validation.errors
                };
            }

            return {
                success: true,
                data: normalized,
                errors: []
            };
        } catch (error) {
            return {
                success: false,
                data: null,
                errors: [`Error procesando datos: ${error.message}`]
            };
        }
    }
};

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.FinancingDataFixer = FinancingDataFixer;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = FinancingDataFixer;
} 