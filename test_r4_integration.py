#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/var/www/llevateloexpress')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

def test_r4_configuration():
    print("🧪 PROBANDO CONFIGURACIÓN R4 CONECTA...")
    print("-" * 50)
    
    try:
        # Test 1: Importar configuración
        from django.conf import settings
        print(f"✅ Configuración Django cargada")
        print(f"✅ URL Base R4: {getattr(settings, 'R4_BASE_URL', 'NO CONFIGURADO')}")
        print(f"✅ Commerce Token configurado: {'SÍ' if getattr(settings, 'R4_COMMERCE_TOKEN', '') else 'NO'}")
        print(f"✅ Debug R4: {getattr(settings, 'R4_DEBUG', False)}")
        
        # Test 2: Importar cliente R4
        from payments.services.r4_client import r4_client
        print(f"✅ Cliente R4 importado correctamente")
        
        # Test 3: Importar procesador
        from payments.services.payment_processor import payment_processor
        print(f"✅ Procesador de pagos importado correctamente")
        
        # Test 4: Probar HMAC utils
        from payments.services.hmac_utils import generate_hmac_signature
        test_signature = generate_hmac_signature("test", "key")
        print(f"✅ Utilidades HMAC funcionando (test: {test_signature[:8]}...)")
        
        print("\n✅ CONFIGURACIÓN BÁSICA CORRECTA!")
        
        # Test 5: Probar conexión solo si hay token
        commerce_token = getattr(settings, 'R4_COMMERCE_TOKEN', '')
        if commerce_token and commerce_token != 'TU_COMMERCE_TOKEN_AQUI':
            print("\n🔍 Probando conexión R4...")
            referencia = "12345678"
            telefono = "04141234567"
            
            result = r4_client.consulta_pago_movil(referencia, telefono)
            print(f"📋 RESULTADO CONEXIÓN:")
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
            
            if result.get('success'):
                print(f"   ✅ Conexión R4 exitosa!")
            else:
                print(f"   ⚠️ Respuesta R4: {result}")
        else:
            print("\n⚠️ Commerce Token no configurado - saltando prueba de conexión")
            print("   Para probar conexión real, configura R4_COMMERCE_TOKEN en .env.production")
        
    except ImportError as e:
        print(f"❌ Error de importación: {str(e)}")
        print("Verificar que todas las dependencias estén instaladas")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("-" * 50)
    print("🏁 Prueba completada")

if __name__ == "__main__":
    test_r4_configuration()
