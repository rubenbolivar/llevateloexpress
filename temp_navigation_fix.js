/**
 * PARCHE TEMPORAL DE NAVEGACIÓN
 * Este archivo resuelve temporalmente el error: FinancingRequestV2.nextStep is not a function
 * Usar hasta que se sincronice la versión definitiva
 */

// Esperar a que FinancingRequestV2 esté disponible
function waitForFinancingV2() {
    if (window.FinancingRequestV2 && window.FinancingRequestV2.nextStep) {
        console.log('✅ FinancingRequestV2 ya está disponible');
        applyNavigationFix();
    } else if (window.FinancingRequestV2) {
        console.log('🔧 Aplicando parche de navegación a FinancingRequestV2...');
        applyNavigationFix();
    } else {
        console.log('⏳ Esperando FinancingRequestV2...');
        setTimeout(waitForFinancingV2, 100);
    }
}

function applyNavigationFix() {
    try {
        // Obtener la instancia existente
        const instance = window.FinancingRequestV2;
        
        if (instance && typeof instance.nextStep === 'function') {
            // Aplicar compatibilidad directa con la clase
            FinancingRequestV2.nextStep = () => instance.nextStep();
            FinancingRequestV2.prevStep = () => instance.prevStep();
            FinancingRequestV2.submitRequest = () => instance.submitRequest();
            
            console.log('✅ Parche de navegación aplicado exitosamente');
            console.log('✅ FinancingRequestV2.nextStep ahora está disponible');
            
            // Verificar que funciona
            if (typeof FinancingRequestV2.nextStep === 'function') {
                console.log('🎯 PARCHE CONFIRMADO: navegación funcionará correctamente');
            }
        } else {
            console.log('❌ No se pudo aplicar el parche - instancia no válida');
        }
    } catch (error) {
        console.error('❌ Error aplicando parche de navegación:', error);
    }
}

// Ejecutar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', waitForFinancingV2);
} else {
    waitForFinancingV2();
}

console.log('🔧 Parche temporal de navegación cargado'); 