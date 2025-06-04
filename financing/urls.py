from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import debug_financing_request

router = DefaultRouter()
router.register(r'plans', views.FinancingPlanViewSet, basename='financing-plan')
router.register(r'requests', views.FinancingRequestViewSet, basename='financing-request')
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path("debug-request/", debug_financing_request, name="debug-financing-request"),
    path('', include(router.urls)),
    
    # Calculadora de financiamiento
    path('calculate/', views.FinancingCalculatorView.as_view(), name='financing-calculate'),
    
    # Vistas adicionales para clientes
    path('my-requests/', views.CustomerApplicationsView.as_view(), name='customer-requests'),
    path('payment-schedule/', views.PaymentScheduleListView.as_view(), name='payment-schedule-list'),
    
    # Simulador configurado
    path('simulator/config/', views.SimulatorConfigurationView.as_view(), name='simulator-config'),
    path('simulator/calculate/', views.SimulatorCalculateView.as_view(), name='simulator-calculate'),
    
    # Calculadora integrada (nueva)
    path('calculator/config/', views.CalculatorConfigurationView.as_view(), name='calculator-config'),
    path('calculator/calculate/', views.CalculatorCalculateView.as_view(), name='calculator-calculate'),
] 