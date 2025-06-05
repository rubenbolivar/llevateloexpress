#!/usr/bin/env python3

# Script interactivo para crear motocicletas Haojue paso a paso
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')

try:
    import django
    django.setup()
    print("✅ Django configurado correctamente")
except ImportError:
    print("❌ No se pudo importar Django")
    sys.exit(1)

from products.models import Product, Category
import json

def create_haojue_motorcycles():
    print("\n=== CREANDO MOTOCICLETAS HAOJUE EN DJANGO SHELL ===\n")
    
    # Verificar categoría
    try:
        category = Category.objects.get(id='motocicletas')
        print(f"✅ Categoría encontrada: {category.name}")
    except Category.DoesNotExist:
        print("❌ Categoría 'motocicletas' no encontrada")
        return
    
    # Motocicleta 1: Haojue DL160
    print("\n1. Creando Haojue DL160...")
    dl160, created = Product.objects.update_or_create(
        name='Haojue DL160',
        defaults={
            'category': category,
            'brand': 'Haojue',
            'price': 3800,
            'image': 'products/haojue_dl160.jpg',
            'description': 'Motocicleta con enfoque de doble propósito, diseñada para versatilidad y estilo. Ofrece postura de conducción ergonómica con características modernas como frenos ABS, iluminación LED completa y tablero digital.',
            'features': json.dumps([
                'Motor monocilíndrico 162cc refrigerado por aire',
                'Potencia 14.75 HP @ 8000 RPM con 14 Nm de torque',
                'Inyección electrónica de combustible (FI)',
                'Frenos ABS de doble canal (versiones selectas)',
                'Iluminación LED completa con farola OSRAM',
                'Tablero digital moderno',
                'Neumáticos aptos para diversos terrenos',
                'Puerto USB y luces de emergencia'
            ], ensure_ascii=False),
            'specs_general': json.dumps([
                {'label': 'Marca', 'value': 'Haojue'},
                {'label': 'Modelo', 'value': 'DL160'},
                {'label': 'Año', 'value': '2024'},
                {'label': 'Tipo', 'value': 'Doble Propósito'},
                {'label': 'Peso en marcha', 'value': '148 kg'},
                {'label': 'Altura del asiento', 'value': '795 mm'},
                {'label': 'Distancia entre ejes', 'value': '1345 mm'},
                {'label': 'Dimensiones (LxAxA)', 'value': '2025 x 775 x 1195 mm'}
            ], ensure_ascii=False),
            'specs_engine': json.dumps([
                {'label': 'Tipo de motor', 'value': 'Monocilíndrico, 4 tiempos, refrigerado por aire'},
                {'label': 'Cilindrada', 'value': '162 cc'},
                {'label': 'Potencia máxima', 'value': '11 kW (14.75 HP) @ 8000 rpm'},
                {'label': 'Torque máximo', 'value': '14 Nm @ 6500 rpm'},
                {'label': 'Alimentación', 'value': 'Inyección electrónica (FI)'},
                {'label': 'Transmisión', 'value': '5 velocidades manual'},
                {'label': 'Arranque', 'value': 'Eléctrico'},
                {'label': 'Cadena de transmisión', 'value': 'D.I.D.'}
            ], ensure_ascii=False),
            'specs_comfort': json.dumps([
                {'label': 'Capacidad combustible', 'value': '13 litros'},
                {'label': 'Tecnología ESR', 'value': 'Bajo consumo de combustible'},
                {'label': 'Autonomía aproximada', 'value': '400+ km'},
                {'label': 'Puerto USB', 'value': 'Carga de dispositivos'},
                {'label': 'Luces de emergencia', 'value': 'Sistema de seguridad'},
                {'label': 'Ergonomía', 'value': 'Posición de conducción cómoda'},
                {'label': 'Tablero', 'value': 'Digital completo'}
            ], ensure_ascii=False),
            'specs_safety': json.dumps([
                {'label': 'Freno delantero', 'value': 'Disco con ABS (versiones selectas)'},
                {'label': 'Freno trasero', 'value': 'Disco con ABS (versiones selectas)'},
                {'label': 'Suspensión delantera', 'value': 'Horquilla telescópica invertida'},
                {'label': 'Suspensión trasera', 'value': 'Monoamortiguador KYB'},
                {'label': 'Neumático delantero', 'value': '100/80-17'},
                {'label': 'Neumático trasero', 'value': '130/70-17'},
                {'label': 'Iluminación', 'value': 'LED completa con farola OSRAM'},
                {'label': 'Sistema ABS', 'value': 'Doble canal (versiones selectas)'}
            ], ensure_ascii=False),
            'stock': 6,
            'featured': True
        }
    )
    print(f"{'✅ CREADO' if created else '🔄 ACTUALIZADO'}: {dl160.name} - ${dl160.price}")
    
    # Motocicleta 2: Haojue DK150
    print("\n2. Creando Haojue DK150...")
    dk150, created = Product.objects.update_or_create(
        name='Haojue DK150',
        defaults={
            'category': category,
            'brand': 'Haojue',
            'price': 3200,
            'image': 'products/haojue_dk150.jpg',
            'description': 'Motocicleta de estilo urbano que ofrece combinación de rendimiento, confort y diseño moderno para uso diario. Opción práctica y económica con motor eficiente.',
            'features': json.dumps([
                'Motor monocilíndrico 149cc refrigerado por aire',
                'Potencia 11.1 HP @ 8000 RPM eficiente',
                'Panel de instrumentos completo',
                'Neumáticos anchos sin cámara para mayor seguridad',
                'Caballete central incluido',
                'Componentes plásticos de alta calidad',
                'Arranque eléctrico y pedal',
                'Diseño urbano moderno y práctico'
            ], ensure_ascii=False),
            'specs_general': json.dumps([
                {'label': 'Marca', 'value': 'Haojue'},
                {'label': 'Modelo', 'value': 'DK150'},
                {'label': 'Año', 'value': '2024'},
                {'label': 'Tipo', 'value': 'Street / Urbana'},
                {'label': 'Peso seco', 'value': '120 kg'},
                {'label': 'Peso en marcha', 'value': '135 kg'},
                {'label': 'Altura del asiento', 'value': '760 mm'},
                {'label': 'Distancia entre ejes', 'value': '1285 mm'},
                {'label': 'Dimensiones (LxAxA)', 'value': '2020 x 755 x 1100 mm'}
            ], ensure_ascii=False),
            'specs_engine': json.dumps([
                {'label': 'Tipo de motor', 'value': 'Monocilíndrico, 4 tiempos, refrigerado por aire'},
                {'label': 'Cilindrada', 'value': '149 cc'},
                {'label': 'Potencia máxima', 'value': '8.3 kW (11.1 HP) @ 8000 rpm'},
                {'label': 'Torque máximo', 'value': '11.4 Nm (1.16 kgf.m) @ 6000 rpm'},
                {'label': 'Alimentación', 'value': 'Carburador'},
                {'label': 'Transmisión', 'value': '5 velocidades manual'},
                {'label': 'Arranque', 'value': 'Eléctrico y pedal'},
                {'label': 'Refrigeración', 'value': 'Por aire'}
            ], ensure_ascii=False),
            'specs_comfort': json.dumps([
                {'label': 'Capacidad combustible', 'value': '12.5 litros'},
                {'label': 'Consumo estimado', 'value': '45 km/l'},
                {'label': 'Autonomía aproximada', 'value': '560 km'},
                {'label': 'Caballete central', 'value': 'Facilita mantenimiento'},
                {'label': 'Panel instrumentos', 'value': 'Completo y funcional'},
                {'label': 'Ergonomía', 'value': 'Diseño cómodo para ciudad'},
                {'label': 'Calidad construcción', 'value': 'Componentes plásticos premium'}
            ], ensure_ascii=False),
            'specs_safety': json.dumps([
                {'label': 'Freno delantero', 'value': 'Disco hidráulico'},
                {'label': 'Freno trasero', 'value': 'Tambor'},
                {'label': 'Suspensión delantera', 'value': 'Horquilla telescópica hidráulica'},
                {'label': 'Suspensión trasera', 'value': 'Doble amortiguador con basculante'},
                {'label': 'Neumático delantero', 'value': '80/100-18 sin cámara'},
                {'label': 'Neumático trasero', 'value': '100/80-18 sin cámara'},
                {'label': 'Neumáticos', 'value': 'Anchos para mayor estabilidad'},
                {'label': 'Sistema frenos', 'value': 'Hidráulico delantero'}
            ], ensure_ascii=False),
            'stock': 8,
            'featured': True
        }
    )
    print(f"{'✅ CREADO' if created else '🔄 ACTUALIZADO'}: {dk150.name} - ${dk150.price}")
    
    # Motocicleta 3: Haojue HJ150-8
    print("\n3. Creando Haojue HJ150-8...")
    hj150, created = Product.objects.update_or_create(
        name='Haojue HJ150-8',
        defaults={
            'category': category,
            'brand': 'Haojue',
            'price': 3400,
            'image': 'products/haojue_hj150_8.jpg',
            'description': 'Motocicleta confiable y segura catalogada como doble propósito ligero. Destaca por ser cómoda de manejar y eficiente, ideal para quienes buscan una moto sin vibraciones excesivas.',
            'features': json.dumps([
                'Motor monocilíndrico 149cc confiable',
                'Potencia 11.13 HP @ 8000 RPM sin vibraciones',
                'Diseño doble propósito ligero',
                'Manejo cómodo y eficiente',
                'Rendimiento consistente ciudad y campo',
                'Arranque eléctrico y pedal de respaldo',
                'Construcción robusta y duradera',
                'Bajo mantenimiento'
            ], ensure_ascii=False),
            'specs_general': json.dumps([
                {'label': 'Marca', 'value': 'Haojue'},
                {'label': 'Modelo', 'value': 'HJ150-8'},
                {'label': 'Año', 'value': '2024'},
                {'label': 'Tipo', 'value': 'Doble Propósito Ligero'},
                {'label': 'Peso neto', 'value': '125 kg'},
                {'label': 'Peso en marcha', 'value': '128 kg'},
                {'label': 'Altura del asiento', 'value': '745 mm'},
                {'label': 'Distancia entre ejes', 'value': '1285 mm'},
                {'label': 'Dimensiones (LxAxA)', 'value': '1975 x 800 x 1110 mm'}
            ], ensure_ascii=False),
            'specs_engine': json.dumps([
                {'label': 'Tipo de motor', 'value': 'Monocilíndrico, 4 tiempos, refrigerado por aire'},
                {'label': 'Cilindrada', 'value': '149 cc'},
                {'label': 'Potencia máxima', 'value': '8.3 kW (11.13 HP) @ 8000 rpm'},
                {'label': 'Torque máximo', 'value': '11.4 Nm @ 6500 rpm'},
                {'label': 'Alimentación', 'value': 'Carburador'},
                {'label': 'Transmisión', 'value': '5 velocidades manual'},
                {'label': 'Arranque', 'value': 'Eléctrico y pedal'},
                {'label': 'Vibraciones', 'value': 'Mínimas gracias a diseño balanceado'}
            ], ensure_ascii=False),
            'specs_comfort': json.dumps([
                {'label': 'Capacidad combustible', 'value': '13 litros'},
                {'label': 'Consumo estimado', 'value': '42 km/l'},
                {'label': 'Autonomía aproximada', 'value': '540 km'},
                {'label': 'Comodidad manejo', 'value': 'Sin vibraciones excesivas'},
                {'label': 'Versatilidad', 'value': 'Ciudad y caminos irregulares'},
                {'label': 'Confiabilidad', 'value': 'Rendimiento consistente'},
                {'label': 'Ergonomía', 'value': 'Posición cómoda para viajes largos'}
            ], ensure_ascii=False),
            'specs_safety': json.dumps([
                {'label': 'Freno delantero', 'value': 'Disco hidráulico'},
                {'label': 'Freno trasero', 'value': 'Tambor'},
                {'label': 'Suspensión delantera', 'value': 'Horquilla telescópica'},
                {'label': 'Suspensión trasera', 'value': 'Doble amortiguador'},
                {'label': 'Neumático delantero', 'value': '2.75-18'},
                {'label': 'Neumático trasero', 'value': '110/90-16'},
                {'label': 'Estabilidad', 'value': 'Diseño equilibrado para diversos terrenos'},
                {'label': 'Durabilidad', 'value': 'Construcción robusta'}
            ], ensure_ascii=False),
            'stock': 7,
            'featured': False
        }
    )
    print(f"{'✅ CREADO' if created else '🔄 ACTUALIZADO'}: {hj150.name} - ${hj150.price}")
    
    # Motocicleta 4: Haojue NK150
    print("\n4. Creando Haojue NK150...")
    nk150, created = Product.objects.update_or_create(
        name='Haojue NK150',
        defaults={
            'category': category,
            'brand': 'Haojue',
            'price': 3600,
            'image': 'products/haojue_nk150.jpg',
            'description': 'Motocicleta doble propósito diseñada para aventura en diversos terrenos. Caracterizada por guardabarros delantero tipo "pico" para reducir resistencia al viento y proteger faros.',
            'features': json.dumps([
                'Motor monocilíndrico 150cc OHC potente',
                'Potencia 12.20 HP @ 7500 RPM para aventura',
                'Guardabarros tipo "pico" aerodinámico',
                'Tablero digital moderno',
                'Suspensión monoamortiguador central',
                'Frenos ABS delanteros (versiones FI)',
                'Neumáticos off-road 90/90-19 y 110/90-17',
                'Diseño aventurero y funcional'
            ], ensure_ascii=False),
            'specs_general': json.dumps([
                {'label': 'Marca', 'value': 'Haojue'},
                {'label': 'Modelo', 'value': 'NK150'},
                {'label': 'Año', 'value': '2024'},
                {'label': 'Tipo', 'value': 'Doble Propósito / Adventure'},
                {'label': 'Peso en marcha', 'value': '137 kg (302 lb)'},
                {'label': 'Altura del asiento', 'value': '839 mm'},
                {'label': 'Distancia entre ejes', 'value': '1360 mm'},
                {'label': 'País de origen', 'value': 'China'}
            ], ensure_ascii=False),
            'specs_engine': json.dumps([
                {'label': 'Tipo de motor', 'value': 'Monocilíndrico, 4 tiempos, OHC, refrigerado por aire'},
                {'label': 'Cilindrada', 'value': '149/150 cc'},
                {'label': 'Potencia máxima', 'value': '9.1 kW (12.20 HP) @ 7500 rpm'},
                {'label': 'Torque máximo', 'value': '12.7 Nm @ 6000 rpm'},
                {'label': 'Alimentación', 'value': 'Carburador / FI (versiones selectas)'},
                {'label': 'Transmisión', 'value': '5 velocidades manual'},
                {'label': 'Arranque', 'value': 'Eléctrico y pedal'},
                {'label': 'Sistema OHC', 'value': 'Mayor eficiencia y potencia'}
            ], ensure_ascii=False),
            'specs_comfort': json.dumps([
                {'label': 'Capacidad combustible', 'value': '12.5 litros'},
                {'label': 'Consumo estimado', 'value': '40 km/l'},
                {'label': 'Autonomía aproximada', 'value': '500 km'},
                {'label': 'Tablero digital', 'value': 'Información completa'},
                {'label': 'Guardabarros pico', 'value': 'Aerodinámica mejorada'},
                {'label': 'Protección faros', 'value': 'Diseño funcional'},
                {'label': 'Aventura', 'value': 'Capacidad multi-terreno'}
            ], ensure_ascii=False),
            'specs_safety': json.dumps([
                {'label': 'Freno delantero', 'value': 'Disco con ABS (versiones FI)'},
                {'label': 'Freno trasero', 'value': 'Tambor'},
                {'label': 'Suspensión delantera', 'value': 'Horquilla telescópica'},
                {'label': 'Suspensión trasera', 'value': 'Monoamortiguador central'},
                {'label': 'Neumático delantero', 'value': '90/90-19 off-road'},
                {'label': 'Neumático trasero', 'value': '110/90-17 off-road'},
                {'label': 'Sistema ABS', 'value': 'Delantero (versiones FI)'},
                {'label': 'Terrenos', 'value': 'Asfalto y caminos irregulares'}
            ], ensure_ascii=False),
            'stock': 5,
            'featured': False
        }
    )
    print(f"{'✅ CREADO' if created else '🔄 ACTUALIZADO'}: {nk150.name} - ${nk150.price}")
    
    # Resumen final
    print("\n=== RESUMEN DE PRODUCTOS HAOJUE ===")
    haojue_products = Product.objects.filter(brand='Haojue')
    for product in haojue_products:
        print(f"• {product.name} - ${product.price} - Stock: {product.stock} - {'⭐ Destacado' if product.featured else 'Normal'}")
    
    print(f"\n✅ Total productos Haojue creados: {haojue_products.count()}")
    print("🌐 Los productos estarán disponibles en: https://llevateloexpress.com/catalogo.html")

if __name__ == '__main__':
    create_haojue_motorcycles() 