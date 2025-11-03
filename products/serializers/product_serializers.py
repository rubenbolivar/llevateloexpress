from rest_framework import serializers
from products.models import Category, Product
from products.llevo_models import LlevoRate
import json

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon']

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    price_llevo = serializers.SerializerMethodField()
    price_ves = serializers.SerializerMethodField()

    # Información del plan de financiamiento
    financing_plan_name = serializers.CharField(
        source='financing_plan.name',
        read_only=True,
        allow_null=True
    )
    financing_plan_slug = serializers.CharField(
        source='financing_plan.slug',
        read_only=True,
        allow_null=True
    )
    financing_term_months = serializers.IntegerField(
        source='financing_plan.max_term_months',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'brand',
            'price', 'price_llevo', 'price_ves',
            'inicial_llevos', 'cuota_mensual_llevos',
            'financing_plan_name', 'financing_plan_slug', 'financing_term_months',
            'image', 'featured', 'out_of_stock'
        ]
    
    def get_price_llevo(self, obj):
        """Convertir precio USD a LLEVO o usar price_llevo si existe"""
        if obj.price_llevo:
            return int(obj.price_llevo)
        
        # Fallback: convertir USD a LLEVO (redondeo estándar)
        current_rate = LlevoRate.get_current_rate()
        if current_rate and obj.price:
            # USD a LLEVO: USD ÷ (LLEVO_VES_VALUE ÷ USDT_VES_RATE)
            conversion_factor = current_rate.llevo_value / current_rate.usdt_ves_rate
            return round(obj.price / conversion_factor)
        return int(obj.price) if obj.price else 0
    
    def get_price_ves(self, obj):
        """Convertir LLEVO a VES para referencia"""
        price_llevo = self.get_price_llevo(obj)
        current_rate = LlevoRate.get_current_rate()
        if current_rate and price_llevo:
            return float(price_llevo * current_rate.llevo_value)
        return 0.0

class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    price_llevo = serializers.SerializerMethodField()
    price_ves = serializers.SerializerMethodField()

    # Detalles completos del financiamiento
    financing_details = serializers.SerializerMethodField()

    # Override JSON fields to ensure consistent string output
    features = serializers.SerializerMethodField()
    specs_general = serializers.SerializerMethodField()
    specs_engine = serializers.SerializerMethodField()
    specs_comfort = serializers.SerializerMethodField()
    specs_safety = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'brand',
            'price', 'price_llevo', 'price_ves',
            'inicial_llevos', 'cuota_mensual_llevos',
            'financing_details',
            'image', 'description', 'features',
            'specs_general', 'specs_engine', 'specs_comfort', 'specs_safety',
            'stock', 'featured'
        ]
    
    def get_features(self, obj):
        """Ensure features is always returned as JSON string for consistent frontend parsing"""
        if obj.features is None:
            return "[]"
        if isinstance(obj.features, str):
            return obj.features
        return json.dumps(obj.features)
    
    def get_specs_general(self, obj):
        """Ensure specs_general is always returned as JSON string for consistent frontend parsing"""
        if obj.specs_general is None:
            return "[]"
        if isinstance(obj.specs_general, str):
            return obj.specs_general
        return json.dumps(obj.specs_general)
    
    def get_specs_engine(self, obj):
        """Ensure specs_engine is always returned as JSON string for consistent frontend parsing"""
        if obj.specs_engine is None:
            return "[]"
        if isinstance(obj.specs_engine, str):
            return obj.specs_engine
        return json.dumps(obj.specs_engine)
    
    def get_specs_comfort(self, obj):
        """Ensure specs_comfort is always returned as JSON string for consistent frontend parsing"""
        if obj.specs_comfort is None:
            return "[]"
        if isinstance(obj.specs_comfort, str):
            return obj.specs_comfort
        return json.dumps(obj.specs_comfort)
    
    def get_specs_safety(self, obj):
        """Ensure specs_safety is always returned as JSON string for consistent frontend parsing"""
        if obj.specs_safety is None:
            return "[]"
        if isinstance(obj.specs_safety, str):
            return obj.specs_safety
        return json.dumps(obj.specs_safety)

    def get_price_llevo(self, obj):
        """Convertir precio USD a LLEVO o usar price_llevo si existe"""
        if obj.price_llevo:
            return int(obj.price_llevo)

        # Fallback: convertir USD a LLEVO (redondeo estándar)
        current_rate = LlevoRate.get_current_rate()
        if current_rate and obj.price:
            # USD a LLEVO: USD ÷ (LLEVO_VES_VALUE ÷ USDT_VES_RATE)
            conversion_factor = current_rate.llevo_value / current_rate.usdt_ves_rate
            return round(obj.price / conversion_factor)
        return int(obj.price) if obj.price else 0

    def get_price_ves(self, obj):
        """Convertir LLEVO a VES para referencia"""
        price_llevo = self.get_price_llevo(obj)
        current_rate = LlevoRate.get_current_rate()
        if current_rate and price_llevo:
            return float(price_llevo * current_rate.llevo_value)
        return 0.0

    def get_financing_details(self, obj):
        """Retorna detalles completos del financiamiento"""
        return obj.get_financing_details()
