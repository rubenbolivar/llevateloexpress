#!/usr/bin/env python
"""
Script de diagnóstico para investigar el problema del dashboard vacío
donde las solicitudes son visibles en el admin pero no en el dashboard del usuario.
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
from django.db.models import Q
import traceback

def diagnostic_dashboard_issue():
    """Diagnosticar el problema del dashboard vacío"""
    
    print("=== DIAGNÓSTICO DEL PROBLEMA DEL DASHBOARD ===")
    print()
    
    # Usuario de prueba
    test_email = "1@centrodelpan.com"
    
    print(f"🔍 Investigando usuario: {test_email}")
    print("-" * 50)
    
    try:
        # 1. Verificar que el usuario existe
        print("1. VERIFICACIÓN DEL USUARIO")
        try:
            user = User.objects.get(email=test_email)
            print(f"   ✅ Usuario encontrado:")
            print(f"      - ID: {user.id}")
            print(f"      - Username: {user.username}")
            print(f"      - Email: {user.email}")
            print(f"      - Nombre: {user.first_name} {user.last_name}")
            print(f"      - Activo: {user.is_active}")
            print(f"      - Fecha registro: {user.date_joined}")
        except User.DoesNotExist:
            print(f"   ❌ Usuario con email {test_email} NO EXISTE")
            return
        
        print()
        
        # 2. Verificar Customer asociado
        print("2. VERIFICACIÓN DEL CUSTOMER")
        try:
            customer = Customer.objects.get(user=user)
            print(f"   ✅ Customer encontrado:")
            print(f"      - ID: {customer.id}")
            print(f"      - Teléfono: {customer.phone}")
            print(f"      - Documento: {customer.identity_document}")
            print(f"      - Verificado: {customer.verified}")
            print(f"      - Perfil completo: {customer.is_profile_complete}")
            print(f"      - Fecha creación: {customer.created_at}")
        except Customer.DoesNotExist:
            print(f"   ❌ NO EXISTE Customer para este usuario")
            print(f"   🔧 POSIBLE SOLUCIÓN: Crear Customer automáticamente")
            customer = None
        
        print()
        
        # 3. Verificar solicitudes de financiamiento
        print("3. VERIFICACIÓN DE SOLICITUDES DE FINANCIAMIENTO")
        
        # 3a. Todas las solicitudes en el sistema
        all_requests = FinancingRequest.objects.all().order_by('-created_at')
        print(f"   📊 Total de solicitudes en el sistema: {all_requests.count()}")
        
        if all_requests.exists():
            print(f"   📋 Últimas 5 solicitudes en el sistema:")
            for req in all_requests[:5]:
                customer_info = "SIN CUSTOMER" if not req.customer else f"Customer {req.customer.id}"
                user_info = "SIN USER" if not req.customer or not req.customer.user else f"User {req.customer.user.email}"
                print(f"      - #{req.id} | {req.application_number} | {customer_info} | {user_info}")
        
        print()
        
        # 3b. Solicitudes filtradas por el Customer (como en CustomerApplicationsView)
        if customer:
            customer_requests = FinancingRequest.objects.filter(customer=customer).order_by('-created_at')
            print(f"   🎯 Solicitudes del Customer {customer.id}: {customer_requests.count()}")
            
            if customer_requests.exists():
                print(f"   📋 Solicitudes del Customer:")
                for req in customer_requests:
                    print(f"      - #{req.id} | {req.application_number} | {req.status} | {req.created_at}")
            else:
                print(f"   ❌ NO HAY solicitudes para este Customer")
        else:
            print(f"   ⚠️  No se puede verificar solicitudes sin Customer")
        
        print()
        
        # 3c. Buscar solicitudes que podrían estar mal asociadas
        print("4. BÚSQUEDA DE SOLICITUDES MAL ASOCIADAS")
        
        # Solicitudes sin customer
        orphan_requests = FinancingRequest.objects.filter(customer__isnull=True)
        print(f"   🔍 Solicitudes sin Customer: {orphan_requests.count()}")
        
        # Solicitudes con customers que no tienen user
        broken_requests = FinancingRequest.objects.filter(customer__user__isnull=True)
        print(f"   🔍 Solicitudes con Customer sin User: {broken_requests.count()}")
        
        # Buscar por patrón del application_number o datos similares
        similar_requests = FinancingRequest.objects.filter(
            Q(notes__icontains=test_email) |
            Q(application_number__icontains="202500") |
            Q(customer__user__email__icontains="centrodelpan")
        ).order_by('-created_at')
        
        print(f"   🔍 Solicitudes que podrían estar relacionadas: {similar_requests.count()}")
        
        if similar_requests.exists():
            print(f"   📋 Posibles solicitudes relacionadas:")
            for req in similar_requests:
                customer_email = "SIN EMAIL" if not req.customer or not req.customer.user else req.customer.user.email
                print(f"      - #{req.id} | {req.application_number} | Customer: {customer_email}")
        
        print()
        
        # 4. Diagnóstico del endpoint my-requests
        print("5. SIMULACIÓN DEL ENDPOINT /api/financing/my-requests/")
        
        if customer:
            # Simular el query que hace CustomerApplicationsView
            dashboard_requests = FinancingRequest.objects.filter(
                customer__user=user
            ).order_by('-created_at')
            
            print(f"   🎯 Resultado del filtro customer__user={user.id}: {dashboard_requests.count()} solicitudes")
            
            if dashboard_requests.exists():
                print(f"   ✅ El dashboard DEBERÍA mostrar {dashboard_requests.count()} solicitudes")
                for req in dashboard_requests:
                    print(f"      - #{req.id} | {req.application_number} | {req.status}")
            else:
                print(f"   ❌ El dashboard NO MOSTRARÁ solicitudes (problema confirmado)")
        else:
            print(f"   ❌ Sin Customer, el endpoint retornará 0 solicitudes")
        
        print()
        
        # 5. Recomendaciones
        print("6. RECOMENDACIONES")
        print("-" * 30)
        
        if not customer:
            print("   🔧 SOLUCIÓN PRIORITARIA:")
            print("      - Crear registro Customer para este usuario")
            print("      - Verificar proceso de registro en frontend")
            print("      - Implementar creación automática de Customer")
        
        if customer and customer_requests.count() == 0:
            print("   🔧 INVESTIGAR:")
            print("      - ¿Se están creando las solicitudes correctamente?")
            print("      - ¿Se está asociando el Customer correcto en el momento de creación?")
            print("      - Revisar el proceso de creación de solicitudes en el frontend")
        
        if similar_requests.exists() and (not customer or customer_requests.count() == 0):
            print("   🔧 POSIBLE REPARACIÓN:")
            print("      - Verificar si hay solicitudes que deben ser re-asociadas")
            print("      - Implementar script de migración de solicitudes órfanas")
        
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    diagnostic_dashboard_issue() 