from rest_framework import serializers
from django.contrib.auth.models import User
from financing.models import (
    FinancingPlan, FinancingRequest, Payment, 
    PaymentSchedule, ApplicationStatusHistory
)
from products.serializers.product_serializers import ProductListSerializer
from users.models import Customer
from products.llevo_models import LlevoRate


class FinancingPlanSerializer(serializers.ModelSerializer):
    """Serializer para planes de financiamiento"""
    class Meta:
        model = FinancingPlan
        fields = [
            'id', 'name', 'slug', 'description',
            'min_down_payment_percentage', 'max_term_months',
            'interest_rate', 'min_amount', 'max_amount', 'is_active'
        ]


class PaymentScheduleSerializer(serializers.ModelSerializer):
    """Serializer para el calendario de pagos con nuevas reglas de ventanas"""
    status = serializers.SerializerMethodField()
    amount_llevo = serializers.SerializerMethodField()
    amount_ves = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    window_status = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentSchedule
        fields = [
            'id', 'application', 'payment_number', 'due_date', 'amount', 'amount_llevo', 'amount_llevos', 'amount_ves',
            'is_paid', 'paid_date', 'paid_amount',
            'days_late', 'late_fee', 'status', 'status_display',
            'payment_window_start', 'payment_window_end',
            'penalty_amount', 'penalty_applied',
            'window_status', 'days_until_due', 'days_overdue'
        ]
    
    def get_status(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        
        if obj.is_paid:
            return 'paid'
        
        # Verificar si esta vencido (paso la ventana de pago)
        if obj.payment_window_end and today > obj.payment_window_end:
            return 'overdue'
        
        # Esta en ventana de pago
        if obj.payment_window_start and obj.payment_window_end:
            if obj.payment_window_start <= today <= obj.payment_window_end:
                return 'in_window'
        
        return 'pending'
    
    def get_status_display(self, obj):
        status = self.get_status(obj)
        status_map = {
            'paid': 'Pagado',
            'overdue': 'Vencido',
            'in_window': 'En ventana de pago',
            'pending': 'Pendiente'
        }
        return status_map.get(status, 'Desconocido')
    
    def get_window_status(self, obj):
        """Estado de la ventana de pago en espanol"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if obj.is_paid:
            return 'Cuota pagada'
        
        if not obj.payment_window_start or not obj.payment_window_end:
            return 'Sin ventana definida'
        
        if today < obj.payment_window_start:
            days_to_start = (obj.payment_window_start - today).days
            return f'Inicia en {days_to_start} dias'
        elif obj.payment_window_start <= today <= obj.payment_window_end:
            days_left = (obj.payment_window_end - today).days
            if days_left == 0:
                return 'Ultimo dia sin penalizacion'
            return f'{days_left} dias para pagar sin penalizacion'
        else:
            return 'Vencido - Aplica penalizacion de  USD'
    
    def get_days_until_due(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        if obj.is_paid or not obj.payment_window_end:
            return 0
        days = (obj.payment_window_end - today).days
        return max(0, days)
    
    def get_days_overdue(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        if obj.is_paid or not obj.payment_window_end:
            return 0
        if today > obj.payment_window_end:
            return (today - obj.payment_window_end).days
        return 0
    
    def get_amount_llevo(self, obj):
        """Usar amount_llevos si existe, sino convertir"""
        if obj.amount_llevos:
            return float(obj.amount_llevos)
        # Fallback: convertir desde USD
        current_rate = LlevoRate.get_current_rate()
        if current_rate and obj.amount:
            conversion_factor = current_rate.llevo_value / current_rate.usdt_ves_rate
            return round(float(obj.amount) / float(conversion_factor))
        return int(obj.amount) if obj.amount else 0
    
    def get_amount_ves(self, obj):
        """Convertir LLEVO a VES para pagos R4"""
        from decimal import Decimal
        current_rate = LlevoRate.get_current_rate()
        amount_llevo = obj.amount_llevos if obj.amount_llevos else obj.amount
        if current_rate and amount_llevo:
            amount_ves = Decimal(str(amount_llevo)) * current_rate.llevo_value
            return float(amount_ves)
        return 0.0



class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para pagos"""
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_type', 'payment_type_display',
            'payment_method', 'payment_method_display',
            'amount', 'payment_date', 'reference_number',
            'status', 'status_display', 'receipt', 'notes',
            'created_at'
        ]
        read_only_fields = ['created_at']


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer para el historial de estados"""
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    from_status_display = serializers.CharField(source='get_from_status_display', read_only=True)
    to_status_display = serializers.CharField(source='get_to_status_display', read_only=True)
    
    class Meta:
        model = ApplicationStatusHistory
        fields = [
            'id', 'from_status', 'from_status_display',
            'to_status', 'to_status_display',
            'changed_by', 'changed_by_name',
            'change_date', 'notes'
        ]


class FinancingRequestListSerializer(serializers.ModelSerializer):
    """Serializer para listado de solicitudes"""
    customer_name = serializers.CharField(source='customer.user.get_full_name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    product_price_llevo = serializers.SerializerMethodField()
    payment_amount_llevo = serializers.SerializerMethodField()
    payment_amount_ves = serializers.SerializerMethodField()
    initial_payment_completed = serializers.SerializerMethodField()
    down_payment_ves = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancingRequest
        fields = [
            'id', 'application_number', 'customer_name',
            'product_name', 'product_image', 'product_price', 'product_price_llevo',
            'status', 'status_display', 'payment_amount', 'payment_amount_llevo', 'payment_amount_ves',
            "down_payment_llevos",
            'payment_frequency', 'created_at', 'initial_payment_completed', 'down_payment_ves'
        ]
    
    def get_product_price_llevo(self, obj):
        """Usar el valor LLEVO predefinido del producto (misma lógica que solicitud)"""
        # Usar el valor LLEVO predefinido del producto, no conversiones
        if obj.product and hasattr(obj.product, 'price_llevo'):
            return obj.product.price_llevo or 0
        # Fallback a conversión si no existe valor predefinido
        current_rate = LlevoRate.get_current_rate()
        if current_rate and obj.product_price:
            conversion_factor = current_rate.llevo_value / current_rate.usdt_ves_rate
            return round(obj.product_price / conversion_factor)
        return int(obj.product_price) if obj.product_price else 0
    
    def get_payment_amount_llevo(self, obj):
        """Usar el valor LLEVO predefinido del producto (misma lógica que solicitud)"""
        # Usar el valor LLEVO predefinido del producto, no conversiones
        if obj.product and hasattr(obj.product, 'cuota_mensual_llevos'):
            return obj.product.cuota_mensual_llevos or 0
        # Fallback al valor almacenado si existe
        return obj.payment_amount_llevos if obj.payment_amount_llevos else 0
    
    def get_payment_amount_ves(self, obj):
        """Convertir LLEVO a VES para pagos R4"""
        from decimal import Decimal
        current_rate = LlevoRate.get_current_rate()
        if current_rate and obj.payment_amount:
            # USD a LLEVO, luego LLEVO a VES
            conversion_factor = current_rate.usdt_ves_rate / (15 * Decimal('1.18'))
            amount_llevo = obj.payment_amount * conversion_factor
            amount_ves = Decimal(str(amount_llevo)) * current_rate.llevo_value
            return float(amount_ves)
        return 0.0

    def get_initial_payment_completed(self, obj):
        """Verificar si el pago inicial ya fue completado"""
        from financing.models import Payment
        return Payment.objects.filter(
            application=obj,
            payment_type='initial',
            status='verified'
        ).exists()

    def get_down_payment_ves(self, obj):
        """Convertir pago inicial LLEVO a VES"""
        from decimal import Decimal
        current_rate = LlevoRate.get_current_rate()
        down_payment_llevos = obj.down_payment_llevos or 0
        if current_rate and down_payment_llevos:
            return float(Decimal(str(down_payment_llevos)) * current_rate.llevo_value)
        return 0.0


class FinancingRequestDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para solicitudes"""
    customer_name = serializers.CharField(source='customer.user.get_full_name', read_only=True)
    product_details = ProductListSerializer(source='product', read_only=True)
    financing_plan_details = FinancingPlanSerializer(source='financing_plan', read_only=True)
    payment_schedule = PaymentScheduleSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_frequency_display = serializers.CharField(source='get_payment_frequency_display', read_only=True)
    
    class Meta:
        model = FinancingRequest
        fields = [
            'id', 'application_number', 'customer', 'customer_name',
            'product', 'product_details', 'financing_plan', 'financing_plan_details',
            'status', 'status_display',
            'product_price', 'down_payment_percentage', 'down_payment_amount',
            'financed_amount', 'interest_rate', 'total_interest', 'total_amount',
            'payment_frequency', 'payment_frequency_display',
            'number_of_payments', 'payment_amount',
            'employment_type', 'monthly_income',
            'income_proof', 'id_document', 'address_proof',
            'review_notes', 'rejection_reason',
            'created_at', 'submitted_at', 'approved_at',
            'payment_schedule', 'payments', 'status_history'
        ]
        read_only_fields = [
            'application_number', 'created_at', 'submitted_at', 'approved_at'
        ]


class FinancingRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear solicitudes"""
    class Meta:
        model = FinancingRequest
        fields = [
            'product', 'financing_plan',
            'product_price', 'down_payment_percentage', 'down_payment_amount',
            'financed_amount', 'interest_rate', 'total_interest', 'total_amount',
            'payment_frequency', 'number_of_payments', 'payment_amount',
            'employment_type', 'monthly_income',
            # Campos LLEVO (sistema principal)
            'product_price_llevos', 'down_payment_llevos',
            'financed_amount_llevos', 'payment_amount_llevos',
        ]
    
    def validate(self, data):
        """Validar los datos de la solicitud"""
        # Validar que el porcentaje de inicial esté dentro del rango permitido
        plan = data['financing_plan']
        if data['down_payment_percentage'] < plan.min_down_payment_percentage:
            raise serializers.ValidationError({
                'down_payment_percentage': f'El porcentaje mínimo de inicial es {plan.min_down_payment_percentage}%'
            })
        
        # Validar que el monto esté dentro del rango permitido
        if data['product_price'] < plan.min_amount:
            raise serializers.ValidationError({
                'product_price': f'El monto mínimo para este plan es ${plan.min_amount}'
            })
        
        if data['product_price'] > plan.max_amount:
            raise serializers.ValidationError({
                'product_price': f'El monto máximo para este plan es ${plan.max_amount}'
            })
        
        return data
    
    def create(self, validated_data):
        """Crear la solicitud y registrar el estado inicial"""
        # Obtener el cliente del usuario autenticado
        request = self.context.get('request')
        
        try:
            customer = request.user.customer
        except:
            raise serializers.ValidationError({
                'customer': 'El usuario no tiene un perfil de cliente asociado'
            })
        
        # Crear la solicitud
        application = FinancingRequest.objects.create(
            customer=customer,
            **validated_data
        )
        
        # Registrar el estado inicial
        ApplicationStatusHistory.objects.create(
            application=application,
            from_status='draft',
            to_status='draft',
            changed_by=request.user,
            notes='Solicitud creada'
        )
        
        return application


class FinancingRequestUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar solicitudes"""
    class Meta:
        model = FinancingRequest
        fields = [
            'employment_type', 'monthly_income',
            'income_proof', 'id_document', 'address_proof'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer para registrar pagos"""
    class Meta:
        model = Payment
        fields = [
            'application', 'payment_schedule', 'payment_type',
            'payment_method', 'amount', 'payment_date',
            'reference_number', 'receipt', 'notes'
        ]
    
    def create(self, validated_data):
        """Crear el pago"""
        request = self.context.get('request')
        validated_data['submitted_by'] = request.user
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class FinancingCalculatorSerializer(serializers.Serializer):
    """Serializer para el calculador de financiamiento"""
    product_id = serializers.IntegerField(required=True)
    financing_plan_id = serializers.IntegerField(required=True)
    down_payment_percentage = serializers.IntegerField(min_value=0, max_value=100)
    payment_frequency = serializers.ChoiceField(
        choices=FinancingRequest.PAYMENT_FREQUENCIES
    )
    term_months = serializers.IntegerField(min_value=1)
    
    def validate(self, data):
        """Validar los datos del cálculo"""
        from products.models import Product
        
        # Validar que el producto existe
        try:
            product = Product.objects.get(id=data['product_id'])
            data['product'] = product
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                'product_id': 'Producto no encontrado'
            })
        
        # Validar que el plan existe
        try:
            plan = FinancingPlan.objects.get(id=data['financing_plan_id'])
            data['financing_plan'] = plan
        except FinancingPlan.DoesNotExist:
            raise serializers.ValidationError({
                'financing_plan_id': 'Plan de financiamiento no encontrado'
            })
        
        # Validar restricciones del plan
        if data['down_payment_percentage'] < plan.min_down_payment_percentage:
            raise serializers.ValidationError({
                'down_payment_percentage': f'El porcentaje mínimo de inicial es {plan.min_down_payment_percentage}%'
            })
        
        if data['term_months'] > plan.max_term_months:
            raise serializers.ValidationError({
                'term_months': f'El plazo máximo es {plan.max_term_months} meses'
            })
        
        return data
