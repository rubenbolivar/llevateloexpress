from django.db import models
from decimal import Decimal

class LlevoRate(models.Model):
    """
    Modelo para manejar tasas de conversión LLEVO
    1 LLEVO = (USDT-VES P2P Rate) × 15 × 1.18
    """
    usdt_ves_rate = models.DecimalField(
        max_digits=12, 
        decimal_places=6, 
        verbose_name="Tasa USDT-VES P2P",
        help_text="Tasa actual USDT a VES en P2P"
    )
    llevo_value = models.DecimalField(
        max_digits=12, 
        decimal_places=6, 
        verbose_name="Valor LLEVO en VES",
        help_text="Calculado automáticamente: USDT-VES × 15 × 1.18",
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    notes = models.TextField(blank=True, verbose_name="Notas", help_text="Observaciones sobre esta tasa")
    
    class Meta:
        verbose_name = "Tasa LLEVO"
        verbose_name_plural = "Tasas LLEVO"
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        # Calcular automáticamente el valor LLEVO
        self.llevo_value = self.usdt_ves_rate * Decimal('15') * Decimal('1.18')
        
        # Si es activa, desactivar otras tasas
        if self.is_active:
            LlevoRate.objects.filter(is_active=True).update(is_active=False)
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"1 LLEVO = {self.llevo_value:,.2f} VES (USDT-VES: {self.usdt_ves_rate})"
    
    @classmethod
    def get_current_rate(cls):
        """Obtener la tasa activa actual"""
        try:
            return cls.objects.filter(is_active=True).latest('created_at')
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def convert_llevo_to_ves(cls, llevo_amount):
        """Convertir LLEVO a VES usando la tasa actual"""
        current_rate = cls.get_current_rate()
        if current_rate:
            return llevo_amount * current_rate.llevo_value
        return llevo_amount * Decimal('0')  # Sin tasa activa
    
    @classmethod
    def convert_usd_to_llevo(cls, usd_amount):
        """Convertir USD a LLEVO (para migración)"""
        current_rate = cls.get_current_rate()
        if current_rate:
            # 1 USD ≈ 1 USDT en conversión aproximada
            # LLEVO = USD / (USDT-VES / (15 × 1.18))
            llevo_per_usd = current_rate.usdt_ves_rate / (Decimal('15') * Decimal('1.18'))
            return usd_amount * llevo_per_usd
        return usd_amount  # Fallback 1:1 si no hay tasa