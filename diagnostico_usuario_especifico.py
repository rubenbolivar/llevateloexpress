#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from django.contrib.auth.models import User
from financing.models import FinancingRequest
from products.llevo_models import LlevoRate

print('🔍 DIAGNÓSTICO USUARIO: 1@centrodelpan.com')
print('=' * 60)

try:
    user = User.objects.get(email='1@centrodelpan.com')
    print(f'✅ Usuario encontrado: {user.email}')
    
    # Buscar solicitudes de financiamiento del usuario
    requests = FinancingRequest.objects.filter(customer__user=user)
    print(f'📋 Solicitudes encontradas: {requests.count()}')
    
    current_rate = LlevoRate.get_current_rate()
    print(f'💱 Tasa LLEVO actual: {current_rate.llevo_value} VES')
    
    for req in requests:
        print(f'\n🔸 Solicitud #{req.application_number}')
        print(f'  Estado: {req.status}')
        print(f'  Producto: {req.product_name if req.product_name else N/A}')
        print(f'  Cuota LLEVO: {req.payment_amount_llevos} LLEVO')
        
        # Calcular cuota correcta en VES
        cuota_ves_correcta = req.payment_amount_llevos * current_rate.llevo_value
        print(f'  Cuota VES correcta: {cuota_ves_correcta:,.2f} VES')
        
        # Revisar campo product_price (USD legacy)
        if req.product_price:
            print(f'  Precio producto USD: {req.product_price}')
            # Posible bug: usar precio USD como si fuera LLEVO
            precio_usd_como_llevo = float(req.product_price) * current_rate.llevo_value
            print(f'  ⚠️  Si multiplica precio USD × tasa LLEVO: {precio_usd_como_llevo:,.2f} VES')
            
            # Verificar si 503390.25 coincide con algún cálculo
            if abs(precio_usd_como_llevo - 503390.25) < 100:
                print(f'  🎯 POSIBLE CAUSA ENCONTRADA!')

except User.DoesNotExist:
    print('❌ Usuario no encontrado')
except Exception as e:
    print(f'❌ Error: {e}')
