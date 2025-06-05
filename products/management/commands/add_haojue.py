from django.core.management.base import BaseCommand
from products.models import Product, Category
import json

class Command(BaseCommand):
    help = 'Agregar motocicletas Haojue con especificaciones técnicas reales'
    
    def handle(self, *args, **options):
        self.stdout.write('=== AGREGANDO MOTOCICLETAS HAOJUE ===')
        
        # Verificar que existe la categoría motocicletas
        try:
            category = Category.objects.get(id='motocicletas')
            self.stdout.write(f'✅ Categoría encontrada: {category.name}')
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Error: Categoría "motocicletas" no encontrada'))
            return
        
        # Datos de las motocicletas Haojue
        haojue_motorcycles = {
            'Haojue DL160': {
                'price': 3800,
                'image': 'products/haojue_dl160.jpg',
                'description': 'Motocicleta con enfoque de doble propósito, diseñada para versatilidad y estilo. Ofrece postura de conducción ergonómica con características modernas como frenos ABS, iluminación LED completa y tablero digital. Su diseño permite conducción urbana y aventuras ligeras fuera del asfalto.',
                'features': [
                    'Motor monocilíndrico 162cc refrigerado por aire',
                    'Potencia 14.75 HP @ 8000 RPM con 14 Nm de torque',
                    'Inyección electrónica de combustible (FI)',
                    'Frenos ABS de doble canal (versiones selectas)',
                    'Iluminación LED completa con farola OSRAM',
                    'Tablero digital moderno',
                    'Neumáticos aptos para diversos terrenos',
                    'Puerto USB y luces de emergencia'
                ],
                'specs_general': [
                    {'label': 'Marca', 'value': 'Haojue'},
                    {'label': 'Modelo', 'value': 'DL160'},
                    {'label': 'Año', 'value': '2024'},
                    {'label': 'Tipo', 'value': 'Doble Propósito'},
                    {'label': 'Peso en marcha', 'value': '148 kg'},
                    {'label': 'Altura del asiento', 'value': '795 mm'},
                    {'label': 'Distancia entre ejes', 'value': '1345 mm'},
                    {'label': 'Dimensiones (LxAxA)', 'value': '2025 x 775 x 1195 mm'}
                ],
                'specs_engine': [
                    {'label': 'Tipo de motor', 'value': 'Monocilíndrico, 4 tiempos, refrigerado por aire'},
                    {'label': 'Cilindrada', 'value': '162 cc'},
                    {'label': 'Potencia máxima', 'value': '11 kW (14.75 HP) @ 8000 rpm'},
                    {'label': 'Torque máximo', 'value': '14 Nm @ 6500 rpm'},
                    {'label': 'Alimentación', 'value': 'Inyección electrónica (FI)'},
                    {'label': 'Transmisión', 'value': '5 velocidades manual'},
                    {'label': 'Arranque', 'value': 'Eléctrico'},
                    {'label': 'Cadena de transmisión', 'value': 'D.I.D.'}
                ],
                'specs_comfort': [
                    {'label': 'Capacidad combustible', 'value': '13 litros'},
                    {'label': 'Tecnología ESR', 'value': 'Bajo consumo de combustible'},
                    {'label': 'Autonomía aproximada', 'value': '400+ km'},
                    {'label': 'Puerto USB', 'value': 'Carga de dispositivos'},
                    {'label': 'Luces de emergencia', 'value': 'Sistema de seguridad'},
                    {'label': 'Ergonomía', 'value': 'Posición de conducción cómoda'},
                    {'label': 'Tablero', 'value': 'Digital completo'}
                ],
                'specs_safety': [
                    {'label': 'Freno delantero', 'value': 'Disco con ABS (versiones selectas)'},
                    {'label': 'Freno trasero', 'value': 'Disco con ABS (versiones selectas)'},
                    {'label': 'Suspensión delantera', 'value': 'Horquilla telescópica invertida'},
                    {'label': 'Suspensión trasera', 'value': 'Monoamortiguador KYB'},
                    {'label': 'Neumático delantero', 'value': '100/80-17'},
                    {'label': 'Neumático trasero', 'value': '130/70-17'},
                    {'label': 'Iluminación', 'value': 'LED completa con farola OSRAM'},
                    {'label': 'Sistema ABS', 'value': 'Doble canal (versiones selectas)'}
                ],
                'stock': 6,
                'featured': True
            },
            
            'Haojue DK150': {
                'price': 3200,
                'image': 'products/haojue_dk150.jpg',
                'description': 'Motocicleta de estilo urbano que ofrece combinación de rendimiento, confort y diseño moderno para uso diario. Opción práctica y económica con motor eficiente, panel de instrumentos completo y neumáticos anchos. Incluye caballete central para facilitar mantenimiento.',
                'features': [
                    'Motor monocilíndrico 149cc refrigerado por aire',
                    'Potencia 11.1 HP @ 8000 RPM eficiente',
                    'Panel de instrumentos completo',
                    'Neumáticos anchos sin cámara para mayor seguridad',
                    'Caballete central incluido',
                    'Componentes plásticos de alta calidad',
                    'Arranque eléctrico y pedal',
                    'Diseño urbano moderno y práctico'
                ],
                'specs_general': [
                    {'label': 'Marca', 'value': 'Haojue'},
                    {'label': 'Modelo', 'value': 'DK150'},
                    {'label': 'Año', 'value': '2024'},
                    {'label': 'Tipo', 'value': 'Street / Urbana'},
                    {'label': 'Peso seco', 'value': '120 kg'},
                    {'label': 'Peso en marcha', 'value': '135 kg'},
                    {'label': 'Altura del asiento', 'value': '760 mm'},
                    {'label': 'Distancia entre ejes', 'value': '1285 mm'},
                    {'label': 'Dimensiones (LxAxA)', 'value': '2020 x 755 x 1100 mm'}
                ],
                'specs_engine': [
                    {'label': 'Tipo de motor', 'value': 'Monocilíndrico, 4 tiempos, refrigerado por aire'},
                    {'label': 'Cilindrada', 'value': '149 cc'},
                    {'label': 'Potencia máxima', 'value': '8.3 kW (11.1 HP) @ 8000 rpm'},
                    {'label': 'Torque máximo', 'value': '11.4 Nm (1.16 kgf.m) @ 6000 rpm'},
                    {'label': 'Alimentación', 'value': 'Carburador'},
                    {'label': 'Transmisión', 'value': '5 velocidades manual'},
                    {'label': 'Arranque', 'value': 'Eléctrico y pedal'},
                    {'label': 'Refrigeración', 'value': 'Por aire'}
                ],
                'specs_comfort': [
                    {'label': 'Capacidad combustible', 'value': '12.5 litros'},
                    {'label': 'Consumo estimado', 'value': '45 km/l'},
                    {'label': 'Autonomía aproximada', 'value': '560 km'},
                    {'label': 'Caballete central', 'value': 'Facilita mantenimiento'},
                    {'label': 'Panel instrumentos', 'value': 'Completo y funcional'},
                    {'label': 'Ergonomía', 'value': 'Diseño cómodo para ciudad'},
                    {'label': 'Calidad construcción', 'value': 'Componentes plásticos premium'}
                ],
                'specs_safety': [
                    {'label': 'Freno delantero', 'value': 'Disco hidráulico'},
                    {'label': 'Freno trasero', 'value': 'Tambor'},
                    {'label': 'Suspensión delantera', 'value': 'Horquilla telescópica hidráulica'},
                    {'label': 'Suspensión trasera', 'value': 'Doble amortiguador con basculante'},
                    {'label': 'Neumático delantero', 'value': '80/100-18 sin cámara'},
                    {'label': 'Neumático trasero', 'value': '100/80-18 sin cámara'},
                    {'label': 'Neumáticos', 'value': 'Anchos para mayor estabilidad'},
                    {'label': 'Sistema frenos', 'value': 'Hidráulico delantero'}
                ],
                'stock': 8,
                'featured': True
            },
            
            'Haojue HJ150-8': {
                'price': 3400,
                'image': 'products/haojue_hj150_8.jpg',
                'description': 'Motocicleta confiable y segura catalogada como doble propósito ligero. Destaca por ser cómoda de manejar y eficiente, ideal para quienes buscan una moto sin vibraciones excesivas. Diseño funcional para rendimiento consistente tanto en ciudad como en caminos menos convencionales.',
                'features': [
                    'Motor monocilíndrico 149cc confiable',
                    'Potencia 11.13 HP @ 8000 RPM sin vibraciones',
                    'Diseño doble propósito ligero',
                    'Manejo cómodo y eficiente',
                    'Rendimiento consistente ciudad y campo',
                    'Arranque eléctrico y pedal de respaldo',
                    'Construcción robusta y duradera',
                    'Bajo mantenimiento'
                ],
                'specs_general': [
                    {'label': 'Marca', 'value': 'Haojue'},
                    {'label': 'Modelo', 'value': 'HJ150-8'},
                    {'label': 'Año', 'value': '2024'},
                    {'label': 'Tipo', 'value': 'Doble Propósito Ligero'},
                    {'label': 'Peso neto', 'value': '125 kg'},
                    {'label': 'Peso en marcha', 'value': '128 kg'},
                    {'label': 'Altura del asiento', 'value': '745 mm'},
                    {'label': 'Distancia entre ejes', 'value': '1285 mm'},
                    {'label': 'Dimensiones (LxAxA)', 'value': '1975 x 800 x 1110 mm'}
                ],
                'specs_engine': [
                    {'label': 'Tipo de motor', 'value': 'Monocilíndrico, 4 tiempos, refrigerado por aire'},
                    {'label': 'Cilindrada', 'value': '149 cc'},
                    {'label': 'Potencia máxima', 'value': '8.3 kW (11.13 HP) @ 8000 rpm'},
                    {'label': 'Torque máximo', 'value': '11.4 Nm @ 6500 rpm'},
                    {'label': 'Alimentación', 'value': 'Carburador'},
                    {'label': 'Transmisión', 'value': '5 velocidades manual'},
                    {'label': 'Arranque', 'value': 'Eléctrico y pedal'},
                    {'label': 'Vibraciones', 'value': 'Mínimas gracias a diseño balanceado'}
                ],
                'specs_comfort': [
                    {'label': 'Capacidad combustible', 'value': '13 litros'},
                    {'label': 'Consumo estimado', 'value': '42 km/l'},
                    {'label': 'Autonomía aproximada', 'value': '540 km'},
                    {'label': 'Comodidad manejo', 'value': 'Sin vibraciones excesivas'},
                    {'label': 'Versatilidad', 'value': 'Ciudad y caminos irregulares'},
                    {'label': 'Confiabilidad', 'value': 'Rendimiento consistente'},
                    {'label': 'Ergonomía', 'value': 'Posición cómoda para viajes largos'}
                ],
                'specs_safety': [
                    {'label': 'Freno delantero', 'value': 'Disco hidráulico'},
                    {'label': 'Freno trasero', 'value': 'Tambor'},
                    {'label': 'Suspensión delantera', 'value': 'Horquilla telescópica'},
                    {'label': 'Suspensión trasera', 'value': 'Doble amortiguador'},
                    {'label': 'Neumático delantero', 'value': '2.75-18'},
                    {'label': 'Neumático trasero', 'value': '110/90-16'},
                    {'label': 'Estabilidad', 'value': 'Diseño equilibrado para diversos terrenos'},
                    {'label': 'Durabilidad', 'value': 'Construcción robusta'}
                ],
                'stock': 7,
                'featured': False
            },
            
            'Haojue NK150': {
                'price': 3600,
                'image': 'products/haojue_nk150.jpg',
                'description': 'Motocicleta doble propósito diseñada para aventura en diversos terrenos. Caracterizada por guardabarros delantero tipo "pico" para reducir resistencia al viento y proteger faros. Ofrece comodidad en conducción y potencia para transitar ciudad y caminos irregulares.',
                'features': [
                    'Motor monocilíndrico 150cc OHC potente',
                    'Potencia 12.20 HP @ 7500 RPM para aventura',
                    'Guardabarros tipo "pico" aerodinámico',
                    'Tablero digital moderno',
                    'Suspensión monoamortiguador central',
                    'Frenos ABS delanteros (versiones FI)',
                    'Neumáticos off-road 90/90-19 y 110/90-17',
                    'Diseño aventurero y funcional'
                ],
                'specs_general': [
                    {'label': 'Marca', 'value': 'Haojue'},
                    {'label': 'Modelo', 'value': 'NK150'},
                    {'label': 'Año', 'value': '2024'},
                    {'label': 'Tipo', 'value': 'Doble Propósito / Adventure'},
                    {'label': 'Peso en marcha', 'value': '137 kg (302 lb)'},
                    {'label': 'Altura del asiento', 'value': '839 mm'},
                    {'label': 'Distancia entre ejes', 'value': '1360 mm'},
                    {'label': 'País de origen', 'value': 'China'}
                ],
                'specs_engine': [
                    {'label': 'Tipo de motor', 'value': 'Monocilíndrico, 4 tiempos, OHC, refrigerado por aire'},
                    {'label': 'Cilindrada', 'value': '149/150 cc'},
                    {'label': 'Potencia máxima', 'value': '9.1 kW (12.20 HP) @ 7500 rpm'},
                    {'label': 'Torque máximo', 'value': '12.7 Nm @ 6000 rpm'},
                    {'label': 'Alimentación', 'value': 'Carburador / FI (versiones selectas)'},
                    {'label': 'Transmisión', 'value': '5 velocidades manual'},
                    {'label': 'Arranque', 'value': 'Eléctrico y pedal'},
                    {'label': 'Sistema OHC', 'value': 'Mayor eficiencia y potencia'}
                ],
                'specs_comfort': [
                    {'label': 'Capacidad combustible', 'value': '12.5 litros'},
                    {'label': 'Consumo estimado', 'value': '40 km/l'},
                    {'label': 'Autonomía aproximada', 'value': '500 km'},
                    {'label': 'Tablero digital', 'value': 'Información completa'},
                    {'label': 'Guardabarros pico', 'value': 'Aerodinámica mejorada'},
                    {'label': 'Protección faros', 'value': 'Diseño funcional'},
                    {'label': 'Aventura', 'value': 'Capacidad multi-terreno'}
                ],
                'specs_safety': [
                    {'label': 'Freno delantero', 'value': 'Disco con ABS (versiones FI)'},
                    {'label': 'Freno trasero', 'value': 'Tambor'},
                    {'label': 'Suspensión delantera', 'value': 'Horquilla telescópica'},
                    {'label': 'Suspensión trasera', 'value': 'Monoamortiguador central'},
                    {'label': 'Neumático delantero', 'value': '90/90-19 off-road'},
                    {'label': 'Neumático trasero', 'value': '110/90-17 off-road'},
                    {'label': 'Sistema ABS', 'value': 'Delantero (versiones FI)'},
                    {'label': 'Terrenos', 'value': 'Asfalto y caminos irregulares'}
                ],
                'stock': 5,
                'featured': False
            }
        }
        
        # Crear o actualizar cada motocicleta
        added_count = 0
        updated_count = 0
        
        for name, data in haojue_motorcycles.items():
            try:
                # Verificar si el producto ya existe
                product, created = Product.objects.update_or_create(
                    name=name,
                    defaults={
                        'category': category,
                        'brand': 'Haojue',
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
                    self.stdout.write(f'✅ CREADO: {name} - ${data["price"]} - Stock: {data["stock"]}')
                    added_count += 1
                else:
                    self.stdout.write(f'🔄 ACTUALIZADO: {name} - ${data["price"]} - Stock: {data["stock"]}')
                    updated_count += 1
                    
                # Mostrar resumen de especificaciones
                self.stdout.write(f'   📋 Características: {len(data["features"])} items')
                self.stdout.write(f'   📊 Specs General: {len(data["specs_general"])} items')
                self.stdout.write(f'   🔧 Specs Motor: {len(data["specs_engine"])} items')
                self.stdout.write(f'   🛋️ Specs Confort: {len(data["specs_comfort"])} items')
                self.stdout.write(f'   🛡️ Specs Seguridad: {len(data["specs_safety"])} items')
                self.stdout.write('')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ ERROR con {name}: {str(e)}'))
                continue
        
        self.stdout.write('\n=== RESUMEN FINAL ===')
        self.stdout.write(f'✅ Productos CREADOS: {added_count}')
        self.stdout.write(f'🔄 Productos ACTUALIZADOS: {updated_count}')
        self.stdout.write(f'📊 Total productos Haojue: {added_count + updated_count}')
        
        # Verificar productos Haojue en la base de datos
        haojue_products = Product.objects.filter(brand='Haojue')
        self.stdout.write('\n=== PRODUCTOS HAOJUE EN LA BASE DE DATOS ===')
        for product in haojue_products:
            self.stdout.write(f'• {product.name} - ${product.price} - Stock: {product.stock} - Destacado: {product.featured}')
        
        self.stdout.write('\n✅ Proceso completado exitosamente!')
        self.stdout.write('🌐 Los productos estarán disponibles en: https://llevateloexpress.com/catalogo.html') 