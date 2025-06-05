#!/usr/bin/env python
"""
Script para probar directamente el endpoint my-requests
y entender por qué el dashboard no muestra las solicitudes.
"""

import os
import sys
import django

# Configurar el entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import Customer
from financing.models import FinancingRequest
from financing.views import CustomerApplicationsView
from financing.serializers.financing_serializers import FinancingRequestListSerializer
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
import json

def test_my_requests_endpoint():
    """Probar el endpoint my-requests directamente"""
    
    print("=== PRUEBA DEL ENDPOINT /api/financing/my-requests/ ===")
    print()
    
    # Usuario de prueba
    test_email = "1@centrodelpan.com"
    
    try:
        # 1. Obtener el usuario
        user = User.objects.get(email=test_email)
        print(f"✅ Usuario encontrado: {user.username} (ID: {user.id})")
        
        # 2. Verificar Customer
        customer = Customer.objects.get(user=user)
        print(f"✅ Customer encontrado: {customer.id}")
        
        # 3. Simular la vista CustomerApplicationsView
        print("\n🔍 SIMULANDO CustomerApplicationsView...")
        
        # Crear un request factory simulado
        factory = RequestFactory()
        request = factory.get('/api/financing/my-requests/')
        request.user = user  # Simular usuario autenticado
        
        # Crear instancia de la vista
        view = CustomerApplicationsView()
        view.request = request
        view.format_kwarg = None
        
        # Obtener el queryset (mismo que usa la vista)
        queryset = view.get_queryset()
        print(f"📊 Queryset resultante: {queryset.count()} solicitudes")
        
        if queryset.exists():
            print("📋 Solicitudes encontradas por la vista:")
            for req in queryset[:5]:  # Mostrar las primeras 5
                print(f"   - #{req.id} | {req.application_number} | {req.status} | {req.created_at}")
        else:
            print("❌ La vista NO retorna solicitudes")
        
        # 4. Probar el serializer
        print("\n🔍 PROBANDO SERIALIZER...")
        
        if queryset.exists():
            serializer = FinancingRequestListSerializer(queryset, many=True)
            serialized_data = serializer.data
            
            print(f"📦 Datos serializados: {len(serialized_data)} solicitudes")
            
            if serialized_data:
                print("📋 Primera solicitud serializada:")
                first_request = serialized_data[0]
                for key, value in first_request.items():
                    print(f"   {key}: {value}")
            
            # Convertir a JSON para verificar que sea válido
            json_data = json.dumps(serialized_data, indent=2, default=str)
            print(f"\n✅ JSON válido generado: {len(json_data)} caracteres")
            
        else:
            print("❌ No hay datos para serializar")
        
        # 5. Verificar directamente el filtro
        print("\n🔍 VERIFICACIÓN DIRECTA DEL FILTRO...")
        
        # Filtro exacto que usa CustomerApplicationsView
        direct_filter = FinancingRequest.objects.filter(
            customer__user=user
        ).order_by('-created_at')
        
        print(f"📊 Filtro directo customer__user={user.id}: {direct_filter.count()} solicitudes")
        
        # Verificar con filtros alternativos
        customer_filter = FinancingRequest.objects.filter(customer=customer)
        print(f"📊 Filtro customer={customer.id}: {customer_filter.count()} solicitudes")
        
        customer_id_filter = FinancingRequest.objects.filter(customer_id=customer.id)
        print(f"📊 Filtro customer_id={customer.id}: {customer_id_filter.count()} solicitudes")
        
        # 6. Verificar problema de autenticación
        print("\n🔍 VERIFICANDO AUTENTICACIÓN...")
        print(f"   - user.is_authenticated: {user.is_authenticated}")
        print(f"   - user.is_active: {user.is_active}")
        print(f"   - user.is_anonymous: {user.is_anonymous}")
        
        # 7. Análisis de conclusiones
        print("\n📋 ANÁLISIS DE RESULTADOS:")
        print("-" * 40)
        
        if queryset.count() > 0:
            print("✅ La vista CustomerApplicationsView SÍ encuentra solicitudes")
            print("❓ El problema podría estar en:")
            print("   - Autenticación en el frontend")
            print("   - Procesamiento de la respuesta en JavaScript")
            print("   - Configuración de CORS o headers")
            print("   - Error en el manejo de la respuesta del API")
        else:
            print("❌ La vista CustomerApplicationsView NO encuentra solicitudes")
            print("❓ Investigar:")
            print("   - ¿Problema de permisos en la vista?")
            print("   - ¿Usuario no está siendo pasado correctamente?")
            print("   - ¿Filtro customer__user no funciona?")
        
    except User.DoesNotExist:
        print(f"❌ Usuario {test_email} no existe")
    except Customer.DoesNotExist:
        print(f"❌ Customer no existe para el usuario")
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_my_requests_endpoint() 