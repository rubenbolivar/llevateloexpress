from rest_framework import serializers
from products.models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon']

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'category_name', 'brand', 'price', 'image', 'featured']

class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'category_name', 'brand', 'price', 
                 'image', 'description', 'features', 'specs_general', 'specs_engine', 
                 'specs_comfort', 'specs_safety', 'stock', 'featured']
