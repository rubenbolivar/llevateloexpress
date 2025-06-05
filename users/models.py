from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from financing.models import FinancingPlan

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    address = models.TextField(blank=True, verbose_name="Dirección")
    identity_document = models.CharField(max_length=20, verbose_name="Documento de identidad")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")
    occupation = models.CharField(max_length=100, blank=True, verbose_name="Ocupación")
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                                       verbose_name="Ingreso mensual")
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False, verbose_name="Verificado")
    is_profile_complete = models.BooleanField(default=False, verbose_name="Perfil completo")
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('in_review', 'En Revisión'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
        ('completed', 'Completada'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Cliente")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    financing_plan = models.ForeignKey(FinancingPlan, on_delete=models.CASCADE, verbose_name="Plan de financiamiento")
    application_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de solicitud")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto inicial")
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cuota mensual")
    term = models.IntegerField(verbose_name="Plazo (meses)")
    notes = models.TextField(blank=True, verbose_name="Notas")
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de aprobación")
    documents = models.JSONField(null=True, blank=True, verbose_name="Documentos requeridos")
    
    class Meta:
        verbose_name = "Solicitud"
        verbose_name_plural = "Solicitudes"
        ordering = ['-application_date']
    
    def __str__(self):
        return f"Solicitud de {self.customer} para {self.product.name}"
import uuid
from django.utils import timezone
from datetime import timedelta

class PasswordResetToken(models.Model):
    """
    Modelo para gestionar tokens de recuperación de contraseña
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="Token")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de uso")
    is_used = models.BooleanField(default=False, verbose_name="Usado")
    expires_at = models.DateTimeField(verbose_name="Fecha de expiración")
    
    class Meta:
        verbose_name = "Token de Recuperación"
        verbose_name_plural = "Tokens de Recuperación"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)  # Token válido por 24 horas
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Verifica si el token es válido (no usado y no expirado)"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Marca el token como usado"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"Token para {self.user.email} - {'Válido' if self.is_valid() else 'Inválido'}" 