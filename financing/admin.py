from django.contrib import admin
from .models import FinancingPlan, Simulation

@admin.register(FinancingPlan)
class FinancingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'min_initial_percentage', 'interest_rate', 'is_active')
    list_filter = ('plan_type', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'plan_type', 'slug', 'description', 'icon', 'banner_image', 'is_active')
        }),
        ('Parámetros Financieros', {
            'fields': ('min_initial_percentage', 'max_initial_percentage', 'interest_rate', 
                      'min_term', 'max_term', 'adjudication_percentage')
        }),
        ('Detalles adicionales', {
            'fields': ('benefits', 'requirements'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Simulation)
class SimulationAdmin(admin.ModelAdmin):
    list_display = ('get_user_or_ip', 'product', 'plan', 'product_value', 'monthly_payment', 'created_at')
    list_filter = ('plan', 'created_at')
    search_fields = ('user__username', 'user__email', 'product__name')
    readonly_fields = ('created_at', 'ip_address')
    
    def get_user_or_ip(self, obj):
        if obj.user:
            return obj.user.username
        return f"Anónimo ({obj.ip_address})"
    get_user_or_ip.short_description = 'Usuario'
