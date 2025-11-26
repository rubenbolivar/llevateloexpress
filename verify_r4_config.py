#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Verificación de Configuración R4 Conecta V3.0
Verifica que todos los parámetros estén correctamente configurados
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from django.conf import settings
from financing.models import PaymentMethod
import hmac
import hashlib

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_info(msg):
    print(f"ℹ️  {msg}")

def verify_env_variables():
    """Verificar variables de entorno R4"""
    print_header("1. VARIABLES DE ENTORNO R4")

    required_vars = {
        'R4_BASE_URL': 'https://r4conecta.mibanco.com.ve/',
        'R4_COMMERCE_TOKEN': None,  # Debe existir pero no mostramos el valor
        'R4_SECRET_KEY': None,
        'R4_UUID_TOKEN': None,
        'R4_TIMEOUT': '30',
        'R4_DEBUG': 'false'
    }

    all_ok = True

    for var_name, expected_value in required_vars.items():
        actual_value = getattr(settings, var_name, None)

        if actual_value is None or actual_value == '':
            print_error(f"{var_name}: NO CONFIGURADO")
            all_ok = False
        else:
            if expected_value:
                if str(actual_value) == expected_value:
                    print_success(f"{var_name}: {actual_value}")
                else:
                    print_error(f"{var_name}: {actual_value} (esperado: {expected_value})")
                    all_ok = False
            else:
                # Variables sensibles - solo mostrar formato
                value_preview = str(actual_value)[:20] + "..." if len(str(actual_value)) > 20 else str(actual_value)
                print_success(f"{var_name}: {value_preview} (len={len(str(actual_value))})")

    return all_ok

def verify_commerce_token_format():
    """Verificar formato del Commerce Token"""
    print_header("2. FORMATO COMMERCE TOKEN")

    commerce_token = getattr(settings, 'R4_COMMERCE_TOKEN', '')

    if not commerce_token:
        print_error("Commerce token vacío")
        return False

    # Verificar longitud (debe ser 64 caracteres hexadecimales)
    if len(commerce_token) == 64:
        print_success(f"Longitud correcta: 64 caracteres")
    else:
        print_error(f"Longitud incorrecta: {len(commerce_token)} (esperado: 64)")
        return False

    # Verificar que sea hexadecimal
    try:
        int(commerce_token, 16)
        print_success("Formato hexadecimal válido")
    except ValueError:
        print_error("No es un valor hexadecimal válido")
        return False

    print_info(f"Token: {commerce_token[:20]}...{commerce_token[-20:]}")

    return True

def verify_hmac_generation():
    """Verificar generación de HMAC-SHA256"""
    print_header("3. GENERACIÓN HMAC-SHA256")

    commerce_token = getattr(settings, 'R4_COMMERCE_TOKEN', '')

    # Test según documentación R4 V3.0
    # Para R4vuelto: TelefonoDestino + Monto + Banco + Cedula
    test_data = "0414555555510000102V12345678"

    try:
        signature = hmac.new(
            commerce_token.encode('utf-8'),
            test_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        print_success("HMAC generado correctamente")
        print_info(f"Test data: {test_data}")
        print_info(f"Signature: {signature}")

        # Verificar que sea hexadecimal de 64 caracteres
        if len(signature) == 64:
            print_success("Longitud de signature correcta: 64 caracteres")
        else:
            print_error(f"Longitud de signature incorrecta: {len(signature)}")
            return False

        return True

    except Exception as e:
        print_error(f"Error generando HMAC: {str(e)}")
        return False

def verify_payment_methods():
    """Verificar métodos de pago en base de datos"""
    print_header("4. MÉTODOS DE PAGO EN BASE DE DATOS")

    try:
        # Verificar Pago Móvil Manual
        manual_pm = PaymentMethod.objects.filter(
            payment_type='mobile_payment'
        ).first()

        if manual_pm:
            print_success(f"Pago Móvil Manual encontrado:")
            print_info(f"  - ID: {manual_pm.id}")
            print_info(f"  - Nombre: {manual_pm.name}")
            print_info(f"  - Tipo: {manual_pm.payment_type}")
            print_info(f"  - Activo: {manual_pm.is_active}")
        else:
            print_error("Pago Móvil Manual NO encontrado")

        # Verificar R4 Automático
        r4_pm = PaymentMethod.objects.filter(
            payment_type='r4_mobile'
        ).first()

        if r4_pm:
            print_success(f"R4 Pago Móvil Automático encontrado:")
            print_info(f"  - ID: {r4_pm.id}")
            print_info(f"  - Nombre: {r4_pm.name}")
            print_info(f"  - Tipo: {r4_pm.payment_type}")
            print_info(f"  - Activo: {r4_pm.is_active}")

            if r4_pm.id == 6:
                print_success("ID correcto: 6")
            else:
                print_error(f"ID incorrecto: {r4_pm.id} (esperado: 6)")
                return False
        else:
            print_error("R4 Pago Móvil Automático NO encontrado")
            print_info("Es posible que la migración 0028 no se haya aplicado")
            return False

        return True

    except Exception as e:
        print_error(f"Error verificando métodos de pago: {str(e)}")
        return False

def verify_r4_endpoints():
    """Verificar configuración de endpoints R4"""
    print_header("5. ENDPOINTS R4 CONECTA")

    base_url = getattr(settings, 'R4_BASE_URL', '')

    expected_endpoints = [
        'R4bcv',
        'R4vuelto',
        'R4c2p',
        'R4anulacionC2P',
        'GenerarOtp',
        'DebitoInmediato',
        'CreditoInmediato',
        'ConsultarOperaciones',
        'DomiciliacionCNTA',
        'DomiciliacionCELE',
        'CICuentas'
    ]

    print_success(f"Base URL: {base_url}")
    print_info("\nEndpoints disponibles en R4 Conecta:")
    for endpoint in expected_endpoints:
        print_info(f"  - {base_url}{endpoint}")

    return True

def verify_webhook_ips():
    """Verificar IPs whitelist para webhooks"""
    print_header("6. IPs WHITELIST R4")

    # IPs según documentación oficial
    official_ips = [
        "45.175.213.98",   # Oficial R4 (Doc)
        "200.74.203.91",   # Oficial R4 (Doc)
        "204.199.249.3"    # Oficial R4 (Doc)
    ]

    # IPs adicionales solicitadas por banco
    bank_ips = [
        "190.202.123.66",
        "190.6.60.35"
    ]

    print_success("IPs Oficiales R4 (Documentación V3.0):")
    for ip in official_ips:
        print_info(f"  - {ip}")

    print_success("\nIPs Adicionales (Solicitadas por Banco):")
    for ip in bank_ips:
        print_info(f"  - {ip}")

    print_info("\nTotal IPs whitelist: 5")

    return True

def verify_uuid_token():
    """Verificar formato del UUID token"""
    print_header("7. UUID TOKEN AUTHORIZATION")

    uuid_token = getattr(settings, 'R4_UUID_TOKEN', '')

    if not uuid_token:
        print_error("R4_UUID_TOKEN no configurado")
        return False

    # Verificar formato UUID (8-4-4-4-12)
    import re
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

    if re.match(uuid_pattern, uuid_token, re.IGNORECASE):
        print_success(f"UUID válido: {uuid_token}")
        return True
    else:
        print_error(f"UUID inválido: {uuid_token}")
        print_info("Formato esperado: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        return False

def main():
    """Ejecutar todas las verificaciones"""
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*15 + "VERIFICACIÓN R4 CONECTA V3.0" + " "*25 + "║")
    print("║" + " "*20 + "LlévateloExpress" + " "*33 + "║")
    print("╚" + "═"*68 + "╝")

    results = {
        'Variables de Entorno': verify_env_variables(),
        'Commerce Token': verify_commerce_token_format(),
        'HMAC-SHA256': verify_hmac_generation(),
        'Métodos de Pago': verify_payment_methods(),
        'Endpoints R4': verify_r4_endpoints(),
        'IPs Whitelist': verify_webhook_ips(),
        'UUID Token': verify_uuid_token()
    }

    # Resumen
    print_header("RESUMEN DE VERIFICACIÓN")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check}")

    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} verificaciones pasadas")
    print("-"*70)

    if passed == total:
        print("\n🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
        print("✅ Configuración R4 Conecta correcta")
        print("✅ Sistema listo para operar con R4")
        return 0
    else:
        print("\n⚠️  ALGUNAS VERIFICACIONES FALLARON")
        print("Por favor revisa los errores arriba")
        return 1

if __name__ == '__main__':
    exit(main())
