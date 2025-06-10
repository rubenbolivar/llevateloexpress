from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0013_add_sender_identification_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='receipt_file',
            field=models.FileField(blank=True, null=True, upload_to='payments/receipts/', verbose_name='Archivo de comprobante'),
        ),
    ]
