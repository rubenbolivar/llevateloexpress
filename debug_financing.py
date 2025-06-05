import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from financing.models import *
from users.models import Customer

print('=== PLANES DE FINANCIAMIENTO ===')
plans = FinancingPlan.objects.all()
print(f'Total plans: {plans.count()}')
for p in plans:
    print(f'ID: {p.id}, Nombre: {p.name}, Active: {p.is_active}')

print('\n=== CONFIGURACIONES ===')
configs = FinancingConfiguration.objects.all()
print(f'Total configs: {configs.count()}')
for c in configs:
    print(f'ID: {c.id}, Nombre: {c.name}, Active: {c.is_active}')

print('\n=== MODALIDADES CALCULADORA ===')
modes = CalculatorMode.objects.all()
print(f'Total modes: {modes.count()}')
for m in modes:
    print(f'ID: {m.id}, Nombre: {m.name}, Tipo: {m.mode_type}, Active: {m.is_active}')
    if m.mode_type == 'credito':
        print(f'  - Down payments: {m.available_down_payments}')
        print(f'  - Terms: {m.available_terms}')
        print(f'  - Interest rate: {m.interest_rate}%')

print('\n=== CUSTOMERS ===')
customers = Customer.objects.all()
print(f'Total customers: {customers.count()}')

print('\n=== VERIFICAR SI PODEMOS CREAR UN PLAN POR DEFECTO ===')
if plans.count() == 0:
    print('No hay planes de financiamiento. Creando plan por defecto...')
    default_plan = FinancingPlan.objects.create(
        name='Plan Básico de Crédito Inmediato',
        slug='plan-basico-credito',
        description='Plan básico para solicitudes desde la calculadora',
        min_down_payment_percentage=30,
        max_term_months=24,
        interest_rate=0.00,
        min_amount=1000.00,
        max_amount=50000.00,
        is_active=True
    )
    print(f'Plan creado: ID {default_plan.id} - {default_plan.name}')
else:
    print('Ya existen planes de financiamiento.') 