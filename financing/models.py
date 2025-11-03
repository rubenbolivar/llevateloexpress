from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from django.core.exceptions import ValidationError
import os

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
    
    # Montos en LLEVO (sistema actual)
    product_price_llevos = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Precio del producto (LLEVO)"
    )
    down_payment_llevos = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Monto de inicial (LLEVO)"
    )
    financed_amount_llevos = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Monto a financiar (LLEVO)"
    )
    payment_amount_llevos = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Monto de cada cuota (LLEVO)"
    )
    
    # Montos antiguos (mantenidos por compatibilidad)
    product_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio del producto (USD) - DEPRECADO"
    )
    down_payment_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Porcentaje de inicial"
    )
    down_payment_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Monto de inicial (USD) - DEPRECADO"
    )
    financed_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Monto a financiar (USD) - DEPRECADO"
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
        verbose_name="Monto de cada cuota (USD) - DEPRECADO"
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


class PaymentMethod(models.Model):
    """Métodos de pago disponibles"""
    TYPES = [
        ('bank_transfer', 'Transferencia Bancaria'),
        ('mobile_payment', 'Pago Móvil'),
        ('zelle', 'Zelle'),
        ('binance', 'Binance Pay'),
        ('cash', 'Efectivo'),
        ('check', 'Cheque'),
        ('other', 'Otro')
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre del método")
    payment_type = models.CharField(max_length=20, choices=TYPES, verbose_name="Tipo de pago")
    description = models.TextField(blank=True, verbose_name="Descripción")
    instructions = models.TextField(blank=True, verbose_name="Instrucciones para el usuario")
    requires_reference = models.BooleanField(default=True, verbose_name="Requiere número de referencia")
    requires_receipt = models.BooleanField(default=True, verbose_name="Requiere comprobante")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.IntegerField(default=0, verbose_name="Orden de visualización")
    
    # Configuración específica
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Monto mínimo")
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Monto máximo")
    processing_time_hours = models.IntegerField(default=24, verbose_name="Tiempo de procesamiento (horas)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class CompanyBankAccount(models.Model):
    """Cuentas bancarias de la empresa para recibir pagos"""
    ACCOUNT_TYPES = [
        ('checking', 'Cuenta Corriente'),
        ('savings', 'Cuenta de Ahorros'),
        ('business', 'Cuenta Empresarial')
    ]
    
    CURRENCIES = [
        ('VES', 'Bolívares (VES)'),
        ('USD', 'Dólares (USD)'),
        ('EUR', 'Euros (EUR)')
    ]
    
    bank_name = models.CharField(max_length=100, verbose_name="Nombre del banco")
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, verbose_name="Tipo de cuenta")
    account_number = models.CharField(max_length=50, verbose_name="Número de cuenta")
    account_holder = models.CharField(max_length=200, verbose_name="Titular de la cuenta")
    routing_number = models.CharField(max_length=50, blank=True, verbose_name="Número de ruta/ABA")
    
    # Información adicional
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='USD', verbose_name="Moneda")
    identification_number = models.CharField(max_length=50, blank=True, verbose_name="RIF/Cédula titular")
    email = models.EmailField(blank=True, verbose_name="Email de notificaciones")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    
    # Configuración
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    is_default = models.BooleanField(default=False, verbose_name="Cuenta principal")
    payment_methods = models.ManyToManyField(PaymentMethod, blank=True, verbose_name="Métodos de pago asociados")
    
    # Instrucciones específicas
    instructions = models.TextField(blank=True, verbose_name="Instrucciones especiales")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cuenta Bancaria de la Empresa"
        verbose_name_plural = "Cuentas Bancarias de la Empresa"
        ordering = ['-is_default', 'bank_name']
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_number} ({self.currency})"
    
    def save(self, *args, **kwargs):
        # Solo una cuenta puede ser principal por moneda
        if self.is_default:
            CompanyBankAccount.objects.filter(
                currency=self.currency, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Pagos realizados - MODELO EXPANDIDO PARA COMPROBANTES"""
    TYPES = [
        ('initial', 'Pago Inicial'),
        ('installment', 'Cuota Mensual'),
        ('late_fee', 'Mora'),
        ('penalty', 'Penalización'),
        ('partial', 'Pago Parcial'),
        ('adjustment', 'Ajuste'),
        ('refund', 'Reembolso')
    ]
    
    STATUSES = [
        ('pending', 'Pendiente de Verificación'),
        ('verified', 'Verificado y Aprobado'),
        ('rejected', 'Rechazado'),
        ('processing', 'En Proceso de Verificación'),
        ('requires_review', 'Requiere Revisión Manual')
    ]
    
    # Relaciones principales
    application = models.ForeignKey(
        FinancingRequest, 
        on_delete=models.CASCADE, 
        related_name='payments',
        verbose_name="Solicitud de Financiamiento"
    )
    # Método de pago (CharField para compatibilidad con BD existente)
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Transferencia Bancaria'),
        ('mobile_payment', 'Pago Móvil'),
        ('zelle', 'Zelle'),
        ('binance', 'Binance Pay'),
        ('cash', 'Efectivo'),
        ('check', 'Cheque'),
        ('other', 'Otro')
    ]
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Método de Pago"
    )
    # company_account = models.ForeignKey(
    #     CompanyBankAccount,
    #     on_delete=models.PROTECT,
    #     null=True,
    #     blank=True,
    #     verbose_name="Cuenta de Destino"
    # )
    payment_schedule = models.ForeignKey(
        'PaymentSchedule',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name="Cuota Programada"
    )
    
    # Información básica del pago
    payment_type = models.CharField(max_length=20, choices=TYPES, verbose_name="Tipo de Pago")
    status = models.CharField(max_length=20, choices=STATUSES, default='pending', verbose_name="Estado")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Pagado")
    currency = models.CharField(max_length=3, default='USD', verbose_name="Moneda")
    
    # Fechas
    payment_date = models.DateTimeField(verbose_name="Fecha del Pago")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Verificación")
    
    # Detalles del comprobante
    reference_number = models.CharField(
        max_length=100, 
        null=True,
        blank=True,
        verbose_name="Número de Referencia",
        help_text="Número de referencia del banco o sistema de pago"
    )
    transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="ID de Transacción",
        help_text="ID único de la transacción (para Zelle, Binance, etc.)"
    )
    
    # Información bancaria específica
    sender_bank = models.CharField(max_length=100, null=True, blank=True, verbose_name="Banco Emisor")
    sender_account = models.CharField(max_length=50, null=True, blank=True, verbose_name="Cuenta Emisora")
    sender_name = models.CharField(max_length=200, null=True, blank=True, verbose_name="Nombre del Emisor")
    sender_identification = models.CharField(max_length=50, null=True, blank=True, verbose_name="Cédula/RIF Emisor")
    sender_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Teléfono Emisor")
    
    # Comprobante (archivo)
    receipt_file = models.FileField(
        upload_to='payments/receipts/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name="Comprobante de Pago",
        help_text="Captura de pantalla o PDF del comprobante"
    )
    
    # Notas y observaciones
    notes = models.TextField(
        blank=True,
        default='',
        verbose_name="Notas",
        help_text="Notas generales sobre el pago"
    )
    customer_notes = models.TextField(
        blank=True,
        verbose_name="Notas del Cliente",
        help_text="Comentarios adicionales del cliente sobre el pago"
    )
    admin_notes = models.TextField(
        blank=True,
        verbose_name="Notas del Administrador",
        help_text="Comentarios internos sobre la verificación"
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de Rechazo",
        help_text="Razón específica si el pago fue rechazado"
    )
    
    # Control administrativo
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='submitted_payments',
        verbose_name="Registrado por"
    )
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='recorded_payments',
        verbose_name="Grabado por"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments',
        verbose_name="Verificado por"
    )
    
    # Metadatos
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-payment_date']
        permissions = [
            ("can_verify_payment", "Puede verificar pagos"),
            ("can_reject_payment", "Puede rechazar pagos"),
            ("can_view_all_payments", "Puede ver todos los pagos"),
        ]
    
    def __str__(self):
        return f"{self.get_payment_type_display()} - ${self.amount} - {self.get_status_display()}"
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.amount <= 0:
            raise ValidationError("El monto debe ser mayor que cero")
        
        # Validaciones básicas (simplificadas para compatibilidad con CharField)
        if self.payment_method in ['bank_transfer', 'mobile_payment', 'zelle'] and not self.reference_number:
            raise ValidationError("Este método de pago requiere número de referencia")
        
        if self.payment_method != 'cash' and not self.receipt_file:
            raise ValidationError("Este método de pago requiere comprobante")
        
        # Nota: Validaciones de montos mínimos/máximos temporalmente deshabilitadas
        # hasta implementar la migración completa a ForeignKey
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_receipt_filename(self):
        """Obtiene el nombre del archivo de comprobante"""
        if self.receipt_file:
            return os.path.basename(self.receipt_file.name)
        return None
    
    def mark_as_verified(self, verified_by_user, admin_notes=""):
        """Marca el pago como verificado"""
        self.status = 'verified'
        self.verified_by = verified_by_user
        self.verified_at = timezone.now()
        if admin_notes:
            self.admin_notes = admin_notes
        self.save()
        
        # Actualizar el cronograma de pagos si aplica
        if self.payment_schedule:
            self.payment_schedule.mark_as_paid(self.amount, self.payment_date.date())
    
    def mark_as_rejected(self, rejected_by_user, rejection_reason):
        """Marca el pago como rechazado"""
        self.status = 'rejected'
        self.verified_by = rejected_by_user
        self.verified_at = timezone.now()
        self.rejection_reason = rejection_reason
        self.save()
    
    def get_verification_timeline(self):
        """Calcula el tiempo transcurrido para verificación"""
        if not self.submitted_at:  # Nueva validación para evitar TypeError
            return None
        if self.verified_at:
            return self.verified_at - self.submitted_at
        return timezone.now() - self.submitted_at


class PaymentAttachment(models.Model):
    """Archivos adjuntos adicionales para pagos"""
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name="Pago"
    )
    file = models.FileField(
        upload_to='payments/attachments/%Y/%m/%d/',
        verbose_name="Archivo Adjunto"
    )
    file_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Tipo de Archivo",
        help_text="Detectado automáticamente"
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descripción del Archivo"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Subido por"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Subida")
    
    class Meta:
        verbose_name = "Archivo Adjunto de Pago"
        verbose_name_plural = "Archivos Adjuntos de Pagos"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Adjunto de {self.payment} - {self.description}"
    
    def save(self, *args, **kwargs):
        if self.file:
            # Detectar tipo de archivo
            file_extension = os.path.splitext(self.file.name)[1].lower()
            type_mapping = {
                '.pdf': 'PDF Document',
                '.jpg': 'JPEG Image',
                '.jpeg': 'JPEG Image',
                '.png': 'PNG Image',
                '.gif': 'GIF Image',
                '.doc': 'Word Document',
                '.docx': 'Word Document',
                '.xls': 'Excel Spreadsheet',
                '.xlsx': 'Excel Spreadsheet'
            }
            self.file_type = type_mapping.get(file_extension, 'Unknown')
        
        super().save(*args, **kwargs)


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
    
    def mark_as_paid(self, paid_amount, paid_date):
        """Marca la cuota como pagada"""
        self.is_paid = True
        self.paid_amount = paid_amount
        self.paid_date = paid_date
        self.save()


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

# SIGNALS PARA GENERACIÓN AUTOMÁTICA DE CRONOGRAMAS
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=FinancingRequest)
def track_status_change(sender, instance, **kwargs):
    """Detecta cambios de estado en solicitudes de financiamiento"""
    if instance.pk:
        try:
            old_instance = FinancingRequest.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except FinancingRequest.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=FinancingRequest)
def auto_generate_payment_schedule(sender, instance, created, **kwargs):
    """Genera automáticamente el cronograma de pagos cuando se aprueba una solicitud"""
    if not created:  # Solo para actualizaciones, no para nuevas solicitudes
        old_status = getattr(instance, '_old_status', None)
        current_status = instance.status
        
        # Si cambió de cualquier estado a 'approved', generar cronograma
        if old_status != 'approved' and current_status == 'approved':
            print(f"Generando cronograma automatico para solicitud {instance.application_number}")
            instance.calculate_payment_schedule()
            print(f"Cronograma generado exitosamente para {instance.application_number}")
            
            # Registrar en el historial
            from django.contrib.auth.models import User
            changed_by_user = instance.reviewed_by
            if not changed_by_user:
                # Usar el primer superuser disponible como fallback
                changed_by_user = User.objects.filter(is_superuser=True).first()
            
            # Crear historial solo si no existe uno reciente
            if changed_by_user:
                recent_history = ApplicationStatusHistory.objects.filter(
                    application=instance,
                    to_status=current_status,
                    changed_by=changed_by_user,
                    change_date__gte=timezone.now() - timezone.timedelta(seconds=5)
                ).exists()
                
                if not recent_history:
                    ApplicationStatusHistory.objects.create(
                        application=instance,
                        from_status=old_status or 'unknown',
                        to_status=current_status,
                        changed_by=changed_by_user,
                        notes="Aprobado - Cronograma de pagos generado automáticamente"
                    )
