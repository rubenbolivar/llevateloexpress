#!/usr/bin/env python3
"""
Script para poblar las fichas técnicas reales de productos de LlévateloExpress
Datos obtenidos de fuentes oficiales y especificaciones reales
"""
import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from products.models import Product

def populate_real_specs():
    print('=== POBLANDO FICHAS TÉCNICAS REALES ===')
    
    # Datos técnicos reales obtenidos de fuentes oficiales
    real_specs = {
        'Suzuki DR 650': {
            'description': 'Motocicleta dual sport legendaria, perfecta para aventuras tanto en carretera como fuera de ella. Reconocida mundialmente por su fiabilidad y versatilidad.',
            'features': [
                'Motor monocilíndrico 644cc SOHC refrigerado por aire y aceite',
                'Potencia 43 HP @ 6500 RPM con 54 Nm de torque',
                'Suspensión telescópica delantera con 260mm de recorrido',
                'Frenos de disco flotante delantero de 290mm',
                'Llantas de aleación con radios de acero inoxidable',
                'Neumáticos mixtos 90/90-21 delante y 120/90-17 atrás',
                'Arranque eléctrico con descompresión automática',
                'Carburador Mikuni BST40 de 40mm'
            ],
            'specs_general': [
                {'label': 'Marca', 'value': 'Suzuki'},
                {'label': 'Modelo', 'value': 'DR 650S'},
                {'label': 'Año', 'value': '2024'},
                {'label': 'Tipo', 'value': 'Dual Sport'},
                {'label': 'Peso en seco', 'value': '147 kg'},
                {'label': 'Altura del asiento', 'value': '885 mm (885 mm estándar / 845 mm kit bajo)'},
                {'label': 'Despeje al suelo', 'value': '265 mm'},
                {'label': 'Distancia entre ejes', 'value': '1490 mm'}
            ],
            'specs_engine': [
                {'label': 'Tipo de motor', 'value': '4 tiempos, monocilíndrico, SOHC, 4 válvulas'},
                {'label': 'Cilindrada', 'value': '644 cc'},
                {'label': 'Diámetro x Carrera', 'value': '100.0 x 82.0 mm'},
                {'label': 'Relación de compresión', 'value': '9.5:1'},
                {'label': 'Potencia máxima', 'value': '43 HP @ 6500 rpm'},
                {'label': 'Torque máximo', 'value': '54 Nm @ 5500 rpm'},
                {'label': 'Refrigeración', 'value': 'Aire y aceite (SACS)'},
                {'label': 'Alimentación', 'value': 'Carburador Mikuni BST40'}
            ],
            'specs_comfort': [
                {'label': 'Transmisión', 'value': '5 velocidades manual'},
                {'label': 'Embrague', 'value': 'Multidisco húmedo'},
                {'label': 'Arranque', 'value': 'Eléctrico'},
                {'label': 'Capacidad combustible', 'value': '13.0 litros'},
                {'label': 'Consumo estimado', 'value': '18.5 km/l'},
                {'label': 'Autonomía aproximada', 'value': '240 km'},
                {'label': 'Garantía', 'value': '12 meses'}
            ],
            'specs_safety': [
                {'label': 'Freno delantero', 'value': 'Disco flotante 290mm con pinza doble pistón'},
                {'label': 'Freno trasero', 'value': 'Disco 240mm con pinza doble pistón'},
                {'label': 'Suspensión delantera', 'value': 'Telescópica ajustable, 260mm recorrido'},
                {'label': 'Suspensión trasera', 'value': 'Link con monoamortiguador, 260mm recorrido'},
                {'label': 'Neumático delantero', 'value': '90/90-21 M/C 54S'},
                {'label': 'Neumático trasero', 'value': '120/90-17 M/C 64S'}
            ]
        },
        
        'Suzuki GN 125': {
            'description': 'Motocicleta custom clásica de 125cc, ideal para uso urbano y viajes cortos. Reconocida por su fiabilidad, bajo consumo y facilidad de mantenimiento.',
            'features': [
                'Motor monocilíndrico 124cc SOHC refrigerado por aire',
                'Potencia 12.5 HP @ 9000 RPM con 8.6 Nm de torque',
                'Diseño custom con asiento bajo a 745mm',
                'Excelente economía de combustible 35-40 km/l',
                'Transmisión de 5 velocidades suave',
                'Freno delantero de disco hidráulico',
                'Arranque eléctrico confiable',
                'Mantenimiento económico y sencillo'
            ],
            'specs_general': [
                {'label': 'Marca', 'value': 'Suzuki'},
                {'label': 'Modelo', 'value': 'GN 125'},
                {'label': 'Año', 'value': '2024'},
                {'label': 'Tipo', 'value': 'Custom / Street'},
                {'label': 'Peso en seco', 'value': '105 kg'},
                {'label': 'Altura del asiento', 'value': '745 mm'},
                {'label': 'Despeje al suelo', 'value': '175 mm'},
                {'label': 'Distancia entre ejes', 'value': '1280 mm'}
            ],
            'specs_engine': [
                {'label': 'Tipo de motor', 'value': '4 tiempos, monocilíndrico, SOHC, 2 válvulas'},
                {'label': 'Cilindrada', 'value': '124 cc'},
                {'label': 'Diámetro x Carrera', 'value': '57.0 x 48.8 mm'},
                {'label': 'Relación de compresión', 'value': '9.5:1'},
                {'label': 'Potencia máxima', 'value': '12.5 HP @ 9000 rpm'},
                {'label': 'Torque máximo', 'value': '8.6 Nm @ 7000 rpm'},
                {'label': 'Refrigeración', 'value': 'Por aire'},
                {'label': 'Alimentación', 'value': 'Carburador Mikuni BS26'}
            ],
            'specs_comfort': [
                {'label': 'Transmisión', 'value': '5 velocidades manual'},
                {'label': 'Embrague', 'value': 'Multidisco húmedo'},
                {'label': 'Arranque', 'value': 'Eléctrico'},
                {'label': 'Capacidad combustible', 'value': '10.3 litros'},
                {'label': 'Consumo estimado', 'value': '35-40 km/l'},
                {'label': 'Autonomía aproximada', 'value': '330 km'},
                {'label': 'Velocidad máxima', 'value': '110 km/h'}
            ],
            'specs_safety': [
                {'label': 'Freno delantero', 'value': 'Disco hidráulico con pinza monopistón'},
                {'label': 'Freno trasero', 'value': 'Tambor mecánico'},
                {'label': 'Suspensión delantera', 'value': 'Telescópica hidráulica'},
                {'label': 'Suspensión trasera', 'value': 'Doble amortiguador regulable'},
                {'label': 'Neumático delantero', 'value': '2.75-18 (90/90-18)'},
                {'label': 'Neumático trasero', 'value': '3.50-16 (110/90-16)'}
            ]
        },
        
        'Suzuki V-Strom 250': {
            'description': 'Adventure compacta perfecta para iniciarse en el mundo trail. Combina la versatilidad de una adventure con el manejo ágil de una moto de media cilindrada.',
            'features': [
                'Motor monocilíndrico 249cc SOHC refrigerado por aceite',
                'Potencia 26 HP @ 9300 RPM con 22.2 Nm de torque',
                'Diseño inspirado en las V-Strom mayores',
                'ABS de 2 canales de serie',
                'Neumáticos trail 110/80-19 y 140/70-17',
                'Instrumentación digital completa',
                'Parabrisas ajustable manualmente',
                'Conexiones USB para dispositivos'
            ],
            'specs_general': [
                {'label': 'Marca', 'value': 'Suzuki'},
                {'label': 'Modelo', 'value': 'V-Strom 250SX'},
                {'label': 'Año', 'value': '2024'},
                {'label': 'Tipo', 'value': 'Adventure'},
                {'label': 'Peso', 'value': '167 kg'},
                {'label': 'Altura del asiento', 'value': '835 mm'},
                {'label': 'Despeje al suelo', 'value': '205 mm'},
                {'label': 'Distancia entre ejes', 'value': '1440 mm'}
            ],
            'specs_engine': [
                {'label': 'Tipo de motor', 'value': '4 tiempos, monocilíndrico, SOHC'},
                {'label': 'Cilindrada', 'value': '249 cc'},
                {'label': 'Diámetro x Carrera', 'value': '76.0 x 54.9 mm'},
                {'label': 'Relación de compresión', 'value': '10.7:1'},
                {'label': 'Potencia máxima', 'value': '26 HP @ 9300 rpm'},
                {'label': 'Torque máximo', 'value': '22.2 Nm @ 7300 rpm'},
                {'label': 'Refrigeración', 'value': 'Por aceite'},
                {'label': 'Alimentación', 'value': 'Inyección electrónica'}
            ],
            'specs_comfort': [
                {'label': 'Transmisión', 'value': '6 velocidades manual'},
                {'label': 'Embrague', 'value': 'Multidisco húmedo'},
                {'label': 'Arranque', 'value': 'Eléctrico'},
                {'label': 'Capacidad combustible', 'value': '12 litros'},
                {'label': 'Consumo estimado', 'value': '36 km/l'},
                {'label': 'Autonomía aproximada', 'value': '430 km'},
                {'label': 'Velocidad máxima', 'value': '140 km/h'}
            ],
            'specs_safety': [
                {'label': 'Sistema ABS', 'value': 'ABS 2 canales'},
                {'label': 'Freno delantero', 'value': 'Disco único 300mm'},
                {'label': 'Freno trasero', 'value': 'Disco único 220mm'},
                {'label': 'Suspensión delantera', 'value': 'Telescópica, 120mm recorrido'},
                {'label': 'Suspensión trasera', 'value': 'Monoamortiguador, 7 posiciones'},
                {'label': 'Neumático delantero', 'value': '110/80-19 M/C 57S'},
                {'label': 'Neumático trasero', 'value': '140/70-17 M/C 66S'}
            ]
        },
        
        'Voge 525 DSX': {
            'description': 'Adventure moderna con equipamiento premium. Motor bicilíndrico potente, suspensiones KYB, frenos Nissin y pantalla de 7" con navegación.',
            'features': [
                'Motor bicilíndrico 494cc DOHC refrigerado por líquido',
                'Potencia 47.6 HP @ 8500 RPM con 44.5 Nm de torque',
                'Suspensiones KYB completamente ajustables',
                'Frenos Nissin con ABS desconectable',
                'Pantalla LCD 7" con Bluetooth y navegación',
                'Control de tracción TCS desconectable',
                'Neumáticos Metzeler Tourance sin cámara',
                'Cámara frontal HD integrada'
            ],
            'specs_general': [
                {'label': 'Marca', 'value': 'Voge'},
                {'label': 'Modelo', 'value': '525 DSX'},
                {'label': 'Año', 'value': '2025'},
                {'label': 'Tipo', 'value': 'Adventure'},
                {'label': 'Peso en seco', 'value': '190 kg'},
                {'label': 'Altura del asiento', 'value': '830 mm'},
                {'label': 'Despeje al suelo', 'value': '200 mm'},
                {'label': 'Distancia entre ejes', 'value': '1450 mm'}
            ],
            'specs_engine': [
                {'label': 'Tipo de motor', 'value': 'Bicilíndrico en línea, 4 tiempos, DOHC, 8 válvulas'},
                {'label': 'Cilindrada', 'value': '494 cc'},
                {'label': 'Diámetro x Carrera', 'value': '68 x 68 mm'},
                {'label': 'Relación de compresión', 'value': '11.5:1'},
                {'label': 'Potencia máxima', 'value': '47.6 HP @ 8500 rpm'},
                {'label': 'Torque máximo', 'value': '44.5 Nm @ 7000 rpm'},
                {'label': 'Refrigeración', 'value': 'Líquida'},
                {'label': 'Alimentación', 'value': 'Inyección electrónica'}
            ],
            'specs_comfort': [
                {'label': 'Transmisión', 'value': '6 velocidades manual'},
                {'label': 'Embrague', 'value': 'Multidisco húmedo antirrebote'},
                {'label': 'Modos de conducción', 'value': '2 modos (Estándar / Sport)'},
                {'label': 'Capacidad combustible', 'value': '16.5 litros'},
                {'label': 'Consumo estimado', 'value': '3.9 L/100km'},
                {'label': 'Autonomía aproximada', 'value': '350 km'},
                {'label': 'Garantía', 'value': '5 años'}
            ],
            'specs_safety': [
                {'label': 'Sistema ABS', 'value': 'ABS doble canal desconectable'},
                {'label': 'Control tracción', 'value': 'TCS desconectable'},
                {'label': 'Freno delantero', 'value': 'Doble disco flotante 298mm Nissin'},
                {'label': 'Freno trasero', 'value': 'Disco 240mm Nissin'},
                {'label': 'Suspensión delantera', 'value': 'Horquilla invertida KYB 41mm, 150mm recorrido'},
                {'label': 'Suspensión trasera', 'value': 'Monoamortiguador KYB con bieletas, 145mm'},
                {'label': 'Neumático delantero', 'value': '110/80-R19 Metzeler Tourance'},
                {'label': 'Neumático trasero', 'value': '150/70-R17 Metzeler Tourance'}
            ]
        }
    }
    
    # Datos básicos para modelos pendientes (se completarán después)
    pending_models = {
        'Voge 900 DSX': {
            'description': 'Adventure de gran cilindrada con tecnología avanzada y prestaciones superiores.',
            'features': [
                'Motor bicilíndrico de gran cilindrada',
                'Electrónica avanzada de serie',
                'Suspensiones premium totalmente ajustables',
                'Instrumentación digital de última generación'
            ],
            'specs_general': [
                {'label': 'Marca', 'value': 'Voge'},
                {'label': 'Modelo', 'value': '900 DSX'},
                {'label': 'Tipo', 'value': 'Adventure'},
                {'label': 'Año', 'value': '2024'}
            ],
            'specs_engine': [
                {'label': 'Disponible', 'value': 'Especificaciones completas próximamente'}
            ],
            'specs_comfort': [
                {'label': 'Disponible', 'value': 'Especificaciones completas próximamente'}
            ],
            'specs_safety': [
                {'label': 'Disponible', 'value': 'Especificaciones completas próximamente'}
            ]
        },
        
        'Voge AC 525 X': {
            'description': 'Motocicleta custom moderna con estilo clásico y tecnología contemporánea.',
            'features': [
                'Diseño custom elegante',
                'Motor eficiente y confiable',
                'Posición de manejo cómoda',
                'Equipamiento moderno'
            ],
            'specs_general': [
                {'label': 'Marca', 'value': 'Voge'},
                {'label': 'Modelo', 'value': 'AC 525 X'},
                {'label': 'Tipo', 'value': 'Custom'},
                {'label': 'Año', 'value': '2024'}
            ],
            'specs_engine': [
                {'label': 'Disponible', 'value': 'Especificaciones completas próximamente'}
            ],
            'specs_comfort': [
                {'label': 'Disponible', 'value': 'Especificaciones completas próximamente'}
            ],
            'specs_safety': [
                {'label': 'Disponible', 'value': 'Especificaciones completas próximamente'}
            ]
        },
        
        'Voge Rally 300': {
            'description': 'Adventure compacta perfecta para iniciarse en el mundo off-road y aventura.',
            'features': [
                'Motor monocilíndrico eficiente',
                'Diseño adventure compacto',
                'Manejo ágil y accesible',
                'Equipamiento trail básico'
            ],
            'specs_general': [
                {'label': 'Marca', 'value': 'Voge'},
                {'label': 'Modelo', 'value': 'Rally 300'},
                {'label': 'Tipo', 'value': 'Adventure'},
                {'label': 'Año', 'value': '2024'}
            ],
            'specs_engine': [
                {'label': 'Disponible', 'value': 'Especificaciones completas próximamente'}
            ],
            'specs_comfort': [
                {'label': 'Disponible', 'value': 'Especificaciones completas próximamente'}
            ],
            'specs_safety': [
                {'label': 'Disponible', 'value': 'Especificaciones completas próximamente'}
            ]
        },
        
        'Voge SR4': {
            'description': 'Scooter premium con tecnología avanzada y gran capacidad de carga.',
            'features': [
                'Motor eficiente y silencioso',
                'Amplio espacio de almacenamiento',
                'Instrumentación digital moderna',
                'Comodidad urbana superior'
            ],
            'specs_general': [
                {'label': 'Marca', 'value': 'Voge'},
                {'label': 'Modelo', 'value': 'SR4'},
                {'label': 'Tipo', 'value': 'Scooter'},
                {'label': 'Año', 'value': '2024'}
            ],
            'specs_engine': [
                {'label': 'Disponible', 'value': 'Especificaciones completas próximamente'}
            ],
            'specs_comfort': [
                {'label': 'Disponible', 'value': 'Especificaciones completas próximamente'}
            ],
            'specs_safety': [
                {'label': 'Disponible', 'value': 'Especificaciones completas próximamente'}
            ]
        }
    }
    
    # Combinar datos completos y pendientes
    all_specs = {**real_specs, **pending_models}
    
    updated_count = 0
    
    for product in Product.objects.all():
        if product.name in all_specs:
            spec_data = all_specs[product.name]
            
            # Actualizar descripción
            if product.description != spec_data['description']:
                product.description = spec_data['description']
                updated_count += 1
                print(f'✅ Descripción actualizada: {product.name}')
            
            # Actualizar características
            if spec_data['features']:
                product.features = json.dumps(spec_data['features'], ensure_ascii=False)
                print(f'✅ Características agregadas: {product.name} ({len(spec_data["features"])} características)')
            
            # Actualizar especificaciones técnicas por categorías
            if 'specs_general' in spec_data:
                product.specs_general = json.dumps(spec_data['specs_general'], ensure_ascii=False)
                print(f'✅ Especificaciones generales agregadas: {product.name}')
                
            if 'specs_engine' in spec_data:
                product.specs_engine = json.dumps(spec_data['specs_engine'], ensure_ascii=False)
                print(f'✅ Especificaciones del motor agregadas: {product.name}')
                
            if 'specs_comfort' in spec_data:
                product.specs_comfort = json.dumps(spec_data['specs_comfort'], ensure_ascii=False)
                print(f'✅ Especificaciones de confort agregadas: {product.name}')
                
            if 'specs_safety' in spec_data:
                product.specs_safety = json.dumps(spec_data['specs_safety'], ensure_ascii=False)
                print(f'✅ Especificaciones de seguridad agregadas: {product.name}')
            
            product.save()
            print(f'✅ Producto actualizado: {product.name}')
            
        else:
            print(f'⚠️  Producto no encontrado en datos: {product.name}')
    
    print(f'\n=== RESUMEN ===')
    print(f'Productos con fichas técnicas completas: 4/8')
    print(f'Productos con datos básicos: 4/8')
    print(f'Total productos actualizados: {updated_count}')
    print(f'\nProductos con especificaciones completas:')
    for name in real_specs.keys():
        print(f'  ✅ {name}')
    print(f'\nProductos con datos básicos (pendientes de completar):')
    for name in pending_models.keys():
        print(f'  🔄 {name}')

if __name__ == '__main__':
    populate_real_specs() 