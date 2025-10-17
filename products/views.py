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
    # Solo mostrar productos que NO estén marcados como sin stock
    queryset = Product.objects.filter(out_of_stock=False)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

class FeaturedProductsView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    
    def get_queryset(self):
        # Solo productos destacados que NO estén marcados como sin stock
        return Product.objects.filter(featured=True, out_of_stock=False)

class ProductsByCategoryView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    
    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        # Solo productos de la categoría que NO estén marcados como sin stock
        return Product.objects.filter(category__slug=category_slug, out_of_stock=False)

class CalculadoraProductsView(generics.ListAPIView):
    """
    Vista específica para la calculadora CrediLlevo
    Devuelve solo productos que tienen precio_llevo e inicial_llevos configurados
    y que NO estén marcados como sin stock
    SIN PAGINACIÓN para garantizar que todos los productos estén disponibles
    """
    serializer_class = ProductListSerializer
    pagination_class = None  # Deshabilitar paginación para calculadora

    def get_queryset(self):
        return Product.objects.filter(
            price_llevo__isnull=False,
            price_llevo__gt=0,
            inicial_llevos__isnull=False,
            inicial_llevos__gt=0,
            out_of_stock=False  # Agregar filtro para excluir productos sin stock
        ).order_by('category__name', 'brand', 'name')
