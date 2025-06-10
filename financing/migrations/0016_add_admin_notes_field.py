from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0015_add_customer_notes_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='admin_notes',
            field=models.TextField(blank=True, verbose_name='Notas del administrador'),
        ),
    ]
