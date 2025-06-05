from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # CSRF Token
    path('csrf-token/', views.GetCSRFToken.as_view(), name='csrf-token'),
    
    # Autenticación
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('public-register/', views.PublicRegisterView.as_view(), name='public-register'),
    
    # Recuperación de contraseña
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Perfil de usuario
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Solicitudes
    path('applications/', views.ApplicationListView.as_view(), name='application-list'),
    path('applications/create/', views.ApplicationCreateView.as_view(), name='application-create'),
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application-detail'),
] 