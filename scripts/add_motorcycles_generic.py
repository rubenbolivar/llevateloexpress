#!/usr/bin/env python3
"""
Script genérico para agregar motocicletas usando Django Shell
Uso: python scripts/add_motorcycles_generic.py [archivo_json]
"""
import os
import sys
import django
import json
import argparse
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from products.models import Product, Category

class MotorcycleManager:
    def __init__(self):
        self.category = None
        self.setup_category()
    
    def setup_category(self):
        """Verificar y configurar la categoría de motocicletas"""
        try:
            self.category = Category.objects.get(id='motocicletas')
            print(f'✅ Categoría encontrada: {self.category.name}')
        except Category.DoesNotExist:
            print('❌ Error: Categoría "motocicletas" no encontrada')
            sys.exit(1)
    
    def add_motorcycle(self, motorcycle_data):
        """Agregar una motocicleta a la base de datos"""
        try:
            name = motorcycle_data['name']
            defaults = {
                'category': self.category,
                'brand': motorcycle_data['brand'],
                'price': motorcycle_data['price'],
                'image': motorcycle_data.get('image', f'products/{name.lower().replace(" ", "_")}.jpg'),
                'description': motorcycle_data['description'],
                'features': json.dumps(motorcycle_data.get('features', []), ensure_ascii=False),
                'specs_general': json.dumps(motorcycle_data.get('specs_general', []), ensure_ascii=False),
                'specs_engine': json.dumps(motorcycle_data.get('specs_engine', []), ensure_ascii=False),
                'specs_comfort': json.dumps(motorcycle_data.get('specs_comfort', []), ensure_ascii=False),
                'specs_safety': json.dumps(motorcycle_data.get('specs_safety', []), ensure_ascii=False),
                'stock': motorcycle_data.get('stock', 0),
                'featured': motorcycle_data.get('featured', False)
            }
            
            product, created = Product.objects.update_or_create(
                name=name,
                defaults=defaults
            )
            
            status = 'CREADO' if created else 'ACTUALIZADO'
            print(f'✅ {name} {status}: ${product.price} - Stock: {product.stock}')
            
            # Mostrar resumen de especificaciones
            features_count = len(motorcycle_data.get('features', []))
            specs_counts = {
                'general': len(motorcycle_data.get('specs_general', [])),
                'engine': len(motorcycle_data.get('specs_engine', [])),
                'comfort': len(motorcycle_data.get('specs_comfort', [])),
                'safety': len(motorcycle_data.get('specs_safety', []))
            }
            
            print(f'   📋 Características: {features_count} items')
            print(f'   📊 Specs General: {specs_counts["general"]} | Motor: {specs_counts["engine"]} | Confort: {specs_counts["comfort"]} | Seguridad: {specs_counts["safety"]}')
            
            return product, created
            
        except Exception as e:
            print(f'❌ Error agregando {motorcycle_data.get("name", "motocicleta")}: {str(e)}')
            return None, False
    
    def add_motorcycles_from_file(self, file_path):
        """Agregar motocicletas desde archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                motorcycles_data = json.load(f)
            
            if not isinstance(motorcycles_data, list):
                print('❌ Error: El archivo JSON debe contener una lista de motocicletas')
                return False
            
            print(f'📁 Cargando {len(motorcycles_data)} motocicletas desde {file_path}')
            
            added_count = 0
            updated_count = 0
            
            for i, motorcycle_data in enumerate(motorcycles_data, 1):
                print(f'\n{i}. Procesando {motorcycle_data.get("name", "motocicleta sin nombre")}...')
                product, created = self.add_motorcycle(motorcycle_data)
                if product:
                    if created:
                        added_count += 1
                    else:
                        updated_count += 1
            
            self.print_summary(motorcycle_data.get('brand', 'Todas las marcas'), added_count, updated_count)
            return True
            
        except FileNotFoundError:
            print(f'❌ Error: Archivo {file_path} no encontrado')
            return False
        except json.JSONDecodeError:
            print(f'❌ Error: Archivo {file_path} no es un JSON válido')
            return False
        except Exception as e:
            print(f'❌ Error procesando archivo: {str(e)}')
            return False
    
    def add_motorcycles_interactive(self):
        """Agregar motocicletas de manera interactiva"""
        print('🔧 Modo interactivo - Agregar motocicleta')
        print('Presiona Ctrl+C para cancelar en cualquier momento\n')
        
        try:
            # Datos básicos
            name = input('Nombre de la motocicleta: ').strip()
            if not name:
                print('❌ El nombre es obligatorio')
                return False
            
            brand = input('Marca: ').strip()
            if not brand:
                print('❌ La marca es obligatoria')
                return False
            
            price = input('Precio (USD): ').strip()
            try:
                price = float(price)
            except ValueError:
                print('❌ El precio debe ser un número válido')
                return False
            
            description = input('Descripción: ').strip()
            
            # Stock y featured
            stock = input('Stock disponible (0): ').strip()
            stock = int(stock) if stock else 0
            
            featured = input('¿Es producto destacado? (s/N): ').strip().lower()
            featured = featured in ['s', 'si', 'yes', 'y']
            
            motorcycle_data = {
                'name': name,
                'brand': brand,
                'price': price,
                'description': description,
                'stock': stock,
                'featured': featured,
                'features': [],
                'specs_general': [],
                'specs_engine': [],
                'specs_comfort': [],
                'specs_safety': []
            }
            
            # Agregar características opcionales
            print('\n📋 Agregar características (opcional, presiona Enter para omitir):')
            while True:
                feature = input('Característica (Enter para terminar): ').strip()
                if not feature:
                    break
                motorcycle_data['features'].append(feature)
            
            # Agregar especificaciones básicas
            print('\n📊 Agregar especificaciones básicas (opcional):')
            specs_sections = [
                ('specs_general', 'Información General'),
                ('specs_engine', 'Motor y Transmisión'),
                ('specs_comfort', 'Confort y Tecnología'),
                ('specs_safety', 'Seguridad')
            ]
            
            for section_key, section_name in specs_sections:
                print(f'\n{section_name}:')
                while True:
                    label = input(f'  Etiqueta (Enter para omitir {section_name}): ').strip()
                    if not label:
                        break
                    value = input(f'  Valor para "{label}": ').strip()
                    if value:
                        motorcycle_data[section_key].append({'label': label, 'value': value})
            
            print('\n🚀 Creando motocicleta...')
            product, created = self.add_motorcycle(motorcycle_data)
            
            if product:
                print(f'\n✅ Motocicleta {"creada" if created else "actualizada"} exitosamente!')
                return True
            else:
                print('\n❌ Error creando la motocicleta')
                return False
                
        except KeyboardInterrupt:
            print('\n\n⚠️ Operación cancelada por el usuario')
            return False
        except Exception as e:
            print(f'\n❌ Error en modo interactivo: {str(e)}')
            return False
    
    def print_summary(self, brand=None, added_count=0, updated_count=0):
        """Mostrar resumen final"""
        print(f'\n=== RESUMEN FINAL ===')
        print(f'✅ Productos CREADOS: {added_count}')
        print(f'🔄 Productos ACTUALIZADOS: {updated_count}')
        print(f'📊 Total procesados: {added_count + updated_count}')
        
        # Mostrar productos de la marca
        if brand and brand != 'Todas las marcas':
            products = Product.objects.filter(brand=brand)
            print(f'\n=== PRODUCTOS {brand.upper()} EN LA BASE DE DATOS ===')
            for product in products:
                featured_icon = '⭐' if product.featured else '📦'
                print(f'{featured_icon} {product.name} - ${product.price} - Stock: {product.stock}')
            print(f'\n📈 Total productos {brand}: {products.count()}')
        
        print('\n🌐 Los productos estarán disponibles en: https://llevateloexpress.com/catalogo.html')

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Agregar motocicletas usando Django Shell')
    parser.add_argument('file', nargs='?', help='Archivo JSON con datos de motocicletas')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Modo interactivo para agregar una motocicleta')
    parser.add_argument('--list-examples', action='store_true',
                       help='Mostrar ejemplos de estructura JSON')
    
    args = parser.parse_args()
    
    if args.list_examples:
        show_json_examples()
        return
    
    manager = MotorcycleManager()
    
    if args.interactive:
        success = manager.add_motorcycles_interactive()
    elif args.file:
        if not Path(args.file).exists():
            print(f'❌ Error: Archivo {args.file} no encontrado')
            sys.exit(1)
        success = manager.add_motorcycles_from_file(args.file)
    else:
        print('❌ Error: Debes especificar un archivo JSON o usar --interactive')
        print('Uso: python scripts/add_motorcycles_generic.py [archivo.json]')
        print('     python scripts/add_motorcycles_generic.py --interactive')
        print('     python scripts/add_motorcycles_generic.py --list-examples')
        sys.exit(1)
    
    if success:
        print('\n🎉 Proceso completado exitosamente!')
    else:
        print('\n❌ El proceso terminó con errores')
        sys.exit(1)

def show_json_examples():
    """Mostrar ejemplos de estructura JSON"""
    example = {
        "motorcycles": [
            {
                "name": "Ejemplo Moto 150",
                "brand": "MarcaEjemplo",
                "price": 3500,
                "description": "Descripción de la motocicleta ejemplo",
                "stock": 5,
                "featured": True,
                "image": "products/ejemplo_moto_150.jpg",
                "features": [
                    "Motor monocilíndrico 150cc",
                    "Frenos de disco delanteros",
                    "Tablero digital"
                ],
                "specs_general": [
                    {"label": "Marca", "value": "MarcaEjemplo"},
                    {"label": "Modelo", "value": "Ejemplo 150"},
                    {"label": "Año", "value": "2024"}
                ],
                "specs_engine": [
                    {"label": "Cilindrada", "value": "150 cc"},
                    {"label": "Potencia", "value": "12 HP"}
                ],
                "specs_comfort": [
                    {"label": "Capacidad combustible", "value": "12 litros"}
                ],
                "specs_safety": [
                    {"label": "Freno delantero", "value": "Disco"}
                ]
            }
        ]
    }
    
    print('📋 Ejemplo de estructura JSON:')
    print(json.dumps(example, indent=2, ensure_ascii=False))
    print('\n💡 Todos los campos excepto "name", "brand" y "price" son opcionales')

if __name__ == '__main__':
    main() 