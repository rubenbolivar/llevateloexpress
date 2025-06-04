#!/usr/bin/env python3
"""
Script para agregar categoría ATV y productos Loncin ATV Xwolf 700 LV y Xwolf 300
"""
import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from products.models import Product, Category

def add_atv_category_and_products():
    print('=== AGREGANDO CATEGORÍA ATV Y PRODUCTOS LONCIN ===')
    
    # Crear categoría ATV si no existe
    try:
        atv_category, created = Category.objects.get_or_create(
            id='atv',
            defaults={
                'name': 'ATV',
                'slug': 'atv',
                'description': 'Vehículos todo terreno para aventura y trabajo.',
                'icon': 'fa-motorcycle'
            }
        )
        
        if created:
            print(f'✅ Categoría ATV creada: {atv_category.name}')
        else:
            print(f'✅ Categoría ATV ya existe: {atv_category.name}')
            
    except Exception as e:
        print(f'❌ Error creando categoría ATV: {str(e)}')
        return False
    
    # Datos de los ATV Loncin
    loncin_atvs = {
        'Loncin ATV Xwolf 700 LV': {
            'price': 9500,
            'image': 'products/default.jpg',
            'description': 'ATV premium 4x4 con motor 686cc refrigerado por líquido, 47 HP, transmisión CVT, dirección asistida EPS, winch eléctrico 3000 lbs, instrumentación LCD color y máximo equipamiento para trabajo y aventura extrema.',
            'features': [
                'Motor 686cc monocilíndrico SOHC refrigerado por líquido',
                'Potencia 47 HP @ 5,500 rpm',
                'Torque 66 Nm @ 4,500 rpm',
                'Transmisión CVT P/R/N/H/L',
                'Sistema 4x4 con diferencial delantero',
                'Dirección asistida eléctrica EPS',
                'Winch eléctrico 3000 lbs incluido',
                'Instrumentación LCD multifuncional color'
            ],
            'specs_general': [
                {'label': 'Marca', 'value': 'Loncin'},
                {'label': 'Modelo', 'value': 'Xwolf 700 LV'},
                {'label': 'Año', 'value': '2024'},
                {'label': 'Tipo', 'value': 'ATV Utilitario 4x4'},
                {'label': 'Peso neto', 'value': '385 kg'},
                {'label': 'Distancia entre ejes', 'value': '1480 mm'},
                {'label': 'Altura libre suelo', 'value': '280 mm'},
                {'label': 'Dimensiones (LxAxA)', 'value': '2220 x 1180 x 1350 mm'}
            ],
            'specs_engine': [
                {'label': 'Tipo de motor', 'value': 'Monocilíndrico, SOHC, 4 tiempos, refrigerado por líquido'},
                {'label': 'Cilindrada', 'value': '686 cc'},
                {'label': 'Diámetro x Carrera', 'value': '102 x 84 mm'},
                {'label': 'Potencia máxima', 'value': '35 kW (47 HP) @ 5,500 rpm'},
                {'label': 'Torque máximo', 'value': '66 Nm @ 4,500 rpm'},
                {'label': 'Relación compresión', 'value': '9.7:1'},
                {'label': 'Alimentación', 'value': 'Inyección electrónica EFI'},
                {'label': 'Arranque', 'value': 'Eléctrico'}
            ],
            'specs_comfort': [
                {'label': 'Capacidad combustible', 'value': '25 litros'},
                {'label': 'Velocidad máxima', 'value': '100 km/h'},
                {'label': 'Instrumentación', 'value': 'LCD multifuncional color'},
                {'label': 'Dirección asistida', 'value': 'EPS eléctrica'},
                {'label': 'Asientos', 'value': 'Doble asiento con respaldo'},
                {'label': 'Conectividad', 'value': 'DC 15A + USB dual'},
                {'label': 'Winch', 'value': '3000 lbs eléctrico'},
                {'label': 'Capacidad remolque', 'value': '800 kg con bola 2 pulgadas'}
            ],
            'specs_safety': [
                {'label': 'Freno delantero', 'value': 'Disco hidráulico Ø 210mm'},
                {'label': 'Freno trasero', 'value': 'Disco hidráulico Ø 210mm'},
                {'label': 'Suspensión delantera', 'value': 'Doble brazo A, 190mm recorrido'},
                {'label': 'Suspensión trasera', 'value': 'Doble brazo A, 230mm recorrido'},
                {'label': 'Neumáticos delanteros', 'value': '25×8-12 aleación'},
                {'label': 'Neumáticos traseros', 'value': '25×10-12 aleación'},
                {'label': 'Protecciones', 'value': 'Guardabarros, protector manillar, protector inferior'},
                {'label': 'Equipamiento', 'value': 'Parrillas delanteras y traseras con cubiertas'}
            ],
            'stock': 3,
            'featured': True
        },
        
        'Loncin ATV Xwolf 300': {
            'price': 4800,
            'image': 'products/default.jpg',
            'description': 'ATV 2x4 con motor 271cc refrigerado por líquido, 22.5 HP, transmisión CVT H/L, winch eléctrico 3000 lbs, capacidad de remolque 800 kg, instrumentación digital y construcción robusta para trabajo y diversión.',
            'features': [
                'Motor 271cc monocilíndrico refrigerado por líquido',
                'Potencia 22.5 HP @ 7,000 rpm',
                'Torque 25.5 Nm @ 5,500 rpm',
                'Transmisión CVT H/L/N/R',
                'Sistema 2WD con transmisión por eje',
                'Winch eléctrico 3000 lbs incluido',
                'Capacidad vadeo 600 mm',
                'Instrumentación digital completa'
            ],
            'specs_general': [
                {'label': 'Marca', 'value': 'Loncin'},
                {'label': 'Modelo', 'value': 'Xwolf 300'},
                {'label': 'Año', 'value': '2024'},
                {'label': 'Tipo', 'value': 'ATV Utilitario 2x4'},
                {'label': 'Peso neto', 'value': '240 kg'},
                {'label': 'Distancia entre ejes', 'value': '1210 mm'},
                {'label': 'Altura libre suelo', 'value': '270 mm'},
                {'label': 'Dimensiones (LxAxA)', 'value': '1915 x 1095 x 1175 mm'}
            ],
            'specs_engine': [
                {'label': 'Tipo de motor', 'value': 'Monocilíndrico, 4 tiempos, refrigerado por líquido'},
                {'label': 'Cilindrada', 'value': '271 cc'},
                {'label': 'Diámetro x Carrera', 'value': '72.8 x 65.2 mm'},
                {'label': 'Potencia máxima', 'value': '16.8 kW (22.5 HP) @ 7,000 rpm'},
                {'label': 'Torque máximo', 'value': '25.5 Nm @ 5,500 rpm'},
                {'label': 'Relación compresión', 'value': '11:1'},
                {'label': 'Alimentación', 'value': 'Carburador'},
                {'label': 'Arranque', 'value': 'Eléctrico'}
            ],
            'specs_comfort': [
                {'label': 'Capacidad combustible', 'value': '14 litros'},
                {'label': 'Velocidad máxima', 'value': '88 km/h'},
                {'label': 'Instrumentación', 'value': 'Digital multifuncional'},
                {'label': 'Capacidad vadeo', 'value': '600 mm'},
                {'label': 'Asiento', 'value': 'Individual ergonómico'},
                {'label': 'Capacidad carga', 'value': '163 kg'},
                {'label': 'Winch', 'value': '3000 lbs eléctrico'},
                {'label': 'Capacidad remolque', 'value': '800 kg'}
            ],
            'specs_safety': [
                {'label': 'Freno delantero', 'value': 'Disco hidráulico'},
                {'label': 'Freno trasero', 'value': 'Disco hidráulico'},
                {'label': 'Suspensión delantera', 'value': 'Doble brazo A con amortiguador'},
                {'label': 'Suspensión trasera', 'value': 'Brazo oscilante con amortiguador'},
                {'label': 'Neumáticos delanteros', 'value': '24×8-12 todo terreno'},
                {'label': 'Neumáticos traseros', 'value': '24×10-12 todo terreno'},
                {'label': 'Protecciones', 'value': 'Guardabarros reforzado CAE'},
                {'label': 'Construcción', 'value': 'Chasis acero aleación soldadura robótica'}
            ],
            'stock': 4,
            'featured': True
        }
    }
    
    # Crear o actualizar cada ATV
    added_count = 0
    updated_count = 0
    
    for name, data in loncin_atvs.items():
        try:
            # Verificar si el producto ya existe
            product, created = Product.objects.update_or_create(
                name=name,
                defaults={
                    'category': atv_category,
                    'brand': 'Loncin',
                    'price': data['price'],
                    'image': data['image'],
                    'description': data['description'],
                    'features': json.dumps(data['features'], ensure_ascii=False),
                    'specs_general': json.dumps(data['specs_general'], ensure_ascii=False),
                    'specs_engine': json.dumps(data['specs_engine'], ensure_ascii=False),
                    'specs_comfort': json.dumps(data['specs_comfort'], ensure_ascii=False),
                    'specs_safety': json.dumps(data['specs_safety'], ensure_ascii=False),
                    'stock': data['stock'],
                    'featured': data['featured']
                }
            )
            
            if created:
                print(f'✅ CREADO: {name} - ${data["price"]} - Stock: {data["stock"]}')
                added_count += 1
            else:
                print(f'🔄 ACTUALIZADO: {name} - ${data["price"]} - Stock: {data["stock"]}')
                updated_count += 1
                
            # Mostrar resumen de especificaciones
            print(f'   📋 Características: {len(data["features"])} items')
            print(f'   📊 Specs General: {len(data["specs_general"])} items')
            print(f'   🔧 Specs Motor: {len(data["specs_engine"])} items')
            print(f'   🛋️ Specs Confort: {len(data["specs_comfort"])} items')
            print(f'   🛡️ Specs Seguridad: {len(data["specs_safety"])} items')
            print()
            
        except Exception as e:
            print(f'❌ ERROR con {name}: {str(e)}')
            continue
    
    print(f'\n=== RESUMEN FINAL ===')
    print(f'✅ Productos CREADOS: {added_count}')
    print(f'🔄 Productos ACTUALIZADOS: {updated_count}')
    print(f'📊 Total productos Loncin ATV nuevos: {added_count + updated_count}')
    
    # Verificar productos Loncin en la base de datos
    loncin_products = Product.objects.filter(brand='Loncin')
    print(f'\n=== PRODUCTOS LONCIN EN LA BASE DE DATOS ===')
    for product in loncin_products:
        print(f'• {product.name} - ${product.price} - Stock: {product.stock} - Destacado: {product.featured}')
    
    # Verificar categorías totales
    total_categories = Category.objects.count()
    print(f'\n=== VERIFICACIÓN DE CATEGORÍAS ===')
    print(f'📂 Total categorías: {total_categories}')
    for category in Category.objects.all():
        print(f'• {category.id}: {category.name}')
    
    print(f'\n✅ Proceso completado exitosamente!')
    print(f'🌐 Los productos estarán disponibles en: https://llevateloexpress.com/catalogo.html')
    return True

if __name__ == '__main__':
    add_atv_category_and_products() 