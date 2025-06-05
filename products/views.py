from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.response import Response
from .models import Category, Product
from .serializers.product_serializers import CategorySerializer, ProductListSerializer, ProductDetailSerializer

# Create your views here.

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

class FeaturedProductsView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    
    def get_queryset(self):
        return Product.objects.filter(featured=True)

class ProductsByCategoryView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    
    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        return Product.objects.filter(category__slug=category_slug)
