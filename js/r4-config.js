// Configuración R4 Conecta para LlévateloExpress
const R4Config = {
    // Datos del comercio registrado en R4
    commercePhone: '0412 1193126',
    commerceBank: 'Mi Banco',
    commerceName: 'LlévateloExpress',
    commerceId: 'LLEV001',
    
    // URLs de webhooks (ya implementados)
    webhooks: {
        validate: '/api/payments/webhooks/r4/validate-client/',
        notify: '/api/payments/webhooks/r4/notify/'
    },
    
    // Configuración de interfaz
    ui: {
        modalTitle: '💰 Pago Móvil R4',
        instructions: 'Realiza tu pago móvil con los siguientes datos:',
        successMessage: 'Una vez realizado el pago, será procesado automáticamente'
    }
};

// Exportar configuración
window.R4Config = R4Config;