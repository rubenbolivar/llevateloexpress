from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum, Count
from .models import (
    FinancingPlan, FinancingRequest, Payment, 
    PaymentSchedule, ApplicationStatusHistory,
    FinancingConfiguration, DownPaymentOption,
    FinancingTerm, PaymentFrequency, ProductCategory, SimulatorProduct, HelpText,
    CalculatorMode
)

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
    list_display = (
        'id', 'application_number', 'payment_type', 'amount', 
        'payment_date', 'payment_method', 'status_badge', 'recorded_by'
    )
    list_filter = ('payment_type', 'payment_method', 'status', 'payment_date')
    search_fields = (
        'application__application_number', 
        'reference_number',
        'application__customer__user__first_name',
        'application__customer__user__last_name'
    )
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Información del Pago', {
            'fields': (
                'application', 'payment_schedule', 'payment_type',
                'amount', 'payment_date'
            )
        }),
        ('Método de Pago', {
            'fields': (
                'payment_method', 'reference_number', 'status'
            )
        }),
        ('Documentación', {
            'fields': ('receipt', 'notes')
        }),
        ('Registro', {
            'fields': (
                'recorded_by', 'verified_by', 'created_at', 'updated_at'
            )
        }),
    )
    
    actions = ['verify_payments', 'reject_payments']
    
    def application_number(self, obj):
        return obj.application.application_number
    application_number.short_description = 'Número de Solicitud'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'yellow',
            'verified': 'green',
            'rejected': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def verify_payments(self, request, queryset):
        """Verificar pagos pendientes"""
        count = queryset.filter(status='pending').update(
            status='verified',
            verified_by=request.user
        )
        
        # Actualizar cuotas pagadas
        for payment in queryset.filter(status='verified', payment_schedule__isnull=False):
            schedule = payment.payment_schedule
            schedule.is_paid = True
            schedule.paid_date = payment.payment_date.date()
            schedule.paid_amount = payment.amount
            schedule.save()
            
        self.message_user(request, f'{count} pagos verificados exitosamente.')
    verify_payments.short_description = "Verificar pagos seleccionados"
    
    def reject_payments(self, request, queryset):
        """Rechazar pagos"""
        count = queryset.filter(status='pending').update(
            status='rejected',
            verified_by=request.user
        )
        self.message_user(request, f'{count} pagos rechazados.')
    reject_payments.short_description = "Rechazar pagos seleccionados"

@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'application_number', 'payment_number', 'due_date', 
        'amount', 'is_paid_badge', 'days_late', 'late_fee'
    )
    list_filter = ('is_paid', 'due_date')
    search_fields = (
        'application__application_number',
        'application__customer__user__first_name',
        'application__customer__user__last_name'
    )
    date_hierarchy = 'due_date'
    
    def application_number(self, obj):
        return obj.application.application_number
    application_number.short_description = 'Número de Solicitud'
    
    def is_paid_badge(self, obj):
        if obj.is_paid:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">Pagado</span>'
            )
        elif obj.days_late > 0:
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px 10px; border-radius: 3px;">Vencido</span>'
            )
        else:
            return format_html(
                '<span style="background-color: yellow; color: black; padding: 3px 10px; border-radius: 3px;">Pendiente</span>'
            )
    is_paid_badge.short_description = 'Estado'
    
    def get_queryset(self, request):
        """Actualizar automáticamente los días de atraso"""
        qs = super().get_queryset(request)
        # Actualizar días de atraso para cuotas no pagadas
        for schedule in qs.filter(is_paid=False):
            schedule.calculate_late_fee()
            schedule.save()
        return qs

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
