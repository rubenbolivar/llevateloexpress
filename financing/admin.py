from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum, Count
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.contrib.admin import SimpleListFilter
from .models import (
    FinancingPlan, FinancingRequest, Payment, 
    PaymentSchedule, ApplicationStatusHistory,
    FinancingConfiguration, DownPaymentOption,
    FinancingTerm, PaymentFrequency, ProductCategory, SimulatorProduct, HelpText,
    CalculatorMode, PaymentMethod, CompanyBankAccount  # PaymentAttachment comentado temporalmente
)
import datetime

# Inline para el historial de estados
class ApplicationStatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ('from_status', 'to_status', 'changed_by', 'change_date', 'notes')
    can_delete = False

# Inline para el calendario de pagos
class PaymentScheduleInline(admin.TabularInline):
    model = PaymentSchedule
    extra = 0
    readonly_fields = ('payment_number', 'due_date', 'amount', 'is_paid', 'paid_date', 'days_late', 'late_fee')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

# Inline para pagos
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('payment_type', 'payment_method', 'amount', 'payment_date', 'status', 'reference_number')
    readonly_fields = ('created_at',)

# Inline para archivos adjuntos de pagos
# PaymentAttachmentInline comentado temporalmente hasta crear la migración correspondiente
# class PaymentAttachmentInline(admin.TabularInline):
#     model = PaymentAttachment
#     extra = 0
#     readonly_fields = ('file_type', 'uploaded_by', 'uploaded_at')
#     fields = ('file', 'description', 'file_type', 'uploaded_by', 'uploaded_at')

# Filtros personalizados
class PaymentStatusFilter(SimpleListFilter):
    title = 'Estado del Pago'
    parameter_name = 'payment_status'
    
    def lookups(self, request, model_admin):
        return (
            ('pending', 'Pendientes de Verificación'),
            ('verified', 'Verificados'),
            ('rejected', 'Rechazados'),
            ('processing', 'En Proceso'),
        )
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset

class PaymentDateFilter(SimpleListFilter):
    title = 'Fecha del Pago'
    parameter_name = 'payment_date'
    
    def lookups(self, request, model_admin):
        return (
            ('today', 'Hoy'),
            ('week', 'Esta Semana'),
            ('month', 'Este Mes'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'today':
            return queryset.filter(payment_date__date=datetime.date.today())
        elif self.value() == 'week':
            start_week = datetime.date.today() - datetime.timedelta(days=7)
            return queryset.filter(payment_date__date__gte=start_week)
        elif self.value() == 'month':
            start_month = datetime.date.today().replace(day=1)
            return queryset.filter(payment_date__date__gte=start_month)
        return queryset

@admin.register(FinancingPlan)
class FinancingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_down_payment_percentage', 'max_term_months', 'interest_rate', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Configuración del Plan', {
            'fields': (
                'min_down_payment_percentage',
                'max_term_months',
                'interest_rate'
            )
        }),
        ('Restricciones', {
            'fields': ('min_amount', 'max_amount')
        }),
    )

@admin.register(FinancingRequest)
class FinancingRequestAdmin(admin.ModelAdmin):
    list_display = (
        'application_number', 'customer_name', 'product_name', 
        'status_badge', 'product_price', 'created_at'
    )
    list_filter = ('status', 'payment_frequency', 'created_at', 'financing_plan')
    search_fields = (
        'application_number', 'customer__user__first_name', 
        'customer__user__last_name', 'customer__identity_document',
        'product__name'
    )
    readonly_fields = (
        'application_number', 'created_at', 'updated_at', 
        'submitted_at', 'approved_at', 'review_date'
    )
    
    inlines = [PaymentInline, PaymentScheduleInline, ApplicationStatusHistoryInline]
    
    fieldsets = (
        ('Información de la Solicitud', {
            'fields': (
                'application_number', 'customer', 'product', 
                'financing_plan', 'status'
            )
        }),
        ('Detalles Financieros', {
            'fields': (
                'product_price', 'down_payment_percentage', 'down_payment_amount',
                'financed_amount', 'interest_rate', 'total_interest', 'total_amount'
            )
        }),
        ('Plan de Pagos', {
            'fields': (
                'payment_frequency', 'number_of_payments', 'payment_amount'
            )
        }),
        ('Información del Cliente', {
            'fields': (
                'employment_type', 'monthly_income'
            ),
            'classes': ('collapse',)
        }),
        ('Documentación', {
            'fields': (
                'income_proof', 'id_document', 'address_proof'
            ),
            'classes': ('collapse',)
        }),
        ('Evaluación', {
            'fields': (
                'reviewed_by', 'review_date', 'review_notes', 'rejection_reason'
            ),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': (
                'created_at', 'updated_at', 'submitted_at', 'approved_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_applications', 'reject_applications', 'generate_payment_schedule']
    
    def customer_name(self, obj):
        return obj.customer.user.get_full_name()
    customer_name.short_description = 'Cliente'
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Producto'
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'submitted': 'blue',
            'under_review': 'yellow',
            'documentation_required': 'orange',
            'approved': 'green',
            'rejected': 'red',
            'active': 'green',
            'completed': 'gray',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def approve_applications(self, request, queryset):
        """Acción para aprobar solicitudes"""
        count = 0
        for app in queryset.filter(status__in=['submitted', 'under_review']):
            old_status = app.status
            app.status = 'approved'
            app.approved_at = timezone.now()
            app.reviewed_by = request.user
            app.review_date = timezone.now()
            app.save()
            
            # Registrar cambio de estado
            ApplicationStatusHistory.objects.create(
                application=app,
                from_status=old_status,
                to_status='approved',
                changed_by=request.user,
                notes='Aprobado desde el panel de administración'
            )
            
            # Generar calendario de pagos
            app.calculate_payment_schedule()
            count += 1
            
        self.message_user(request, f'{count} solicitudes aprobadas exitosamente.')
    approve_applications.short_description = "Aprobar solicitudes seleccionadas"
    
    def reject_applications(self, request, queryset):
        """Acción para rechazar solicitudes"""
        count = 0
        for app in queryset.filter(status__in=['submitted', 'under_review']):
            old_status = app.status
            app.status = 'rejected'
            app.reviewed_by = request.user
            app.review_date = timezone.now()
            app.save()
            
            # Registrar cambio de estado
            ApplicationStatusHistory.objects.create(
                application=app,
                from_status=old_status,
                to_status='rejected',
                changed_by=request.user,
                notes='Rechazado desde el panel de administración'
            )
            count += 1
            
        self.message_user(request, f'{count} solicitudes rechazadas.')
    reject_applications.short_description = "Rechazar solicitudes seleccionadas"
    
    def generate_payment_schedule(self, request, queryset):
        """Generar calendario de pagos para solicitudes aprobadas"""
        count = 0
        for app in queryset.filter(status='approved'):
            app.calculate_payment_schedule()
            count += 1
        self.message_user(request, f'Calendario de pagos generado para {count} solicitudes.')
    generate_payment_schedule.short_description = "Generar calendario de pagos"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'get_application_number', 'get_customer_name', 'payment_type', 
        'amount', 'currency', 'payment_method', 'status', 'payment_date',
        'has_receipt', 'verification_actions'
    ]
    list_filter = [
        PaymentStatusFilter, 'payment_type', 'currency', 
        PaymentDateFilter, 'payment_method'
    ]
    search_fields = [
        'application__application_number', 'application__customer__user__first_name',
        'application__customer__user__last_name', 'reference_number',
        'transaction_id', 'sender_name'
    ]
    readonly_fields = [
        'submitted_at', 'verified_at', 'submitted_by', 'get_receipt_preview',
        'get_verification_timeline'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('application', 'payment_type')
        }),
        ('Detalles del Pago', {
            'fields': ('amount', 'payment_date', 'status')
        }),
        ('Comprobante', {
            'fields': ('reference_number', 'transaction_id', 'receipt_file', 'get_receipt_preview')
        }),
        ('Información del Emisor', {
            'fields': ('sender_bank', 'sender_account', 'sender_name', 'sender_identification'),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('customer_notes', 'admin_notes', 'rejection_reason')
        }),
        ('Control Administrativo', {
            'fields': ('submitted_by', 'verified_by', 'submitted_at', 'verified_at', 'get_verification_timeline'),
            'classes': ('collapse',)
        }),
    )
    
    # inlines = [PaymentAttachmentInline]  # Comentado temporalmente hasta crear la migración
    
    actions = ['mark_as_verified', 'mark_as_rejected', 'mark_as_processing']
    
    def get_application_number(self, obj):
        return obj.application.application_number
    get_application_number.short_description = 'No. Solicitud'
    
    def get_customer_name(self, obj):
        return obj.application.customer.user.get_full_name()
    get_customer_name.short_description = 'Cliente'
    
    def has_receipt(self, obj):
        if obj.receipt_file:
            return format_html('<span style="color: green;">✓ Sí</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    has_receipt.short_description = 'Comprobante'
    
    def get_receipt_preview(self, obj):
        if obj.receipt_file:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px;" /><br>'
                '<a href="{}" target="_blank">Ver archivo completo</a>',
                obj.receipt_file.url, obj.receipt_file.url
            )
        return "No hay comprobante"
    get_receipt_preview.short_description = 'Vista Previa'
    
    def verification_actions(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<span style="background: orange; color: white; padding: 3px 8px; border-radius: 3px;">Pendiente de Verificación</span>'
            )
        elif obj.status == 'verified':
            return format_html(
                '<span style="background: green; color: white; padding: 3px 8px; border-radius: 3px;">✓ Verificado</span>'
            )
        elif obj.status == 'rejected':
            return format_html(
                '<span style="background: red; color: white; padding: 3px 8px; border-radius: 3px;">✗ Rechazado</span>'
            )
        return obj.get_status_display()
    verification_actions.short_description = 'Estado de Verificación'
    
    def get_verification_timeline(self, obj):
        timeline = obj.get_verification_timeline()
        if timeline:
            total_seconds = int(timeline.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "N/A"
    get_verification_timeline.short_description = 'Tiempo de Verificación'
    
    # Acciones personalizadas
    def mark_as_verified(self, request, queryset):
        updated = 0
        for payment in queryset:
            if payment.status == 'pending':
                payment.mark_as_verified(request.user, "Verificado masivamente desde admin")
                updated += 1
        
        self.message_user(request, f'{updated} pagos marcados como verificados.')
    mark_as_verified.short_description = "Marcar como verificados"
    
    def mark_as_rejected(self, request, queryset):
        updated = 0
        for payment in queryset:
            if payment.status == 'pending':
                payment.mark_as_rejected(request.user, "Rechazado masivamente desde admin")
                updated += 1
        
        self.message_user(request, f'{updated} pagos marcados como rechazados.')
    mark_as_rejected.short_description = "Marcar como rechazados"
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='processing')
        self.message_user(request, f'{updated} pagos marcados como en proceso.')
    mark_as_processing.short_description = "Marcar como en proceso"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'application__customer__user'
        )

# PaymentAttachment admin comentado temporalmente hasta crear la migración correspondiente
# @admin.register(PaymentAttachment)
# class PaymentAttachmentAdmin(admin.ModelAdmin):
#     list_display = ['payment', 'description', 'file_type', 'uploaded_by', 'uploaded_at']
#     list_filter = ['file_type', 'uploaded_at']
#     search_fields = ['payment__application__application_number', 'description']
#     readonly_fields = ['file_type', 'uploaded_by', 'uploaded_at']

@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'get_application_number', 'payment_number', 'due_date', 
        'amount', 'is_paid', 'paid_amount', 'days_late', 'late_fee'
    ]
    list_filter = ['is_paid', 'due_date']
    search_fields = ['application__application_number']
    readonly_fields = ['days_late', 'late_fee']
    
    def get_application_number(self, obj):
        return obj.application.application_number
    get_application_number.short_description = 'No. Solicitud'

# Configuración del simulador
class DownPaymentOptionInline(admin.TabularInline):
    model = DownPaymentOption
    extra = 1
    fields = ['percentage', 'is_active', 'order']


class FinancingTermInline(admin.TabularInline):
    model = FinancingTerm
    extra = 1
    fields = ['months', 'is_active', 'order']


class PaymentFrequencyInline(admin.TabularInline):
    model = PaymentFrequency
    extra = 1
    fields = ['frequency', 'is_active', 'order']


@admin.register(FinancingConfiguration)
class FinancingConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active']
    inlines = [DownPaymentOptionInline, FinancingTermInline, PaymentFrequencyInline]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['created_at']
        return []


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'order', 'product_count']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Productos'


@admin.register(SimulatorProduct)
class SimulatorProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_active', 'order']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_active', 'order']
    ordering = ['category', 'order', 'name']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('category', 'name', 'price', 'description')
        }),
        ('Configuración', {
            'fields': ('image_url', 'is_active', 'order')
        }),
    )


@admin.register(HelpText)
class HelpTextAdmin(admin.ModelAdmin):
    list_display = ['section', 'title', 'is_active', 'updated_at']
    list_filter = ['section', 'is_active']
    search_fields = ['title', 'content']
    
    fieldsets = (
        (None, {
            'fields': ('section', 'title', 'content', 'is_active')
        }),
    )
    
    class Media:
        js = ('https://cdn.ckeditor.com/4.16.2/standard/ckeditor.js',)
        
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['content'].widget.attrs['class'] = 'ckeditor'
        return form


@admin.register(CalculatorMode)
class CalculatorModeAdmin(admin.ModelAdmin):
    list_display = ['name', 'mode_type', 'is_active', 'order']
    list_filter = ['mode_type', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'order']
    ordering = ['order', 'name']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'mode_type', 'description', 'is_active', 'order')
        }),
        ('Configuración Compra Programada', {
            'fields': (
                'adjudication_percentage', 'initial_fee_percentage',
                'min_initial_contribution', 'max_initial_contribution'
            ),
            'description': 'Configuración específica para la modalidad de Compra Programada'
        }),
        ('Configuración Crédito Inmediato', {
            'fields': (
                'available_down_payments', 'available_terms', 'interest_rate'
            ),
            'description': 'Configuración específica para la modalidad de Crédito Inmediato'
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Agregar ayuda contextual
        form.base_fields['available_down_payments'].help_text = (
            "Para Crédito Inmediato: Porcentajes separados por coma (ej: 30,40,50,60)"
        )
        form.base_fields['available_terms'].help_text = (
            "Para Crédito Inmediato: Plazos en meses separados por coma (ej: 6,12,18,24)"
        )
        
        return form

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'payment_type', 'is_active', 'requires_reference', 
        'requires_receipt', 'min_amount', 'max_amount', 'order'
    ]
    list_filter = ['payment_type', 'is_active', 'requires_reference', 'requires_receipt']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'payment_type', 'description', 'instructions')
        }),
        ('Configuración', {
            'fields': ('requires_reference', 'requires_receipt', 'is_active', 'order')
        }),
        ('Límites', {
            'fields': ('min_amount', 'max_amount', 'processing_time_hours')
        }),
    )

@admin.register(CompanyBankAccount)
class CompanyBankAccountAdmin(admin.ModelAdmin):
    list_display = [
        'bank_name', 'account_number', 'currency', 'account_type',
        'is_active', 'is_default', 'get_payment_methods_count'
    ]
    list_filter = ['currency', 'account_type', 'is_active', 'is_default']
    search_fields = ['bank_name', 'account_number', 'account_holder']
    filter_horizontal = ['payment_methods']
    
    fieldsets = (
        ('Información Bancaria', {
            'fields': ('bank_name', 'account_type', 'account_number', 
                      'account_holder', 'routing_number')
        }),
        ('Detalles', {
            'fields': ('currency', 'identification_number', 'email', 'phone')
        }),
        ('Configuración', {
            'fields': ('is_active', 'is_default', 'payment_methods', 'instructions')
        }),
    )
    
    def get_payment_methods_count(self, obj):
        return obj.payment_methods.count()
    get_payment_methods_count.short_description = 'Métodos Asociados'

# Personalización del admin site
admin.site.site_header = "LlévateloExpress - Administración"
admin.site.site_title = "LlévateloExpress Admin"
admin.site.index_title = "Panel de Administración"
