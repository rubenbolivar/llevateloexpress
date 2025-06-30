import logging
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from financing.models import Payment, PaymentSchedule, FinancingRequest
from .r4_client import r4_client

logger = logging.getLogger(__name__)

class PaymentProcessor:
    
    @staticmethod
    def verify_mobile_payment(referencia, telefono_origen, payment_schedule_id=None):
        """
        Verifica un pago móvil usando R4 Conecta
        """
        try:
            # Consultar R4
            result = r4_client.consulta_pago_movil(referencia, telefono_origen)
            
            if result['success'] and result['found']:
                # Si se proporciona payment_schedule_id, actualizar estado
                if payment_schedule_id:
                    try:
                        schedule = PaymentSchedule.objects.get(id=payment_schedule_id)
                        
                        # Crear registro de pago
                        payment = Payment.objects.create(
                            application=schedule.application,
                            payment_schedule=schedule,
                            payment_type='installment',
                            payment_method='mobile_payment',
                            amount=schedule.amount,
                            payment_date=timezone.now(),
                            reference_number=referencia,
                            status='verified',
                            notes=f"Pago verificado automáticamente vía R4. Tel: {telefono_origen}"
                        )
                        
                        # Marcar cuota como pagada
                        schedule.is_paid = True
                        schedule.save()
                        
                        # Enviar notificación
                        PaymentProcessor._send_payment_confirmation(payment)
                        
                        logger.info(f"Pago verificado y registrado: {referencia}")
                        
                        return {
                            'verified': True,
                            'payment_id': payment.id,
                            'message': 'Pago verificado y registrado exitosamente'
                        }
                        
                    except PaymentSchedule.DoesNotExist:
                        logger.error(f"PaymentSchedule {payment_schedule_id} no encontrado")
                        return {
                            'verified': True,
                            'error': 'Cuota no encontrada',
                            'message': 'Pago encontrado pero cuota no existe'
                        }
                else:
                    # Solo verificación, sin registro
                    return {
                        'verified': True,
                        'message': 'Pago móvil encontrado'
                    }
            else:
                return {
                    'verified': False,
                    'message': result.get('message', 'Pago no encontrado')
                }
                
        except Exception as e:
            logger.error(f"Error verificando pago móvil: {str(e)}")
            return {
                'verified': False,
                'error': str(e),
                'message': 'Error al verificar pago'
            }
    
    @staticmethod
    def _send_payment_confirmation(payment):
        """
        Envía email de confirmación de pago
        """
        try:
            subject = f"Pago Confirmado - LlévateloExpress"
            
            message = f"""
            Estimado/a cliente,
            
            Su pago ha sido confirmado exitosamente:
            
            Solicitud: {payment.application.application_number}
            Monto: ${payment.amount}
            Referencia: {payment.reference_number}
            Fecha: {payment.payment_date.strftime('%d/%m/%Y %H:%M')}
            
            Gracias por su pago.
            
            LlévateloExpress
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [payment.application.customer.user.email],
                fail_silently=False,
            )
            
            logger.info(f"Email confirmación enviado para pago {payment.id}")
            
        except Exception as e:
            logger.error(f"Error enviando email confirmación: {str(e)}")

# Instancia global del procesador
payment_processor = PaymentProcessor()
