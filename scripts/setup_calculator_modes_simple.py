#!/usr/bin/env python3
"""
Script para configurar los modos iniciales de la calculadora
Version sin emojis para evitar problemas de encoding
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
    
    print("Configurando modos de calculadora...")
    
    # Modo Compra Programada
    programada, created = CalculatorMode.objects.get_or_create(
        name="Compra Programada",
        mode_type="programada",
        defaults={
            'description': 'Adjudicacion al 45% del valor total del vehiculo',
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
        print(f"Creado: {programada.name}")
    else:
        print(f"Ya existe: {programada.name}")
    
    # Modo Credito Inmediato
    credito, created = CalculatorMode.objects.get_or_create(
        name="Credito Inmediato",
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
        print(f"Creado: {credito.name}")
    else:
        print(f"Ya existe: {credito.name}")
    
    print("Configuracion de modos completada!")
    
    # Mostrar resumen
    print("\nResumen de configuracion:")
    for mode in CalculatorMode.objects.all():
        status = 'Activo' if mode.is_active else 'Inactivo'
        print(f"- {mode.name} ({mode.mode_type}): {status}")

if __name__ == "__main__":
    setup_calculator_modes() 