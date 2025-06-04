#!/usr/bin/env python3
"""
Script para configurar los modos iniciales de la calculadora
Version final con todos los campos requeridos
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
            'min_initial_contribution': 10.00,
            'max_initial_contribution': 15.00,
            'available_down_payments': '10,11,12,13,14,15',
            'available_terms': '12,18,24,36,48,60',
            'interest_rate': 0.00,
            'is_active': True,
            'order': 1
        }
    )
    
    if created:
        print(f"Creado: {programada.name}")
    else:
        print(f"Ya existe: {programada.name}")
    
    # Modo Credito Inmediato - con valores no nulos
    credito, created = CalculatorMode.objects.get_or_create(
        name="Credito Inmediato",
        mode_type="credito",
        defaults={
            'description': 'Entrega inmediata con pago inicial y financiamiento',
            'adjudication_percentage': 0.00,  # 0 para credito inmediato
            'initial_fee_percentage': 0.00,   # 0 para credito inmediato
            'min_initial_contribution': 30.00,
            'max_initial_contribution': 60.00,
            'available_down_payments': '30,40,50,60',
            'available_terms': '6,12,18,24',
            'interest_rate': 0.00,
            'is_active': True,
            'order': 2
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