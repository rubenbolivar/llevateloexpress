# Generated manually - R4 Automatización
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0028_add_r4_payment_type'),
        ('products', '0001_initial'),  # Para LlevoRate
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='amount_llevos',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                null=True,
                blank=True,
                verbose_name='Monto en LLEVOS',
                help_text='Equivalente del pago en tokens LLEVO'
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='llevo_rate_at_payment',
            field=models.DecimalField(
                decimal_places=6,
                max_digits=12,
                null=True,
                blank=True,
                verbose_name='Tasa LLEVO al momento del pago',
                help_text='Valor de 1 LLEVO en VES cuando se realizó el pago'
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='llevo_rate_snapshot',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                to='products.llevorate',
                null=True,
                blank=True,
                verbose_name='Snapshot de tasa LLEVO',
                help_text='Referencia a la tasa LLEVO vigente al momento del pago'
            ),
        ),
    ]
