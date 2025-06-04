#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from products.models import Category, Product

def import_products():
    """Importar productos manualmente"""
    print("Importando productos...")
    
    # Producto 1: Voge Rally 300
    try:
        category = Category.objects.get(id='motocicletas')
        
        product = Product(
            name="Voge Rally 300",
            category=category,
            brand="Voge",
            price=4500,
            image="products/300.jpg",
            description="La Voge Rally 300 es una motocicleta de aventura ligera que combina versatilidad y rendimiento. Perfecta para quienes buscan una moto capaz tanto en ciudad como en caminos de tierra.",
            features=[
                "Motor monocilíndrico de 292cc refrigerado por líquido",
                "Potencia máxima de 29 HP a 8500 rpm",
                "Transmisión de 6 velocidades",
                "Frenos de disco con ABS desconectable",
                "Suspensión invertida ajustable",
                "Panel de instrumentos TFT a color",
                "Iluminación full LED",
                "Capacidad de tanque: 16 litros"
            ],
            specs_general=[
                {"label": "Marca", "value": "Voge"},
                {"label": "Modelo", "value": "Rally 300"},
                {"label": "Año", "value": "2023"},
                {"label": "Tipo", "value": "Adventure"},
                {"label": "País de Origen", "value": "China"},
                {"label": "Garantía", "value": "2 años o 20,000 km"},
                {"label": "Colores disponibles", "value": "Negro, Rojo, Gris"},
                {"label": "Peso", "value": "178 kg"}
            ],
            specs_engine=[
                {"label": "Tipo de motor", "value": "Monocilíndrico 4T, DOHC, 4 válvulas"},
                {"label": "Cilindrada", "value": "292 cc"},
                {"label": "Potencia máxima", "value": "29 HP a 8500 rpm"},
                {"label": "Torque máximo", "value": "25.3 Nm a 6500 rpm"},
                {"label": "Transmisión", "value": "6 velocidades"},
                {"label": "Sistema de refrigeración", "value": "Líquido"},
                {"label": "Capacidad de tanque", "value": "16 litros"},
                {"label": "Consumo promedio", "value": "3.3 L/100km"}
            ],
            specs_comfort=[
                {"label": "Asiento", "value": "Doble altura, ergonómico"},
                {"label": "Altura del asiento", "value": "825 mm"},
                {"label": "Panel de instrumentos", "value": "TFT a color de 5\""},
                {"label": "Iluminación", "value": "Full LED"},
                {"label": "USB", "value": "Sí, puerto cargador 2.1A"},
                {"label": "Posición de manejo", "value": "Adventure, semi-erguida"},
                {"label": "Capacidad de carga", "value": "12 kg"},
                {"label": "Parabrisas", "value": "Ajustable 3 posiciones"}
            ],
            specs_safety=[
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
            stock=8,
            featured=True
        )
        product.save()
        print(f"✓ Producto importado: {product.name}")
    except Exception as e:
        print(f"✗ Error al importar Voge Rally 300: {e}")
    
    # Producto 2: Voge 525 DSX
    try:
        category = Category.objects.get(id='motocicletas')
        
        product = Product(
            name="Voge 525 DSX",
            category=category,
            brand="Voge",
            price=6800,
            image="products/525dsx.jpg",
            description="La Voge 525 DSX es una motocicleta trail de media cilindrada que ofrece excelentes prestaciones para aventuras on/off-road. Su diseño moderno y equipamiento premium la hacen destacar en su segmento.",
            features=[
                "Motor bicilíndrico en línea de 494cc",
                "Potencia de 46.2 HP a 8500 rpm",
                "Transmisión de 6 velocidades",
                "Sistema de frenos ABS Bosch de doble canal",
                "Suspensión KYB totalmente ajustable",
                "Pantalla TFT de 7 pulgadas",
                "Modos de conducción",
                "Control de tracción"
            ],
            specs_general=[
                {"label": "Marca", "value": "Voge"},
                {"label": "Modelo", "value": "525 DSX"},
                {"label": "Año", "value": "2023"},
                {"label": "Tipo", "value": "Trail Adventure"},
                {"label": "País de Origen", "value": "China"}
            ],
            specs_engine=[
                {"label": "Tipo de motor", "value": "Bicilíndrico en línea, 4T, DOHC, 8 válvulas"},
                {"label": "Cilindrada", "value": "494 cc"},
                {"label": "Potencia máxima", "value": "46.2 HP a 8500 rpm"}
            ],
            specs_comfort=[
                {"label": "Asiento", "value": "Ergonómico, tapizado antideslizante"},
                {"label": "Altura del asiento", "value": "840 mm"},
                {"label": "Panel de instrumentos", "value": "TFT a color de 7 pulgadas"}
            ],
            specs_safety=[
                {"label": "Freno delantero", "value": "Doble disco 320mm, pinzas radiales de 4 pistones"},
                {"label": "Freno trasero", "value": "Disco 260mm, pinza flotante de 2 pistones"},
                {"label": "ABS", "value": "Bosch 9.1 MB, modos Road/Off-road"}
            ],
            stock=5,
            featured=True
        )
        product.save()
        print(f"✓ Producto importado: {product.name}")
    except Exception as e:
        print(f"✗ Error al importar Voge 525 DSX: {e}")
    
    # Producto 3: Suzuki DR 650
    try:
        category = Category.objects.get(id='motocicletas')
        
        product = Product(
            name="Suzuki DR 650",
            category=category,
            brand="Suzuki",
            price=8500,
            image="products/dr650.jpg",
            description="La legendaria Suzuki DR 650 es sinónimo de confiabilidad y versatilidad. Una moto dual-purpose que ha probado su valor tanto en largas travesías como en el uso diario.",
            features=[
                "Motor monocilíndrico SOHC de 644cc refrigerado por aire",
                "Potencia de 46 HP",
                "Transmisión de 5 velocidades",
                "Freno de disco delantero y trasero",
                "Suspensión de largo recorrido",
                "Altura de asiento ajustable",
                "Peso en seco de 166 kg",
                "Tanque de combustible de 13 litros"
            ],
            specs_general=[
                {"label": "Marca", "value": "Suzuki"},
                {"label": "Modelo", "value": "DR 650"},
                {"label": "Año", "value": "2023"},
                {"label": "Tipo", "value": "Dual Purpose"},
                {"label": "País de Origen", "value": "Japón"}
            ],
            specs_engine=[
                {"label": "Tipo de motor", "value": "Monocilíndrico SOHC, 4T, 4 válvulas"},
                {"label": "Cilindrada", "value": "644 cc"},
                {"label": "Potencia máxima", "value": "46 HP a 6400 rpm"}
            ],
            specs_comfort=[
                {"label": "Altura del asiento", "value": "840-870 mm (ajustable)"},
                {"label": "Panel de instrumentos", "value": "Analógico"}
            ],
            specs_safety=[
                {"label": "Freno delantero", "value": "Disco 290mm, pinza de 2 pistones"},
                {"label": "Freno trasero", "value": "Disco 240mm, pinza de 1 pistón"},
                {"label": "ABS", "value": "No disponible"}
            ],
            stock=4,
            featured=True
        )
        product.save()
        print(f"✓ Producto importado: {product.name}")
    except Exception as e:
        print(f"✗ Error al importar Suzuki DR 650: {e}")

    # Producto 4: Toyota Hilux
    try:
        category = Category.objects.get(id='vehiculos')
        
        product = Product(
            name="Toyota Hilux 2.8 SRX",
            category=category,
            brand="Toyota",
            price=55000,
            image="products/hilux.jpg",
            description="La Toyota Hilux es reconocida mundialmente por su durabilidad y capacidad todoterreno. Esta versión SRX ofrece el equilibrio perfecto entre robustez y confort.",
            features=[
                "Motor turbodiésel 2.8L de 204 HP",
                "Transmisión automática de 6 velocidades",
                "Tracción 4x4 con reductora",
                "Capacidad de carga de 1 tonelada",
                "Sistema multimedia con pantalla táctil de 8\"",
                "Sistema de asistencia en descensos",
                "7 airbags",
                "Control de estabilidad y tracción"
            ],
            specs_general=[
                {"label": "Marca", "value": "Toyota"},
                {"label": "Modelo", "value": "Hilux SRX"},
                {"label": "Año", "value": "2023"},
                {"label": "Tipo", "value": "Camioneta Pick-up"},
                {"label": "País de Origen", "value": "Tailandia/Argentina"}
            ],
            specs_engine=[
                {"label": "Tipo de motor", "value": "Turbodiésel 4 cilindros en línea"},
                {"label": "Cilindrada", "value": "2.8L (2755cc)"},
                {"label": "Potencia máxima", "value": "204 HP a 3400 rpm"}
            ],
            specs_comfort=[
                {"label": "Asientos", "value": "Tapizados en cuero"},
                {"label": "Climatización", "value": "Automática bizona"},
                {"label": "Sistema de sonido", "value": "6 altavoces con Apple CarPlay/Android Auto"}
            ],
            specs_safety=[
                {"label": "Airbags", "value": "7 (frontales, laterales, cortina y rodilla)"},
                {"label": "Asistencias", "value": "Control de estabilidad, asistente de arranque en pendiente"},
                {"label": "Cámara", "value": "Visión trasera con guías dinámicas"}
            ],
            stock=3,
            featured=True
        )
        product.save()
        print(f"✓ Producto importado: {product.name}")
    except Exception as e:
        print(f"✗ Error al importar Toyota Hilux: {e}")

    # Producto 5: Massey Ferguson Tractor
    try:
        category = Category.objects.get(id='maquinaria')
        
        product = Product(
            name="Massey Ferguson MF 7719",
            category=category,
            brand="Massey Ferguson",
            price=120000,
            image="products/mf7719.jpg",
            description="El Massey Ferguson 7719 combina potencia, eficiencia y tecnología avanzada para operaciones agrícolas de gran escala. Su motor AGCO Power ofrece rendimiento superior con bajo consumo de combustible.",
            features=[
                "Motor AGCO Power de 7.4L y 190 HP",
                "Transmisión Dyna-6 (24 velocidades)",
                "Sistema hidráulico de centro cerrado",
                "Capacidad de levante de 9600 kg",
                "Cabina presurizada con aire acondicionado",
                "Sistema de gestión de potencia Engine Power Management",
                "Sistema de guiado por GPS opcional",
                "Eje delantero suspendido"
            ],
            specs_general=[
                {"label": "Marca", "value": "Massey Ferguson"},
                {"label": "Modelo", "value": "MF 7719"},
                {"label": "Año", "value": "2023"},
                {"label": "Tipo", "value": "Tractor agrícola"},
                {"label": "País de Origen", "value": "Reino Unido/Brasil"}
            ],
            specs_engine=[
                {"label": "Tipo de motor", "value": "AGCO Power, 6 cilindros turbo"},
                {"label": "Cilindrada", "value": "7.4L"},
                {"label": "Potencia máxima", "value": "190 HP (205 HP con EPM)"}
            ],
            specs_comfort=[
                {"label": "Cabina", "value": "Presurizada con filtro de carbón activo"},
                {"label": "Climatización", "value": "Aire acondicionado automático"},
                {"label": "Asiento", "value": "Suspensión neumática con calefacción"}
            ],
            specs_safety=[
                {"label": "ROPS/FOPS", "value": "Cumple normativas internacionales"},
                {"label": "Frenos", "value": "Discos húmedos autoajustables"},
                {"label": "Iluminación", "value": "12 luces de trabajo LED"}
            ],
            stock=2,
            featured=True
        )
        product.save()
        print(f"✓ Producto importado: {product.name}")
    except Exception as e:
        print(f"✗ Error al importar Massey Ferguson: {e}")

    print(f"\nSe importaron 5 productos de muestra correctamente.")
    return True

if __name__ == "__main__":
    print("=== Iniciando importación de productos de muestra ===")
    success = import_products()
    print("¡Importación completada!") 