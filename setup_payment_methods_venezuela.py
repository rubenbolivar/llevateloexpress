#!/usr/bin/env python3
"""
Script para configurar métodos de pago y cuentas bancarias para LlévateloExpress
Diseñado específicamente para el mercado venezolano
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from financing.models import PaymentMethod, CompanyBankAccount

def setup_payment_methods():
    """Crear métodos de pago para Venezuela"""
    
    print("🔧 Configurando métodos de pago para Venezuela...")
    
    # 1. Transferencia Bancaria (VES)
    transferencia_ves, created = PaymentMethod.objects.get_or_create(
        payment_type='bank_transfer',
        name='Transferencia Bancaria (VES)',
        defaults={
            'description': 'Transferencia bancaria en bolívares desde cualquier banco venezolano',
            'instructions': 'Realiza una transferencia a la cuenta indicada y adjunta el comprobante',
            'requires_reference': True,
            'requires_receipt': True,
            'min_amount': 10.00,  # Mínimo en VES
            'max_amount': None,
            'processing_time_hours': 24,
            'is_active': True,
            'order': 1
        }
    )
    print(f"✅ {transferencia_ves.name} - {'Creado' if created else 'Ya existe'}")
    
    # 2. Pago Móvil (VES)
    pago_movil, created = PaymentMethod.objects.get_or_create(
        payment_type='mobile_payment',
        name='Pago Móvil',
        defaults={
            'description': 'Pago móvil desde cualquier banco venezolano',
            'instructions': 'Realiza un pago móvil al número indicado y adjunta la captura de pantalla',
            'requires_reference': True,
            'requires_receipt': True,
            'min_amount': 5.00,
            'max_amount': 50000.00,  # Límite típico pago móvil
            'processing_time_hours': 12,
            'is_active': True,
            'order': 2
        }
    )
    print(f"✅ {pago_movil.name} - {'Creado' if created else 'Ya existe'}")
    
    # 3. Zelle (USD)
    zelle, created = PaymentMethod.objects.get_or_create(
        payment_type='zelle',
        name='Zelle',
        defaults={
            'description': 'Transferencia Zelle en dólares estadounidenses',
            'instructions': 'Envía el pago por Zelle al email indicado y adjunta el comprobante',
            'requires_reference': False,  # Zelle no usa números de referencia tradicionales
            'requires_receipt': True,
            'min_amount': 50.00,  # Mínimo en USD
            'max_amount': 5000.00,  # Límite diario típico
            'processing_time_hours': 6,
            'is_active': True,
            'order': 3
        }
    )
    print(f"✅ {zelle.name} - {'Creado' if created else 'Ya existe'}")
    
    # 4. Transferencia Internacional (USD)
    transferencia_usd, created = PaymentMethod.objects.get_or_create(
        payment_type='bank_transfer',
        name='Transferencia Internacional (USD)',
        defaults={
            'description': 'Transferencia bancaria internacional en dólares',
            'instructions': 'Realiza una transferencia internacional a la cuenta indicada',
            'requires_reference': True,
            'requires_receipt': True,
            'min_amount': 100.00,
            'max_amount': None,
            'processing_time_hours': 48,
            'is_active': True,
            'order': 4
        }
    )
    print(f"✅ {transferencia_usd.name} - {'Creado' if created else 'Ya existe'}")
    
    # 5. Efectivo (para pagos iniciales)
    efectivo, created = PaymentMethod.objects.get_or_create(
        payment_type='cash',
        name='Efectivo',
        defaults={
            'description': 'Pago en efectivo en nuestras oficinas',
            'instructions': 'Acércate a nuestras oficinas con el monto exacto',
            'requires_reference': False,
            'requires_receipt': False,  # Se genera recibo en oficina
            'min_amount': 10.00,
            'max_amount': 1000.00,  # Límite de efectivo
            'processing_time_hours': 1,
            'is_active': True,
            'order': 5
        }
    )
    print(f"✅ {efectivo.name} - {'Creado' if created else 'Ya existe'}")
    
    return {
        'transferencia_ves': transferencia_ves,
        'pago_movil': pago_movil,
        'zelle': zelle,
        'transferencia_usd': transferencia_usd,
        'efectivo': efectivo
    }

def setup_company_accounts(payment_methods):
    """Crear cuentas bancarias de ejemplo para LlévateloExpress"""
    
    print("\n🏦 Configurando cuentas bancarias de la empresa...")
    
    # 1. Cuenta Banesco VES (Para transferencias y pago móvil)
    banesco_ves, created = CompanyBankAccount.objects.get_or_create(
        bank_name='Banesco',
        account_number='01340123456789012345',
        currency='VES',
        defaults={
            'account_type': 'business',
            'account_holder': 'LlévateloExpress C.A.',
            'identification_number': 'J-12345678-9',
            'email': 'pagos@llevateloexpress.com',
            'phone': '+58414-1234567',
            'is_active': True,
            'is_default': True,
            'instructions': 'Transferir exactamente el monto indicado. Incluir número de solicitud en concepto.'
        }
    )
    if created:
        banesco_ves.payment_methods.add(
            payment_methods['transferencia_ves'],
            payment_methods['pago_movil']
        )
    print(f"✅ {banesco_ves.bank_name} VES - {'Creado' if created else 'Ya existe'}")
    
    # 2. Cuenta BOD VES (Alternativa)
    bod_ves, created = CompanyBankAccount.objects.get_or_create(
        bank_name='Banco de Venezuela',
        account_number='01020123456789012345',
        currency='VES',
        defaults={
            'account_type': 'business',
            'account_holder': 'LlévateloExpress C.A.',
            'identification_number': 'J-12345678-9',
            'email': 'pagos@llevateloexpress.com',
            'phone': '+58414-1234567',
            'is_active': True,
            'is_default': False,
            'instructions': 'Cuenta alternativa para transferencias y pago móvil en VES.'
        }
    )
    if created:
        bod_ves.payment_methods.add(
            payment_methods['transferencia_ves'],
            payment_methods['pago_movil']
        )
    print(f"✅ {bod_ves.bank_name} VES - {'Creado' if created else 'Ya existe'}")
    
    # 3. Cuenta Zelle USD
    zelle_account, created = CompanyBankAccount.objects.get_or_create(
        bank_name='Zelle',
        account_number='pagos@llevateloexpress.com',
        currency='USD',
        defaults={
            'account_type': 'business',
            'account_holder': 'LlévateloExpress LLC',
            'email': 'pagos@llevateloexpress.com',
            'phone': '+1-555-123-4567',
            'is_active': True,
            'is_default': True,
            'instructions': 'Enviar a: pagos@llevateloexpress.com. Incluir número de solicitud en memo.'
        }
    )
    if created:
        zelle_account.payment_methods.add(payment_methods['zelle'])
    print(f"✅ Zelle USD - {'Creado' if created else 'Ya existe'}")
    
    # 4. Cuenta Internacional USD
    international_usd, created = CompanyBankAccount.objects.get_or_create(
        bank_name='Wells Fargo',
        account_number='1234567890',
        currency='USD',
        defaults={
            'account_type': 'business',
            'account_holder': 'LlévateloExpress LLC',
            'routing_number': '121000248',
            'identification_number': 'EIN: 12-3456789',
            'email': 'international@llevateloexpress.com',
            'phone': '+1-555-123-4567',
            'is_active': True,
            'is_default': False,
            'instructions': '''
            Para transferencias internacionales:
            SWIFT: WFBIUS6S
            Dirección: 420 Montgomery Street, San Francisco, CA 94104
            Beneficiario: LlévateloExpress LLC
            '''
        }
    )
    if created:
        international_usd.payment_methods.add(payment_methods['transferencia_usd'])
    print(f"✅ {international_usd.bank_name} USD - {'Creado' if created else 'Ya existe'}")
    
    return {
        'banesco_ves': banesco_ves,
        'bod_ves': bod_ves,
        'zelle_account': zelle_account,
        'international_usd': international_usd
    }

def main():
    print("🚀 Configurando sistema de pagos para LlévateloExpress")
    print("📍 Enfoque: Mercado venezolano con soporte internacional")
    print("=" * 60)
    
    try:
        # Configurar métodos de pago
        payment_methods = setup_payment_methods()
        
        # Configurar cuentas bancarias
        accounts = setup_company_accounts(payment_methods)
        
        print("\n" + "=" * 60)
        print("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("\n📋 RESUMEN:")
        print(f"   • {len(payment_methods)} métodos de pago configurados")
        print(f"   • {len(accounts)} cuentas bancarias configuradas")
        print("\n🎯 MÉTODOS DISPONIBLES:")
        for method in payment_methods.values():
            print(f"   • {method.name} ({'Activo' if method.is_active else 'Inactivo'})")
        
        print("\n🏦 CUENTAS CONFIGURADAS:")
        for account in accounts.values():
            methods_count = account.payment_methods.count()
            print(f"   • {account.bank_name} ({account.currency}) - {methods_count} métodos")
        
        print("\n🔗 PRÓXIMOS PASOS:")
        print("   1. Crear migraciones: python manage.py makemigrations")
        print("   2. Aplicar migraciones: python manage.py migrate")
        print("   3. Verificar en admin: /admin/financing/paymentmethod/")
        print("   4. Probar APIs: /api/financing/payment-methods/")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("🔧 Asegúrate de que Django esté configurado correctamente")
        sys.exit(1)

if __name__ == '__main__':
    main() 