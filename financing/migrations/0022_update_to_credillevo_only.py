# Generated migration for CrediLlevo-only system
from django.db import migrations


def update_financing_plans_to_credillevo_only(apps, schema_editor):
    """
    Clean database and create single CrediLlevo plan using SQL
    """
    # Use raw SQL to avoid ORM complications
    with schema_editor.connection.cursor() as cursor:
        # Delete test data in order using SQL
        cursor.execute("DELETE FROM financing_applicationstatushistory;")
        cursor.execute("DELETE FROM financing_payment;")
        cursor.execute("DELETE FROM financing_paymentschedule;")
        cursor.execute("DELETE FROM financing_financingrequest;")
        cursor.execute("DELETE FROM financing_financingplan;")
        
        # Create the single CrediLlevo Inmediato plan
        cursor.execute("""
            INSERT INTO financing_financingplan 
            (name, slug, description, min_down_payment_percentage, max_term_months, 
             interest_rate, min_amount, max_amount, is_active, created_at, updated_at)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, [
            "CrediLlevo Inmediato",
            "credillevo-inmediato", 
            "Plan de financiamiento CrediLlevo Inmediato con pagos fijos en LLEVOs durante 24 meses, sin intereses.",
            30,  # min_down_payment_percentage
            24,  # max_term_months
            0.00,  # interest_rate
            100.00,  # min_amount
            100000.00,  # max_amount
            True  # is_active
        ])


def reverse_update_financing_plans(apps, schema_editor):
    """
    Reverse the migration - this would require manual recreation of old plans
    """
    # For safety, we won't automatically recreate the old complex system
    # This would need to be done manually if needed
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0021_add_notes_field_to_payment'),
    ]

    operations = [
        migrations.RunPython(
            update_financing_plans_to_credillevo_only,
            reverse_update_financing_plans,
        ),
    ]