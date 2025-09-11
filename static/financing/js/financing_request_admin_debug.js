// JavaScript simplificado para debug del autocompletado de financiamiento

(function($) {
    'use strict';
    
    console.log('🟢 Financing admin JS loaded successfully');
    
    $(document).ready(function() {
        console.log('🟢 Document ready, initializing...');
        
        // Verificar que jQuery está disponible
        if (typeof $ === 'undefined') {
            console.error('❌ jQuery no está disponible');
            return;
        }
        
        // Verificar que django.jQuery está disponible
        if (typeof django !== 'undefined' && typeof django.jQuery !== 'undefined') {
            $ = django.jQuery;
            console.log('🟢 Using django.jQuery');
        } else {
            console.log('🟡 Using global jQuery');
        }
        
        // Función para obtener datos del producto
        function loadProductData(productId) {
            console.log('🔍 Loading data for product ID:', productId);
            
            if (!productId || productId === '') {
                console.log('⚠️ No product ID provided, clearing fields');
                clearFinancingData();
                return;
            }
            
            // URL del endpoint
            const url = `/api/financing/admin/product-data/${productId}/`;
            console.log('📡 Making request to:', url);
            
            // Mostrar loading
            showMessage('Cargando datos del producto...', 'info');
            
            $.ajax({
                url: url,
                method: 'GET',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
                    'Content-Type': 'application/json'
                },
                success: function(response) {
                    console.log('✅ Success response:', response);
                    
                    if (response && response.success && response.data) {
                        populateFinancingData(response.data);
                        showMessage('Datos cargados correctamente', 'success');
                    } else {
                        console.error('❌ Invalid response format:', response);
                        showMessage('Error: Formato de respuesta inválido', 'error');
                    }
                },
                error: function(xhr, status, error) {
                    console.error('❌ AJAX Error:');
                    console.error('Status:', status);
                    console.error('Error:', error);
                    console.error('Response:', xhr.responseText);
                    console.error('Status Code:', xhr.status);
                    
                    let errorMessage = 'Error desconocido';
                    if (xhr.status === 403) {
                        errorMessage = 'Sin permisos (403)';
                    } else if (xhr.status === 404) {
                        errorMessage = 'Endpoint no encontrado (404)';
                    } else if (xhr.status === 500) {
                        errorMessage = 'Error del servidor (500)';
                    }
                    
                    showMessage(`Error al cargar datos: ${errorMessage}`, 'error');
                }
            });
        }
        
        // Función para poblar campos
        function populateFinancingData(data) {
            console.log('📝 Populating fields with data:', data);
            
            const fieldsToUpdate = [
                { id: '#id_product_price_llevos', value: data.price_llevos, name: 'Precio' },
                { id: '#id_down_payment_llevos', value: data.inicial_llevos, name: 'Inicial' },
                { id: '#id_financed_amount_llevos', value: data.financed_amount_llevos, name: 'Financiado' },
                { id: '#id_payment_amount_llevos', value: data.payment_amount_llevos, name: 'Cuota' },
                { id: '#id_number_of_payments', value: data.number_of_payments, name: 'Número de cuotas' },
                { id: '#id_payment_frequency', value: data.payment_frequency, name: 'Frecuencia' }
            ];
            
            fieldsToUpdate.forEach(field => {
                const element = $(field.id);
                if (element.length > 0 && field.value !== undefined && field.value !== null) {
                    element.val(field.value);
                    console.log(`✅ Updated ${field.name}: ${field.value}`);
                } else if (element.length === 0) {
                    console.error(`❌ Field not found: ${field.id}`);
                } else {
                    console.log(`⚠️ No value for ${field.name}`);
                }
            });
        }
        
        // Función para limpiar campos
        function clearFinancingData() {
            console.log('🧹 Clearing financing data');
            const fields = [
                '#id_product_price_llevos',
                '#id_down_payment_llevos', 
                '#id_financed_amount_llevos',
                '#id_payment_amount_llevos',
                '#id_number_of_payments',
                '#id_payment_frequency'
            ];
            
            fields.forEach(fieldId => {
                const element = $(fieldId);
                if (element.length > 0) {
                    element.val('');
                }
            });
        }
        
        // Función para mostrar mensajes
        function showMessage(message, type) {
            console.log(`💬 Message (${type}): ${message}`);
            
            // Remover mensajes previos
            $('.financing-message').remove();
            
            const colors = {
                success: { bg: '#d4edda', border: '#c3e6cb', color: '#155724' },
                error: { bg: '#f8d7da', border: '#f5c6cb', color: '#721c24' },
                info: { bg: '#d1ecf1', border: '#bee5eb', color: '#0c5460' }
            };
            
            const style = colors[type] || colors.info;
            
            const messageDiv = $(`
                <div class="financing-message" style="
                    position: fixed;
                    top: 100px;
                    right: 20px;
                    z-index: 9999;
                    max-width: 300px;
                    background: ${style.bg};
                    border: 1px solid ${style.border};
                    color: ${style.color};
                    padding: 12px 15px;
                    border-radius: 5px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    font-weight: bold;
                ">
                    ${message}
                </div>
            `);
            
            $('body').append(messageDiv);
            
            setTimeout(function() {
                messageDiv.fadeOut(500, function() {
                    messageDiv.remove();
                });
            }, 5000);
        }
        
        // Event listener para cambio de producto
        const productField = $('#id_product');
        console.log('🔍 Product field found:', productField.length > 0);
        
        if (productField.length > 0) {
            productField.change(function() {
                const productId = $(this).val();
                console.log('🔄 Product changed to:', productId);
                
                if (productId && productId !== '') {
                    loadProductData(productId);
                } else {
                    clearFinancingData();
                }
            });
            
            // Cargar datos si ya hay un producto seleccionado
            const initialProductId = productField.val();
            if (initialProductId && initialProductId !== '') {
                console.log('🚀 Loading initial product data for ID:', initialProductId);
                loadProductData(initialProductId);
            }
        } else {
            console.error('❌ Product field #id_product not found!');
        }
        
        console.log('🟢 Initialization complete');
    });
    
})(window.jQuery || window.$ || django.jQuery);