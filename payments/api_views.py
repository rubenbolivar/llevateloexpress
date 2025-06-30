from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging

from .services.payment_processor import payment_processor
from financing.models import PaymentSchedule

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_mobile_payment(request):
    """
    Endpoint para verificar pago móvil
    POST /api/payments/verify-mobile/
    """
    try:
        data = request.data
        referencia = data.get('referencia')
        telefono_origen = data.get('telefono_origen')
        payment_schedule_id = data.get('payment_schedule_id')
        
        # Validar datos requeridos
        if not referencia or not telefono_origen:
            return Response({
                'success': False,
                'message': 'Referencia y teléfono son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar pago
        result = payment_processor.verify_mobile_payment(
            referencia, 
            telefono_origen, 
            payment_schedule_id
        )
        
        if result.get('verified'):
            return Response({
                'success': True,
                'verified': True,
                'message': result.get('message'),
                'payment_id': result.get('payment_id')
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': True,
                'verified': False,
                'message': result.get('message')
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Error en verify_mobile_payment: {str(e)}")
        return Response({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_methods(request):
    """
    Endpoint para obtener métodos de pago disponibles
    GET /api/payments/methods/
    """
    methods = [
        {
            'id': 'mobile_payment',
            'name': 'Pago Móvil',
            'description': 'Pago a través de transferencia móvil',
            'enabled': True,
            'fields': ['referencia', 'telefono_origen']
        },
        {
            'id': 'transfer',
            'name': 'Transferencia Bancaria',
            'description': 'Transferencia a cuenta bancaria',
            'enabled': True,
            'fields': ['referencia', 'banco_origen']
        }
    ]
    
    return Response({
        'success': True,
        'methods': methods
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_payment_schedule(request):
    """
    Endpoint para obtener calendario de pagos del usuario
    GET /api/payments/schedule/
    """
    try:
        user = request.user
        
        # Obtener schedule de pagos del usuario
        schedules = PaymentSchedule.objects.filter(
            application__customer__user=user
        ).select_related('application').order_by('due_date')
        
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'id': schedule.id,
                'application_number': schedule.application.application_number,
                'payment_number': schedule.payment_number,
                'due_date': schedule.due_date.strftime('%Y-%m-%d'),
                'amount': str(schedule.amount),
                'is_paid': schedule.is_paid,
                'days_late': schedule.days_late,
                'late_fee': str(schedule.late_fee),
                'can_pay': not schedule.is_paid
            })
        
        return Response({
            'success': True,
            'schedule': schedule_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en user_payment_schedule: {str(e)}")
        return Response({
            'success': False,
            'message': 'Error obteniendo calendario'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# ================================
# VISTAS R4 SISTEMA DE PAGOS
# ================================

@api_view(['GET'])
@permission_classes([])
def r4_system_status(request):
    return Response({
        'system': 'R4 Conecta Mi Banco',
        'version': '2.0', 
        'status': 'operational'
    })

@api_view(['POST'])
@permission_classes([])
def r4_simulate(request):
    amount = request.data.get('amount', 0)
    return Response({
        'simulation': {'amount': amount, 'system': 'R4'},
        'success': True
    })

@api_view(['POST'])
@permission_classes([])
def r4_mobile_query(request):
    return Response({
        'query_result': {'system': 'R4', 'found': True},
        'success': True
    })

@api_view(['POST'])
@permission_classes([])
def r4_dispersion(request):
    return Response({
        'dispersion': {'status': 'processed', 'system': 'R4'},
        'success': True
    })
