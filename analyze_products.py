#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/var/www/llevateloexpress')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from products.models import Category, Product
import json

def analyze_products():
    print("=" * 60)
    print("📊 ANÁLISIS COMPLETO DEL SISTEMA DE PRODUCTOS")
    print("=" * 60)
    
    # Categorías
    print("\n🏷️  CATEGORÍAS:")
    categories = Category.objects.all()
    for cat in categories:
        print(f"  • {cat.id}: {cat.name}")
        print(f"    - Slug: {cat.slug}")
        print(f"    - Descripción: {cat.description}")
        print(f"    - Icono: {cat.icon}")
        print(f"    - Productos: {cat.products.count()}")
        print()
    
    # Productos
    print("\n🏍️  PRODUCTOS:")
    products = Product.objects.all()
    for product in products:
        print(f"\n📦 {product.name} (ID: {product.id})")
        print(f"  - Categoría: {product.category.name}")
        print(f"  - Marca: {product.brand}")
        print(f"  - Precio: ${product.price}")
        print(f"  - Stock: {product.stock}")
        print(f"  - Destacado: {'✅' if product.featured else '❌'}")
        
        # Features
        if product.features:
            print(f"  - Features: {len(product.features)} características")
            for i, feature in enumerate(product.features[:3]):  # Solo las primeras 3
                print(f"    • {feature}")
            if len(product.features) > 3:
                print(f"    ... y {len(product.features) - 3} más")
        
        # Especificaciones
        specs = [
            ("General", product.specs_general),
            ("Motor", product.specs_engine),
            ("Confort", product.specs_comfort),
            ("Seguridad", product.specs_safety)
        ]
        
        for spec_name, spec_data in specs:
            if spec_data:
                print(f"  - Specs {spec_name}: {len(spec_data)} elementos")
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    analyze_products() 