import logging
import uuid
from datetime import datetime
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from financing.models import Payment, FinancingRequest
from users.models import Customer
import json

logger = logging.getLogger(__name__)

# IPs oficiales R4 según documentación V3.0
R4_ALLOWED_IPS = [
    "45.175.213.98",
    "200.74.203.91",
    "190.202.123.66",
    "204.199.249.3",
    "190.6.60.35"
]

def get_client_ip(request):
    """Obtiene la IP real del cliente considerando proxies"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def validate_r4_authorization(request):
    """
    Valida el token UUID de Authorization según documentación R4 V3.0
    
    Según documentación oficial (líneas 349-351, 448-450):
    --header Authorization: {{TOKEN AUTHORIZATION}} creado por el comercio, en formato UUID
    Ejemplo: f8423bb2-10c9-4d0f-8300-aaf8fea18c72
    """
    auth_header = request.META.get("HTTP_AUTHORIZATION")
    
    if not auth_header:
        logger.warning("R4 webhook - Falta header Authorization")
        return False
    
    # Verificar que el token UUID coincida con el configurado
    expected_uuid = settings.R4_UUID_TOKEN
    if not expected_uuid:
        logger.error("R4_UUID_TOKEN no configurado en settings")
        return False
    
    if auth_header != expected_uuid:
        logger.warning(f"R4 webhook - Token UUID inválido: {auth_header}")
        return False
    
    logger.info(f"R4 webhook - Token UUID válido: {auth_header}")
    return True

@csrf_exempt
@require_http_methods(["POST"])
def r4_notification_webhook(request):
    """
    Webhook R4notifica - Notificación de pagos móviles entrantes
    Según documentación R4 V3.0 - Página 9 (líneas 420-496)
    
    URL: https://dominio.cliente/R4notifica
    """
    try:
        # 1. Validar IP de origen (líneas 172-173)
        client_ip = get_client_ip(request)
        if settings.DEBUG and client_ip in ["127.0.0.1", "::1"]:
            pass  # Permitir localhost en debug
        elif client_ip not in R4_ALLOWED_IPS:
            logger.warning(f"Webhook R4notifica rechazado - IP no autorizada: {client_ip}")
            return HttpResponseForbidden("IP no autorizada")

        # 2. Validar token UUID Authorization (líneas 448-450)
        if not validate_r4_authorization(request):
            return HttpResponseForbidden("Token Authorization inválido")

        # 3. Parsear datos JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            logger.error("R4notifica - JSON inválido")
            return JsonResponse({"abono": False, "error": "JSON inválido"}, status=400)

        # 4. Validar campos requeridos según documentación (líneas 477-485)
        required_fields = [
            "IdComercio",        # String - 8 numérico
            "TelefonoComercio",  # String - 11 numérico
            "TelefonoEmisor",    # String - 11 numérico
            "BancoEmisor",       # String - 3 numérico
            "Monto",             # String con decimales
            "FechaHora",         # String
            "Referencia",        # String
            "CodigoRed"          # String
        ]
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            logger.error(f"R4notifica - Campos faltantes: {missing_fields}")
            return JsonResponse({"abono": False, "error": f"Campos faltantes: {missing_fields}"}, status=400)

        # 5. Extraer datos del pago
        codigo_red = data.get("CodigoRed")
        referencia = data.get("Referencia")
        monto = data.get("Monto")
        
        logger.info(f"R4notifica - Pago recibido: Ref:{referencia}, Monto:{monto}, Código:{codigo_red}")

        # 6. Procesar solo si el código es exitoso (línea 531: 00 = APROBADO)
        if codigo_red == "00":
            # TODO: Implementar lógica de registro automático de pago
            # 1. Buscar solicitud de financiamiento por referencia/monto
            # 2. Crear Payment record automáticamente
            # 3. Actualizar estado de solicitud
            # 4. Enviar confirmación por email
            
            logger.info(f"R4notifica - Pago procesado exitosamente: {referencia}")
            return JsonResponse({"abono": True, "message": "Pago procesado"})
        else:
            logger.warning(f"R4notifica - Pago con código no exitoso: {codigo_red}")
            return JsonResponse({"abono": False, "message": f"Código no exitoso: {codigo_red}"})

    except Exception as e:
        logger.error(f"Error en R4notifica webhook: {str(e)}")
        return JsonResponse({"abono": False, "message": "Error interno"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def r4_client_validation_webhook(request):
    """
    Webhook R4consulta - Validación de clientes
    Según documentación R4 V3.0 - Página 7-8 (líneas 320-386)
    
    URL: https://dominio.cliente/R4consulta
    """
    try:
        # 1. Validar IP de origen (líneas 172-173)
        client_ip = get_client_ip(request)
        if settings.DEBUG and client_ip in ["127.0.0.1", "::1"]:
            pass  # Permitir localhost en debug
        elif client_ip not in R4_ALLOWED_IPS:
            logger.warning(f"Webhook R4consulta rechazado - IP no autorizada: {client_ip}")
            return HttpResponseForbidden("IP no autorizada")

        # 2. Validar token UUID Authorization (líneas 349-351)
        if not validate_r4_authorization(request):
            return HttpResponseForbidden("Token Authorization inválido")

        # 3. Parsear datos JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            logger.error("R4consulta - JSON inválido")
            return JsonResponse({"status": False, "error": "JSON inválido"}, status=400)

        # 4. Validar campos según documentación (líneas 372-375)
        required_fields = ["IdCliente", "TelefonoComercio"]  # Monto es opcional
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            logger.error(f"R4consulta - Campos faltantes: {missing_fields}")
            return JsonResponse({"status": False, "error": f"Campos faltantes: {missing_fields}"}, status=400)

        # 5. Extraer datos
        id_cliente = data.get("IdCliente")          # String - 8 numérico
        monto = data.get("Monto")                   # String - opcional
        telefono_comercio = data.get("TelefonoComercio")  # String - 11 numérico

        logger.info(f"R4consulta - Validando cliente: {id_cliente}, Monto: {monto}")

        # 6. Buscar cliente en nuestro sistema
        customer = Customer.objects.filter(identity_document=id_cliente).first()
        
        if customer:
            # Cliente autorizado - permitir pago (líneas 377-381)
            logger.info(f"R4consulta - Cliente autorizado: {id_cliente}")
            return JsonResponse({"status": True})
        else:
            # Cliente no encontrado - rechazar pago (líneas 383-386)
            # Según documentación: "status false" hace que el pago sea reversado
            logger.warning(f"R4consulta - Cliente no autorizado: {id_cliente}")
            return JsonResponse({"status": False})

    except Exception as e:
        logger.error(f"Error en R4consulta webhook: {str(e)}")
        return JsonResponse({"status": False, "message": "Error interno"}, status=500)
