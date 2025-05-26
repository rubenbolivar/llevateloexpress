#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django
import json
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from products.models import Category, Product
from financing.models import FinancingPlan

def clean_text_for_latin1(text):
    """Limpia el texto manteniendo los caracteres latinos correctamente"""
    if isinstance(text, str):
        # Asegurar que el texto esté correctamente codificado
        return text.encode('latin-1', 'ignore').decode('latin-1')
    return text

def clean_json_for_latin1(data):
    """Limpia datos JSON para compatibilidad con LATIN1"""
    if isinstance(data, list):
        return [clean_json_for_latin1(item) for item in data]
    elif isinstance(data, dict):
        return {k: clean_json_for_latin1(v) for k, v in data.items()}
    elif isinstance(data, str):
        return clean_text_for_latin1(data)
    else:
        return data

def import_categories():
    """Importa las categorías que están en el frontend"""
    print("\n=== Importando Categorías ===")
    
    categories = [
        {
            'id': 'motocicletas',
            'name': 'Motocicletas',
            'slug': 'motocicletas',
            'description': 'Desde modelos económicos hasta deportivos de alta gama.',
            'icon': 'fa-motorcycle'
        },
        {
            'id': 'vehiculos',
            'name': 'Vehículos',
            'slug': 'vehiculos',
            'description': 'Autos, camionetas y vehículos comerciales de las mejores marcas.',
            'icon': 'fa-car'
        },
        {
            'id': 'maquinaria',
            'name': 'Maquinaria Agrícola',
            'slug': 'maquinaria-agricola',
            'description': 'Tractores y equipos para optimizar tu producción agrícola.',
            'icon': 'fa-tractor'
        },
        {
            'id': 'camiones',
            'name': 'Camiones',
            'slug': 'camiones',
            'description': 'Camiones de carga, transporte y distribución de distintas capacidades.',
            'icon': 'fa-truck'
        },
        {
            'id': 'equipos',
            'name': 'Maquinaria y Equipos',
            'slug': 'maquinaria-equipos',
            'description': 'Equipamiento especializado para la industria y el comercio.',
            'icon': 'fa-cogs'
        }
    ]
    
    for cat_data in categories:
        try:
            category, created = Category.objects.update_or_create(
                id=cat_data['id'],
                defaults={
                    'name': cat_data['name'],
                    'slug': cat_data['slug'],
                    'description': cat_data['description'],
                    'icon': cat_data['icon']
                }
            )
            if created:
                print(f"[OK] Categoría creada: {category.name}")
            else:
                print(f"[OK] Categoría actualizada: {category.name}")
        except Exception as e:
            print(f"[ERROR] Error con categoría {cat_data['name']}: {e}")
    
    return True

def import_products():
    """Importa los productos que están en el frontend"""
    print("\n=== Importando Productos ===")
    
    # Lista de productos del frontend
    products_data = [
        {
            'name': "Voge Rally 300",
            'category': "motocicletas",
            'brand': "Voge",
            'price': 4500,
            'image': "products/300.jpg",
            'description': "La Voge Rally 300 es una motocicleta de aventura ligera que combina versatilidad y rendimiento. Perfecta para quienes buscan una moto capaz tanto en ciudad como en caminos de tierra.",
            'features': [
                "Motor monocilíndrico de 292cc refrigerado por líquido",
                "Potencia máxima de 29 HP a 8500 rpm",
                "Transmisión de 6 velocidades",
                "Frenos de disco con ABS desconectable",
                "Suspensión invertida ajustable",
                "Panel de instrumentos TFT a color",
                "Iluminación full LED",
                "Capacidad de tanque: 16 litros"
            ],
            'specs_general': [
                {"label": "Marca", "value": "Voge"},
                {"label": "Modelo", "value": "Rally 300"},
                {"label": "Año", "value": "2023"},
                {"label": "Tipo", "value": "Adventure"},
                {"label": "País de Origen", "value": "China"},
                {"label": "Garantía", "value": "2 años o 20,000 km"},
                {"label": "Colores disponibles", "value": "Negro, Rojo, Gris"},
                {"label": "Peso", "value": "178 kg"}
            ],
            'specs_engine': [
                {"label": "Tipo de motor", "value": "Monocilíndrico 4T, DOHC, 4 válvulas"},
                {"label": "Cilindrada", "value": "292 cc"},
                {"label": "Potencia máxima", "value": "29 HP a 8500 rpm"},
                {"label": "Torque máximo", "value": "25.3 Nm a 6500 rpm"},
                {"label": "Transmisión", "value": "6 velocidades"},
                {"label": "Sistema de refrigeración", "value": "Líquido"},
                {"label": "Capacidad de tanque", "value": "16 litros"},
                {"label": "Consumo promedio", "value": "3.3 L/100km"}
            ],
            'specs_comfort': [
                {"label": "Asiento", "value": "Doble altura, ergonómico"},
                {"label": "Altura del asiento", "value": "825 mm"},
                {"label": "Panel de instrumentos", "value": "TFT a color de 5 pulgadas"},
                {"label": "Iluminación", "value": "Full LED"},
                {"label": "USB", "value": "Sí, puerto cargador 2.1A"},
                {"label": "Posición de manejo", "value": "Adventure, semi-erguida"},
                {"label": "Capacidad de carga", "value": "12 kg"},
                {"label": "Parabrisas", "value": "Ajustable 3 posiciones"}
            ],
            'specs_safety': [
                {"label": "Freno delantero", "value": "Disco 300mm, pinza de 4 pistones, ABS"},
                {"label": "Freno trasero", "value": "Disco 240mm, pinza de 1 pistón, ABS"},
                {"label": "Sistema de frenos", "value": "Hidráulico, doble disco, ABS desconectable"},
                {"label": "ABS", "value": "Bosch 9.1 MB, desconectable"},
                {"label": "Control de tracción", "value": "No disponible"},
                {"label": "Suspensión delantera", "value": "Horquilla invertida 41mm, ajustable"},
                {"label": "Suspensión trasera", "value": "Monoamortiguador con depósito separado"},
                {"label": "Tipo de suspensión", "value": "Invertida delantera, monoamortiguador trasero"},
                {"label": "Recorrido suspensiones", "value": "160mm delantero / 150mm trasero"}
            ],
            'stock': 8,
            'featured': True
        },
        {
            'name': "Voge 525 DSX",
            'category': "motocicletas",
            'brand': "Voge",
            'price': 6800,
            'image': "products/525dsx.jpg",
            'description': "La Voge 525 DSX es una motocicleta trail de media cilindrada que ofrece excelentes prestaciones para aventuras on/off-road. Su diseño moderno y equipamiento premium la hacen destacar en su segmento.",
            'features': [
                "Motor bicilíndrico en línea de 494cc",
                "Potencia de 46.2 HP a 8500 rpm",
                "Transmisión de 6 velocidades",
                "Sistema de frenos ABS Bosch de doble canal",
                "Suspensión KYB totalmente ajustable",
                "Pantalla TFT de 7 pulgadas",
                "Modos de conducción",
                "Control de tracción"
            ],
            'specs_general': [
                {"label": "Marca", "value": "Voge"},
                {"label": "Modelo", "value": "525 DSX"},
                {"label": "Año", "value": "2023"},
                {"label": "Tipo", "value": "Trail Adventure"},
                {"label": "País de Origen", "value": "China"}
            ],
            'specs_engine': [
                {"label": "Tipo de motor", "value": "Bicilíndrico en línea, 4T, DOHC, 8 válvulas"},
                {"label": "Cilindrada", "value": "494 cc"},
                {"label": "Potencia máxima", "value": "46.2 HP a 8500 rpm"}
            ],
            'specs_comfort': [
                {"label": "Asiento", "value": "Ergonómico, tapizado antideslizante"},
                {"label": "Altura del asiento", "value": "840 mm"},
                {"label": "Panel de instrumentos", "value": "TFT a color de 7 pulgadas"}
            ],
            'specs_safety': [
                {"label": "Freno delantero", "value": "Doble disco 320mm, pinzas radiales de 4 pistones"},
                {"label": "Freno trasero", "value": "Disco 260mm, pinza flotante de 2 pistones"},
                {"label": "ABS", "value": "Bosch 9.1 MB, modos Road/Off-road"}
            ],
            'stock': 5,
            'featured': True
        },
        {
            'name': "Voge AC 525 X",
            'category': "motocicletas",
            'brand': "Voge",
            'price': 7200,
            'image': "products/ac525.jpg",
            'description': "La Voge AC 525 X representa la evolución en el segmento adventure touring. Con su diseño sofisticado y tecnología avanzada, ofrece el equilibrio perfecto entre confort y capacidad todoterreno.",
            'features': [
                "Motor bicilíndrico de 494cc refrigerado por líquido",
                "48 HP de potencia máxima",
                "Transmisión de 6 velocidades con embrague anti-rebote",
                "Sistema de frenos ABS Bosch con modo off-road",
                "Suspensión KYB con recorrido extendido",
                "Pantalla TFT con conectividad bluetooth",
                "Control de crucero",
                "Protectores de motor y manos incluidos"
            ],
            'specs_general': [
                {"label": "Marca", "value": "Voge"},
                {"label": "Modelo", "value": "AC 525 X"},
                {"label": "Año", "value": "2023"},
                {"label": "Tipo", "value": "Adventure Touring"},
                {"label": "País de Origen", "value": "China"}
            ],
            'specs_engine': [
                {"label": "Tipo de motor", "value": "Bicilíndrico en línea, 4T, DOHC, 8 válvulas"},
                {"label": "Cilindrada", "value": "494 cc"},
                {"label": "Potencia máxima", "value": "48 HP a 8750 rpm"}
            ],
            'specs_comfort': [
                {"label": "Asiento", "value": "Touring, altura ajustable 830-850 mm"},
                {"label": "Altura del asiento", "value": "830-850 mm (ajustable)"},
                {"label": "Panel de instrumentos", "value": "TFT a color de 7 pulgadas con conectividad bluetooth"}
            ],
            'specs_safety': [
                {"label": "Freno delantero", "value": "Doble disco 320mm, pinzas Brembo monobloque de 4 pistones"},
                {"label": "Freno trasero", "value": "Disco 260mm, pinza Brembo de 2 pistones"},
                {"label": "ABS", "value": "Bosch 9.3 MP, modos Road/Off-road/Desconectable"}
            ],
            'stock': 6,
            'featured': True
        },
        {
            'name': "Suzuki DR 650",
            'category': "motocicletas",
            'brand': "Suzuki",
            'price': 8500,
            'image': "products/dr650.jpg",
            'description': "La legendaria Suzuki DR 650 es sinónimo de confiabilidad y versatilidad. Una moto dual-purpose que ha probado su valor tanto en largas travesías como en el uso diario.",
            'features': [
                "Motor monocilíndrico SOHC de 644cc refrigerado por aire",
                "Potencia de 46 HP",
                "Transmisión de 5 velocidades",
                "Freno de disco delantero y trasero",
                "Suspensión de largo recorrido",
                "Altura de asiento ajustable",
                "Peso en seco de 166 kg",
                "Tanque de combustible de 13 litros"
            ],
            'specs_general': [
                {"label": "Marca", "value": "Suzuki"},
                {"label": "Modelo", "value": "DR 650"},
                {"label": "Año", "value": "2023"},
                {"label": "Tipo", "value": "Dual Purpose"},
                {"label": "País de Origen", "value": "Japón"}
            ],
            'specs_engine': [
                {"label": "Tipo de motor", "value": "Monocilíndrico SOHC, 4T, 4 válvulas"},
                {"label": "Cilindrada", "value": "644 cc"},
                {"label": "Potencia máxima", "value": "46 HP a 6400 rpm"}
            ],
            'specs_comfort': [
                {"label": "Altura del asiento", "value": "840-870 mm (ajustable)"},
                {"label": "Panel de instrumentos", "value": "Analógico"}
            ],
            'specs_safety': [
                {"label": "Freno delantero", "value": "Disco 290mm, pinza de 2 pistones"},
                {"label": "Freno trasero", "value": "Disco 240mm, pinza de 1 pistón"},
                {"label": "ABS", "value": "No disponible"}
            ],
            'stock': 4,
            'featured': True
        },
        {
            'name': "Suzuki GN 125",
            'category': "motocicletas",
            'brand': "Suzuki",
            'price': 2200,
            'image': "products/gn125.jpg",
            'description': "La Suzuki GN 125 es una motocicleta clásica ideal para principiantes y uso urbano. Su diseño atemporal, bajo consumo y fácil mantenimiento la han convertido en un referente de su categoría.",
            'features': [
                "Motor monocilíndrico de 124cc refrigerado por aire",
                "Potencia de 12.5 HP a 9500 rpm",
                "Transmisión de 5 velocidades",
                "Freno de disco delantero y tambor trasero",
                "Arranque eléctrico y por patada",
                "Consumo aproximado de 2.2L/100km",
                "Peso en orden de marcha: 113 kg",
                "Capacidad de tanque: 10.5 litros"
            ],
            'specs_general': [
                {"label": "Marca", "value": "Suzuki"},
                {"label": "Modelo", "value": "GN 125"},
                {"label": "Año", "value": "2023"},
                {"label": "Tipo", "value": "Street / Commuter"},
                {"label": "País de Origen", "value": "Japón"}
            ],
            'specs_engine': [
                {"label": "Tipo de motor", "value": "Monocilíndrico, 4T, SOHC, 2 válvulas"},
                {"label": "Cilindrada", "value": "124 cc"},
                {"label": "Potencia máxima", "value": "12.5 HP a 9500 rpm"}
            ],
            'specs_comfort': [
                {"label": "Asiento", "value": "Biplaza, estilo clásico"},
                {"label": "Altura del asiento", "value": "770 mm"},
                {"label": "Panel de instrumentos", "value": "Analógico, velocímetro y tacómetro"}
            ],
            'specs_safety': [
                {"label": "Freno delantero", "value": "Disco 240mm, pinza de 2 pistones"},
                {"label": "Freno trasero", "value": "Tambor 130mm"},
                {"label": "Sistema de frenos", "value": "Hidráulico delantero, mecánico trasero"}
            ],
            'stock': 12,
            'featured': True
        },
        {
            'name': "Voge SR4",
            'category': "motocicletas",
            'brand': "Voge",
            'price': 5500,
            'image': "products/sr4.jpg",
            'description': "La Voge SR4 es una motocicleta deportiva que combina estilo y rendimiento. Su diseño moderno y tecnología avanzada la convierten en una opción atractiva para los amantes de las motos deportivas.",
            'features': [
                "Motor bicilíndrico en línea de 350cc",
                "Potencia de 42.5 HP a 9000 rpm",
                "Transmisión de 6 velocidades",
                "Sistema de frenos ABS de doble canal",
                "Suspensión invertida ajustable",
                "Pantalla TFT a color",
                "Iluminación full LED",
                "Modos de conducción seleccionables"
            ],
            'specs_general': [
                {"label": "Marca", "value": "Voge"},
                {"label": "Modelo", "value": "SR4"},
                {"label": "Año", "value": "2023"},
                {"label": "Tipo", "value": "Sport"},
                {"label": "País de Origen", "value": "China"}
            ],
            'specs_engine': [
                {"label": "Tipo de motor", "value": "Bicilíndrico en línea, 4T, DOHC, 8 válvulas"},
                {"label": "Cilindrada", "value": "350 cc"},
                {"label": "Potencia máxima", "value": "42.5 HP a 9000 rpm"}
            ],
            'specs_comfort': [
                {"label": "Asiento", "value": "Deportivo biplaza"},
                {"label": "Altura del asiento", "value": "810 mm"},
                {"label": "Panel de instrumentos", "value": "TFT a color de 5 pulgadas"}
            ],
            'specs_safety': [
                {"label": "Freno delantero", "value": "Doble disco 300mm, pinzas radiales de 4 pistones"},
                {"label": "Freno trasero", "value": "Disco 240mm, pinza flotante de 1 pistón"},
                {"label": "ABS", "value": "Bosch 9.1 MB, doble canal"}
            ],
            'stock': 7,
            'featured': True
        },
        {
            'name': "Suzuki V-Strom 250",
            'category': "motocicletas",
            'brand': "Suzuki",
            'price': 5800,
            'image': "products/vstrom.jpg",
            'description': "La Suzuki V-Strom 250 es una aventurera ligera que hereda el ADN de la familia V-Strom. Perfecta para iniciarse en el mundo adventure, ofrece comodidad y versatilidad en un paquete accesible.",
            'features': [
                "Motor bicilíndrico paralelo de 248cc",
                "Potencia de 25 HP a 8000 rpm",
                "Transmisión de 6 velocidades",
                "Sistema ABS de serie",
                "Suspensión telescópica delantera",
                "Panel LCD multifunción",
                "Parabrisas ajustable",
                "Capacidad de tanque: 17.3 litros"
            ],
            'specs_general': [
                {"label": "Marca", "value": "Suzuki"},
                {"label": "Modelo", "value": "V-Strom 250"},
                {"label": "Año", "value": "2023"},
                {"label": "Tipo", "value": "Adventure"},
                {"label": "País de Origen", "value": "Japón"}
            ],
            'specs_engine': [
                {"label": "Tipo de motor", "value": "Bicilíndrico paralelo, 4T, SOHC, 4 válvulas"},
                {"label": "Cilindrada", "value": "248 cc"},
                {"label": "Potencia máxima", "value": "25 HP a 8000 rpm"}
            ],
            'specs_comfort': [
                {"label": "Asiento", "value": "Biplaza escalonado"},
                {"label": "Altura del asiento", "value": "800 mm"},
                {"label": "Panel de instrumentos", "value": "LCD multifunción"}
            ],
            'specs_safety': [
                {"label": "Freno delantero", "value": "Disco 290mm, pinza de 2 pistones"},
                {"label": "Freno trasero", "value": "Disco 240mm, pinza de 1 pistón"},
                {"label": "ABS", "value": "Bosch, doble canal"}
            ],
            'stock': 9,
            'featured': True
        }
    ]
    
    for prod_data in products_data:
        try:
            # Obtener la categoría
            category = Category.objects.get(id=prod_data['category'])
            
            # Limpiar los datos para LATIN1
            clean_data = {
                'category': category,
                'brand': clean_text_for_latin1(prod_data['brand']),
                'price': Decimal(str(prod_data['price'])),
                'image': prod_data['image'],
                'description': clean_text_for_latin1(prod_data['description']),
                'features': json.dumps(clean_json_for_latin1(prod_data['features']), ensure_ascii=False),
                'specs_general': json.dumps(clean_json_for_latin1(prod_data['specs_general']), ensure_ascii=False),
                'specs_engine': json.dumps(clean_json_for_latin1(prod_data['specs_engine']), ensure_ascii=False),
                'specs_comfort': json.dumps(clean_json_for_latin1(prod_data['specs_comfort']), ensure_ascii=False),
                'specs_safety': json.dumps(clean_json_for_latin1(prod_data['specs_safety']), ensure_ascii=False),
                'stock': prod_data['stock'],
                'featured': prod_data['featured']
            }
            
            # Crear o actualizar el producto
            product, created = Product.objects.update_or_create(
                name=clean_text_for_latin1(prod_data['name']),
                defaults=clean_data
            )
            
            if created:
                print(f"[OK] Producto creado: {product.name}")
            else:
                print(f"[OK] Producto actualizado: {product.name}")
                
        except Category.DoesNotExist:
            print(f"[ERROR] Error: Categoría '{prod_data['category']}' no encontrada para {prod_data['name']}")
        except Exception as e:
            print(f"[ERROR] Error con producto {prod_data['name']}: {e}")
            import traceback
            traceback.print_exc()
    
    return True

def import_financing_plans():
    """Importa planes de financiamiento básicos"""
    print("\n=== Importando Planes de Financiamiento ===")
    
    plans = [
        {
            'name': "Plan 50-50",
            'plan_type': 'credito',
            'slug': 'plan-50-50',
            'description': "Paga el 50% de inicial y financia el resto a 12 meses sin intereses.",
            'min_initial_percentage': 50,
            'max_initial_percentage': 50,
            'interest_rate': 0,
            'min_term': 12,
            'max_term': 12,
            'benefits': "Sin intereses, entrega inmediata, proceso rápido",
            'requirements': "Documento de identidad, comprobante de ingresos",
            'icon': 'fa-percentage',
            'is_active': True
        },
        {
            'name': "Plan 70-30",
            'plan_type': 'credito',
            'slug': 'plan-70-30',
            'description': "Financia el 70% del valor con una inicial del 30%.",
            'min_initial_percentage': 30,
            'max_initial_percentage': 30,
            'interest_rate': 12,
            'min_term': 6,
            'max_term': 24,
            'benefits': "Mayor financiamiento, cuotas flexibles",
            'requirements': "Documento de identidad, comprobante de ingresos, referencias",
            'icon': 'fa-chart-line',
            'is_active': True
        },
        {
            'name': "Compra Programada",
            'plan_type': 'programada',
            'slug': 'compra-programada',
            'description': "Adjudicación al 45% del valor total del vehículo.",
            'min_initial_percentage': 10,
            'max_initial_percentage': 20,
            'interest_rate': 8,
            'min_term': 12,
            'max_term': 60,
            'adjudication_percentage': 45,
            'benefits': "Menor inicial, plazos largos, adjudicación garantizada",
            'requirements': "Documento de identidad, referencias personales",
            'icon': 'fa-calendar-check',
            'is_active': True
        }
    ]
    
    for plan_data in plans:
        try:
            # Limpiar datos para LATIN1
            clean_data = {}
            for key, value in plan_data.items():
                if isinstance(value, str):
                    clean_data[key] = clean_text_for_latin1(value)
                else:
                    clean_data[key] = value
            
            plan, created = FinancingPlan.objects.update_or_create(
                slug=clean_data['slug'],
                defaults=clean_data
            )
            
            if created:
                print(f"[OK] Plan creado: {plan.name}")
            else:
                print(f"[OK] Plan actualizado: {plan.name}")
                
        except Exception as e:
            print(f"[ERROR] Error con plan {plan_data['name']}: {e}")
    
    return True

def main():
    """Función principal"""
    print("=== Importación de Datos del Frontend (Compatible con LATIN1) ===")
    print("Este script importará las categorías y productos del frontend al admin de Django")
    print("Manteniendo correctamente los acentos y caracteres especiales del español")
    
    # Importar categorías
    categories_ok = import_categories()
    
    # Importar productos
    products_ok = import_products()
    
    # Importar planes de financiamiento
    plans_ok = import_financing_plans()
    
    # Resumen
    print("\n=== Resumen de Importación ===")
    
    if categories_ok and products_ok and plans_ok:
        print("[OK] Importación completada exitosamente")
        
        # Mostrar estadísticas
        from django.db.models import Count
        cat_count = Category.objects.count()
        prod_count = Product.objects.count()
        plan_count = FinancingPlan.objects.count()
        
        print(f"\nEstadísticas:")
        print(f"- Categorías: {cat_count}")
        print(f"- Productos: {prod_count}")
        print(f"- Planes de financiamiento: {plan_count}")
        
        # Productos por categoría
        print(f"\nProductos por categoría:")
        for cat in Category.objects.annotate(product_count=Count('products')):
            print(f"- {cat.name}: {cat.product_count} productos")
    else:
        print("[ERROR] Hubo errores durante la importación")

if __name__ == "__main__":
    main() 