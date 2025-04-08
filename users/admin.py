from django.contrib import admin
from .models import Customer, Application

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'identity_document', 'verified')
    list_filter = ('verified',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone', 'identity_document')
    readonly_fields = ('created_at',)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'financing_plan', 'status', 'application_date')
    list_filter = ('status', 'financing_plan', 'application_date')
    search_fields = ('customer__user__username', 'customer__user__email', 'product__name')
    readonly_fields = ('application_date',)
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('customer',)
        }),
        ('Detalles de Financiamiento', {
            'fields': ('product', 'financing_plan', 'initial_amount', 'monthly_payment', 'term')
        }),
        ('Estado de la Solicitud', {
            'fields': ('status', 'application_date', 'approved_date', 'notes')
        }),
        ('Documentación', {
            'fields': ('documents',),
            'classes': ('collapse',)
        }),
    )
