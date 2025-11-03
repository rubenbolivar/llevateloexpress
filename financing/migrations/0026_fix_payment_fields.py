# Generated migration to fix Payment model fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0024_remove_unnecessary_fields'),
    ]

    operations = [
        # 1. Agregar campo sender_phone (nuevo campo necesario para pago móvil)
        migrations.AddField(
            model_name='payment',
            name='sender_phone',
            field=models.CharField(
                max_length=20, 
                blank=True, 
                null=True,
                verbose_name='Teléfono Emisor',
                help_text='Número de teléfono desde el cual se realizó el pago móvil'
            ),
        ),
        
        # 2. Hacer sender_bank nullable (no siempre es requerido)
        migrations.AlterField(
            model_name='payment',
            name='sender_bank',
            field=models.CharField(
                max_length=100, 
                blank=True, 
                null=True,
                verbose_name='Banco Emisor'
            ),
        ),
        
        # 3. Hacer sender_account nullable
        migrations.AlterField(
            model_name='payment',
            name='sender_account',
            field=models.CharField(
                max_length=50, 
                blank=True, 
                null=True,
                verbose_name='Cuenta Emisora'
            ),
        ),
    ]
