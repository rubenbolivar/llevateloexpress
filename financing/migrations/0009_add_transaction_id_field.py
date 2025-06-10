from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0008_add_missing_payment_fields_fix'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='ID de transacción'),
        ),
    ]
