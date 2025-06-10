from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0014_add_receipt_file_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='customer_notes',
            field=models.TextField(blank=True, verbose_name='Notas del cliente'),
        ),
    ]
