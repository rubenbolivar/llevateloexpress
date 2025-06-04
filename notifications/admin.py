from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    NotificationType, 
    EmailTemplate, 
    UserNotificationPreference, 
    EmailNotification, 
    EmailQueue
)


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description', 'is_active')
        }),
        ('Información Temporal', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['notification_type', 'subject', 'is_active', 'created_at']
    list_filter = ['notification_type', 'is_active', 'created_at']
    search_fields = ['subject', 'html_content', 'text_content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('notification_type', 'subject', 'is_active')
        }),
        ('Contenido', {
            'fields': ('html_content', 'text_content'),
        }),
        ('Variables Disponibles', {
            'fields': ('available_variables',),
            'description': 'Variables que se pueden usar en la plantilla (formato JSON)'
        }),
        ('Información Temporal', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Configurar el widget para campos de texto grandes
        form.base_fields['html_content'].widget.attrs['rows'] = 15
        form.base_fields['text_content'].widget.attrs['rows'] = 10
        return form


@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_notifications_enabled', 'frequency', 'created_at']
    list_filter = ['email_notifications_enabled', 'frequency', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Configuraciones Generales', {
            'fields': ('email_notifications_enabled', 'frequency')
        }),
        ('Preferencias por Tipo de Notificación', {
            'fields': (
                'welcome_enabled',
                'registration_confirmation_enabled',
                'financing_application_enabled',
                'application_approved_enabled',
                'application_rejected_enabled',
                'application_pending_enabled',
                'payment_reminder_enabled',
                'payment_confirmation_enabled',
                'document_request_enabled',
                'newsletter_enabled',
                'promotion_enabled',
                'system_maintenance_enabled',
            ),
            'classes': ('collapse',),
        }),
        ('Información Temporal', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'get_recipient_name', 
        'recipient_email', 
        'notification_type', 
        'get_status_badge', 
        'created_at', 
        'sent_at'
    ]
    list_filter = ['status', 'notification_type', 'created_at', 'sent_at']
    search_fields = [
        'recipient_email', 
        'subject', 
        'user__username', 
        'user__email', 
        'user__first_name', 
        'user__last_name'
    ]
    readonly_fields = [
        'created_at', 
        'sent_at', 
        'opened_at', 
        'clicked_at', 
        'get_html_preview'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Destinatario', {
            'fields': ('user', 'recipient_email')
        }),
        ('Detalles de la Notificación', {
            'fields': ('notification_type', 'email_template', 'subject')
        }),
        ('Estado', {
            'fields': ('status', 'error_message', 'retry_count', 'max_retries')
        }),
        ('Contenido', {
            'fields': ('get_html_preview', 'html_content', 'text_content'),
            'classes': ('collapse',),
        }),
        ('Contexto de Datos', {
            'fields': ('context_data',),
            'classes': ('collapse',),
        }),
        ('Metadatos', {
            'fields': ('email_provider_id',),
            'classes': ('collapse',),
        }),
        ('Información Temporal', {
            'fields': ('created_at', 'sent_at', 'opened_at', 'clicked_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_recipient_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return "Usuario no registrado"
    get_recipient_name.short_description = "Destinatario"
    
    def get_status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'sent': '#28a745',
            'failed': '#dc3545',
            'bounced': '#fd7e14',
            'opened': '#17a2b8',
            'clicked': '#6f42c1',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = "Estado"
    
    def get_html_preview(self, obj):
        if obj.html_content:
            # Mostrar una vista previa limitada del HTML
            preview = obj.html_content[:500] + "..." if len(obj.html_content) > 500 else obj.html_content
            return format_html(
                '<div style="border: 1px solid #ddd; padding: 10px; max-height: 200px; overflow-y: auto;">'
                '<small>Vista previa del HTML:</small><br>{}</div>',
                mark_safe(preview)
            )
        return "No hay contenido HTML"
    get_html_preview.short_description = "Vista Previa HTML"
    
    actions = ['mark_as_pending', 'retry_failed_notifications']
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} notificaciones marcadas como pendientes.')
    mark_as_pending.short_description = "Marcar como pendientes"
    
    def retry_failed_notifications(self, request, queryset):
        count = 0
        for notification in queryset.filter(status='failed'):
            if notification.can_retry():
                notification.status = 'pending'
                notification.save()
                count += 1
        self.message_user(request, f'{count} notificaciones fallidas marcadas para reintentar.')
    retry_failed_notifications.short_description = "Reintentar notificaciones fallidas"


@admin.register(EmailQueue)
class EmailQueueAdmin(admin.ModelAdmin):
    list_display = [
        'get_email_subject', 
        'get_recipient_email', 
        'priority', 
        'scheduled_at', 
        'is_processed'
    ]
    list_filter = ['priority', 'is_processed', 'scheduled_at']
    search_fields = [
        'email_notification__subject', 
        'email_notification__recipient_email',
        'email_notification__user__username'
    ]
    readonly_fields = ['processing_started_at']
    date_hierarchy = 'scheduled_at'
    
    fieldsets = (
        ('Email', {
            'fields': ('email_notification',)
        }),
        ('Configuración de Cola', {
            'fields': ('priority', 'scheduled_at', 'is_processed')
        }),
        ('Procesamiento', {
            'fields': ('processing_started_at',),
            'classes': ('collapse',),
        }),
    )
    
    def get_email_subject(self, obj):
        return obj.email_notification.subject
    get_email_subject.short_description = "Asunto"
    
    def get_recipient_email(self, obj):
        return obj.email_notification.recipient_email
    get_recipient_email.short_description = "Destinatario"
    
    actions = ['mark_as_processed', 'mark_as_unprocessed']
    
    def mark_as_processed(self, request, queryset):
        updated = queryset.update(is_processed=True)
        self.message_user(request, f'{updated} elementos marcados como procesados.')
    mark_as_processed.short_description = "Marcar como procesados"
    
    def mark_as_unprocessed(self, request, queryset):
        updated = queryset.update(is_processed=False)
        self.message_user(request, f'{updated} elementos marcados como no procesados.')
    mark_as_unprocessed.short_description = "Marcar como no procesados"
