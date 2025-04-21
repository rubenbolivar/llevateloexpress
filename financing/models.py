from django.db import models
from django.contrib.auth.models import User
from products.models import Product

# Create your models here.

class FinancingPlan(models.Model):
    PLAN_TYPES = (
        ('programada', 'Compra Programada'),
        ('credito', 'Crédito Inmediato'),
    )
    
    name = models.CharField(max_length=100, verbose_name="Nombre")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, verbose_name="Tipo de plan")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Descripción")
    min_initial_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Porcentaje inicial mínimo")
    max_initial_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Porcentaje inicial máximo")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Tasa de interés anual")
    min_term = models.IntegerField(verbose_name="Plazo mínimo (meses)")
    max_term = models.IntegerField(verbose_name="Plazo máximo (meses)")
    adjudication_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, 
                                               verbose_name="Porcentaje para adjudicación")
    benefits = models.TextField(verbose_name="Beneficios")
    requirements = models.TextField(verbose_name="Requisitos")
    icon = models.CharField(max_length=50, default="fa-money-bill", verbose_name="Ícono (FontAwesome)") 
    banner_image = models.ImageField(upload_to='plans/', null=True, blank=True, verbose_name="Imagen de banner")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Plan de Financiamiento"
        verbose_name_plural = "Planes de Financiamiento"
    
    def __str__(self):
        return self.name

class Simulation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuario")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Producto")
    plan = models.ForeignKey(FinancingPlan, on_delete=models.CASCADE, verbose_name="Plan")
    product_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor del producto")
    initial_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Porcentaje inicial")
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto inicial")
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cuota mensual")
    term = models.IntegerField(verbose_name="Plazo (meses)")
    simulation_data = models.JSONField(verbose_name="Datos completos")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    
    class Meta:
        verbose_name = "Simulación"
        verbose_name_plural = "Simulaciones"
        ordering = ['-created_at']
    
    def __str__(self):
        product_name = self.product.name if self.product else "Producto personalizado"
        return f"Simulación de {product_name} - {self.plan.name}"
