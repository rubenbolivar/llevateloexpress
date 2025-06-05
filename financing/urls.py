from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'plans', views.FinancingPlanViewSet, basename='financing-plan')
router.register(r'requests', views.FinancingRequestViewSet, basename='financing-request')
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
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
    
    # Sistema de pagos manuales con comprobantes
    path('payment-methods/', views.PaymentMethodListView.as_view(), name='payment-methods'),
    path('submit-payment/', views.PaymentSubmissionView.as_view(), name='submit-payment'),
    path('my-payments/', views.UserPaymentsView.as_view(), name='user-payments'),
    
    # Sistema de pagos manuales con comprobantes
    path('payment-methods/', views.PaymentMethodListView.as_view(), name='payment-methods'),
    path('submit-payment/', views.PaymentSubmissionView.as_view(), name='submit-payment'),
    path('my-payments/', views.UserPaymentsView.as_view(), name='user-payments'),
    path('payment-status/<int:payment_id>/', views.PaymentStatusView.as_view(), name='payment-status'),
    path('upload-attachment/<int:payment_id>/', views.upload_additional_attachment, name='upload-attachment'),
]