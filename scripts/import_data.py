#!/usr/bin/env python
import os
import json
import re
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from products.models import Category, Product

def parse_js_to_json(content, variable_name):
    """Convierte una variable JS en JSON válido"""
    # Buscamos el patrón const VARIABLE_NAME = [...];
    pattern = rf'const\s+{variable_name}\s*=\s*(\[[\s\S]*?\]);'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return None
    
    # Extraemos el array
    js_array = match.group(1)
    
    # Convertimos propiedades JS a formato JSON (añadimos comillas a las claves)
    js_array = re.sub(r'(\s*)(\w+)(:)', r'\1"\2"\3', js_array)
    
    # Convertimos las comillas simples a dobles para valores string
    js_array = re.sub(r"'([^']*)'", r'"\1"', js_array)
    
    try:
        # Parseamos el JSON resultante
        return json.loads(js_array)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Problematic text: {js_array[:100]}...")
        return None

def import_categories():
    """Importa las categorías desde models.js"""
    try:
        with open('js/models.js', 'r', encoding='utf-8') as file:
            content = file.read()
            
        categories_data = parse_js_to_json(content, 'PRODUCT_CATEGORIES')
        
        if not categories_data:
            print("No se pudieron extraer las categorías de models.js")
            return False
        
        print(f"Se encontraron {len(categories_data)} categorías")
        
        for cat in categories_data:
            try:
                Category.objects.create(
                    id=cat['id'],
                    name=cat['name'],
                    slug=cat['slug'],
                    description=cat['description'],
                    icon=cat['icon']
                )
                print(f"✓ Categoría importada: {cat['name']}")
            except Exception as e:
                print(f"✗ Error al importar categoría {cat['name']}: {e}")
        
        return True
    except Exception as e:
        print(f"Error al procesar el archivo models.js: {e}")
        return False

def import_products():
    """Importa los productos desde products.js"""
    try:
        with open('js/products.js', 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Buscar el patrón window.products = [...];
        pattern = r'window\.products\s*=\s*(\[[\s\S]*?\]);'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            print("No se pudo encontrar la definición de productos en products.js")
            return False
        
        # Extraemos el array y convertimos a JSON
        js_array = match.group(1)
        # Convertimos propiedades JS a formato JSON
        js_array = re.sub(r'(\s*)(\w+)(:)', r'\1"\2"\3', js_array)
        # Convertimos comillas simples a dobles
        js_array = re.sub(r"'([^']*)'", r'"\1"', js_array)
        
        try:
            products_data = json.loads(js_array)
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON de productos: {e}")
            return False
        
        print(f"Se encontraron {len(products_data)} productos")
        
        for prod in products_data:
            try:
                # Buscar la categoría
                category = Category.objects.get(id=prod['category'])
                
                # Crear el producto
                Product.objects.create(
                    name=prod['name'],
                    category=category,
                    brand=prod['brand'],
                    price=prod['price'],
                    # Ajustamos la ruta de la imagen para que sea relativa a MEDIA_ROOT
                    image=f"products/{os.path.basename(prod['image'])}",
                    description=prod['description'],
                    features=prod['features'],
                    specs_general=prod['specs']['general'],
                    specs_engine=prod['specs']['engine'],
                    specs_comfort=prod['specs']['comfort'],
                    specs_safety=prod['specs']['safety'],
                    stock=prod['stock'],
                    featured=prod['featured']
                )
                print(f"✓ Producto importado: {prod['name']}")
            except Category.DoesNotExist:
                print(f"✗ Categoría {prod['category']} no encontrada para el producto {prod['name']}")
            except Exception as e:
                print(f"✗ Error al importar producto {prod['name']}: {e}")
        
        return True
    except Exception as e:
        print(f"Error al procesar el archivo products.js: {e}")
        return False

def import_sample_plans():
    """Importa planes de financiamiento de muestra"""
    from financing.models import FinancingPlan
    
    plans = [
        {
            'name': "Compra Programada Estándar",
            'plan_type': 'programada',
            'slug': 'compra-programada-estandar',
            'description': "Plan de compra programada con adjudicación al 45% del valor total.",
            'min_initial_percentage': 10,
            'max_initial_percentage': 15,
            'interest_rate': 5.5,
            'min_term': 6,
            'max_term': 60,
            'adjudication_percentage': 45,
            'benefits': """
            - Adjudicación al 45% del valor total
            - Entrega garantizada del vehículo o equipamiento
            - Sin revisión crediticia exhaustiva
            - Posibilidad de acumulación de puntos por pagos puntuales
            """,
            'requirements': """
            - Documento de identidad
            - Comprobante de domicilio
            - Referencias personales (2)
            - Aporte inicial del 10% al 15%
            """,
            'icon': 'fa-calendar-check',
            'is_active': True
        },
        {
            'name': "Crédito Inmediato 50-50",
            'plan_type': 'credito',
            'slug': 'credito-inmediato-50-50',
            'description': "Plan de crédito inmediato con 50% de inicial y 50% financiado.",
            'min_initial_percentage': 50,
            'max_initial_percentage': 50,
            'interest_rate': 12,
            'min_term': 6,
            'max_term': 24,
            'benefits': """
            - Entrega inmediata del vehículo o equipamiento
            - Proceso de aprobación rápido (24-48 horas)
            - Sin penalidad por pagos anticipados
            - Documentación simplificada
            """,
            'requirements': """
            - Documento de identidad
            - Comprobante de domicilio
            - Comprobante de ingresos
            - Referencias bancarias
            - Pago inicial del 50%
            """,
            'icon': 'fa-bolt',
            'is_active': True
        },
        {
            'name': "Crédito Inmediato 40-60",
            'plan_type': 'credito',
            'slug': 'credito-inmediato-40-60',
            'description': "Plan de crédito inmediato con 40% de inicial y 60% financiado.",
            'min_initial_percentage': 40,
            'max_initial_percentage': 40,
            'interest_rate': 14,
            'min_term': 12,
            'max_term': 36,
            'benefits': """
            - Entrega inmediata del vehículo o equipamiento
            - Mayor facilidad de aprobación
            - Plazos extendidos de financiamiento
            - Posibilidad de refinanciamiento
            """,
            'requirements': """
            - Documento de identidad
            - Comprobante de domicilio
            - Comprobante de ingresos
            - Referencias bancarias y personales
            - Pago inicial del 40%
            """,
            'icon': 'fa-percentage',
            'is_active': True
        },
        {
            'name': "Plan Agrícola",
            'plan_type': 'programada',
            'slug': 'plan-agricola',
            'description': "Plan especial para financiamiento de maquinaria agrícola, con condiciones adaptadas al ciclo agrícola.",
            'min_initial_percentage': 15,
            'max_initial_percentage': 20,
            'interest_rate': 6,
            'min_term': 12,
            'max_term': 48,
            'adjudication_percentage': 40,
            'benefits': """
            - Adjudicación al 40% del valor total
            - Pagos ajustados a ciclos de cosecha
            - Entrega garantizada de la maquinaria
            - Capacitación incluida para operación del equipo
            """,
            'requirements': """
            - Documento de identidad
            - Comprobante de propiedad o arrendamiento de tierras
            - Historial de producción
            - Referencias comerciales del sector
            - Aporte inicial del 15% al 20%
            """,
            'icon': 'fa-tractor',
            'is_active': True
        }
    ]
    
    for plan_data in plans:
        try:
            # Verificar si ya existe un plan con este slug
            if not FinancingPlan.objects.filter(slug=plan_data['slug']).exists():
                FinancingPlan.objects.create(**plan_data)
                print(f"✓ Plan de financiamiento importado: {plan_data['name']}")
            else:
                print(f"Plan de financiamiento ya existe: {plan_data['name']}")
        except Exception as e:
            print(f"✗ Error al importar plan {plan_data['name']}: {e}")
    
    print(f"Se importaron {len(plans)} planes de financiamiento")
    return True

if __name__ == "__main__":
    print("=== Iniciando importación de datos ===")
    
    print("\n[1/3] Importando categorías...")
    categories_imported = import_categories()
    
    if categories_imported:
        print("\n[2/3] Importando productos...")
        products_imported = import_products()
    else:
        print("\n[2/3] ✗ No se pueden importar productos sin categorías")
        products_imported = False
    
    print("\n[3/3] Importando planes de financiamiento de muestra...")
    plans_imported = import_sample_plans()
    
    print("\n=== Resumen de importación ===")
    print(f"Categorías: {'✓ Importadas' if categories_imported else '✗ Error'}")
    print(f"Productos: {'✓ Importados' if products_imported else '✗ Error'}")
    print(f"Planes de financiamiento: {'✓ Importados' if plans_imported else '✗ Error'}")
    
    print("\n¡Importación completada!") 