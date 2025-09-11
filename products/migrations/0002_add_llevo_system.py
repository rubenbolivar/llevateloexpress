# Generated migration for LLEVO system

from django.db import migrations, models
import decimal

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        # Agregar campo price_llevo a Product
        migrations.AddField(
            model_name='product',
            name='price_llevo',
            field=models.DecimalField(
                blank=True, 
                decimal_places=2, 
                max_digits=10, 
                null=True, 
                verbose_name='Precio (LLEVO)'
            ),
        ),
        
        # Crear tabla LlevoRate
        migrations.CreateModel(
            name='LlevoRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usdt_ves_rate', models.DecimalField(
                    decimal_places=6, 
                    help_text='Tasa actual USDT a VES en P2P', 
                    max_digits=12, 
                    verbose_name='Tasa USDT-VES P2P'
                )),
                ('llevo_value', models.DecimalField(
                    decimal_places=6, 
                    editable=False, 
                    help_text='Calculado automáticamente: USDT-VES × 15 × 1.18', 
                    max_digits=12, 
                    verbose_name='Valor LLEVO en VES'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activa')),
                ('notes', models.TextField(
                    blank=True, 
                    help_text='Observaciones sobre esta tasa', 
                    verbose_name='Notas'
                )),
            ],
            options={
                'verbose_name': 'Tasa LLEVO',
                'verbose_name_plural': 'Tasas LLEVO',
                'ordering': ['-created_at'],
            },
        ),
        
        # Actualizar campo price existente 
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(
                decimal_places=2, 
                help_text='DEPRECADO: Use price_llevo', 
                max_digits=10, 
                verbose_name='Precio (USD)'
            ),
        ),
    ]