# Generated migration to remove unnecessary fields from FinancingPlan
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0023_update_credillevo_initial_amounts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financingplan',
            name='available_initial_amounts_llevos',
        ),
        migrations.RemoveField(
            model_name='financingplan',
            name='uses_fixed_llevo_amounts',
        ),
    ]