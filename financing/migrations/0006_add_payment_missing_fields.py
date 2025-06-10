from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('financing', '0005_add_missing_payment_fields'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='payment',
            name='currency',
            field=models.CharField(default='USD', max_length=3, verbose_name='Moneda'),
        ),
        migrations.AddField(
            model_name='payment',
            name='submitted_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Fecha de Registro'),
        ),
    ]
