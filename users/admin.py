from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Customer, Application

# Personalizar el admin de User para vincular con Customer
class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    verbose_name_plural = 'Perfil de Cliente'
    fk_name = 'user'

# Registrar User personalizado
class CustomUserAdmin(UserAdmin):
    inlines = (CustomerInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')

# Anular el registro del UserAdmin predeterminado
admin.site.unregister(User)
# Registrar nuestro UserAdmin personalizado
admin.site.register(User, CustomUserAdmin)

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
