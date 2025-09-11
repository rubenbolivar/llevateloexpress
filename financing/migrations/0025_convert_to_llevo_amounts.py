# Generated migration to convert FinancingRequest to LLEVO amounts
from django.db import migrations, models
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0024_remove_unnecessary_fields'),
    ]

    operations = [
        # Add new LLEVO fields
        migrations.AddField(
            model_name='financingrequest',
            name='product_price_llevos',
            field=models.PositiveIntegerField(
                null=True,
                blank=True,
                verbose_name="Precio del producto (LLEVO)"
            ),
        ),
        migrations.AddField(
            model_name='financingrequest',
            name='down_payment_llevos',
            field=models.PositiveIntegerField(
                null=True,
                blank=True,
                verbose_name="Monto de inicial (LLEVO)"
            ),
        ),
        migrations.AddField(
            model_name='financingrequest',
            name='financed_amount_llevos',
            field=models.PositiveIntegerField(
                null=True,
                blank=True,
                verbose_name="Monto a financiar (LLEVO)"
            ),
        ),
        migrations.AddField(
            model_name='financingrequest',
            name='payment_amount_llevos',
            field=models.PositiveIntegerField(
                null=True,
                blank=True,
                verbose_name="Monto de cada cuota (LLEVO)"
            ),
        ),
        
        # Update verbose names of old fields to indicate they're deprecated
        migrations.AlterField(
            model_name='financingrequest',
            name='product_price',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                verbose_name="Precio del producto (USD) - DEPRECADO"
            ),
        ),
        migrations.AlterField(
            model_name='financingrequest',
            name='down_payment_amount',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                verbose_name="Monto de inicial (USD) - DEPRECADO"
            ),
        ),
        migrations.AlterField(
            model_name='financingrequest',
            name='financed_amount',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                verbose_name="Monto a financiar (USD) - DEPRECADO"
            ),
        ),
        migrations.AlterField(
            model_name='financingrequest',
            name='payment_amount',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                verbose_name="Monto de cada cuota (USD) - DEPRECADO"
            ),
        ),
    ]