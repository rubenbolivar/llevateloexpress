#!/usr/bin/env python3
"""
Script para agregar motocicletas VOGE 350 AC y SR3 con especificaciones técnicas reales
"""
import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from products.models import Product, Category

def add_voge_motorcycles():
    print('=== AGREGANDO MOTOCICLETAS VOGE ===')
    
    # Verificar que existe la categoría motocicletas
    try:
        category = Category.objects.get(id='motocicletas')
        print(f'✅ Categoría encontrada: {category.name}')
    except Category.DoesNotExist:
        print('❌ Error: Categoría "motocicletas" no encontrada')
        return False
    
    # Datos de las motocicletas VOGE
    voge_motorcycles = {
        'VOGE 350 AC': {
            'price': 4200,
            'image': 'products/default.jpg',
            'description': 'Motocicleta naked retro con motor bicilíndrico de 322cc, perfecto balance entre estilo clásico y tecnología moderna. Ofrece 40.2 HP, refrigeración líquida, transmisión 6 velocidades y diseño elegante ideal para uso urbano y touring.',
            'features': [
                'Motor 322cc bicilíndrico DOHC, 8 válvulas',
                'Potencia 40.2 HP @ 10,500 rpm',
                'Torque 30 Nm @ 9,000 rpm',
                'Refrigeración líquida',
                'Transmisión 6 velocidades',
                'Inyección electrónica EFI',
                'Arranque eléctrico',
                'Iluminación LED completa'
            ],
            'specs_general': [
                {'label': 'Marca', 'value': 'VOGE'},
                {'label': 'Modelo', 'value': '350 AC'},
                {'label': 'Año', 'value': '2024'},
                {'label': 'Tipo', 'value': 'Naked Retro'},
                {'label': 'Peso en orden marcha', 'value': '165 kg'},
                {'label': 'Altura del asiento', 'value': '780 mm'},
                {'label': 'Distancia entre ejes', 'value': '1400 mm'},
                {'label': 'Dimensiones (LxAxA)', 'value': '2040 x 770 x 1070 mm'}
            ],
            'specs_engine': [
                {'label': 'Tipo de motor', 'value': 'Bicilíndrico, 4 tiempos, DOHC, 8 válvulas, refrigerado por líquido'},
                {'label': 'Cilindrada', 'value': '322 cc'},
                {'label': 'Potencia máxima', 'value': '30 kW (40.2 HP) @ 10,500 rpm'},
                {'label': 'Torque máximo', 'value': '30 Nm @ 9,000 rpm'},
                {'label': 'Relación compresión', 'value': '11.2:1'},
                {'label': 'Alimentación', 'value': 'Inyección electrónica EFI'},
                {'label': 'Transmisión', 'value': '6 velocidades'},
                {'label': 'Arranque', 'value': 'Eléctrico'}
            ],
            'specs_comfort': [
                {'label': 'Capacidad combustible', 'value': '12.5 litros'},
                {'label': 'Consumo estimado', 'value': 'Eficiente'},
                {'label': 'Batería', 'value': '12V 7AH'},
                {'label': 'Instrumentación', 'value': 'Panel digital LED 7 pulgadas'},
                {'label': 'Iluminación', 'value': 'LED completa'},
                {'label': 'Ergonomía', 'value': 'Posición cómoda retro'},
                {'label': 'Calidad construcción', 'value': 'Europea'},
                {'label': 'Estilo', 'value': 'Naked retro moderno'}
            ],
            'specs_safety': [
                {'label': 'Freno delantero', 'value': 'Disco con ABS dual canal'},
                {'label': 'Freno trasero', 'value': 'Disco con ABS dual canal'},
                {'label': 'ABS', 'value': 'Dual canal'},
                {'label': 'Suspensión delantera', 'value': 'Horquilla telescópica'},
                {'label': 'Suspensión trasera', 'value': 'Doble amortiguador'},
                {'label': 'Neumático delantero', 'value': 'Disco'},
                {'label': 'Neumático trasero', 'value': '150/60-17'},
                {'label': 'Certificación', 'value': 'Euro 5'}
            ],
            'stock': 5,
            'featured': True
        },
        
        'VOGE SR3': {
            'price': 4600,
            'image': 'products/default.jpg',
            'description': 'Scooter premium de 244cc con tecnología avanzada: ABS, TCS (control tracción), sistema Keyless, Dash Cam integrada y pantalla LCD 7 pulgadas. El scooter más completo y tecnológico de la gama VOGE para máximo confort urbano.',
            'features': [
                'Motor 244cc monocilíndrico DOHC, 4 válvulas',
                'Potencia 25.8 HP @ 8,250 rpm',
                'Torque 23 Nm @ 5,500 rpm',
                'ABS dual canal + TCS',
                'Sistema Keyless',
                'Dash Cam HD integrada',
                'Pantalla LCD 7 pulgadas',
                'Refrigeración líquida'
            ],
            'specs_general': [
                {'label': 'Marca', 'value': 'VOGE'},
                {'label': 'Modelo', 'value': 'SR3'},
                {'label': 'Año', 'value': '2024'},
                {'label': 'Tipo', 'value': 'Scooter Premium'},
                {'label': 'Peso en orden marcha', 'value': '165 kg'},
                {'label': 'Altura del asiento', 'value': '770 mm'},
                {'label': 'Distancia entre ejes', 'value': '1525 mm'},
                {'label': 'Dimensiones (LxAxA)', 'value': '2100 x 795 x 1390 mm'}
            ],
            'specs_engine': [
                {'label': 'Tipo de motor', 'value': 'Monocilíndrico, 4 tiempos, DOHC, 4 válvulas, refrigerado por líquido'},
                {'label': 'Cilindrada', 'value': '244 cc'},
                {'label': 'Potencia máxima', 'value': '19 kW (25.8 HP) @ 8,250 rpm'},
                {'label': 'Torque máximo', 'value': '23 Nm @ 5,500 rpm'},
                {'label': 'Alimentación', 'value': 'Inyección electrónica EFI'},
                {'label': 'Transmisión', 'value': 'CVT automática'},
                {'label': 'Arranque', 'value': 'Eléctrico'},
                {'label': 'Refrigeración', 'value': 'Líquida'}
            ],
            'specs_comfort': [
                {'label': 'Capacidad combustible', 'value': '14 litros'},
                {'label': 'Consumo', 'value': '35 km/l'},
                {'label': 'Velocidad máxima', 'value': '125 km/h'},
                {'label': 'Instrumentación', 'value': 'Pantalla LCD 7 pulgadas color'},
                {'label': 'Sistema Keyless', 'value': 'Proximidad smart key'},
                {'label': 'Dash Cam', 'value': 'HD 1080p integrada'},
                {'label': 'Puerto USB', 'value': 'Carga dispositivos'},
                {'label': 'Parabrisas', 'value': 'Ajustable'}
            ],
            'specs_safety': [
                {'label': 'Freno delantero', 'value': 'Doble disco Ø 260 mm con ABS'},
                {'label': 'Freno trasero', 'value': 'Disco Ø 240 mm con ABS'},
                {'label': 'ABS', 'value': 'Dual canal'},
                {'label': 'TCS', 'value': 'Control tracción desconectable'},
                {'label': 'Suspensión delantera', 'value': 'Horquilla telescópica Ø 35mm'},
                {'label': 'Suspensión trasera', 'value': 'Doble amortiguador regulable'},
                {'label': 'Neumáticos delanteros', 'value': '120/70-14'},
                {'label': 'Neumáticos traseros', 'value': '140/60-13'}
            ],
            'stock': 4,
            'featured': True
        }
    }
    
    # Crear o actualizar cada motocicleta
    added_count = 0
    updated_count = 0
    
    for name, data in voge_motorcycles.items():
        try:
            # Verificar si el producto ya existe
            product, created = Product.objects.update_or_create(
                name=name,
                defaults={
                    'category': category,
                    'brand': 'Voge',
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
    print(f'📊 Total productos VOGE nuevos: {added_count + updated_count}')
    
    # Verificar productos VOGE en la base de datos
    voge_products = Product.objects.filter(brand='Voge')
    print(f'\n=== PRODUCTOS VOGE EN LA BASE DE DATOS ===')
    for product in voge_products:
        print(f'• {product.name} - ${product.price} - Stock: {product.stock} - Destacado: {product.featured}')
    
    print(f'\n✅ Proceso completado exitosamente!')
    print(f'🌐 Los productos estarán disponibles en: https://llevateloexpress.com/catalogo.html')
    return True

if __name__ == '__main__':
    add_voge_motorcycles() 