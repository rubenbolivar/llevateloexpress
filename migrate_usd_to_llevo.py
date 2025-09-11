#!/usr/bin/env python
"""
Script para migrar precios de USD a LLEVO
Uso: python migrate_usd_to_llevo.py
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
sys.path.append('/Users/rubenbolivar/Desktop/LLevateloExpress-VPS')
django.setup()

from products.models import Product
from products.llevo_models import LlevoRate

def migrate_prices():
    """Migrar precios USD a LLEVO usando tasa actual"""
    print("🚀 Iniciando migración de precios USD → LLEVO")
    
    # Verificar si hay tasa LLEVO activa
    current_rate = LlevoRate.get_current_rate()
    if not current_rate:
        print("❌ No hay tasa LLEVO activa. Creando tasa por defecto...")
        # Crear tasa por defecto (ejemplo: USDT-VES = 40, LLEVO = 40 × 15 × 1.18 = 708)
        default_rate = LlevoRate.objects.create(
            usdt_ves_rate=Decimal('40.0'),
            notes="Tasa por defecto para migración inicial"
        )
        print(f"✅ Tasa por defecto creada: 1 LLEVO = {default_rate.llevo_value} VES")
        current_rate = default_rate
    
    # Obtener productos con precio USD
    products_with_usd = Product.objects.filter(price__isnull=False, price_llevo__isnull=True)
    total_products = products_with_usd.count()
    
    print(f"📊 Productos a migrar: {total_products}")
    print(f"📈 Tasa actual: 1 LLEVO = {current_rate.llevo_value} VES")
    
    if total_products == 0:
        print("✅ No hay productos para migrar")
        return
    
    migrated = 0
    for product in products_with_usd:
        try:
            # Convertir USD a LLEVO
            # Aproximación: 1 USD ≈ USDT, entonces LLEVO = USD × (USDT-VES / (15 × 1.18))
            conversion_factor = current_rate.usdt_ves_rate / (Decimal('15') * Decimal('1.18'))
            llevo_price = product.price * conversion_factor
            
            # Actualizar precio LLEVO
            product.price_llevo = llevo_price.quantize(Decimal('0.01'))
            product.save(update_fields=['price_llevo'])
            
            print(f"✅ {product.name}: ${product.price} USD → {product.price_llevo} LLEVO")
            migrated += 1
            
        except Exception as e:
            print(f"❌ Error migrando {product.name}: {e}")
    
    print(f"\n🎉 Migración completada: {migrated}/{total_products} productos migrados")
    print(f"💡 Los precios USD se mantienen como respaldo")

def verify_migration():
    """Verificar estado de la migración"""
    total_products = Product.objects.count()
    with_usd = Product.objects.filter(price__isnull=False).count()
    with_llevo = Product.objects.filter(price_llevo__isnull=False).count()
    
    print("\n📊 ESTADO DE LA MIGRACIÓN:")
    print(f"Total productos: {total_products}")
    print(f"Con precio USD: {with_usd}")
    print(f"Con precio LLEVO: {with_llevo}")
    print(f"Progreso: {(with_llevo/total_products)*100:.1f}%" if total_products > 0 else "No hay productos")

if __name__ == '__main__':
    try:
        migrate_prices()
        verify_migration()
    except Exception as e:
        print(f"💥 Error crítico: {e}")
        sys.exit(1)