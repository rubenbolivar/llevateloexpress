from rest_framework import serializers
from django.contrib.auth.models import User
from financing.models import (
    FinancingPlan, FinancingRequest, Payment, 
    PaymentSchedule, ApplicationStatusHistory
)
from products.serializers.product_serializers import ProductListSerializer
from users.models import Customer


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
    """Serializer para el calendario de pagos"""
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentSchedule
        fields = [
            'id', 'payment_number', 'due_date', 'amount',
            'is_paid', 'paid_date', 'paid_amount',
            'days_late', 'late_fee', 'status'
        ]
    
    def get_status(self, obj):
        if obj.is_paid:
            return 'paid'
        elif obj.days_late > 0:
            return 'overdue'
        else:
            return 'pending'


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
    
    class Meta:
        model = FinancingRequest
        fields = [
            'id', 'application_number', 'customer_name',
            'product_name', 'product_image', 'product_price',
            'status', 'status_display', 'payment_amount',
            'payment_frequency', 'created_at'
        ]


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
            'employment_type', 'monthly_income'
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
        customer = request.user.customer
        
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
        validated_data['recorded_by'] = request.user
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
