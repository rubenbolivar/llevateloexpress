from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0019_add_ip_address_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='user_agent',
            field=models.TextField(blank=True, verbose_name='User Agent'),
        ),
    ]
