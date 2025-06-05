from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('featured-products/', views.FeaturedProductsView.as_view()),
    path('products-by-category/<slug:category_slug>/', views.ProductsByCategoryView.as_view()),
] 