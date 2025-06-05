#!/usr/bin/env python3
"""
Script para crear una solicitud de financiamiento de prueba
"""
import os
import sys
import django
from datetime import datetime
import uuid

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from financing.models import FinancingRequest, FinancingPlan, Product
from users.models import Customer

def crear_solicitud_credito_inmediato():
    """Crea una nueva solicitud de crédito inmediato"""
    try:
        # Datos para la solicitud
        print("🔍 Obteniendo datos necesarios...")
        
        # Cliente
        customer = Customer.objects.first()
        if not customer:
            print("❌ Error: No hay clientes en el sistema")
            return False
        print(f"✅ Cliente: ID {customer.id}")
        
        # Producto Voge SR4
        try:
            product = Product.objects.get(id=6)  # Voge SR4
            print(f"✅ Producto: {product.name} - ${product.price:,.0f}")
        except Product.DoesNotExist:
            print("❌ Error: Producto Voge SR4 no encontrado")
            return False
        
        # Plan Crédito Inmediato 35%
        try:
            plan = FinancingPlan.objects.get(id=5)  # Crédito Inmediato 35%
            print(f"✅ Plan: {plan.name}")
        except FinancingPlan.DoesNotExist:
            print("❌ Error: Plan de financiamiento no encontrado")
            return False
        
        # Contar solicitudes antes
        count_before = FinancingRequest.objects.count()
        print(f"📊 Solicitudes antes: {count_before}")
        
        # Generar número de aplicación único
        app_number = f"CR-TEST-{uuid.uuid4().hex[:8].upper()}"
        
        # Calcular valores financieros
        product_price = float(product.price)
        down_payment_pct = 35
        down_payment_amount = product_price * (down_payment_pct / 100)
        financed_amount = product_price - down_payment_amount
        number_of_payments = 24
        payment_amount = financed_amount / number_of_payments
        
        print("💰 Cálculos financieros:")
        print(f"   Precio: ${product_price:,.2f}")
        print(f"   Inicial ({down_payment_pct}%): ${down_payment_amount:,.2f}")
        print(f"   Financiado: ${financed_amount:,.2f}")
        print(f"   Cuota mensual: ${payment_amount:,.2f}")
        
        # Crear la solicitud
        print("🚀 Creando solicitud...")
        new_request = FinancingRequest.objects.create(
            application_number=app_number,
            customer=customer,
            product=product,
            financing_plan=plan,
            status='pending',
            product_price=product_price,
            down_payment_percentage=down_payment_pct,
            down_payment_amount=down_payment_amount,
            financed_amount=financed_amount,
            interest_rate=0.0,
            total_interest=0.0,
            total_amount=product_price,
            payment_frequency='monthly',
            number_of_payments=number_of_payments,
            payment_amount=payment_amount,
            employment_type='empleado',
            monthly_income=800.00
        )
        
        # Verificar creación
        count_after = FinancingRequest.objects.count()
        
        print("\n🎉 ¡SOLICITUD CREADA EXITOSAMENTE!")
        print(f"📝 ID: {new_request.id}")
        print(f"📋 Número: {new_request.application_number}")
        print(f"👤 Cliente: ID {customer.id}")
        print(f"🏍️ Producto: {product.name}")
        print(f"💰 Plan: {plan.name}")
        print(f"📊 Estado: {new_request.status}")
        print(f"📈 Solicitudes antes: {count_before}")
        print(f"📈 Solicitudes después: {count_after}")
        print(f"📅 Creada: {new_request.created_at}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear solicitud: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando creación de solicitud de prueba...")
    success = crear_solicitud_credito_inmediato()
    if success:
        print("✅ Script completado exitosamente")
    else:
        print("❌ Script falló")
        sys.exit(1) 