// JavaScript para autocompletar datos de financiamiento cuando se selecciona un producto

(function($) {
    'use strict';
    
    $(document).ready(function() {
        console.log('Financing request admin JS loaded');
        
        // Verificar que jQuery está disponible
        if (typeof django !== 'undefined' && typeof django.jQuery !== 'undefined') {
            $ = django.jQuery;
            console.log('Using django.jQuery');
        }
        
        // Función para obtener datos del producto y calcular financiamiento
        function loadProductData(productId) {
            if (!productId || productId === '') {
                clearFinancingData();
                return;
            }
            
            console.log('Loading data for product ID:', productId);
            
            // Usar endpoint simplificado a través de la API
            const url = `/api/financing/admin/product-data/${productId}/`;
            
            console.log('Using API URL:', url);
            
            // Mostrar mensaje de carga
            showMessage('Cargando datos del producto...', 'info');
            
            $.ajax({
                url: url,
                method: 'GET',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
                    'Content-Type': 'application/json'
                },
                success: function(response) {
                    console.log('Product data response:', response);
                    
                    if (response && response.success && response.data) {
                        populateFinancingData(response.data);
                        showMessage('Datos cargados correctamente', 'success');
                    } else {
                        console.error('Error getting product data:', response.error);
                        showMessage('Error al obtener datos del producto', 'error');
                    }
                },
                error: function(xhr, status, error) {
                    console.error('AJAX error:', error, 'Status:', status);
                    let errorMessage = 'Error al conectar con el servidor';
                    if (xhr.status === 403) {
                        errorMessage = 'Sin permisos de acceso';
                    } else if (xhr.status === 404) {
                        errorMessage = 'Servicio no encontrado';
                    }
                    showMessage(errorMessage, 'error');
                }
            });
        }
        
        // Función para poblar los campos con los datos del producto
        function populateFinancingData(data) {
            console.log('Populating fields with data:', data);
            
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
                    console.log(`Updated ${field.name}: ${field.value}`);
                }
            });
        }
        
        // Función para limpiar los campos de financiamiento
        function clearFinancingData() {
            $('#id_product_price_llevos').val('');
            $('#id_down_payment_llevos').val('');
            $('#id_financed_amount_llevos').val('');
            $('#id_payment_amount_llevos').val('');
            $('#id_number_of_payments').val('');
            $('#id_payment_frequency').val('');
        }
        
        // Función para mostrar mensajes
        function showMessage(message, type) {
            console.log(`Message (${type}): ${message}`);
            
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
            }, 4000);
        }
        
        // Event listener para el cambio de producto
        const productField = $('#id_product');
        console.log('Product field found:', productField.length > 0);
        
        if (productField.length > 0) {
            productField.change(function() {
                const productId = $(this).val();
                console.log('Product changed to:', productId);
                
                if (productId && productId !== '') {
                    loadProductData(productId);
                } else {
                    clearFinancingData();
                }
            });
            
            // Si ya hay un producto seleccionado al cargar la página, cargar sus datos
            const initialProductId = productField.val();
            if (initialProductId && initialProductId !== '') {
                console.log('Loading initial product data for:', initialProductId);
                loadProductData(initialProductId);
            }
        } else {
            console.error('Product field #id_product not found!');
        }
        
        console.log('Initialization complete');
    });
    
})(window.jQuery || window.$ || django.jQuery);