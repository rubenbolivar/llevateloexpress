# -*- coding: utf-8 -*-
# Generated manually for R4 Conecta integration
# Migration to update R4 payment method from 'mobile_payment' to 'r4_mobile'

from django.db import migrations


def update_r4_payment_method(apps, schema_editor):
    """
    Actualiza el método de pago R4 (id=6) para usar el nuevo tipo 'r4_mobile'
    según la documentación oficial R4 Conecta V3.0

    IMPORTANTE: Esta migración es segura y reversible.
    - Actualiza SOLO el payment_type del método con ID=6 (🏦 R4 Pago Móvil)
    - Mantiene intacto el método manual (ID=2, Pago Móvil)
    - Preserva todas las IPs whitelist solicitadas por R4
    """
    PaymentMethod = apps.get_model('financing', 'PaymentMethod')

    try:
        # Buscar el método R4 por ID
        r4_method = PaymentMethod.objects.get(id=6)

        # Verificar que es el método correcto antes de actualizar
        if 'R4' in r4_method.name or '🏦' in r4_method.name:
            # Actualizar su payment_type
            old_type = r4_method.payment_type
            r4_method.payment_type = 'r4_mobile'
            r4_method.save()

            print(f"✅ Actualizado método R4:")
            print(f"   Nombre: {r4_method.name}")
            print(f"   Tipo anterior: {old_type}")
            print(f"   Tipo nuevo: r4_mobile")
        else:
            print(f"⚠️  Método ID=6 no parece ser R4. Nombre: {r4_method.name}. Migración omitida por seguridad.")

    except PaymentMethod.DoesNotExist:
        print("⚠️  Método de pago R4 (id=6) no encontrado. Migración omitida.")
    except Exception as e:
        print(f"❌ Error en migración: {str(e)}")
        raise


def reverse_update(apps, schema_editor):
    """
    Función de reversión (rollback) si necesitamos deshacer la migración
    Vuelve a 'mobile_payment' el payment_type del método R4
    """
    PaymentMethod = apps.get_model('financing', 'PaymentMethod')

    try:
        r4_method = PaymentMethod.objects.get(id=6)

        if r4_method.payment_type == 'r4_mobile':
            r4_method.payment_type = 'mobile_payment'
            r4_method.save()
            print("↩️  Revertido método R4 a payment_type='mobile_payment'")
        else:
            print(f"⚠️  Método R4 tiene tipo '{r4_method.payment_type}', no se requiere reversión.")

    except PaymentMethod.DoesNotExist:
        print("⚠️  Método de pago R4 (id=6) no encontrado. Reversión omitida.")
    except Exception as e:
        print(f"❌ Error en reversión: {str(e)}")
        raise


class Migration(migrations.Migration):
    """
    Migración para implementar Opción 3: Nuevo payment_type 'r4_mobile'

    Esta migración es parte de la integración con R4 Conecta V3.0 del Banco R4.

    CAMBIOS:
    - Agrega 'r4_mobile' como nuevo PAYMENT_TYPE en el modelo PaymentMethod
    - Actualiza el registro ID=6 (🏦 R4 Pago Móvil) de 'mobile_payment' a 'r4_mobile'
    - Mantiene ID=2 (Pago Móvil) con 'mobile_payment' para flujo manual

    SEGURIDAD:
    - Mantiene las IPs whitelist solicitadas por R4 (no las modifica)
    - Preserva endpoints R4consulta y R4notifica existentes
    - No afecta datos de pagos históricos
    - Reversible con python manage.py migrate financing 0027

    ARQUITECTURA:
    Permite diferenciar métodos por payment_type en lugar de ID:

    ANTES:
      if (methodId === 6) → R4 automático

    DESPUÉS:
      if (method.payment_type === 'r4_mobile') → R4 automático
      if (method.payment_type === 'mobile_payment') → Manual
    """

    dependencies = [
        ('financing', '0027_merge_20251022_2125'),  # Última migración actual
    ]

    operations = [
        migrations.RunPython(
            update_r4_payment_method,  # Función para aplicar
            reverse_update              # Función para revertir
        ),
    ]
