#!/usr/bin/env python3
import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
sys.path.append('/var/www/llevateloexpress')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from financing.models import FinancingPlan, CalculatorMode
from products.models import Product, Category

def log_debug(message, data=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{timestamp}] {message}')
    if data:
        print(json.dumps(data, indent=2, default=str))
    print('-' * 50)

def analyze_current_state():
    log_debug('INICIANDO ANÁLISIS DEL ESTADO ACTUAL')
    
    # 1. Verificar modalidades
    modes = CalculatorMode.objects.all()
    log_debug(f'MODALIDADES CONFIGURADAS: {modes.count()}')
    for mode in modes:
        mode_data = {
            'id': mode.id,
            'name': mode.name,
            'type': mode.mode_type,
            'available_down_payments': mode.available_down_payments,
            'available_terms': mode.available_terms,
            'is_active': mode.is_active,
            'min_initial_contribution': mode.min_initial_contribution,
            'max_initial_contribution': mode.max_initial_contribution,
            'interest_rate': mode.interest_rate
        }
        log_debug(f'Modalidad: {mode.name}', mode_data)
    
    # 2. Verificar planes
    plans = FinancingPlan.objects.all()
    log_debug(f'PLANES DE FINANCIAMIENTO: {plans.count()}')
    for plan in plans:
        plan_data = {
            'id': plan.id,
            'name': plan.name,
            'slug': plan.slug,
            'min_down_payment_percentage': plan.min_down_payment_percentage,
            'max_term_months': plan.max_term_months,
            'interest_rate': plan.interest_rate,
            'is_active': plan.is_active,
            'min_amount': plan.min_amount,
            'max_amount': plan.max_amount
        }
        log_debug(f'Plan {plan.id}: {plan.name}', plan_data)
    
    # 3. Verificar productos
    categories = Category.objects.all()
    log_debug(f'CATEGORÍAS DE PRODUCTOS: {categories.count()}')
    for cat in categories:
        products = cat.products.all()[:3]  # Mostrar primeros 3
        cat_data = {
            'id': cat.id,
            'name': cat.name,
            'slug': cat.slug,
            'total_products': cat.products.count(),
            'sample_products': [
                {'id': p.id, 'name': p.name, 'price': float(p.price)}
                for p in products
            ]
        }
        log_debug(f'Categoría: {cat.name}', cat_data)

def test_calculator_config_api():
    log_debug('SIMULANDO API CALL: /api/financing/calculator/config/')
    
    try:
        # Simular la respuesta del API
        modes = CalculatorMode.objects.filter(is_active=True)
        categories = Category.objects.all()
        
        config_response = {
            'modes': [],
            'categories': []
        }
        
        for mode in modes:
            config_response['modes'].append({
                'id': mode.id,
                'name': mode.name,
                'mode_type': mode.mode_type,
                'description': mode.description,
                'down_payment_options': mode.available_down_payments,
                'term_options': mode.available_terms,
                'min_initial_contribution': mode.min_initial_contribution,
                'max_initial_contribution': mode.max_initial_contribution
            })
        
        for cat in categories:
            products_data = []
            for product in cat.products.all()[:5]:  # Primeros 5 productos
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'brand': product.brand,
                    'price': float(product.price)
                })
            
            config_response['categories'].append({
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'products': products_data
            })
        
        log_debug('RESPUESTA CONFIG API', config_response)
        return config_response
        
    except Exception as e:
        log_debug(f'ERROR EN CONFIG API: {str(e)}')
        return None

def test_calculation_simulation():
    log_debug('SIMULANDO CÁLCULO DE FINANCIAMIENTO')
    
    # Datos de prueba típicos
    test_data = {
        'mode_type': 'credito',
        'product_price': 15000,
        'down_payment_percentage': 35,
        'term_months': 24,
        'payment_frequency': 'monthly'
    }
    
    log_debug('Datos de entrada', test_data)
    
    # Simular cálculo
    down_payment_amount = test_data['product_price'] * (test_data['down_payment_percentage'] / 100)
    financed_amount = test_data['product_price'] - down_payment_amount
    payment_amount = financed_amount / test_data['term_months']
    
    calculation_result = {
        'financing_plan_id': 8,  # Plan 35%
        'calculation': {
            'vehicle_value': test_data['product_price'],
            'down_payment_percentage': test_data['down_payment_percentage'],
            'down_payment_amount': down_payment_amount,
            'financed_amount': financed_amount,
            'term_months': test_data['term_months'],
            'payment_frequency': test_data['payment_frequency'],
            'payment_amount': payment_amount,
            'total_cost': test_data['product_price'],
            'first_payment_date': '2024-07-01',
            'payoff_date': '2026-06-01'
        },
        'product': {
            'id': 1,
            'name': 'Producto de Prueba',
            'price': test_data['product_price']
        },
        'mode': {
            'name': 'Crédito Inmediato',
            'type': 'credito'
        }
    }
    
    log_debug('Resultado del cálculo', calculation_result)
    return calculation_result

def test_url_encoding():
    log_debug('PROBANDO ENCODING/DECODING DE URL PARAMETERS')
    
    # Obtener resultado de cálculo de prueba
    calc_result = test_calculation_simulation()
    
    # Test encoding como URLSearchParams
    import urllib.parse
    
    params = {
        'mode': 'credito',
        'calculation': json.dumps(calc_result)
    }
    
    # Encoding estándar
    query_string = urllib.parse.urlencode(params)
    log_debug(f'Query string length: {len(query_string)}')
    log_debug(f'Query string preview: {query_string[:200]}...')
    
    # Test parsing
    parsed = urllib.parse.parse_qs(query_string)
    calculation_param = parsed.get('calculation', [None])[0]
    
    if calculation_param:
        try:
            # Test 1: Parsing directo (como debería funcionar)
            decoded_data = json.loads(calculation_param)
            log_debug('✓ PARSING DIRECTO: EXITOSO')
            log_debug('Producto recuperado', decoded_data.get('product', {}))
        except Exception as e:
            log_debug(f'✗ PARSING DIRECTO: ERROR - {str(e)}')
        
        try:
            # Test 2: Con decodeURIComponent adicional
            decoded_uri = urllib.parse.unquote(calculation_param)
            decoded_data = json.loads(decoded_uri)
            log_debug('✓ PARSING CON DECODE ADICIONAL: EXITOSO')
            log_debug('Producto recuperado', decoded_data.get('product', {}))
        except Exception as e:
            log_debug(f'✗ PARSING CON DECODE ADICIONAL: ERROR - {str(e)}')

if __name__ == '__main__':
    print('=' * 60)
    print('DIAGNÓSTICO COMPLETO DEL SISTEMA DE FINANCIAMIENTO')
    print('=' * 60)
    
    analyze_current_state()
    test_calculator_config_api()
    test_url_encoding()
    
    print('=' * 60)
    print('DIAGNÓSTICO COMPLETADO')
    print('=' * 60) 