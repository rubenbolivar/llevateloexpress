from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product

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
    list_display = ('name', 'category', 'brand', 'price', 'stock', 'featured', 'thumbnail')
    list_filter = ('category', 'brand', 'featured')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'featured')
    readonly_fields = ('thumbnail_preview',)
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'category', 'brand', 'price', 'image', 'thumbnail_preview', 'description')
        }),
        ('Características', {
            'fields': ('features',),
        }),
        ('Especificaciones', {
            'fields': ('specs_general', 'specs_engine', 'specs_comfort', 'specs_safety'),
            'classes': ('collapse',)
        }),
        ('Inventario', {
            'fields': ('stock', 'featured')
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
