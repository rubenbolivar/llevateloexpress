from rest_framework import serializers
from .models import EmailNotification, UserNotificationPreference, NotificationType, EmailTemplate


class NotificationTypeSerializer(serializers.ModelSerializer):
    """
    Serializer para tipos de notificaciones
    """
    class Meta:
        model = NotificationType
        fields = ['id', 'code', 'name', 'description', 'is_active']


class EmailTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer para plantillas de email
    """
    notification_type_name = serializers.CharField(source='notification_type.name', read_only=True)
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'notification_type', 'notification_type_name', 'subject', 
            'html_content', 'text_content', 'available_variables', 'is_active'
        ]


class EmailNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer para notificaciones de email
    """
    notification_type_name = serializers.CharField(source='notification_type.name', read_only=True)
    notification_type_code = serializers.CharField(source='notification_type.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_name = serializers.SerializerMethodField()
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailNotification
        fields = [
            'id', 'user_name', 'recipient_email', 'notification_type_name', 
            'notification_type_code', 'subject', 'status', 'status_display',
            'created_at', 'sent_at', 'opened_at', 'clicked_at', 'error_message',
            'retry_count', 'time_since_created'
        ]
    
    def get_user_name(self, obj):
        if obj.user:
            full_name = f"{obj.user.first_name} {obj.user.last_name}".strip()
            return full_name or obj.user.username
        return "Usuario no registrado"
    
    def get_time_since_created(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"hace {diff.days} días"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"hace {hours} horas"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"hace {minutes} minutos"
        else:
            return "hace unos segundos"


class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer para preferencias de notificación de usuario
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserNotificationPreference
        fields = [
            'id', 'user_email', 'user_name', 'email_notifications_enabled', 'frequency',
            'welcome_enabled', 'registration_confirmation_enabled', 
            'financing_application_enabled', 'application_approved_enabled',
            'application_rejected_enabled', 'application_pending_enabled',
            'payment_reminder_enabled', 'payment_confirmation_enabled',
            'document_request_enabled', 'newsletter_enabled', 
            'promotion_enabled', 'system_maintenance_enabled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user_email', 'user_name', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        full_name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        return full_name or obj.user.username


class NotificationStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de notificaciones
    """
    total = serializers.IntegerField()
    unread = serializers.IntegerField()
    failed = serializers.IntegerField()
    by_type = serializers.DictField()


class SendNotificationSerializer(serializers.Serializer):
    """
    Serializer para enviar notificaciones
    """
    notification_type = serializers.CharField(max_length=50)
    recipient_email = serializers.EmailField(required=False)
    context = serializers.JSONField(required=False, default=dict)
    priority = serializers.ChoiceField(
        choices=['high', 'normal', 'low'], 
        default='normal',
        required=False
    )
    schedule_at = serializers.DateTimeField(required=False)
    
    def validate_notification_type(self, value):
        """
        Validar que el tipo de notificación existe y está activo
        """
        try:
            NotificationType.objects.get(code=value, is_active=True)
            return value
        except NotificationType.DoesNotExist:
            raise serializers.ValidationError(
                f"El tipo de notificación '{value}' no existe o no está activo"
            )


class UnsubscribeSerializer(serializers.Serializer):
    """
    Serializer para desuscripción de notificaciones
    """
    email = serializers.EmailField()
    token = serializers.CharField(max_length=100, required=False)
    
    def validate_email(self, value):
        """
        Validar que el email existe en el sistema
        """
        from django.contrib.auth.models import User
        
        try:
            User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Email no encontrado en el sistema") 