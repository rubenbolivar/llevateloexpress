# Generated migration to add inicial_llevos field to Product model
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='inicial_llevos',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Monto de inicial fijo en LLEVOs definido por el admin',
                null=True,
                verbose_name='Inicial (LLEVO)'
            ),
        ),
    ]