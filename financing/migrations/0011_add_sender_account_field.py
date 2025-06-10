from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0010_add_sender_bank_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='sender_account',
            field=models.CharField(blank=True, max_length=100, verbose_name='Cuenta emisora'),
        ),
    ]
