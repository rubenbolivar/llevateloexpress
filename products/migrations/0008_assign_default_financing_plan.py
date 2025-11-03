# Generated migration for assigning default financing plan to existing products

from django.db import migrations


def assign_default_plan_to_products(apps, schema_editor):
    """Asignar plan CrediLlevo Inmediato a productos existentes con configuración LLEVO"""
    Product = apps.get_model('products', 'Product')
    FinancingPlan = apps.get_model('financing', 'FinancingPlan')
    
    try:
        # Obtener el plan CrediLlevo Inmediato (el actual)
        default_plan = FinancingPlan.objects.get(slug='credillevo-inmediato')
        
        # Asignar a todos los productos que tienen configuración LLEVO
        products_to_update = Product.objects.filter(
            price_llevo__isnull=False,
            inicial_llevos__isnull=False,
            financing_plan__isnull=True  # Solo los que no tienen plan
        )
        
        count = products_to_update.update(financing_plan=default_plan)
        print(f'✅ {count} productos asignados al plan CrediLlevo Inmediato')
        
    except FinancingPlan.DoesNotExist:
        print('⚠️ Plan CrediLlevo Inmediato no encontrado')


def reverse_migration(apps, schema_editor):
    """Revertir asignación de planes"""
    Product = apps.get_model('products', 'Product')
    Product.objects.all().update(financing_plan=None)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_add_financing_plan_to_product'),
    ]

    operations = [
        migrations.RunPython(
            assign_default_plan_to_products,
            reverse_migration
        ),
    ]
