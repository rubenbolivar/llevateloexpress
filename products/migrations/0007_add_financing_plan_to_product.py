# Generated migration for adding financing_plan field to Product

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_product_out_of_stock'),
        ('financing', '0025_convert_to_llevo_amounts'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='financing_plan',
            field=models.ForeignKey(
                blank=True,
                help_text='Plan de financiamiento aplicable a este producto',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='products',
                to='financing.financingplan',
                verbose_name='Plan de Financiamiento'
            ),
        ),
    ]
