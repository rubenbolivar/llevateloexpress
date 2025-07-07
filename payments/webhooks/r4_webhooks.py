import logging
import uuid
from datetime import datetime
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.conf import settings
from django.contrib.auth.models import User
from financing.models import Payment, FinancingRequest, Customer
from payments.services.payment_processor import payment_processor
import json

logger = logging.getLogger(__name__)

# IPs oficiales de R4 Conecta según documentación
R4_ALLOWED_IPS = [
    '45.175.213.98',
    '200.74.203.91', 
    '190.202.123.66'
]

def get_client_ip(request):
    """Obtiene la IP real del cliente considerando proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def validate_r4_ip(request):
    """Valida que la request venga de IPs autorizadas de R4"""
    client_ip = get_client_ip(request)
    
    # En desarrollo, permitir localhost
    if settings.DEBUG and client_ip in ['127.0.0.1', '::1']:
        return True
        
    return client_ip in R4_ALLOWED_IPS

def validate_authorization_header(request):
    """Valida el header de autorización UUID de R4"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    if not auth_header:
        return False
    
    try:
        # Validar que sea un UUID válido
        uuid.UUID(auth_header)
        return True
    except ValueError:
        return False

@csrf_exempt
@require_http_methods(["POST"])
def r4_notification_webhook(request):
    """
    Webhook MBnotifica - Recibe notificaciones de pagos móviles entrantes P2P/P2C
    
    Endpoint: /api/payments/webhooks/r4/notify/
    Documentación oficial: MBnotifica
    """
    try:
        # 1. Validar IP de origen
        if not validate_r4_ip(request):
            client_ip = get_client_ip(request)
            logger.warning(f"Webhook R4 rechazado - IP no autorizada: {client_ip}")
            return HttpResponseForbidden("IP no autorizada")
        
        # 2. Validar header Authorization UUID
        if not validate_authorization_header(request):
            logger.warning("Webhook R4 rechazado - Authorization header inválido")
            return JsonResponse({
                'abono': False,
                'error': 'Authorization header requerido (UUID)'
            }, status=400)
        
        # 3. Parsear datos JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            logger.error("Webhook R4 - Error parsing JSON")
            return JsonResponse({
                'abono': False,
                'error': 'JSON inválido'
            }, status=400)
        
        # 4. Validar campos requeridos según documentación
        required_fields = [
            'IdComercio', 'TelefonoComercio', 'TelefonoEmisor',
            'BancoEmisor', 'Monto', 'FechaHora', 'Referencia', 'CodigoRed'
        ]
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            logger.error(f"Webhook R4 - Campos faltantes: {missing_fields}")
            return JsonResponse({
                'abono': False,
                'error': f'Campos requeridos faltantes: {missing_fields}'
            }, status=400)
        
        # 5. Extraer datos
        id_comercio = data.get('IdComercio')
        telefono_comercio = data.get('TelefonoComercio')
        telefono_emisor = data.get('TelefonoEmisor')
        concepto = data.get('Concepto', '')
        banco_emisor = data.get('BancoEmisor')
        monto = data.get('Monto')
        fecha_hora = data.get('FechaHora')
        referencia = data.get('Referencia')
        codigo_red = data.get('CodigoRed')
        
        logger.info(f"Webhook R4 - Notificación recibida: {referencia} por {monto}")
        
        # 6. Validar código de red (debe ser "00" para transacción exitosa)
        if codigo_red != "00":
            logger.warning(f"Webhook R4 - Código de red no exitoso: {codigo_red}")
            return JsonResponse({
                'abono': False,
                'message': f'Transacción no exitosa - Código: {codigo_red}'
            })
        
        # 7. Verificar si ya existe un pago con esta referencia
        existing_payment = Payment.objects.filter(
            reference_number=referencia,
            payment_method='mobile_payment'
        ).first()
        
        if existing_payment:
            logger.info(f"Webhook R4 - Pago ya existe: {referencia}")
            return JsonResponse({
                'abono': True,
                'message': 'Pago ya procesado anteriormente'
            })
        
        # 8. Buscar solicitud de financiamiento activa
        # Intentar encontrar por teléfono del cliente o por identificación
        financing_request = None
        
        # Buscar por teléfono del emisor
        customers = Customer.objects.filter(
            phone_number=telefono_emisor
        ).select_related('user')
        
        if customers.exists():
            financing_request = FinancingRequest.objects.filter(
                customer__in=customers,
                status__in=['approved', 'active']
            ).order_by('-created_at').first()
        
        # Si no se encuentra, buscar por ID de comercio (podría ser cédula)
        if not financing_request:
            try:
                customers_by_id = Customer.objects.filter(
                    identity_document=id_comercio
                ).select_related('user')
                
                if customers_by_id.exists():
                    financing_request = FinancingRequest.objects.filter(
                        customer__in=customers_by_id,
                        status__in=['approved', 'active']
                    ).order_by('-created_at').first()
            except:
                pass
        
        if not financing_request:
            logger.warning(f"Webhook R4 - No se encontró solicitud activa para {telefono_emisor}")
            return JsonResponse({
                'abono': False,
                'message': 'Cliente no encontrado o sin financiamiento activo'
            })
        
        # 9. Crear registro de pago
        try:
            # Parsear fecha
            payment_date = datetime.fromisoformat(fecha_hora.replace('Z', '+00:00'))
            
            payment = Payment.objects.create(
                application=financing_request,
                payment_type='installment',
                payment_method='mobile_payment',
                amount=float(monto),
                payment_date=payment_date,
                reference_number=referencia,
                status='verified',
                currency='VES',  # Asumiendo bolívares por defecto
                sender_bank=banco_emisor,
                sender_name=f"Pago desde {telefono_emisor}",
                notes=f"Pago automático vía R4 webhook. Concepto: {concepto}",
                submitted_by=financing_request.customer.user,
                verified_by=None,  # Verificado automáticamente por R4
                verified_at=payment_date
            )
            
            logger.info(f"Webhook R4 - Pago creado exitosamente: {payment.id}")
            
            # 10. Verificar si este pago corresponde a una cuota programada
            from financing.models import PaymentSchedule
            
            payment_schedule = PaymentSchedule.objects.filter(
                application=financing_request,
                is_paid=False,
                amount=float(monto)
            ).order_by('due_date').first()
            
            if payment_schedule:
                payment.payment_schedule = payment_schedule
                payment_schedule.is_paid = True
                payment_schedule.paid_date = payment_date
                payment_schedule.save()
                payment.save()
                
                logger.info(f"Webhook R4 - Cuota programada marcada como pagada: {payment_schedule.id}")
            
            # 11. Enviar notificación de confirmación
            try:
                payment_processor._send_payment_confirmation(payment)
            except Exception as e:
                logger.error(f"Webhook R4 - Error enviando confirmación: {str(e)}")
            
            return JsonResponse({
                'abono': True,
                'message': 'Pago procesado exitosamente',
                'payment_id': payment.id
            })
            
        except Exception as e:
            logger.error(f"Webhook R4 - Error creando pago: {str(e)}")
            return JsonResponse({
                'abono': False,
                'message': 'Error procesando el pago'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Webhook R4 - Error general: {str(e)}")
        return JsonResponse({
            'abono': False,
            'message': 'Error interno del servidor'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def r4_client_validation_webhook(request):
    """
    Webhook MBconsulta - Valida clientes para transacciones entrantes
    
    Endpoint: /api/payments/webhooks/r4/validate-client/
    Documentación oficial: MBconsulta
    """
    try:
        # 1. Validar IP de origen
        if not validate_r4_ip(request):
            client_ip = get_client_ip(request)
            logger.warning(f"Webhook R4 validación rechazada - IP no autorizada: {client_ip}")
            return HttpResponseForbidden("IP no autorizada")
        
        # 2. Validar header Authorization UUID
        if not validate_authorization_header(request):
            logger.warning("Webhook R4 validación rechazada - Authorization header inválido")
            return JsonResponse({
                'status': False,
                'error': 'Authorization header requerido (UUID)'
            }, status=400)
        
        # 3. Parsear datos JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            logger.error("Webhook R4 validación - Error parsing JSON")
            return JsonResponse({
                'status': False,
                'error': 'JSON inválido'
            }, status=400)
        
        # 4. Validar campos requeridos
        id_cliente = data.get('IdCliente')
        monto = data.get('Monto')
        telefono_comercio = data.get('TelefonoComercio')
        
        if not id_cliente:
            return JsonResponse({
                'status': False,
                'error': 'IdCliente requerido'
            }, status=400)
        
        logger.info(f"Webhook R4 validación - Cliente: {id_cliente}, Monto: {monto}")
        
        # 5. Buscar cliente por cédula/ID
        try:
            customer = Customer.objects.filter(
                identity_document=id_cliente
            ).select_related('user').first()
            
            if not customer:
                logger.info(f"Webhook R4 validación - Cliente no encontrado: {id_cliente}")
                return JsonResponse({
                    'status': False,
                    'message': 'Cliente no registrado'
                })
            
            # 6. Verificar si tiene financiamiento activo
            active_financing = FinancingRequest.objects.filter(
                customer=customer,
                status__in=['approved', 'active']
            ).exists()
            
            if not active_financing:
                logger.info(f"Webhook R4 validación - Cliente sin financiamiento activo: {id_cliente}")
                return JsonResponse({
                    'status': False,
                    'message': 'Cliente sin financiamiento activo'
                })
            
            # 7. Validaciones adicionales opcionales
            if monto:
                try:
                    monto_float = float(monto)
                    # Validar que el monto esté dentro de rangos razonables
                    if monto_float <= 0 or monto_float > 1000000:  # Límite configurable
                        return JsonResponse({
                            'status': False,
                            'message': 'Monto fuera de rango permitido'
                        })
                except (ValueError, TypeError):
                    return JsonResponse({
                        'status': False,
                        'message': 'Monto inválido'
                    })
            
            logger.info(f"Webhook R4 validación - Cliente aprobado: {id_cliente}")
            return JsonResponse({
                'status': True,
                'message': 'Cliente autorizado'
            })
            
        except Exception as e:
            logger.error(f"Webhook R4 validación - Error buscando cliente: {str(e)}")
            return JsonResponse({
                'status': False,
                'message': 'Error validando cliente'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Webhook R4 validación - Error general: {str(e)}")
        return JsonResponse({
            'status': False,
            'message': 'Error interno del servidor'
        }, status=500)