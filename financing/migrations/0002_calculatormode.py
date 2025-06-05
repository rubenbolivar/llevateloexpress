# Generated manually for calculator mode recovery - simplified
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0001_initial'),
    ]

    operations = [
        # Crear solo el modelo CalculatorMode
        migrations.CreateModel(
            name='CalculatorMode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('mode_type', models.CharField(choices=[('programada', 'Compra Programada'), ('credito', 'Crédito Inmediato')], max_length=20, verbose_name='Tipo de modalidad')),
                ('description', models.TextField(verbose_name='Descripción')),
                ('adjudication_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Porcentaje para adjudicación')),
                ('initial_fee_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Porcentaje de cuota inicial')),
                ('min_contribution_percentage', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Porcentaje mínimo de aporte')),
                ('max_contribution_percentage', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Porcentaje máximo de aporte')),
                ('interest_rate', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Tasa de interés anual')),
                ('min_term_months', models.IntegerField(verbose_name='Plazo mínimo (meses)')),
                ('max_term_months', models.IntegerField(verbose_name='Plazo máximo (meses)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Última actualización')),
            ],
            options={
                'verbose_name': 'Modalidad de Calculadora',
                'verbose_name_plural': 'Modalidades de Calculadora',
                'ordering': ['mode_type', 'name'],
            },
        ),
    ] 