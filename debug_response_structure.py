#!/usr/bin/env python
"""
Script para investigar la estructura exacta de datos que retorna 
el endpoint /api/financing/my-requests/
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
import json

def investigate_response_structure():
    """Investigar la estructura exacta de la respuesta del endpoint"""
    
    print("=== INVESTIGACIÓN DE ESTRUCTURA DE RESPUESTA ===")
    print()
    
    test_email = "1@centrodelpan.com"
    
    try:
        # 1. Obtener usuario y customer
        user = User.objects.get(email=test_email)
        customer = Customer.objects.get(user=user)
        print(f"✅ Usuario: {user.username} (ID: {user.id})")
        print(f"✅ Customer: {customer.id}")
        
        # 2. Simular la vista exacta
        factory = RequestFactory()
        request = factory.get('/api/financing/my-requests/')
        request.user = user
        
        view = CustomerApplicationsView()
        view.request = request
        view.format_kwarg = None
        
        # 3. Obtener queryset
        queryset = view.get_queryset()
        print(f"\n📊 Queryset: {queryset.count()} solicitudes")
        
        # 4. Usar el serializer exacto
        serializer = FinancingRequestListSerializer(queryset, many=True)
        serialized_data = serializer.data
        
        print(f"\n🔍 ANÁLISIS DE LA ESTRUCTURA:")
        print(f"   - Tipo de serialized_data: {type(serialized_data)}")
        print(f"   - Es lista: {isinstance(serialized_data, list)}")
        print(f"   - Longitud: {len(serialized_data) if hasattr(serialized_data, '__len__') else 'N/A'}")
        
        # 5. Mostrar estructura de la primera solicitud
        if serialized_data and len(serialized_data) > 0:
            print(f"\n📋 PRIMERA SOLICITUD (estructura):")
            first_item = serialized_data[0]
            print(f"   - Tipo: {type(first_item)}")
            print(f"   - Claves: {list(first_item.keys()) if hasattr(first_item, 'keys') else 'N/A'}")
            
            print(f"\n📋 PRIMERA SOLICITUD (datos completos):")
            print(json.dumps(first_item, indent=2, default=str))
        
        # 6. Simular la respuesta completa como la vería el frontend
        # Esto simula exactamente lo que retorna API.users.authFetch()
        simulated_api_response = {
            'success': True,
            'data': serialized_data  # ← AQUÍ ESTÁ LA CLAVE
        }
        
        print(f"\n🎯 RESPUESTA SIMULADA DEL API:")
        print(f"   - Tipo de response: {type(simulated_api_response)}")
        print(f"   - Claves de response: {list(simulated_api_response.keys())}")
        print(f"   - Tipo de response.data: {type(simulated_api_response['data'])}")
        print(f"   - Es lista response.data: {isinstance(simulated_api_response['data'], list)}")
        
        # 7. Verificar lo que el frontend estaría recibiendo
        frontend_data = simulated_api_response['data']
        
        print(f"\n🔧 LO QUE DEBERÍA PROCESAR EL FRONTEND:")
        print(f"   - requestsResult.success: {simulated_api_response['success']}")
        print(f"   - requestsResult.data: {type(frontend_data)} con {len(frontend_data)} elementos")
        
        # 8. Probar si .map() funcionaría
        try:
            # Simular el código del frontend
            if hasattr(frontend_data, '__iter__') and not isinstance(frontend_data, str):
                test_map = [f"Solicitud {item.get('id', 'N/A')}" for item in frontend_data]
                print(f"   ✅ .map() FUNCIONARÍA: {len(test_map)} elementos procesados")
                print(f"   📝 Ejemplo: {test_map[:3]}...")
            else:
                print(f"   ❌ .map() NO FUNCIONARÍA: {type(frontend_data)} no es iterable")
        except Exception as e:
            print(f"   ❌ .map() FALLARÍA: {e}")
        
        # 9. Mostrar formato JSON exacto que llegará al frontend
        print(f"\n📤 JSON EXACTO PARA EL FRONTEND:")
        json_response = json.dumps(simulated_api_response, indent=2, default=str)
        print(json_response[:500] + "..." if len(json_response) > 500 else json_response)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_response_structure() 