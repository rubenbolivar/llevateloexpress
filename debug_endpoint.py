# DEBUGGING ENDPOINT - TEMPORAL
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Customer
from django.utils import timezone
import json

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def debug_financing_request(request):
    """
    Endpoint temporal para debugging del problema de solicitudes.
    CERO RIESGO - Solo recolecta información.
    """
    debug_info = {
        'timestamp': str(timezone.now()),
        'user_info': {
            'user_id': request.user.id,
            'username': request.user.username,
            'is_authenticated': request.user.is_authenticated,
            'has_customer_attr': hasattr(request.user, 'customer'),
        },
        'customer_info': {
            'customer_count': Customer.objects.filter(user=request.user).count(),
            'customer_exists': Customer.objects.filter(user=request.user).exists(),
        },
        'request_data': dict(request.data),
        'request_method': request.method,
        'content_type': request.content_type,
    }
    
    # Intentar acceder a customer de diferentes maneras
    try:
        customer_direct = Customer.objects.get(user=request.user)
        debug_info['customer_direct'] = {
            'success': True,
            'customer_id': customer_direct.id,
            'verified': customer_direct.verified,
            'is_profile_complete': customer_direct.is_profile_complete,
        }
    except Customer.DoesNotExist:
        debug_info['customer_direct'] = {
            'success': False,
            'error': 'Customer.DoesNotExist'
        }
    except Exception as e:
        debug_info['customer_direct'] = {
            'success': False,
            'error': str(e)
        }
    
    # Intentar el método problemático
    try:
        customer_property = request.user.customer
        debug_info['customer_property'] = {
            'success': True,
            'result': str(customer_property)
        }
    except Exception as e:
        debug_info['customer_property'] = {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }
    
    return Response({
        'status': 'debug_success',
        'message': 'Información de debugging recolectada',
        'debug_data': debug_info
    }) 