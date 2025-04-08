from rest_framework import serializers
from financing.models import FinancingPlan, Simulation
from products.serializers.product_serializers import ProductListSerializer

class FinancingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancingPlan
        fields = ['id', 'name', 'plan_type', 'slug', 'description', 
                 'min_initial_percentage', 'max_initial_percentage',
                 'interest_rate', 'min_term', 'max_term', 'adjudication_percentage',
                 'benefits', 'requirements', 'icon', 'banner_image']

class SimulationSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)
    plan_details = FinancingPlanSerializer(source='plan', read_only=True)
    
    class Meta:
        model = Simulation
        fields = ['id', 'user', 'product', 'product_details', 'plan', 'plan_details', 
                 'product_value', 'initial_percentage', 'initial_amount', 
                 'monthly_payment', 'term', 'simulation_data', 'created_at']
        read_only_fields = ['created_at']

class SimulationCreateSerializer(serializers.ModelSerializer):
    ip_address = serializers.IPAddressField(required=False)
    
    class Meta:
        model = Simulation
        fields = ['product', 'plan', 'product_value', 'initial_percentage', 
                 'initial_amount', 'monthly_payment', 'term', 'simulation_data', 'ip_address']
        
    def create(self, validated_data):
        # Obtener el usuario si está autenticado
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        
        # Obtener la dirección IP
        if not validated_data.get('ip_address') and request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            validated_data['ip_address'] = ip
            
        return super().create(validated_data)
