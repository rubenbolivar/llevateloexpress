from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class NotificationType(models.Model):
    """
    Tipos de notificaciones disponibles en el sistema
    """
    NOTIFICATION_TYPES = [
        ('welcome', 'Bienvenida'),
        ('registration_confirmation', 'Confirmación de Registro'),
        ('financing_application', 'Solicitud de Financiamiento'),
        ('application_approved', 'Solicitud Aprobada'),
        ('application_rejected', 'Solicitud Rechazada'),
        ('application_pending', 'Solicitud Pendiente'),
        ('payment_reminder', 'Recordatorio de Pago'),
        ('payment_confirmation', 'Confirmación de Pago'),
        ('document_request', 'Solicitud de Documentos'),
        ('newsletter', 'Boletín Informativo'),
        ('promotion', 'Promoción Especial'),
        ('system_maintenance', 'Mantenimiento del Sistema'),
    ]
    
    code = models.CharField(max_length=50, unique=True, choices=NOTIFICATION_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tipo de Notificación"
        verbose_name_plural = "Tipos de Notificaciones"
        
    def __str__(self):
        return self.name


class EmailTemplate(models.Model):
    """
    Plantillas de emails para las notificaciones
    """
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200, help_text="Asunto del email")
    html_content = models.TextField(help_text="Contenido HTML del email")
    text_content = models.TextField(blank=True, help_text="Contenido en texto plano (opcional)")
    
    # Variables disponibles en la plantilla
    available_variables = models.JSONField(
        default=dict, 
        help_text="Variables disponibles para usar en la plantilla (JSON)"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Plantilla de Email"
        verbose_name_plural = "Plantillas de Email"
        
    def __str__(self):
        return f"{self.notification_type.name} - {self.subject}"


class UserNotificationPreference(models.Model):
    """
    Preferencias de notificación por usuario
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Preferencias por tipo de notificación
    welcome_enabled = models.BooleanField(default=True)
    registration_confirmation_enabled = models.BooleanField(default=True)
    financing_application_enabled = models.BooleanField(default=True)
    application_approved_enabled = models.BooleanField(default=True)
    application_rejected_enabled = models.BooleanField(default=True)
    application_pending_enabled = models.BooleanField(default=True)
    payment_reminder_enabled = models.BooleanField(default=True)
    payment_confirmation_enabled = models.BooleanField(default=True)
    document_request_enabled = models.BooleanField(default=True)
    newsletter_enabled = models.BooleanField(default=True)
    promotion_enabled = models.BooleanField(default=True)
    system_maintenance_enabled = models.BooleanField(default=True)
    
    # Configuraciones generales
    email_notifications_enabled = models.BooleanField(default=True)
    frequency = models.CharField(max_length=20, choices=[
        ('immediate', 'Inmediato'),
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
    ], default='immediate')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Preferencia de Notificación"
        verbose_name_plural = "Preferencias de Notificaciones"
        
    def __str__(self):
        return f"Preferencias de {self.user.username}"
    
    def is_notification_enabled(self, notification_type_code):
        """
        Verifica si un tipo de notificación está habilitado para el usuario
        """
        if not self.email_notifications_enabled:
            return False
            
        field_name = f"{notification_type_code}_enabled"
        return getattr(self, field_name, True)


class EmailNotification(models.Model):
    """
    Registro de emails enviados
    """
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('sent', 'Enviado'),
        ('failed', 'Error'),
        ('bounced', 'Rebotado'),
        ('opened', 'Abierto'),
        ('clicked', 'Click Realizado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_notifications')
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    email_template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    
    # Contexto usado para generar el email
    context_data = models.JSONField(default=dict)
    
    # Estado del envío
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    # Metadatos adicionales
    email_provider_id = models.CharField(max_length=100, blank=True, help_text="ID del proveedor de email")
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    class Meta:
        verbose_name = "Notificación por Email"
        verbose_name_plural = "Notificaciones por Email"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.notification_type.name} para {self.recipient_email} - {self.status}"
    
    def mark_as_sent(self):
        """Marca la notificación como enviada"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error_message):
        """Marca la notificación como fallida"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save()
    
    def mark_as_opened(self):
        """Marca la notificación como abierta"""
        if self.status == 'sent':
            self.status = 'opened'
            self.opened_at = timezone.now()
            self.save()
    
    def mark_as_clicked(self):
        """Marca la notificación como con click realizado"""
        self.status = 'clicked'
        self.clicked_at = timezone.now()
        self.save()
    
    def can_retry(self):
        """Verifica si se puede reintentar el envío"""
        return self.status == 'failed' and self.retry_count < self.max_retries


class EmailQueue(models.Model):
    """
    Cola de emails para procesar de forma asíncrona
    """
    PRIORITY_CHOICES = [
        ('high', 'Alta'),
        ('normal', 'Normal'),
        ('low', 'Baja'),
    ]
    
    email_notification = models.OneToOneField(EmailNotification, on_delete=models.CASCADE)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    scheduled_at = models.DateTimeField(default=timezone.now)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Cola de Email"
        verbose_name_plural = "Cola de Emails"
        ordering = ['priority', 'scheduled_at']
        
    def __str__(self):
        return f"Cola: {self.email_notification.subject} - {self.priority}"
