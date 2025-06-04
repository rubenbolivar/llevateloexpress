#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/var/www/llevateloexpress')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from products.models import Category, Product
from decimal import Decimal

def create_voge_900_dsx():
    print("🏍️  CREANDO VOGE 900 DSX - NUEVA ADVENTURE PREMIUM")
    print("=" * 60)
    
    # Obtener categoría de motocicletas
    try:
        categoria = Category.objects.get(id='motocicletas')
        print(f"✅ Categoría encontrada: {categoria.name}")
    except Category.DoesNotExist:
        print("❌ Error: Categoría 'motocicletas' no encontrada")
        return
    
    # Verificar si ya existe
    if Product.objects.filter(name="Voge 900 DSX").exists():
        print("⚠️  Producto 'Voge 900 DSX' ya existe. Eliminando para recrear...")
        Product.objects.filter(name="Voge 900 DSX").delete()
    
    # Crear el producto
    voge_900_dsx = Product.objects.create(
        name="Voge 900 DSX",
        category=categoria,
        brand="Voge",
        price=Decimal('16000.00'),
        description="La Voge 900 DSX representa la evolución máxima en el segmento adventure touring. Con su motor bicilíndrico de 895cc y tecnología de vanguardia, está diseñada para conquistar cualquier terreno con comodidad y rendimiento excepcionales.",
        
        # Características principales
        features=[
            "Motor bicilíndrico en línea de 895cc refrigerado por líquido",
            "Potencia de 95 HP a 8500 rpm y 90 Nm de torque",
            "Transmisión de 6 velocidades con quickshifter bidireccional",
            "Sistema de frenos ABS Bosch de triple modo (Road/Off-road/Desconectable)",
            "Suspensión KYB totalmente ajustable con recorrido de 200mm",
            "Pantalla TFT de 7 pulgadas con conectividad smartphone",
            "Control de crucero adaptativo y modos de conducción",
            "Protecciones completas y maletas laterales de serie"
        ],
        
        # Especificaciones generales
        specs_general=[
            {"label": "Marca", "value": "Voge"},
            {"label": "Modelo", "value": "900 DSX"},
            {"label": "Año", "value": "2024"},
            {"label": "Tipo", "value": "Adventure Touring Premium"},
            {"label": "País de Origen", "value": "China"},
            {"label": "Garantía", "value": "3 años o 50,000 km"},
            {"label": "Colores disponibles", "value": "Negro Rally, Azul Aventura, Gris Titanio"},
            {"label": "Peso en orden de marcha", "value": "245 kg"},
            {"label": "Altura del asiento", "value": "850-870 mm (ajustable)"},
            {"label": "Capacidad del tanque", "value": "25 litros"}
        ],
        
        # Especificaciones del motor
        specs_engine=[
            {"label": "Tipo de motor", "value": "Bicilíndrico en línea, 4T, DOHC, 8 válvulas"},
            {"label": "Cilindrada", "value": "895 cc"},
            {"label": "Potencia máxima", "value": "95 HP a 8500 rpm"},
            {"label": "Torque máximo", "value": "90 Nm a 6500 rpm"},
            {"label": "Relación de compresión", "value": "11.5:1"},
            {"label": "Transmisión", "value": "6 velocidades con quickshifter bidireccional"},
            {"label": "Sistema de refrigeración", "value": "Líquido con radiador de alta eficiencia"},
            {"label": "Alimentación", "value": "Inyección electrónica dual throttle"},
            {"label": "Consumo promedio", "value": "5.2 L/100km"},
            {"label": "Emisiones", "value": "Euro 5 certificado"}
        ],
        
        # Especificaciones de confort
        specs_comfort=[
            {"label": "Asiento", "value": "Touring ergonómico, altura ajustable 850-870mm"},
            {"label": "Panel de instrumentos", "value": "TFT a color de 7 pulgadas con navegación GPS"},
            {"label": "Conectividad", "value": "Bluetooth, USB tipo C, carga inalámbrica"},
            {"label": "Iluminación", "value": "Full LED adaptativa con curva automática"},
            {"label": "Posición de manejo", "value": "Touring premium, protección total del viento"},
            {"label": "Capacidad de carga", "value": "35 kg + maletas laterales 60L"},
            {"label": "Parabrisas", "value": "Eléctrico, regulable en altura y ángulo"},
            {"label": "Accesorios de serie", "value": "Maletas laterales, protector motor, barras defensoras"},
            {"label": "Modos de conducción", "value": "Rain, Road, Sport, Off-road, Custom"},
            {"label": "Control de crucero", "value": "Adaptativo con detección de obstáculos"}
        ],
        
        # Especificaciones de seguridad
        specs_safety=[
            {"label": "Freno delantero", "value": "Doble disco 320mm, pinzas Brembo monobloque de 4 pistones"},
            {"label": "Freno trasero", "value": "Disco 280mm, pinza Brembo de 2 pistones"},
            {"label": "Sistema de frenos", "value": "Hidráulico Brembo, doble disco delantero"},
            {"label": "ABS", "value": "Bosch 9.3 MP, triple modo (Road/Off-road/Desconectable)"},
            {"label": "Control de tracción", "value": "Cornering TC con sensor de inclinación"},
            {"label": "Control de elevación", "value": "Wheelie control con 5 niveles"},
            {"label": "Suspensión delantera", "value": "KYB invertida de 45mm, totalmente ajustable, 200mm recorrido"},
            {"label": "Suspensión trasera", "value": "KYB monoamortiguador con depósito separado, 210mm recorrido"},
            {"label": "Neumático delantero", "value": "120/70-R19 TubeLess"},
            {"label": "Neumático trasero", "value": "170/60-R17 TubeLess"},
            {"label": "Tamaño de ruedas", "value": "19 pulgadas delantera, 17 pulgadas trasera"},
            {"label": "Sistema de emergencia", "value": "Llamada automática de emergencia (eCall)"},
            {"label": "Antirrobo", "value": "Inmovilizador electrónico + alarma"}
        ],
        
        stock=3,  # Stock inicial limitado por ser modelo premium
        featured=True  # Destacado por ser el modelo más premium
    )
    
    print(f"✅ Producto creado exitosamente:")
    print(f"   📦 ID: {voge_900_dsx.id}")
    print(f"   🏍️  Nombre: {voge_900_dsx.name}")
    print(f"   🏷️  Categoría: {voge_900_dsx.category.name}")
    print(f"   💰 Precio: ${voge_900_dsx.price}")
    print(f"   📊 Stock: {voge_900_dsx.stock}")
    print(f"   ⭐ Destacado: {'Sí' if voge_900_dsx.featured else 'No'}")
    print(f"   📝 Características: {len(voge_900_dsx.features)}")
    print(f"   🔧 Specs General: {len(voge_900_dsx.specs_general)}")
    print(f"   🏭 Specs Motor: {len(voge_900_dsx.specs_engine)}")
    print(f"   😌 Specs Confort: {len(voge_900_dsx.specs_comfort)}")
    print(f"   🛡️  Specs Seguridad: {len(voge_900_dsx.specs_safety)}")
    
    print("\n" + "=" * 60)
    print("🎉 VOGE 900 DSX AGREGADA EXITOSAMENTE AL CATÁLOGO")
    print("🔗 Verificar en:")
    print("   • Admin: https://llevateloexpress.com/admin/products/product/")
    print("   • API: https://llevateloexpress.com/api/products/products/")
    print("   • Frontend: https://llevateloexpress.com/catalogo.html")
    print("=" * 60)

if __name__ == "__main__":
    create_voge_900_dsx() 