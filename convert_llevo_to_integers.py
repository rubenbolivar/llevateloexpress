#!/usr/bin/env python
"""
Script para convertir precios LLEVO decimales a enteros
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

def convert_llevo_to_integers():
    """Convertir precios LLEVO a enteros redondeados"""
    print("🔄 Convirtiendo precios LLEVO a enteros...")
    
    products = Product.objects.filter(price_llevo__isnull=False)
    total_products = products.count()
    
    print(f"📊 Productos a convertir: {total_products}")
    
    if total_products == 0:
        print("✅ No hay productos con precios LLEVO para convertir")
        return
    
    converted = 0
    for product in products:
        try:
            if product.price_llevo:
                # Convertir a entero (el campo ya es IntegerField en la BD)
                old_price = product.price_llevo
                new_price = int(round(float(product.price_llevo)))
                
                product.price_llevo = new_price
                product.save(update_fields=['price_llevo'])
                
                print(f"✅ {product.name}: {old_price} → {new_price} LLEVO")
                converted += 1
                
        except Exception as e:
            print(f"❌ Error convirtiendo {product.name}: {e}")
    
    print(f"\n🎉 Conversión completada: {converted}/{total_products} productos convertidos")

if __name__ == '__main__':
    try:
        convert_llevo_to_integers()
    except Exception as e:
        print(f"💥 Error crítico: {e}")
        sys.exit(1)