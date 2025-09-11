#!/usr/bin/env python
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from products.llevo_models import LlevoRate
from financing.models import FinancingRequest
from products.models import Product
from decimal import Decimal

print('🔍 DIAGNÓSTICO DEL CÁLCULO LLEVO → VES en Pago R4')
print('=' * 60)

# 1. Verificar tasa LLEVO actual
current_rate = LlevoRate.get_current_rate()
if current_rate:
    print(f'✅ Tasa LLEVO actual: {current_rate.llevo_value} VES')
    print(f'📊 USDT-VES base: {current_rate.usdt_ves_rate}')
    print(f'🧮 Cálculo: {current_rate.usdt_ves_rate} × 15 × 1.18 = {current_rate.llevo_value}')
    print(f'📅 Creada: {current_rate.created_at}')
else:
    print('❌ NO HAY TASA LLEVO ACTIVA')
    sys.exit(1)

print('\n' + '=' * 60)

# 2. Revisar un producto ejemplo
product = Product.objects.filter(price_llevo__isnull=False).first()
if product:
    print(f'📦 Producto ejemplo: {product.name}')
    print(f'💰 Precio LLEVO: {product.price_llevo} LLEVO')
    print(f'🏦 Inicial LLEVO: {product.inicial_llevos} LLEVO')
    print(f'💳 Cuota mensual: {product.cuota_mensual_llevos} LLEVO')
    
    # Calcular equivalencias en VES
    precio_ves = product.price_llevo * current_rate.llevo_value
    inicial_ves = product.inicial_llevos * current_rate.llevo_value
    cuota_ves = product.cuota_mensual_llevos * current_rate.llevo_value
    
    print(f'\n🔄 CONVERSIONES A VES:')
    print(f'Precio total: {product.price_llevo} LLEVO = {precio_ves:,.2f} VES')
    print(f'Inicial: {product.inicial_llevos} LLEVO = {inicial_ves:,.2f} VES')
    print(f'Cuota mensual: {product.cuota_mensual_llevos} LLEVO = {cuota_ves:,.2f} VES')

print('\n' + '=' * 60)

# 3. Revisar solicitudes de financiamiento
requests = FinancingRequest.objects.filter(payment_amount_llevos__isnull=False)[:3]
if requests:
    print(f'📋 Revisando {len(requests)} solicitudes de financiamiento:')
    for req in requests:
        print(f'\n🔸 Solicitud #{req.application_number}')
        print(f'  Cuota LLEVO: {req.payment_amount_llevos} LLEVO')
        cuota_ves_calculada = req.payment_amount_llevos * current_rate.llevo_value
        print(f'  Cuota VES calculada: {cuota_ves_calculada:,.2f} VES')
        
        # Revisar si hay un campo VES almacenado
        if hasattr(req, 'payment_amount_ves') and req.payment_amount_ves:
            print(f'  Cuota VES almacenada: {req.payment_amount_ves:,.2f} VES')
            diferencia = abs(cuota_ves_calculada - float(req.payment_amount_ves))
            if diferencia > 1:
                print(f'  ⚠️  DIFERENCIA: {diferencia:,.2f} VES')
        else:
            print(f'  ℹ️  No hay valor VES almacenado')

print('\n' + '=' * 60)
print('🎯 DIAGNÓSTICO COMPLETADO')
