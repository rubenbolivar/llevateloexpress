#!/usr/bin/env python3
"""
Script para configurar los modos iniciales de la calculadora
Recuperado del commit 316a3f2
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/var/www/llevateloexpress')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from financing.models import CalculatorMode

def setup_calculator_modes():
    """Configurar los modos iniciales de la calculadora"""
    
    print("🔧 Configurando modos de calculadora...")
    
    # Modo Compra Programada
    programada, created = CalculatorMode.objects.get_or_create(
        name="Compra Programada",
        mode_type="programada",
        defaults={
            'description': 'Adjudicación al 45% del valor total del vehículo',
            'adjudication_percentage': 45.00,
            'initial_fee_percentage': 5.00,
            'min_contribution_percentage': 10.00,
            'max_contribution_percentage': 15.00,
            'interest_rate': 0.00,
            'min_term_months': 12,
            'max_term_months': 60,
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Creado: {programada.name}")
    else:
        print(f"ℹ️  Ya existe: {programada.name}")
    
    # Modo Crédito Inmediato
    credito, created = CalculatorMode.objects.get_or_create(
        name="Crédito Inmediato",
        mode_type="credito",
        defaults={
            'description': 'Entrega inmediata con pago inicial y financiamiento',
            'adjudication_percentage': None,
            'initial_fee_percentage': None,
            'min_contribution_percentage': 30.00,
            'max_contribution_percentage': 60.00,
            'interest_rate': 0.00,
            'min_term_months': 6,
            'max_term_months': 24,
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Creado: {credito.name}")
    else:
        print(f"ℹ️  Ya existe: {credito.name}")
    
    print("🎉 Configuración de modos completada!")
    
    # Mostrar resumen
    print("\n📊 Resumen de configuración:")
    for mode in CalculatorMode.objects.all():
        print(f"- {mode.name} ({mode.mode_type}): {'Activo' if mode.is_active else 'Inactivo'}")

if __name__ == "__main__":
    setup_calculator_modes() 