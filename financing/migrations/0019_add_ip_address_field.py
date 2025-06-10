from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0018_add_submitted_by_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='Dirección IP'),
        ),
    ]
