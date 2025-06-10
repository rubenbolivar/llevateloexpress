from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0009_add_transaction_id_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='sender_bank',
            field=models.CharField(blank=True, max_length=100, verbose_name='Banco emisor'),
        ),
    ]
