import logging
import uuid
from datetime import datetime
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from financing.models import Payment, FinancingRequest, PaymentSchedule
from users.models import Customer
import json
from decimal import Decimal
from django.utils import timezone
from products.llevo_models import LlevoRate
from notifications.services import send_payment_confirmed_notification

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
    remote_addr = request.META.get("REMOTE_ADDR")
    x_real_ip = request.META.get("HTTP_X_REAL_IP")

    # Log detallado para debugging
    logger.info(f"IP Detection - X-Forwarded-For: {x_forwarded_for}, Remote-Addr: {remote_addr}, X-Real-IP: {x_real_ip}")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = remote_addr

    logger.info(f"IP Final detectada: {ip}")
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



# =============================================================================
# FUNCIONES AUXILIARES PARA AUTOMATIZACIÓN R4
# =============================================================================

def identificar_cliente_por_telefono(telefono):
    """
    Identifica un cliente por su número de teléfono.
    Busca en Customer.phone y Customer.reference_phone con múltiples variantes.
    """
    import logging
    logger = logging.getLogger('payments.webhooks')
    from users.models import Customer
    
    logger.info(f"📞 identificar_cliente_por_telefono: Buscando teléfono '{telefono}'...")
    
    if not telefono:
        logger.warning("📞 Teléfono vacío, retornando None")
        return None
    
    # Limpiar teléfono
    telefono_limpio = telefono.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    logger.info(f"📞 Teléfono limpio: '{telefono_limpio}'")
    
    # Generar variantes
    variantes = [
        telefono,
        telefono_limpio,
        telefono_limpio.lstrip('0'),
        f"58{telefono_limpio.lstrip('0')}",
        f"+58{telefono_limpio.lstrip('0')}"
    ]
    
    logger.info(f"📞 Variantes generadas: {variantes}")
    
    # Buscar en Customer.phone
    for i, var in enumerate(variantes):
        logger.info(f"📞 Buscando variante #{i+1}: '{var}' en Customer.phone...")
        try:
            customer = Customer.objects.filter(phone=var).first()
            if customer:
                logger.info(f"✅ Cliente ENCONTRADO: Customer ID {customer.id}, phone='{customer.phone}'")
                return customer
            else:
                logger.info(f"   No encontrado con '{var}'")
        except Exception as e:
            logger.error(f"❌ Error buscando con variante '{var}': {str(e)}")
    
    # Buscar en Customer.reference_phone (teléfono de referencia)
    for i, var in enumerate(variantes):
        logger.info(f"📞 Buscando variante #{i+1}: '{var}' en Customer.reference_phone...")
        try:
            customer = Customer.objects.filter(reference_phone=var).first()
            if customer:
                logger.info(f"✅ Cliente ENCONTRADO en reference_phone: Customer ID {customer.id}")
                return customer
            else:
                logger.info(f"   No encontrado con '{var}'")
        except Exception as e:
            logger.error(f"❌ Error buscando con variante '{var}': {str(e)}")
    
    logger.warning(f"❌ Cliente NO encontrado con teléfono '{telefono}' (probadas {len(variantes)} variantes)")
    return None
def crear_pago_sin_asignar(data, razon, client_ip):
    """Crea Payment sin asignar para revisión manual del admin."""
    try:
        payment = Payment.objects.create(
            application=None,
            payment_schedule=None,
            payment_method='r4_automatic',
            payment_type='installment',
            status='requires_review',
            amount=Decimal(data['Monto']),
            currency='VES',
            payment_date=datetime.fromisoformat(data['FechaHora'].replace('Z', '+00:00')),
            submitted_at=timezone.now(),
            reference_number=data.get('Referencia'),
            sender_phone=data.get('TelefonoEmisor'),
            sender_bank=data.get('BancoEmisor'),
            admin_notes=f"""⚠️ PAGO R4 REQUIERE ASIGNACIÓN MANUAL
Razón: {razon}
Monto: Bs. {data['Monto']}
Teléfono: {data.get('TelefonoEmisor')}
Referencia: {data.get('Referencia')}""",
            notes=f"Pago R4 - Ref: {data.get('Referencia')} - Pendiente asignación",
            ip_address=client_ip
        )
        logger.warning(f"⚠️ Payment #{payment.id} SIN ASIGNAR - {razon}")
        return JsonResponse({"abono": True, "message": "Pago registrado para revision manual"})
    except Exception as e:
        logger.error(f"❌ Error creando pago sin asignar: {str(e)}")
        return JsonResponse({"abono": False, "message": "Error interno"}, status=500)


def crear_pago_con_discrepancia(data, solicitud, monto_llevos, esperado_llevos, tasa, razon, client_ip):
    """Crea Payment con discrepancia para revisión manual."""
    try:
        payment = Payment.objects.create(
            application=solicitud,
            payment_schedule=None,
            payment_method='r4_automatic',
            payment_type='installment',
            status='requires_review',
            amount=Decimal(data['Monto']),
            currency='VES',
            amount_llevos=monto_llevos,
            llevo_rate_at_payment=tasa.llevo_value,
            llevo_rate_snapshot=tasa,
            payment_date=datetime.fromisoformat(data['FechaHora'].replace('Z', '+00:00')),
            submitted_at=timezone.now(),
            reference_number=data.get('Referencia'),
            sender_phone=data.get('TelefonoEmisor'),
            sender_bank=data.get('BancoEmisor'),
            admin_notes=f"""⚠️ MONTO NO COINCIDE
{razon}
Esperado: {esperado_llevos} LLEVOS
Recibido: {monto_llevos} LLEVOS
Diferencia: {abs(monto_llevos - esperado_llevos)} LLEVOS
Tasa: {tasa.llevo_value} Bs/LLEVO""",
            notes=f"Pago R4 - Ref: {data.get('Referencia')} - Monto no coincide",
            ip_address=client_ip,
            submitted_by=solicitud.customer.user if solicitud.customer and solicitud.customer.user else None
        )
        logger.warning(f"⚠️ Payment #{payment.id} DISCREPANCIA - Dif: {abs(monto_llevos - esperado_llevos)} LLEVOS")
        return JsonResponse({"abono": True, "message": "Pago registrado para revision manual"})
    except Exception as e:
        logger.error(f"❌ Error creando pago con discrepancia: {str(e)}")
        return JsonResponse({"abono": False, "message": "Error interno"}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def r4_notification_webhook(request):
    """
    Webhook R4notifica - Notificación de pagos móviles entrantes
    Según documentación R4 V3.0 - Página 9 (líneas 420-496)

    URL: https://dominio.cliente/R4notifica

    GET: Prueba de conectividad (para verificación del banco)
    POST: Procesamiento de notificación de pago
    """
    # Responder a solicitudes GET con confirmación de conectividad
    if request.method == "GET":
        logger.info("R4notifica - Prueba de conectividad GET recibida")
        return JsonResponse({
            "service": "R4notifica",
            "status": "operational",
            "message": "Webhook R4 notification endpoint is operational",
            "commerce": "LlévateloExpress C.A.",
            "rif": "J-506654547",
            "method_required": "POST"
        })

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
        logger.warning(f"🔔 R4notifica PAYLOAD COMPLETO: {data}")
        logger.warning("⚡ TEST: Línea inmediatamente después del payload log")
        monto = data.get("Monto")
        
        logger.info(f"R4notifica - Pago recibido: Ref:{referencia}, Monto:{monto}, Código:{codigo_red}")

        # 6. Procesar solo si el código es exitoso (línea 531: 00 = APROBADO)
        logger.warning(f"🔍 DEBUGGER: codigo_red = 047{codigo_red}047, type = {type(codigo_red)}, repr = {repr(codigo_red)}")
        if codigo_red == "00":
            # ============================================================
            # AUTOMATIZACIÓN COMPLETA - R4 NOTIFICA
            # Registro automático de pagos en sistema
            # IMPORTANTE: Tolerancia 0, pagos deben ser 100% exactos
            # ============================================================

            # PASO 1: Identificar cliente por teléfono
            # -----------------------------------------
            logger.info("🔹 PASO 1: Identificando cliente por teléfono...")
            telefono_cliente = data.get('TelefonoEmisor', '')  # Teléfono del cliente que realiza el pago
            logger.info(f"📞 Teléfono extraído del payload: '{telefono_cliente}'")
            
            try:
                cliente = identificar_cliente_por_telefono(telefono_cliente)
                logger.info(f"✅ Resultado búsqueda: {'Cliente encontrado' if cliente else 'Cliente NO encontrado'}")
            except Exception as e:
                logger.error(f"❌ ERROR en identificar_cliente_por_telefono: {str(e)}")
                logger.exception(e)
                cliente = None

            if not cliente:
                # Cliente no encontrado → Crear pago sin asignar para revisión manual
                return crear_pago_sin_asignar(
                    data=data,
                    razon=f"Cliente no encontrado con teléfono {telefono_cliente}",
                    client_ip=client_ip
                )

            # PASO 2: Buscar solicitud de financiamiento activa
            # --------------------------------------------------
            # Buscar solicitud en estado "approved" o "in_payment" (pagando cuotas)
            solicitud = FinancingRequest.objects.filter(
                customer=cliente,
                status__in=['approved', 'in_payment', 'active']
            ).order_by('-created_at').first()

            if not solicitud:
                # Cliente sin solicitud activa → Crear pago sin asignar
                return crear_pago_sin_asignar(
                    data=data,
                    razon=f"Cliente {cliente.user.email if cliente.user else cliente.id} no tiene solicitud activa (approved/in_payment)",
                    client_ip=client_ip
                )

            # PASO 3: Obtener tasa LLEVO vigente (actual)
            # --------------------------------------------
            try:
                tasa_llevo = LlevoRate.objects.filter(is_active=True).order_by('-created_at').first()
                if not tasa_llevo:
                    raise ValueError("No hay tasa LLEVO activa en el sistema")

                # Tasa en formato Decimal para precisión
                tasa_bs_por_llevo = Decimal(str(tasa_llevo.llevo_value))  # Ej: 7080.00

            except Exception as e:
                logger.error(f"Error obteniendo tasa LLEVO: {str(e)}")
                return crear_pago_sin_asignar(
                    data=data,
                    razon=f"Error obteniendo tasa LLEVO: {str(e)}",
                    client_ip=client_ip
                )

            # PASO 4: Convertir Bs → LLEVOS
            # ------------------------------
            # Monto recibido en Bs (VES) desde R4
            monto_bs = Decimal(str(data.get('Monto', '0')))

            # Convertir a LLEVOS: monto_bs / tasa_bs_por_llevo
            # Ejemplo: 885,000 Bs / 7,080 = 125.00 LLEVOS
            monto_llevos = (monto_bs / tasa_bs_por_llevo).quantize(Decimal('0.01'))

            # PASO 5: Determinar tipo de pago (inicial vs cuota)
            # ---------------------------------------------------
            # Verificar si ya se pagó el pago inicial
            pago_inicial_realizado = Payment.objects.filter(
                application=solicitud,
                payment_type='initial',
                status__in=['completed', 'verified']
            ).exists()

            if not pago_inicial_realizado:
                # Este es el PAGO INICIAL
                tipo_pago = 'initial'
                monto_esperado_llevos = solicitud.down_payment_llevos  # En LLEVOS

            else:
                # Este es una CUOTA MENSUAL
                tipo_pago = 'installment'

                # Buscar la próxima cuota pendiente en el calendario
                proxima_cuota = PaymentSchedule.objects.filter(
                    application=solicitud,
                    is_paid=False
                ).order_by('payment_number').first()

                if not proxima_cuota:
                    # No hay cuotas pendientes → Pago excedente o ya completado
                    return crear_pago_sin_asignar(
                        data=data,
                        razon=f"Solicitud {solicitud.id} no tiene cuotas pendientes. Todas pagadas.",
                        client_ip=client_ip
                    )

                monto_esperado_llevos = proxima_cuota.amount  # En LLEVOS

            # PASO 6: Validar monto (TOLERANCIA 0)
            # -------------------------------------
            # DECISIÓN CLIENTE: Los LLEVOS nunca se redondean, pagos deben ser 100% exactos
            TOLERANCIA = Decimal('0')  # CERO tolerancia

            diferencia = abs(monto_llevos - monto_esperado_llevos)

            if diferencia > TOLERANCIA:
                # Monto NO coincide → Crear pago con discrepancia para revisión manual
                razon_discrepancia = f"Monto recibido: {monto_llevos} LLEVOS ({monto_bs} Bs), esperado: {monto_esperado_llevos} LLEVOS. Diferencia: {diferencia} LLEVOS"

                return crear_pago_con_discrepancia(
                    data=data,
                    solicitud=solicitud,
                    monto_llevos=monto_llevos,
                    esperado_llevos=monto_esperado_llevos,
                    tasa=tasa_llevo,
                    razon=razon_discrepancia,
                    client_ip=client_ip
                )

            # PASO 7: CREAR PAYMENT AUTOMÁTICO
            # ---------------------------------
            # Monto exacto, proceder con registro automático
            try:
                pago = Payment.objects.create(
                    application=solicitud,

                    # Monto en Bs (VES) recibido de R4
                    amount=monto_bs,
                    currency='VES',

                    # Monto en LLEVOS calculado
                    amount_llevos=monto_llevos,

                    # Tasa de conversión usada
                    llevo_rate_at_payment=tasa_bs_por_llevo,
                    llevo_rate_snapshot=tasa_llevo,  # FK para auditoría

                    # Tipo de pago
                    payment_type=tipo_pago,

                    # Método de pago
                    payment_method='r4_automatic',

                    # Estado
                    status='verified',  # Aprobado automáticamente

                    # Metadatos R4
                    reference_number=data.get('Referencia', ''),
                    sender_identification=data.get('IdComercio', ''),
                    sender_phone=data.get('TelefonoEmisor', ''),
                    sender_bank=data.get('BancoEmisor', ''),
                    ip_address=client_ip,

                    # Fecha
                    payment_date=timezone.now(),

                    # Notas
                    notes=f"Pago R4 registrado automáticamente. Monto exacto: {monto_llevos} LLEVOS = {monto_bs} Bs (tasa {tasa_bs_por_llevo})"
                )

                logger.info(f"PAGO AUTOMATICO CREADO: Payment ID {pago.id} - {monto_llevos} LLEVOS ({monto_bs} Bs) - Solicitud {solicitud.id}")

            except Exception as e:
                logger.error(f"Error creando Payment automático: {str(e)}")
                return JsonResponse({
                    'abono': False,
                    'message': 'Error interno creando registro de pago'
                }, status=500)

            # PASO 8: Actualizar solicitud
            # -----------------------------
            if tipo_pago == 'initial':
                # Pago inicial completado → Cambiar estado a "in_payment"
                solicitud.status = 'in_payment'
                solicitud.save()

                logger.info(f"Solicitud {solicitud.id} actualizada: Pago inicial completado, estado -> in_payment")

            else:
                # Cuota pagada → Verificar si es la última
                cuotas_pendientes = PaymentSchedule.objects.filter(
                    application=solicitud,
                    is_paid=False
                ).exclude(id=proxima_cuota.id).count()

                if cuotas_pendientes == 0:
                    # Última cuota → Solicitud completada
                    solicitud.status = 'completed'
                    solicitud.save()
                    logger.info(f"Solicitud {solicitud.id} COMPLETADA: Todas las cuotas pagadas")

            # PASO 9: Actualizar calendario PaymentSchedule
            # ----------------------------------------------
            if tipo_pago == 'installment':
                # Marcar la cuota como pagada
                proxima_cuota.is_paid = True
                proxima_cuota.paid_date = timezone.now()
                proxima_cuota.payment = pago  # Vincular al Payment
                proxima_cuota.save()

                logger.info(f"PaymentSchedule {proxima_cuota.id} marcada como pagada (cuota #{proxima_cuota.payment_number})")

            # PASO 10: Responder al banco (R4)
            # ---------------------------------
            logger.info(f"R4notifica - Pago procesado exitosamente: {referencia}")

            # PASO 11: Enviar notificación al cliente
            # -----------------------------------------
            try:
                user = solicitud.customer.user
                payment_data = {
                    "id": pago.id,
                    "application_number": solicitud.application_number,
                    "amount": float(monto_llevos),
                    "currency": "LLEVO",
                    "payment_type": tipo_pago,
                    "reference": referencia,
                    "confirmed_at": timezone.now().isoformat()
                }
                send_payment_confirmed_notification(user, payment_data)
                logger.info(f"Notificación de pago enviada a {user.email}")
            except Exception as notif_error:
                logger.warning(f"Error enviando notificación: {notif_error}")
            # Formato oficial R4 Conecta V3.0 página 10: {"abono": true}
            return JsonResponse({
                'abono': True,
                'message': 'Pago procesado y registrado automáticamente'
            })
        
        else:
            # Código no exitoso (diferente de "00") - no procesar
            logger.warning(f"R4notifica - Pago con código no exitoso: {codigo_red}")
            return JsonResponse({"abono": False, "message": f"Código no exitoso: {codigo_red}"})

    except Exception as e:
        logger.error(f"Error en R4notifica webhook: {str(e)}")
        return JsonResponse({"abono": False, "message": "Error interno"}, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def r4_client_validation_webhook(request):
    """
    Webhook R4consulta - Validación de clientes
    Según documentación R4 V3.0 - Página 7-8 (líneas 320-386)

    URL: https://dominio.cliente/R4consulta

    GET: Prueba de conectividad (para verificación del banco)
    POST: Validación de cliente para pago móvil
    """
    # Responder a solicitudes GET con confirmación de conectividad
    if request.method == "GET":
        logger.info("R4consulta - Prueba de conectividad GET recibida")
        return JsonResponse({
            "service": "R4consulta",
            "status": "operational",
            "message": "Webhook R4 client validation endpoint is operational",
            "commerce": "LlévateloExpress C.A.",
            "rif": "J-506654547",
            "phone": "0422-1002379",
            "method_required": "POST"
        })

    try:
        # 1. Validar IP de origen (líneas 172-173)
        client_ip = get_client_ip(request)

        # DEBUGGING: Log TODOS los requests
        logger.warning(f"🔍 R4consulta REQUEST - IP: {client_ip}, Method: {request.method}")
        logger.warning(f"🔍 Headers: {dict(request.META)}")

        if settings.DEBUG and client_ip in ["127.0.0.1", "::1"]:
            pass  # Permitir localhost en debug
        elif client_ip not in R4_ALLOWED_IPS:
            logger.warning(f"Webhook R4consulta rechazado - IP no autorizada: {client_ip}")
            return HttpResponseForbidden("IP no autorizada")

        # 2. Validar token UUID Authorization (líneas 349-351)
        logger.warning(f"🔍 Validando Authorization header...")
        if not validate_r4_authorization(request):
            logger.warning(f"🔍 Authorization RECHAZADO")
            return HttpResponseForbidden("Token Authorization inválido")

        logger.warning(f"🔍 Authorization ACEPTADO")

        # 3. Parsear datos JSON
        logger.warning(f"🔍 REQUEST BODY RAW: {request.body}")
        try:
            data = json.loads(request.body)
            logger.warning(f"🔍 JSON PARSEADO: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"R4consulta - JSON inválido: {e}")
            logger.error(f"Body recibido: {request.body}")
            return JsonResponse({"status": False, "error": "JSON inválido"}, status=400)

        # 4. Validar campos según documentación (líneas 372-375)
        required_fields = ["IdCliente", "TelefonoComercio"]  # Monto es opcional
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            logger.error(f"R4consulta - Campos faltantes: {missing_fields}")
            return JsonResponse({"status": False, "error": f"Campos faltantes: {missing_fields}"}, status=400)

        logger.warning(f"🔍 Campos validados correctamente")

        # 5. Extraer datos
        id_cliente = data.get("IdCliente")          # String - 8 numérico
        monto = data.get("Monto")                   # String - opcional
        telefono_comercio = data.get("TelefonoComercio")  # String - 11 numérico

        logger.warning(f"🔍 R4consulta - Validando cliente: {id_cliente}, Monto: {monto}, Teléfono: {telefono_comercio}")

        # 6. CASO ESPECIAL: Si IdCliente es el RIF de LlévateloExpress
        # Esto sucede cuando el cliente paga desde su app bancaria a nuestra cuenta empresarial
        # RIF: J-506654547 (sin J = 506654547 o con error de tipeo 5066554547)
        rif_variants = ["506654547", "5066554547", "J506654547", "J-506654547"]

        if id_cliente in rif_variants:
            logger.warning(f"🔍 R4consulta - PAGO A CUENTA EMPRESARIAL AUTORIZADO ✅")
            logger.warning(f"  - IdCliente: {id_cliente} (RIF de LlévateloExpress)")
            logger.warning(f"  - TelefonoComercio: {telefono_comercio}")
            logger.warning(f"  - Monto: {monto}")
            logger.warning(f"  - Tipo: Pago Móvil a cuenta empresarial")
            logger.warning(f"  - Acción: Autorizar pago - La identificación del cliente real vendrá en R4notifica")
            response = JsonResponse({"status": True})
            logger.warning(f"🔍 RESPONSE ENVIADA: {response.content}")
            return response

        # 7. CASO NORMAL: Buscar cliente en nuestro sistema por cédula
        # El IdCliente viene sin el prefijo V/E, por eso buscamos por número
        customer = Customer.objects.filter(identity_document=id_cliente).first()

        # También intentar con V/E prefix si el cliente no se encuentra
        if not customer:
            customer = Customer.objects.filter(identity_document=f"V{id_cliente}").first()
        if not customer:
            customer = Customer.objects.filter(identity_document=f"E{id_cliente}").first()
        if not customer:
            customer = Customer.objects.filter(identity_document=f"V-{id_cliente}").first()
        if not customer:
            customer = Customer.objects.filter(identity_document=f"E-{id_cliente}").first()

        logger.warning(f"🔍 Buscando cliente en BD: {id_cliente}")

        if customer:
            # Cliente autorizado - permitir pago (líneas 377-381)
            logger.warning(f"🔍 R4consulta - Cliente AUTORIZADO ✅")
            logger.warning(f"  - IdCliente (cédula): {id_cliente}")
            logger.warning(f"  - Monto solicitado: {monto}")
            logger.warning(f"  - Cliente encontrado: {customer.user.first_name} {customer.user.last_name}")
            logger.warning(f"  - Email: {customer.user.email if customer.user else 'N/A'}")
            response = JsonResponse({"status": True})
            logger.warning(f"🔍 RESPONSE ENVIADA: {response.content}")
            return response
        else:
            # Cliente no encontrado - rechazar pago (líneas 383-386)
            # Según documentación: "status false" hace que el pago sea reversado
            logger.warning(f"🔍 R4consulta - Cliente NO AUTORIZADO ❌")
            logger.warning(f"  - IdCliente (cédula): {id_cliente}")
            logger.warning(f"  - Monto: {monto}")
            logger.warning(f"  - Cliente no registrado en el sistema")
            logger.warning(f"  - El pago será REVERSADO por R4")
            response = JsonResponse({"status": False})
            logger.warning(f"🔍 RESPONSE ENVIADA: {response.content}")
            return response

    except Exception as e:
        logger.error(f"Error en R4consulta webhook: {str(e)}")
        return JsonResponse({"status": False, "message": "Error interno"}, status=500)
