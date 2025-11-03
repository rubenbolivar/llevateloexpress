from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product
from .llevo_models import LlevoRate

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'icon_display', 'product_count')
    search_fields = ('name', 'id')
    prepopulated_fields = {'slug': ('name',)}
    
    def icon_display(self, obj):
        return format_html('<i class="fa {}"></i> {}', obj.icon, obj.icon)
    icon_display.short_description = 'Icono'
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Productos'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price_llevo_formatted', 'inicial_llevos_formatted', 'cuota_mensual_formatted', 'stock', 'out_of_stock', 'featured', 'thumbnail')
    list_filter = ('category', 'brand', 'featured')
    search_fields = ('name', 'description')
    list_editable = ('stock', 'out_of_stock', 'featured')
    readonly_fields = ('thumbnail_preview', 'price_conversion_preview', 'financing_preview')
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'category', 'brand', 'image', 'thumbnail_preview', 'description')
        }),
        ('Precios y Financiamiento', {
            'fields': ('price_llevo', 'inicial_llevos', 'cuota_mensual_llevos', 'price', 'price_conversion_preview', 'financing_preview'),
            'description': 'Precio principal en LLEVO y monto de inicial fijo definido por el admin.'
        }),
        ('Características', {
            'fields': ('features',),
        }),
        ('Especificaciones', {
            'fields': ('specs_general', 'specs_engine', 'specs_comfort', 'specs_safety'),
            'classes': ('collapse',)
        }),
        ('Inventario', {
            'fields': ('stock', 'out_of_stock', 'featured')
        }),
    )
    
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    thumbnail.short_description = 'Vista previa'
    
    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" style="max-height: 300px; object-fit: contain;" />', obj.image.url)
        return "-"
    thumbnail_preview.short_description = 'Vista previa de imagen'
    
    def price_llevo_formatted(self, obj):
        if obj.price_llevo:
            return format_html(
                '<strong style="color: #28a745;">{} LLEVO</strong>',
                obj.price_llevo
            )
        return "-"
    price_llevo_formatted.short_description = 'Precio LLEVO'
    
    def price_usd_formatted(self, obj):
        if obj.price:
            return format_html(
                '<span style="color: #6c757d;">${} USD</span>',
                f"{obj.price:,.2f}"
            )
        return "-"
    price_usd_formatted.short_description = 'Precio USD (Respaldo)'
    
    def inicial_llevos_formatted(self, obj):
        if obj.inicial_llevos:
            return format_html(
                '<strong style="color: #007bff;">{} LLEVO</strong>',
                obj.inicial_llevos
            )
        return format_html('<span style="color: #dc3545;">No definida</span>')
    inicial_llevos_formatted.short_description = 'Inicial'
    
    def cuota_mensual_formatted(self, obj):
        if obj.cuota_mensual_llevos:
            return format_html(
                '<strong style="color: #17a2b8;">{} LLEVO</strong>',
                obj.cuota_mensual_llevos
            )
        return format_html('<span style="color: #6c757d;">Automática</span>')
    cuota_mensual_formatted.short_description = 'Cuota Mensual'
    
    def price_conversion_preview(self, obj):
        from decimal import Decimal
        current_rate = LlevoRate.get_current_rate()
        if not current_rate:
            return "No hay tasa LLEVO activa"
            
        content = '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">'
        
        if obj.price_llevo and obj.price:
            # Mostrar ambos precios
            llevo_to_ves = obj.price_llevo * current_rate.llevo_value
            content += f'<strong>Precio LLEVO:</strong> {obj.price_llevo} LLEVO<br>'
            content += f'<strong>Precio USD:</strong> ${obj.price:,.2f} USD<br>'
            content += f'<strong>Equivalencia VES:</strong> {llevo_to_ves:,.2f} VES<br>'
            content += f'<small class="text-muted">Tasa actual: 1 LLEVO = {current_rate.llevo_value:,.2f} VES</small>'
        elif obj.price_llevo:
            # Solo precio LLEVO
            llevo_to_ves = obj.price_llevo * current_rate.llevo_value
            content += f'<strong>Precio LLEVO:</strong> {obj.price_llevo} LLEVO<br>'
            content += f'<strong>Equivalencia VES:</strong> {llevo_to_ves:,.2f} VES'
        elif obj.price:
            # Solo precio USD - sugerir conversión (redondeo estándar)
            conversion_factor = current_rate.llevo_value / current_rate.usdt_ves_rate
            suggested_llevo = round(obj.price / conversion_factor)
            content += f'<strong>Precio USD:</strong> ${obj.price:,.2f} USD<br>'
            content += f'<strong style="color: #ffc107;">Sugerencia LLEVO:</strong> {suggested_llevo} LLEVO<br>'
            content += f'<small class="text-muted">Redondeo estándar (≥0.5 → arriba, <0.5 → abajo)</small>'
        else:
            content += '<span class="text-muted">Configure los precios</span>'
            
        content += '</div>'
        return format_html(content)
    price_conversion_preview.short_description = 'Vista previa de conversión'
    
    def financing_preview(self, obj):
        if not obj.price_llevo or not obj.inicial_llevos:
            return format_html('<span class="text-muted">Configure precio e inicial en LLEVO</span>')
        
        # Calcular financiamiento CrediLlevo
        monto_financiado = obj.price_llevo - obj.inicial_llevos
        
        # Usar cuota manual si está configurada, sino calcular automáticamente
        if obj.cuota_mensual_llevos and obj.cuota_mensual_llevos > 0:
            cuota_mensual = obj.cuota_mensual_llevos
            cuota_type = "Manual"
            color = "#17a2b8"  # Azul para manual
        else:
            cuota_mensual = monto_financiado / 24  # 24 meses fijos - cálculo automático
            cuota_type = "Automática"
            color = "#2196f3"  # Azul estándar para automático
        
        content = f'<div style="background: #e3f2fd; padding: 10px; border-radius: 5px; border-left: 4px solid {color};">'
        content += '<strong>Plan CrediLlevo Inmediato:</strong><br>'
        content += f'<strong>Precio:</strong> {obj.price_llevo} LLEVO<br>'
        content += f'<strong>Inicial:</strong> {obj.inicial_llevos} LLEVO<br>'
        content += f'<strong>A financiar:</strong> {monto_financiado} LLEVO<br>'
        content += f'<strong>Cuota mensual:</strong> {cuota_mensual:.0f} LLEVO x 24 meses<br>'
        content += f'<small class="text-muted">Sin intereses • Plazo fijo 24 meses • Cuota {cuota_type}</small>'
        content += '</div>'
        
        return format_html(content)
    financing_preview.short_description = 'Vista previa CrediLlevo'

@admin.register(LlevoRate)
class LlevoRateAdmin(admin.ModelAdmin):
    list_display = ('usdt_ves_rate', 'llevo_value_formatted', 'is_active', 'created_at_formatted')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('llevo_value', 'llevo_calculation_preview')
    search_fields = ('usdt_ves_rate', 'notes')
    
    fieldsets = (
        ('Tasa USDT-VES', {
            'fields': ('usdt_ves_rate', 'llevo_calculation_preview')
        }),
        ('Resultado LLEVO', {
            'fields': ('llevo_value',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active', 'notes')
        }),
    )
    
    def has_module_permission(self, request):
        """Solo superadministradores pueden ver el módulo de tasas LLEVO"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Solo superadministradores pueden ver tasas LLEVO"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Solo superadministradores pueden agregar tasas LLEVO"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Solo superadministradores pueden modificar tasas LLEVO"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Solo superadministradores pueden eliminar tasas LLEVO"""
        return request.user.is_superuser
    
    def llevo_value_formatted(self, obj):
        if obj.llevo_value:
            return format_html(
                '<strong style="color: #28a745;">{} VES</strong>',
                f"{obj.llevo_value:,.2f}"
            )
        return "-"
    llevo_value_formatted.short_description = 'Valor LLEVO'
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = 'Fecha'
    
    def llevo_calculation_preview(self, obj):
        if obj.usdt_ves_rate:
            from decimal import Decimal
            calculation = obj.usdt_ves_rate * Decimal('15') * Decimal('1.18')
            return format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">'
                '<strong>Cálculo:</strong><br>'
                '{} × 15 × 1.18 = <strong style="color: #28a745;">{} VES</strong><br>'
                '<small class="text-muted">1 LLEVO = {} VES</small>'
                '</div>',
                obj.usdt_ves_rate, f"{calculation:,.2f}", f"{calculation:,.2f}"
            )
        return "Ingrese la tasa USDT-VES para ver el cálculo"
    llevo_calculation_preview.short_description = 'Vista previa del cálculo'
