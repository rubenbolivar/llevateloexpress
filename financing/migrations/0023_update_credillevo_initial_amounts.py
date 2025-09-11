# Generated migration to add LLEVO initial amount options
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0022_update_to_credillevo_only'),
    ]

    operations = [
        migrations.AddField(
            model_name='financingplan',
            name='available_initial_amounts_llevos',
            field=models.TextField(
                blank=True,
                help_text="Montos de inicial disponibles en LLEVOs separados por coma (ej: 500,750,1000,1250)",
                verbose_name="Montos de inicial disponibles (LLEVOs)"
            ),
        ),
        migrations.AddField(
            model_name='financingplan',
            name='uses_fixed_llevo_amounts',
            field=models.BooleanField(
                default=True,
                help_text="Si está activado, usa montos fijos en LLEVOs en lugar de porcentajes",
                verbose_name="Usar montos fijos en LLEVOs"
            ),
        ),
        migrations.RunSQL(
            """
            UPDATE financing_financingplan 
            SET available_initial_amounts_llevos = '500,750,1000,1250,1500',
                uses_fixed_llevo_amounts = true
            WHERE slug = 'credillevo-inmediato';
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ]