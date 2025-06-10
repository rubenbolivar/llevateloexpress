from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0016_add_admin_notes_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='rejection_reason',
            field=models.TextField(blank=True, verbose_name='Razón de rechazo'),
        ),
    ]
