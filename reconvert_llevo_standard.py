#!/usr/bin/env python
"""
Script para reconvertir precios LLEVO usando redondeo estándar
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

def reconvert_with_standard_round():
    """Reconvertir todos los precios USD a LLEVO usando redondeo estándar"""
    print("🔄 Reconvirtiendo precios USD → LLEVO con redondeo estándar...")
    
    # Verificar tasa LLEVO activa
    current_rate = LlevoRate.get_current_rate()
    if not current_rate:
        print("❌ No hay tasa LLEVO activa")
        return
    
    # Factor de conversión: USDT-VES ÷ (15 × 1.18)
    conversion_factor = current_rate.usdt_ves_rate / (15 * Decimal('1.18'))
    print(f"📊 Tasa actual: {current_rate.usdt_ves_rate} USDT-VES")
    print(f"📐 Factor de conversión: {conversion_factor}")
    
    # Obtener productos con precio USD
    products = Product.objects.filter(price__isnull=False)
    total_products = products.count()
    
    print(f"📦 Productos a reconvertir: {total_products}")
    print("=" * 80)
    
    converted = 0
    for product in products:
        try:
            if product.price:
                # Calcular precio LLEVO con redondeo estándar
                llevo_decimal = float(product.price * conversion_factor)
                old_llevo = product.price_llevo or 0
                new_llevo = round(llevo_decimal)
                
                # Actualizar precio
                product.price_llevo = new_llevo
                product.save(update_fields=['price_llevo'])
                
                # Mostrar comparación
                change_indicator = "↑" if new_llevo > old_llevo else ("↓" if new_llevo < old_llevo else "=")
                decimal_part = llevo_decimal - int(llevo_decimal)
                
                print(f"✅ {product.name}")
                print(f"   USD: ${product.price}")
                print(f"   Decimal: {llevo_decimal:.2f} (fracción: {decimal_part:.2f})")
                print(f"   Anterior: {old_llevo} LLEVO")
                print(f"   Nuevo: {new_llevo} LLEVO {change_indicator}")
                print(f"   Diferencia: {new_llevo - old_llevo:+d} LLEVO")
                
                # Explicar el redondeo
                if decimal_part >= 0.5:
                    print(f"   Redondeo: {decimal_part:.2f} ≥ 0.5 → ARRIBA")
                else:
                    print(f"   Redondeo: {decimal_part:.2f} < 0.5 → ABAJO")
                
                print("-" * 60)
                converted += 1
                
        except Exception as e:
            print(f"❌ Error con {product.name}: {e}")
    
    print("=" * 80)
    print(f"🎉 Reconversión estándar completada: {converted}/{total_products}")
    
    # Mostrar algunos ejemplos de verificación
    print("\n🔍 VERIFICACIÓN - Ejemplos de redondeo estándar:")
    examples = [
        (500, "Ejemplo $500"),
        (1000, "Ejemplo $1,000"),
        (2000, "Ejemplo $2,000"), 
        (3200, "Ejemplo $3,200"),
        (5000, "Ejemplo $5,000")
    ]
    
    for usd_price, label in examples:
        llevo_decimal = float(usd_price * conversion_factor)
        llevo_rounded = round(llevo_decimal)
        decimal_part = llevo_decimal - int(llevo_decimal)
        direction = "↑" if decimal_part >= 0.5 else "↓"
        print(f"{label}: {llevo_decimal:.2f} → {llevo_rounded} LLEVO {direction}")

if __name__ == '__main__':
    try:
        reconvert_with_standard_round()
    except Exception as e:
        print(f"💥 Error crítico: {e}")
        sys.exit(1)