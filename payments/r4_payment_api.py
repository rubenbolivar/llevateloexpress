#\!/usr/bin/env python3
"""
R4 Payment Integration Views
Integración completa de botón de pago móvil R4 con el sistema existente
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
from financing.models import FinancingRequest, Payment, PaymentSchedule, PaymentMethod
from users.models import Customer
import logging
import uuid
import json

logger = logging.getLogger(__name__)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_r4_payment(request):
    """
    Iniciar pago móvil R4 directo desde el dashboard
    
    Request JSON:
    {
        "financing_request_id": 123,
        "payment_schedule_id": 456,  // Opcional: cuota específica
        "amount": "150.00",
        "payment_type": "installment",  // o "down_payment"
        "customer_notes": "Pago cuota #3"
    }
    """
    try:
        # Validar datos de entrada
        financing_request_id = request.data.get("financing_request_id")
        payment_schedule_id = request.data.get("payment_schedule_id")
        amount = request.data.get("amount")
        payment_type = request.data.get("payment_type", "installment")
        customer_notes = request.data.get("customer_notes", "")

        if not all([financing_request_id, amount]):
            return Response({
                "success": False,
                "error": "Faltan campos requeridos: financing_request_id, amount"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que la solicitud pertenece al usuario
        try:
            customer = Customer.objects.get(user=request.user)
            financing_request = FinancingRequest.objects.get(
                id=financing_request_id,
                customer=customer,
                status="approved"
            )
        except (Customer.DoesNotExist, FinancingRequest.DoesNotExist):
            return Response({
                "success": False,
                "error": "Solicitud de financiamiento no encontrada o no autorizada"
            }, status=status.HTTP_404_NOT_FOUND)

        # Verificar cuota específica si se proporciona
        payment_schedule = None
        if payment_schedule_id:
            try:
                payment_schedule = PaymentSchedule.objects.get(
                    id=payment_schedule_id,
                    financing_request=financing_request
                )
                if payment_schedule.is_paid:
                    return Response({
                        "success": False,
                        "error": "Esta cuota ya fue pagada"
                    }, status=status.HTTP_400_BAD_REQUEST)
            except PaymentSchedule.DoesNotExist:
                return Response({
                    "success": False,
                    "error": "Cuota no encontrada"
                }, status=status.HTTP_404_NOT_FOUND)

        # Obtener método de pago R4
        try:
            r4_payment_method = PaymentMethod.objects.get(
                payment_type="mobile_payment",
                name__icontains="R4",
                is_active=True
            )
        except PaymentMethod.DoesNotExist:
            # Si no existe método R4 específico, usar pago móvil genérico
            try:
                r4_payment_method = PaymentMethod.objects.get(
                    payment_type="mobile_payment",
                    is_active=True
                )
            except PaymentMethod.DoesNotExist:
                return Response({
                    "success": False,
                    "error": "Método de pago móvil no disponible"
                }, status=status.HTTP_400_BAD_REQUEST)

        # Generar referencia única para R4
        payment_reference = f"R4{uuid.uuid4().hex[:8].upper()}"

        # Crear registro de pago con estado pendiente R4
        with transaction.atomic():
            payment = Payment.objects.create(
                application=financing_request,
                payment_schedule=payment_schedule,
                payment_type=payment_type,
                payment_method="mobile_payment",
                amount=float(amount),
                currency="VES",  # R4 maneja bolívares
                payment_date=timezone.now(),
                status="pending",
                reference_number=payment_reference,
                customer_notes=customer_notes,
                notes=f"Pago R4 iniciado - Referencia: {payment_reference}",
                
                # Información del cliente para R4
                sender_name=customer.user.get_full_name() or customer.user.username,
                sender_identification=customer.identity_document,
                
                # Control administrativo
                submitted_by=request.user,
                recorded_by=request.user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")
            )

            logger.info(f"Pago R4 iniciado - Usuario: {request.user.email}, Monto: {amount}, Ref: {payment_reference}")

        # Obtener información de la cuenta R4 de la empresa
        company_r4_info = {
            "phone": "04141234567",  # Configurar en settings
            "name": "LlévateloExpress C.A.",
            "rif": "J-123456789"
        }

        return Response({
            "success": True,
            "message": "Pago móvil R4 iniciado correctamente",
            "payment_id": payment.id,
            "reference": payment_reference,
            "r4_info": company_r4_info,
            "instructions": {
                "step1": "Abre tu app de pago móvil",
                "step2": f"Paga Bs. {amount} al teléfono {company_r4_info[phone]}",
                "step3": f"Usa la referencia: {payment_reference}",
                "step4": "El pago se confirmará automáticamente vía R4",
                "step5": "Recibirás notificación cuando se procese"
            },
            "redirect_url": "/dashboard.html?payment_initiated=" + str(payment.id)
        })

    except Exception as e:
        logger.error(f"Error iniciando pago R4: {str(e)}")
        return Response({
            "success": False,
            "error": "Error interno del servidor"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_r4_payment_status(request, payment_id):
    """
    Consultar estado de un pago R4 específico
    """
    try:
        # Verificar que el pago pertenece al usuario
        customer = Customer.objects.get(user=request.user)
        payment = Payment.objects.get(
            id=payment_id,
            application__customer=customer,
            payment_method="mobile_payment"
        )

        # Determinar estado R4 basado en estado actual
        r4_status_map = {
            "pending": "waiting_payment",
            "verified": "confirmed", 
            "rejected": "rejected",
            "processing": "verifying"
        }

        return Response({
            "success": True,
            "payment_id": payment.id,
            "reference": payment.reference_number,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status,
            "r4_status": r4_status_map.get(payment.status, "unknown"),
            "submitted_at": payment.submitted_at.isoformat(),
            "verified_at": payment.verified_at.isoformat() if payment.verified_at else None,
            "notes": payment.notes
        })

    except (Customer.DoesNotExist, Payment.DoesNotExist):
        return Response({
            "success": False,
            "error": "Pago no encontrado"
        }, status=status.HTTP_404_NOT_FOUND)

def get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
