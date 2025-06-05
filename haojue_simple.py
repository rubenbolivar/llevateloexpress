import os
import sys
import django
import json

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
sys.path.insert(0, os.getcwd())

try:
    django.setup()
    print('✅ Django configurado')
    
    from products.models import Product, Category
    
    # Verificar categoría
    category = Category.objects.get(id='motocicletas')
    print(f'✅ Categoría encontrada: {category.name}')
    
    # Crear Haojue DL160
    print('\n1. Creando Haojue DL160...')
    dl160, created = Product.objects.update_or_create(
        name='Haojue DL160',
        defaults={
            'category': category,
            'brand': 'Haojue',
            'price': 3800,
            'image': 'products/haojue_dl160.jpg',
            'description': 'Motocicleta con enfoque de doble propósito, diseñada para versatilidad y estilo.',
            'features': json.dumps([
                'Motor monocilíndrico 162cc refrigerado por aire',
                'Potencia 14.75 HP @ 8000 RPM',
                'Inyección electrónica de combustible (FI)',
                'Frenos ABS de doble canal',
                'Iluminación LED completa',
                'Tablero digital moderno',
                'Puerto USB y luces de emergencia'
            ], ensure_ascii=False),
            'specs_general': json.dumps([
                {'label': 'Marca', 'value': 'Haojue'},
                {'label': 'Modelo', 'value': 'DL160'},
                {'label': 'Año', 'value': '2024'},
                {'label': 'Tipo', 'value': 'Doble Propósito'},
                {'label': 'Peso en marcha', 'value': '148 kg'},
                {'label': 'Altura del asiento', 'value': '795 mm'}
            ], ensure_ascii=False),
            'specs_engine': json.dumps([
                {'label': 'Cilindrada', 'value': '162 cc'},
                {'label': 'Potencia máxima', 'value': '14.75 HP @ 8000 rpm'},
                {'label': 'Torque máximo', 'value': '14 Nm @ 6500 rpm'},
                {'label': 'Alimentación', 'value': 'Inyección electrónica (FI)'},
                {'label': 'Transmisión', 'value': '5 velocidades manual'}
            ], ensure_ascii=False),
            'specs_comfort': json.dumps([
                {'label': 'Capacidad combustible', 'value': '13 litros'},
                {'label': 'Autonomía aproximada', 'value': '400+ km'},
                {'label': 'Puerto USB', 'value': 'Carga de dispositivos'},
                {'label': 'Tablero', 'value': 'Digital completo'}
            ], ensure_ascii=False),
            'specs_safety': json.dumps([
                {'label': 'Freno delantero', 'value': 'Disco con ABS'},
                {'label': 'Freno trasero', 'value': 'Disco con ABS'},
                {'label': 'Suspensión delantera', 'value': 'Horquilla telescópica invertida'},
                {'label': 'Neumático delantero', 'value': '100/80-17'},
                {'label': 'Iluminación', 'value': 'LED completa'}
            ], ensure_ascii=False),
            'stock': 6,
            'featured': True
        }
    )
    status = 'CREADO' if created else 'ACTUALIZADO'
    print(f'✅ DL160 {status}: ${dl160.price}')
    
    print('\n=== RESUMEN ===')
    haojue_products = Product.objects.filter(brand='Haojue')
    for product in haojue_products:
        print(f'• {product.name} - ${product.price}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc() 