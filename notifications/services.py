import logging
from typing import Dict, Any, Optional, List
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from .models import (
    NotificationType, 
    EmailTemplate, 
    UserNotificationPreference, 
    EmailNotification, 
    EmailQueue
)

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Servicio principal para gestionar notificaciones por email
    """
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@llevateloexpress.com')
    
    def send_notification(self, 
                         user: User, 
                         notification_type_code: str, 
                         context: Dict[str, Any] = None,
                         recipient_email: str = None,
                         priority: str = 'normal',
                         schedule_at: timezone.datetime = None) -> bool:
        """
        Envía una notificación por email a un usuario
        
        Args:
            user: Usuario destinatario
            notification_type_code: Código del tipo de notificación
            context: Contexto adicional para la plantilla
            recipient_email: Email alternativo (si no se usa el del usuario)
            priority: Prioridad del email ('high', 'normal', 'low')
            schedule_at: Programar envío para una fecha específica
            
        Returns:
            bool: True si se procesó correctamente, False en caso contrario
        """
        try:
            # Verificar que el tipo de notificación existe
            notification_type = NotificationType.objects.get(
                code=notification_type_code, 
                is_active=True
            )
            
            # Verificar preferencias del usuario
            if user and not self._user_wants_notification(user, notification_type_code):
                logger.info(f"Usuario {user.username} tiene deshabilitadas las notificaciones de tipo {notification_type_code}")
                return False
            
            # Obtener email del destinatario
            recipient = recipient_email or (user.email if user else None)
            if not recipient:
                logger.error("No se proporcionó email del destinatario")
                return False
            
            # Obtener plantilla de email
            email_template = self._get_email_template(notification_type)
            if not email_template:
                logger.error(f"No se encontró plantilla para el tipo de notificación: {notification_type_code}")
                return False
            
            # Preparar contexto
            full_context = self._prepare_context(user, context or {})
            
            # Renderizar contenido del email
            subject = self._render_template(email_template.subject, full_context)
            html_content = self._render_template(email_template.html_content, full_context)
            text_content = self._render_template(email_template.text_content, full_context) if email_template.text_content else None
            
            # Crear registro de notificación con serialización segura
            email_notification = EmailNotification(
                user=user,
                notification_type=notification_type,
                email_template=email_template,
                recipient_email=recipient,
                subject=subject,
                html_content=html_content,
                text_content=text_content or ''
            )
            # Usar método seguro para caracteres Unicode (crítico para sistemas financieros)
            email_notification.set_context_data_safe(full_context)
            email_notification.save()
            
            # Añadir a la cola o enviar inmediatamente
            if schedule_at or priority != 'normal':
                self._add_to_queue(email_notification, priority, schedule_at)
                return True
            else:
                return self._send_email_now(email_notification)
                
        except NotificationType.DoesNotExist:
            logger.error(f"Tipo de notificación no encontrado: {notification_type_code}")
            return False
        except Exception as e:
            logger.error(f"Error enviando notificación: {str(e)}")
            return False
    
    def _user_wants_notification(self, user: User, notification_type_code: str) -> bool:
        """
        Verifica si el usuario quiere recibir este tipo de notificación
        """
        try:
            preferences = UserNotificationPreference.objects.get(user=user)
            return preferences.is_notification_enabled(notification_type_code)
        except UserNotificationPreference.DoesNotExist:
            # Si no hay preferencias, crear con valores por defecto
            UserNotificationPreference.objects.create(user=user)
            return True
    
    def _get_email_template(self, notification_type: NotificationType) -> Optional[EmailTemplate]:
        """
        Obtiene la plantilla de email activa para el tipo de notificación
        """
        return EmailTemplate.objects.filter(
            notification_type=notification_type, 
            is_active=True
        ).first()
    
    def _prepare_context(self, user: User, additional_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara el contexto completo para renderizar la plantilla
        """
        context = {
            'user': {
                'username': user.username if user else '',
                'first_name': user.first_name if user else '',
                'last_name': user.last_name if user else '',
                'email': user.email if user else '',
                'full_name': f"{user.first_name} {user.last_name}".strip() if user else '',
            },
            'site': {
                'name': 'LlévateloExpress',
                'url': 'https://llevateloexpress.com',
                'contact_email': 'info@llevateloexpress.com',
                'phone': '+584121010744',
            },
            'current_year': timezone.now().year,
            **additional_context
        }
        return context
    
    def _render_template(self, template_content: str, context: Dict[str, Any]) -> str:
        """
        Renderiza una plantilla de Django con el contexto proporcionado
        """
        if not template_content:
            return ''
        
        template = Template(template_content)
        django_context = Context(context)
        return template.render(django_context)
    
    def _add_to_queue(self, email_notification: EmailNotification, priority: str, schedule_at: timezone.datetime = None):
        """
        Añade un email a la cola para procesamiento posterior
        """
        EmailQueue.objects.create(
            email_notification=email_notification,
            priority=priority,
            scheduled_at=schedule_at or timezone.now()
        )
        logger.info(f"Email añadido a la cola: {email_notification.subject}")
    
    def _send_email_now(self, email_notification: EmailNotification) -> bool:
        """
        Envía un email inmediatamente
        """
        try:
            # Crear mensaje de email
            msg = EmailMultiAlternatives(
                subject=email_notification.subject,
                body=email_notification.text_content or 'Este email requiere un cliente que soporte HTML.',
                from_email=self.from_email,
                to=[email_notification.recipient_email]
            )
            
            # Añadir contenido HTML si existe
            if email_notification.html_content:
                msg.attach_alternative(email_notification.html_content, "text/html")
            
            # Enviar email
            msg.send()
            
            # Marcar como enviado
            email_notification.mark_as_sent()
            logger.info(f"Email enviado exitosamente a {email_notification.recipient_email}")
            
            return True
            
        except Exception as e:
            error_message = str(e)
            email_notification.mark_as_failed(error_message)
            logger.error(f"Error enviando email a {email_notification.recipient_email}: {error_message}")
            
            return False
    
    def process_email_queue(self, batch_size: int = 10) -> int:
        """
        Procesa emails pendientes en la cola
        
        Args:
            batch_size: Cantidad de emails a procesar en este lote
            
        Returns:
            int: Cantidad de emails procesados exitosamente
        """
        processed_count = 0
        
        # Obtener emails pendientes de la cola
        pending_emails = EmailQueue.objects.filter(
            is_processed=False,
            scheduled_at__lte=timezone.now()
        ).select_related('email_notification')[:batch_size]
        
        for queue_item in pending_emails:
            email_notification = queue_item.email_notification
            
            # Marcar como en procesamiento
            queue_item.processing_started_at = timezone.now()
            queue_item.save()
            
            # Enviar email
            if self._send_email_now(email_notification):
                queue_item.is_processed = True
                queue_item.save()
                processed_count += 1
            else:
                # Si falla, marcar como no procesado para reintento
                queue_item.processing_started_at = None
                queue_item.save()
        
        if processed_count > 0:
            logger.info(f"Procesados {processed_count} emails de la cola")
        
        return processed_count
    
    def retry_failed_notifications(self, notification_ids: List[int] = None) -> int:
        """
        Reintenta envío de notificaciones fallidas
        
        Args:
            notification_ids: IDs específicos a reintentar (None para todos)
            
        Returns:
            int: Cantidad de notificaciones reintentadas
        """
        queryset = EmailNotification.objects.filter(status='failed')
        
        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)
        
        retried_count = 0
        
        for notification in queryset:
            if notification.can_retry():
                if self._send_email_now(notification):
                    retried_count += 1
        
        logger.info(f"Reintentadas {retried_count} notificaciones fallidas")
        return retried_count
    
    def get_user_notifications(self, user: User, limit: int = 50) -> List[EmailNotification]:
        """
        Obtiene las notificaciones de un usuario
        """
        return EmailNotification.objects.filter(
            user=user
        ).order_by('-created_at')[:limit]
    
    def update_user_preferences(self, user: User, preferences: Dict[str, Any]) -> bool:
        """
        Actualiza las preferencias de notificación de un usuario
        """
        try:
            user_prefs, created = UserNotificationPreference.objects.get_or_create(user=user)
            
            for key, value in preferences.items():
                if hasattr(user_prefs, key):
                    setattr(user_prefs, key, value)
            
            user_prefs.save()
            logger.info(f"Preferencias actualizadas para usuario {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando preferencias para {user.username}: {str(e)}")
            return False


# Instancia global del servicio de notificaciones
notification_service = NotificationService()


# Funciones de conveniencia para tipos específicos de notificaciones
def send_welcome_email(user: User) -> bool:
    """Envía email de bienvenida a un nuevo usuario"""
    context = {
                    'welcome_message': f'¡Bienvenido a LlévateloExpress, {user.first_name}!',
        'next_steps': [
            'Explora nuestro catálogo de productos',
            'Descubre nuestros planes de financiamiento',
            'Completa tu perfil para una mejor experiencia'
        ]
    }
    return notification_service.send_notification(user, 'welcome', context)


def send_registration_confirmation(user: User) -> bool:
    """Envía confirmación de registro"""
    context = {
        'confirmation_message': 'Tu cuenta ha sido creada exitosamente',
        'login_url': 'https://llevateloexpress.com/login.html'
    }
    return notification_service.send_notification(user, 'registration_confirmation', context)


def send_financing_application_notification(user: User, application_data: Dict[str, Any]) -> bool:
    """Envía notificación de solicitud de financiamiento"""
    context = {
        'application_id': application_data.get('id'),
        'product_name': application_data.get('product_name'),
        'amount': application_data.get('amount'),
        'plan': application_data.get('plan'),
        'application_date': application_data.get('created_at')
    }
    return notification_service.send_notification(user, 'financing_application', context)


def send_application_status_notification(user: User, status: str, application_data: Dict[str, Any]) -> bool:
    """Envía notificación de cambio de estado de solicitud"""
    notification_type_map = {
        'approved': 'application_approved',
        'rejected': 'application_rejected',
        'pending': 'application_pending'
    }
    
    notification_type = notification_type_map.get(status)
    if not notification_type:
        return False
    
    context = {
        'application_id': application_data.get('id'),
        'product_name': application_data.get('product_name'),
        'status': status,
        'reason': application_data.get('reason', ''),
        'next_steps': application_data.get('next_steps', [])
    }
    
    return notification_service.send_notification(user, notification_type, context) 