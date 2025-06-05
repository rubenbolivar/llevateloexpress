from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

# Create your models here.

class FinancingPlan(models.Model):
    """Planes de financiamiento disponibles"""
    name = models.CharField(max_length=100, verbose_name="Nombre del plan")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Descripción")
    
    # Configuración del plan
    min_down_payment_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Porcentaje mínimo de inicial"
    )
    max_term_months = models.IntegerField(verbose_name="Plazo máximo en meses")
    interest_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        verbose_name="Tasa de interés anual %"
    )
    
    # Restricciones
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto mínimo")
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto máximo")
    
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Plan de Financiamiento"
        verbose_name_plural = "Planes de Financiamiento"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class FinancingRequest(models.Model):
    """Solicitud de financiamiento"""
    STATUSES = [
        ('draft', 'Borrador'),
        ('submitted', 'Enviada'),
        ('under_review', 'En Revisión'),
        ('documentation_required', 'Documentación Requerida'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
        ('active', 'Activa'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada')
    ]
    
    PAYMENT_FREQUENCIES = [
        ('weekly', 'Semanal'),
        ('biweekly', 'Quincenal'),
        ('monthly', 'Mensual')
    ]
    
    # Identificación única
    application_number = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False,
        verbose_name="Número de solicitud"
    )
    
    # Relaciones
    customer = models.ForeignKey(
        'users.Customer', 
        on_delete=models.CASCADE,
        related_name='financing_applications',
        verbose_name="Cliente"
    )
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.PROTECT,
        verbose_name="Producto"
    )
    financing_plan = models.ForeignKey(
        FinancingPlan, 
        on_delete=models.PROTECT,
        verbose_name="Plan de financiamiento"
    )
    
    # Estado
    status = models.CharField(
        max_length=30, 
        choices=STATUSES, 
        default='draft',
        verbose_name="Estado"
    )
    
    # Montos
    product_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio del producto"
    )
    down_payment_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Porcentaje de inicial"
    )
    down_payment_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Monto de inicial"
    )
    financed_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Monto a financiar"
    )
    interest_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        verbose_name="Tasa de interés"
    )
    total_interest = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Total de intereses"
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Monto total a pagar"
    )
    
    # Plazos
    payment_frequency = models.CharField(
        max_length=20,
        choices=PAYMENT_FREQUENCIES,
        verbose_name="Frecuencia de pago"
    )
    number_of_payments = models.IntegerField(verbose_name="Número de cuotas")
    payment_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Monto de cada cuota"
    )
    
    # Información adicional del cliente
    employment_type = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name="Tipo de empleo"
    )
    monthly_income = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Ingreso mensual"
    )
    
    # Documentación
    income_proof = models.FileField(
        upload_to='applications/income/%Y/%m/', 
        null=True, 
        blank=True,
        verbose_name="Comprobante de ingresos"
    )
    id_document = models.FileField(
        upload_to='applications/ids/%Y/%m/', 
        null=True, 
        blank=True,
        verbose_name="Documento de identidad"
    )
    address_proof = models.FileField(
        upload_to='applications/address/%Y/%m/', 
        null=True, 
        blank=True,
        verbose_name="Comprobante de domicilio"
    )
    
    # Evaluación
    reviewed_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='reviewed_applications',
        verbose_name="Revisado por"
    )
    review_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de revisión")
    review_notes = models.TextField(blank=True, verbose_name="Notas de revisión")
    rejection_reason = models.TextField(blank=True, verbose_name="Motivo de rechazo")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de envío")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de aprobación")
    
    class Meta:
        verbose_name = "Solicitud de Financiamiento"
        verbose_name_plural = "Solicitudes de Financiamiento"
        ordering = ['-created_at']
        permissions = [
            ("can_approve_application", "Can approve financing application"),
            ("can_reject_application", "Can reject financing application"),
        ]
    
    def __str__(self):
        return f"{self.application_number} - {self.customer.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.application_number:
            # Generar número único de solicitud
            self.application_number = self.generate_application_number()
        super().save(*args, **kwargs)
    
    def generate_application_number(self):
        """Genera un número único de solicitud"""
        prefix = "APP"
        year = timezone.now().year
        # Obtener el último número de este año
        last_app = FinancingRequest.objects.filter(
            application_number__startswith=f"{prefix}{year}"
        ).order_by('-application_number').first()
        
        if last_app:
            last_number = int(last_app.application_number[-5:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{year}{new_number:05d}"
    
    def calculate_payment_schedule(self):
        """Calcula y genera el calendario de pagos"""
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        
        if self.status != 'approved':
            return
        
        # Limpiar calendario existente
        self.payment_schedule.all().delete()
        
        # Fecha de inicio (primer pago)
        start_date = self.approved_at.date() if self.approved_at else timezone.now().date()
        
        # Calcular fechas según frecuencia
        for i in range(1, self.number_of_payments + 1):
            if self.payment_frequency == 'weekly':
                due_date = start_date + timedelta(weeks=i)
            elif self.payment_frequency == 'biweekly':
                due_date = start_date + timedelta(weeks=i*2)
            else:  # monthly
                due_date = start_date + relativedelta(months=i)
            
            PaymentSchedule.objects.create(
                application=self,
                payment_number=i,
                due_date=due_date,
                amount=self.payment_amount
            )


class Payment(models.Model):
    """Pagos realizados"""
    TYPES = [
        ('down_payment', 'Inicial'),
        ('installment', 'Cuota'),
        ('late_fee', 'Mora'),
        ('penalty', 'Penalización'),
        ('adjustment', 'Ajuste')
    ]
    
    METHODS = [
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia'),
        ('mobile_payment', 'Pago Móvil'),
        ('zelle', 'Zelle'),
        ('deposit', 'Depósito Bancario'),
        ('other', 'Otro')
    ]
    
    STATUSES = [
        ('pending', 'Pendiente'),
        ('verified', 'Verificado'),
        ('rejected', 'Rechazado')
    ]
    
    # Relaciones
    application = models.ForeignKey(
        FinancingRequest, 
        on_delete=models.CASCADE, 
        related_name='payments',
        verbose_name="Solicitud"
    )
    payment_schedule = models.ForeignKey(
        'PaymentSchedule',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name="Cuota programada"
    )
    
    # Detalles del pago
    payment_type = models.CharField(
        max_length=20, 
        choices=TYPES,
        verbose_name="Tipo de pago"
    )
    payment_method = models.CharField(
        max_length=20, 
        choices=METHODS,
        verbose_name="Método de pago"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default='pending',
        verbose_name="Estado"
    )
    
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Monto"
    )
    payment_date = models.DateTimeField(verbose_name="Fecha de pago")
    reference_number = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Número de referencia"
    )
    
    # Comprobante
    receipt = models.FileField(
        upload_to='payments/receipts/%Y/%m/', 
        null=True, 
        blank=True,
        verbose_name="Comprobante"
    )
    notes = models.TextField(blank=True, verbose_name="Notas")
    
    # Registro
    recorded_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        verbose_name="Registrado por"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments',
        verbose_name="Verificado por"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.amount} - {self.payment_date.strftime('%d/%m/%Y')}"


class PaymentSchedule(models.Model):
    """Calendario de pagos"""
    application = models.ForeignKey(
        FinancingRequest, 
        on_delete=models.CASCADE, 
        related_name='payment_schedule',
        verbose_name="Solicitud"
    )
    payment_number = models.IntegerField(verbose_name="Número de cuota")
    due_date = models.DateField(verbose_name="Fecha de vencimiento")
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Monto"
    )
    
    # Estado
    is_paid = models.BooleanField(default=False, verbose_name="Pagado")
    paid_date = models.DateField(null=True, blank=True, verbose_name="Fecha de pago")
    paid_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Monto pagado"
    )
    
    # Mora
    days_late = models.IntegerField(default=0, verbose_name="Días de atraso")
    late_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Cargo por mora"
    )
    
    class Meta:
        verbose_name = "Cuota Programada"
        verbose_name_plural = "Cuotas Programadas"
        ordering = ['application', 'payment_number']
        unique_together = ['application', 'payment_number']
    
    def __str__(self):
        return f"Cuota {self.payment_number} - {self.due_date}"
    
    def calculate_late_fee(self):
        """Calcula los días de atraso y el cargo por mora"""
        if self.is_paid or self.due_date >= timezone.now().date():
            self.days_late = 0
            self.late_fee = 0
        else:
            self.days_late = (timezone.now().date() - self.due_date).days
            # Calcular mora (ejemplo: 1% del monto por cada 7 días de atraso)
            self.late_fee = (self.amount * 0.01) * (self.days_late // 7)
        return self.late_fee


class ApplicationStatusHistory(models.Model):
    """Historial de cambios de estado de las solicitudes"""
    application = models.ForeignKey(
        FinancingRequest,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name="Solicitud"
    )
    from_status = models.CharField(
        max_length=30,
        choices=FinancingRequest.STATUSES,
        verbose_name="Estado anterior"
    )
    to_status = models.CharField(
        max_length=30,
        choices=FinancingRequest.STATUSES,
        verbose_name="Estado nuevo"
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Cambiado por"
    )
    change_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de cambio")
    notes = models.TextField(blank=True, verbose_name="Notas")
    
    class Meta:
        verbose_name = "Historial de Estado"
        verbose_name_plural = "Historiales de Estado"
        ordering = ['-change_date']
    
    def __str__(self):
        return f"{self.application.application_number}: {self.from_status} → {self.to_status}"


class FinancingConfiguration(models.Model):
    """Configuración global del sistema de financiamiento"""
    name = models.CharField(max_length=100, default="Configuración Principal")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración de Financiamiento"
        verbose_name_plural = "Configuraciones de Financiamiento"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Solo puede haber una configuración activa
        if self.is_active:
            FinancingConfiguration.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class DownPaymentOption(models.Model):
    """Opciones de porcentaje de inicial"""
    configuration = models.ForeignKey(FinancingConfiguration, on_delete=models.CASCADE, related_name='down_payment_options')
    percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Porcentaje de inicial (ej: 30.00)")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Orden de aparición en el simulador")
    
    class Meta:
        verbose_name = "Opción de Inicial"
        verbose_name_plural = "Opciones de Inicial"
        ordering = ['order', 'percentage']
    
    def __str__(self):
        return f"{self.percentage}%"


class FinancingTerm(models.Model):
    """Plazos de financiamiento disponibles"""
    configuration = models.ForeignKey(FinancingConfiguration, on_delete=models.CASCADE, related_name='financing_terms')
    months = models.IntegerField(help_text="Número de meses")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Orden de aparición en el simulador")
    
    class Meta:
        verbose_name = "Plazo de Financiamiento"
        verbose_name_plural = "Plazos de Financiamiento"
        ordering = ['order', 'months']
    
    def __str__(self):
        return f"{self.months} meses"


class PaymentFrequency(models.Model):
    """Frecuencias de pago disponibles"""
    FREQUENCY_CHOICES = [
        ('weekly', 'Semanal'),
        ('biweekly', 'Quincenal'),
        ('monthly', 'Mensual'),
    ]
    
    configuration = models.ForeignKey(FinancingConfiguration, on_delete=models.CASCADE, related_name='payment_frequencies')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Orden de aparición en el simulador")
    
    class Meta:
        verbose_name = "Frecuencia de Pago"
        verbose_name_plural = "Frecuencias de Pago"
        ordering = ['order']
    
    def __str__(self):
        return self.get_frequency_display()
    
    def get_payments_per_year(self):
        """Retorna el número de pagos por año según la frecuencia"""
        if self.frequency == 'weekly':
            return 52
        elif self.frequency == 'biweekly':
            return 26
        elif self.frequency == 'monthly':
            return 12
        return 12


class ProductCategory(models.Model):
    """Categorías de productos para el simulador"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Categoría de Producto"
        verbose_name_plural = "Categorías de Productos"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class SimulatorProduct(models.Model):
    """Productos disponibles en el simulador"""
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True, help_text="URL de la imagen del producto")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Producto del Simulador"
        verbose_name_plural = "Productos del Simulador"
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return f"{self.name} - ${self.price}"


class HelpText(models.Model):
    """Textos de ayuda para el simulador"""
    SECTION_CHOICES = [
        ('product_selection', 'Selección de Producto'),
        ('down_payment', 'Monto Inicial'),
        ('financing_term', 'Plazo de Financiamiento'),
        ('payment_frequency', 'Frecuencia de Pago'),
        ('general', 'Ayuda General'),
    ]
    
    section = models.CharField(max_length=50, choices=SECTION_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Puede usar HTML para formato")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Texto de Ayuda"
        verbose_name_plural = "Textos de Ayuda"
    
    def __str__(self):
        return f"{self.get_section_display()}: {self.title}"


class CalculatorMode(models.Model):
    """Modalidades de la calculadora (Compra Programada, Crédito Inmediato)"""
    MODE_CHOICES = [
        ('programada', 'Compra Programada'),
        ('credito', 'Crédito Inmediato'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre de la modalidad")
    mode_type = models.CharField(max_length=20, choices=MODE_CHOICES, unique=True, verbose_name="Tipo de modalidad")
    description = models.TextField(verbose_name="Descripción")
    
    # Configuración específica para Compra Programada
    adjudication_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=45.00,
        help_text="Porcentaje de adjudicación para compra programada (ej: 45.00)",
        verbose_name="Porcentaje de adjudicación"
    )
    initial_fee_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=5.00,
        help_text="Cuota inicial fija (ej: 5.00)",
        verbose_name="Cuota inicial (%)"
    )
    min_initial_contribution = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10.00,
        help_text="Aporte inicial mínimo (ej: 10.00)",
        verbose_name="Aporte inicial mínimo (%)"
    )
    max_initial_contribution = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=15.00,
        help_text="Aporte inicial máximo (ej: 15.00)",
        verbose_name="Aporte inicial máximo (%)"
    )
    
    # Configuración específica para Crédito Inmediato
    available_down_payments = models.TextField(
        blank=True,
        help_text="Porcentajes de inicial disponibles separados por coma (ej: 30,40,50,60)",
        verbose_name="Porcentajes de inicial disponibles"
    )
    available_terms = models.TextField(
        blank=True,
        help_text="Plazos disponibles en meses separados por coma (ej: 6,12,18,24)",
        verbose_name="Plazos disponibles"
    )
    interest_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        help_text="Tasa de interés anual (0 para sin intereses)",
        verbose_name="Tasa de interés anual (%)"
    )
    
    # Configuración general
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.IntegerField(default=0, help_text="Orden de aparición")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Modalidad de Calculadora"
        verbose_name_plural = "Modalidades de Calculadora"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_down_payment_options(self):
        """Retorna lista de opciones de inicial"""
        if self.available_down_payments:
            return [float(x.strip()) for x in self.available_down_payments.split(',')]
        return []
    
    def get_term_options(self):
        """Retorna lista de plazos disponibles"""
        if self.available_terms:
            return [int(x.strip()) for x in self.available_terms.split(',')]
        return []
