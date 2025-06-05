/**
 * DEBUG FRONTEND FLOW - LlévateloExpress
 * Script para instrumentar y diagnosticar el flujo frontend
 */

const FrontendDebugger = {
    logs: [],
    originalConsoleLog: console.log,
    
    init() {
        this.setupConsoleCapture();
        this.setupLocalStorageCapture();
        this.instrumentCalculatorMethods();
        this.instrumentSolicitudMethods();
        this.log('🚀 Frontend Debugger inicializado');
    },

    log(message, data = null) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            message,
            data: data ? JSON.parse(JSON.stringify(data)) : null,
            url: window.location.href,
            page: this.getCurrentPage()
        };
        
        this.logs.push(logEntry);
        this.originalConsoleLog(`[DEBUG ${timestamp}] ${message}`, data || '');
        
        // También guardar en localStorage para debugging
        try {
            localStorage.setItem('debug_logs', JSON.stringify(this.logs.slice(-50))); // Últimos 50 logs
        } catch (e) {
            // Ignore localStorage errors
        }
    },

    getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('calculadora')) return 'calculadora';
        if (path.includes('solicitud-financiamiento')) return 'solicitud';
        return 'unknown';
    },

    setupConsoleCapture() {
        const self = this;
        console.log = function(...args) {
            self.originalConsoleLog.apply(console, args);
            if (args[0] && typeof args[0] === 'string') {
                self.log(`CONSOLE: ${args[0]}`, args.slice(1));
            }
        };
    },

    setupLocalStorageCapture() {
        const self = this;
        const originalSetItem = Storage.prototype.setItem;
        Storage.prototype.setItem = function(key, value) {
            // Evitar logging de nuestros propios debug logs para prevenir bucle infinito
            if (key !== 'debug_logs') {
                self.log(`LOCALSTORAGE SET: ${key}`, { value: value.substring(0, 200) + '...' });
            }
            originalSetItem.apply(this, arguments);
        };
    },

    instrumentCalculatorMethods() {
        const self = this;
        
        // Esperar a que CalculadoraIntegrada esté disponible
        const checkCalculadora = () => {
            if (window.CalculadoraIntegrada) {
                self.log('✅ CalculadoraIntegrada encontrada');
                
                // Instrumentar requestFinancing
                const originalRequestFinancing = window.CalculadoraIntegrada.requestFinancing;
                window.CalculadoraIntegrada.requestFinancing = function() {
                    self.log('🔄 requestFinancing() LLAMADO');
                    self.log('📊 currentCalculation:', this.currentCalculation);
                    self.log('🎯 currentMode:', this.currentMode);
                    
                    // Capturar datos antes de crear params
                    if (this.currentCalculation) {
                        const params = new URLSearchParams({
                            mode: this.currentMode,
                            calculation: JSON.stringify(this.currentCalculation)
                        });
                        
                        const urlToNavigate = `solicitud-financiamiento.html?${params.toString()}`;
                        self.log('🌐 URL generada:', urlToNavigate);
                        self.log('📏 URL length:', urlToNavigate.length);
                        self.log('🔗 Params preview:', params.toString().substring(0, 300) + '...');
                        
                        // Guardar en localStorage para debugging
                        try {
                            localStorage.setItem('debug_last_calculation', JSON.stringify(this.currentCalculation));
                            localStorage.setItem('debug_last_mode', this.currentMode);
                            localStorage.setItem('debug_last_url', urlToNavigate);
                        } catch (e) {
                            self.log('❌ Error guardando en localStorage:', e.message);
                        }
                    } else {
                        self.log('❌ currentCalculation es NULL');
                    }
                    
                    // Llamar método original
                    return originalRequestFinancing.apply(this, arguments);
                };
                
                // Instrumentar calculate
                const originalCalculate = window.CalculadoraIntegrada.calculate;
                window.CalculadoraIntegrada.calculate = async function() {
                    self.log('🧮 calculate() LLAMADO');
                    
                    try {
                        const result = await originalCalculate.apply(this, arguments);
                        self.log('✅ calculate() EXITOSO');
                        self.log('📊 Resultado calculation:', this.currentCalculation);
                        return result;
                    } catch (error) {
                        self.log('❌ calculate() ERROR:', error.message);
                        throw error;
                    }
                };
                
            } else if (self.getCurrentPage() === 'calculadora') {
                self.log('⏳ Esperando CalculadoraIntegrada...');
                setTimeout(checkCalculadora, 1000);
            }
        };
        
        if (this.getCurrentPage() === 'calculadora') {
            checkCalculadora();
        }
    },

    instrumentSolicitudMethods() {
        const self = this;
        
        if (this.getCurrentPage() === 'solicitud') {
            self.log('📋 Página de solicitud detectada');
            
            // Capturar parámetros URL inmediatamente
            const urlParams = new URLSearchParams(window.location.search);
            const calculationParam = urlParams.get('calculation');
            const modeParam = urlParams.get('mode');
            
            self.log('🔍 Parámetros URL capturados:');
            self.log('  - mode:', modeParam);
            self.log('  - calculation length:', calculationParam ? calculationParam.length : 0);
            self.log('  - calculation preview:', calculationParam ? calculationParam.substring(0, 200) + '...' : 'NULL');
            
            if (calculationParam) {
                try {
                    // Test parsing directo
                    const directParsed = JSON.parse(calculationParam);
                    self.log('✅ PARSING DIRECTO exitoso');
                    self.log('📊 Datos recuperados (directo):', {
                        product: directParsed.product,
                        calculation_summary: {
                            vehicle_value: directParsed.calculation?.vehicle_value,
                            down_payment_amount: directParsed.calculation?.down_payment_amount
                        }
                    });
                } catch (e) {
                    self.log('❌ PARSING DIRECTO falló:', e.message);
                }
                
                try {
                    // Test parsing con decodeURIComponent
                    const decoded = decodeURIComponent(calculationParam);
                    const decodedParsed = JSON.parse(decoded);
                    self.log('✅ PARSING CON DECODE exitoso');
                    self.log('📊 Datos recuperados (decode):', {
                        product: decodedParsed.product,
                        calculation_summary: {
                            vehicle_value: decodedParsed.calculation?.vehicle_value,
                            down_payment_amount: decodedParsed.calculation?.down_payment_amount
                        }
                    });
                } catch (e) {
                    self.log('❌ PARSING CON DECODE falló:', e.message);
                }
            }
            
            // Esperar a que FinancingRequest esté disponible
            const checkFinancingRequest = () => {
                if (window.FinancingRequest) {
                    self.log('✅ FinancingRequest encontrado');
                    
                    // Instrumentar loadCalculationData
                    const originalLoadCalculationData = window.FinancingRequest.loadCalculationData;
                    window.FinancingRequest.loadCalculationData = function() {
                        self.log('📥 loadCalculationData() LLAMADO');
                        
                        try {
                            const result = originalLoadCalculationData.apply(this, arguments);
                            self.log('✅ loadCalculationData() EXITOSO');
                            self.log('📊 calculationData cargado:', this.calculationData);
                            return result;
                        } catch (error) {
                            self.log('❌ loadCalculationData() ERROR:', error.message);
                            throw error;
                        }
                    };
                    
                    // Instrumentar renderCalculationSummary
                    const originalRenderCalculationSummary = window.FinancingRequest.renderCalculationSummary;
                    window.FinancingRequest.renderCalculationSummary = function() {
                        self.log('🎨 renderCalculationSummary() LLAMADO');
                        self.log('📊 calculationData para render:', this.calculationData);
                        
                        try {
                            const result = originalRenderCalculationSummary.apply(this, arguments);
                            self.log('✅ renderCalculationSummary() EXITOSO');
                            
                            // Verificar si se renderizó contenido
                            const summaryContainer = document.getElementById('calculationSummary');
                            const productContainer = document.getElementById('productDetails');
                            const financingContainer = document.getElementById('financingDetails');
                            
                            self.log('🔍 Contenido renderizado:');
                            self.log('  - calculationSummary:', summaryContainer ? summaryContainer.innerHTML.length : 0);
                            self.log('  - productDetails:', productContainer ? productContainer.innerHTML.length : 0);
                            self.log('  - financingDetails:', financingContainer ? financingContainer.innerHTML.length : 0);
                            
                            return result;
                        } catch (error) {
                            self.log('❌ renderCalculationSummary() ERROR:', error.message);
                            throw error;
                        }
                    };
                    
                } else {
                    self.log('⏳ Esperando FinancingRequest...');
                    setTimeout(checkFinancingRequest, 1000);
                }
            };
            
            checkFinancingRequest();
        }
    },

    // Métodos de utilidad para debugging manual
    getCurrentState() {
        const state = {
            page: this.getCurrentPage(),
            url: window.location.href,
            logs_count: this.logs.length,
            latest_logs: this.logs.slice(-10)
        };
        
        if (this.getCurrentPage() === 'calculadora' && window.CalculadoraIntegrada) {
            state.calculator = {
                currentMode: window.CalculadoraIntegrada.currentMode,
                hasCalculation: !!window.CalculadoraIntegrada.currentCalculation,
                hasConfiguration: !!window.CalculadoraIntegrada.configuration
            };
        }
        
        if (this.getCurrentPage() === 'solicitud' && window.FinancingRequest) {
            state.financing_request = {
                hasCalculationData: !!window.FinancingRequest.calculationData,
                currentStep: window.FinancingRequest.currentStep
            };
        }
        
        return state;
    },

    exportLogs() {
        const blob = new Blob([JSON.stringify(this.logs, null, 2)], 
                             { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `debug_logs_${new Date().toISOString()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    },

    clearLogs() {
        this.logs = [];
        localStorage.removeItem('debug_logs');
        this.log('🧹 Logs limpiados');
    }
};

// Auto-inicializar
if (typeof document !== 'undefined' && document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => FrontendDebugger.init());
} else {
    FrontendDebugger.init();
}

// Hacer disponible globalmente
window.FrontendDebugger = FrontendDebugger;

// Logging inicial
FrontendDebugger.log('🔧 Frontend Debug Script cargado', {
    page: FrontendDebugger.getCurrentPage(),
    url: window.location.href,
    userAgent: navigator.userAgent.substring(0, 100)
}); 