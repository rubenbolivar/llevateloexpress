from django.db import models

# Create your models here.

class Category(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Descripción")
    icon = models.CharField(max_length=50, verbose_name="Ícono")
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Categoría")
    brand = models.CharField(max_length=100, verbose_name="Marca")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (USD)", help_text="DEPRECADO: Use price_llevo")
    price_llevo = models.PositiveIntegerField(verbose_name="Precio (LLEVO)", null=True, blank=True, help_text="Precio en LLEVO (número entero)")
    inicial_llevos = models.PositiveIntegerField(verbose_name="Inicial (LLEVO)", null=True, blank=True, help_text="Monto de inicial fijo en LLEVOs definido por el admin")
    cuota_mensual_llevos = models.PositiveIntegerField(verbose_name="Cuota Mensual (LLEVO)", null=True, blank=True, help_text="Cuota mensual específica en LLEVO para 24 meses - si está vacío se calcula automáticamente")
    image = models.ImageField(upload_to='products/', verbose_name="Imagen principal")
    description = models.TextField(verbose_name="Descripción")
    features = models.JSONField(verbose_name="Características", help_text="Lista de características destacadas")
    specs_general = models.JSONField(verbose_name="Especificaciones generales", blank=True, null=True)
    specs_engine = models.JSONField(verbose_name="Especificaciones del motor", blank=True, null=True)
    specs_comfort = models.JSONField(verbose_name="Especificaciones de confort", blank=True, null=True)
    specs_safety = models.JSONField(verbose_name="Especificaciones de seguridad", blank=True, null=True)
    stock = models.IntegerField(default=0, verbose_name="Disponibilidad")
    out_of_stock = models.BooleanField(default=False, verbose_name="Sin Stock", help_text="Marcar si el producto no está disponible (no se mostrará en el catálogo)")
    featured = models.BooleanField(default=False, verbose_name="Destacado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-featured', 'name']
        
    def __str__(self):
        return self.name
