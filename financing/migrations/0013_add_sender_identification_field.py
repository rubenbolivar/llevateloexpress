from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0012_add_sender_name_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='sender_identification',
            field=models.CharField(blank=True, max_length=100, verbose_name='Identificación del emisor'),
        ),
    ]
