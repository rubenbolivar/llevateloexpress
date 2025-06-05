// FIX PARA PRESERVAR PARÁMETROS URL DURANTE NAVEGACIÓN
// Agregar al objeto FinancingRequest en solicitud-financiamiento.js

// Función para preservar parámetros URL durante navegación
preserveUrlParams() {
    const currentUrl = new URL(window.location);
    const step = this.currentStep;
    
    // Mantener todos los parámetros existentes
    const params = new URLSearchParams(window.location.search);
    
    // Actualizar solo el paso actual si es necesario
    if (params.has("step")) {
        params.set("step", step);
    }
    
    // Actualizar URL sin recargar página
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, "", newUrl);
    
    console.log(`URL preservada con parámetros: ${params.toString()}`);
},

// MODIFICAR FUNCIONES EXISTENTES para llamar preserveUrlParams:

// nextStep MODIFICADO:
nextStep() {
    if (this.currentStep < this.totalSteps) {
        // Validar paso actual antes de continuar
        if (this.validateCurrentStep()) {
            this.currentStep++;
            this.renderCurrentStep();
            this.preserveUrlParams(); // ← AGREGAR ESTA LÍNEA
        }
    }
},

// prevStep MODIFICADO:
prevStep() {
    if (this.currentStep > 1) {
        this.currentStep--;
        this.renderCurrentStep();
        this.preserveUrlParams(); // ← AGREGAR ESTA LÍNEA
    }
},

// renderCurrentStep MODIFICADO (agregar al final):
renderCurrentStep() {
    // ... código existente ...
    
    // Al final del método, preservar URL
    this.preserveUrlParams(); // ← AGREGAR ESTA LÍNEA
} 