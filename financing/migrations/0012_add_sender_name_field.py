from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0011_add_sender_account_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='sender_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Nombre del emisor'),
        ),
    ]
