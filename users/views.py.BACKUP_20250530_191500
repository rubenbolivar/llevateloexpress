from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .models import Customer, Application
from .serializers.user_serializers import (
    UserSerializer,
    CustomerSerializer,
    RegisterSerializer,
    ApplicationSerializer,
    ApplicationCreateSerializer,
    CustomTokenObtainPairSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from notifications.services import send_welcome_email, send_registration_confirmation
import logging

# Configuración de logging
logger = logging.getLogger(__name__)

# Vista personalizada para tokens JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Create your views here.

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    """
    Vista para establecer una cookie CSRF cuando se carga la página.
    Esto debe ser llamado antes de realizar cualquier solicitud POST.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        return Response({"success": "CSRF cookie set"})

class RegisterView(generics.CreateAPIView):
    """
    Vista estándar para registrar usuarios a través de la API.
    Utiliza protección CSRF estándar.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def post(self, request, *args, **kwargs):
        logger.info(f"Datos de registro recibidos: {request.data}")
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                logger.info(f"Usuario creado: {user.id} - {user.username}")
                
                # Enviar notificaciones de bienvenida y confirmación
                try:
                    send_welcome_email(user)
                    send_registration_confirmation(user)
                    logger.info(f"Emails de bienvenida enviados a {user.email}")
                except Exception as email_error:
                    logger.warning(f"Error enviando emails de bienvenida a {user.email}: {str(email_error)}")
                    # No fallar el registro si hay error en emails
                
                return Response({
                    "success": True,
                    "message": "Usuario creado exitosamente. Se ha enviado un email de confirmación.",
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email
                }, status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Error de validación: {serializer.errors}")
                return Response({
                    "success": False,
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error en registro: {str(e)}")
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

# Las vistas con @csrf_exempt solo deben usarse en casos específicos donde se requiere 
# y luego de un análisis detallado de seguridad
@method_decorator(csrf_exempt, name='dispatch')
class PublicRegisterView(APIView):
    """
    Vista alternativa exenta de CSRF para casos donde la protección CSRF
    no se puede implementar correctamente.
    Solo debe usarse en situaciones específicas y controladas.
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        logger.info(f"Datos de registro público recibidos: {request.data}")
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"Usuario creado con éxito: {user.id} - {user.username}")
            
            # Enviar notificaciones de bienvenida y confirmación
            try:
                send_welcome_email(user)
                send_registration_confirmation(user)
                logger.info(f"Emails de bienvenida enviados a {user.email}")
            except Exception as email_error:
                logger.warning(f"Error enviando emails de bienvenida a {user.email}: {str(email_error)}")
                # No fallar el registro si hay error en emails
            
            return Response({
                "success": True,
                "message": "Usuario creado exitosamente. Se ha enviado un email de confirmación.",
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Error de validación en registro público: {serializer.errors}")
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer
    
    def get_object(self):
        try:
            return Customer.objects.get(user=self.request.user)
        except Customer.DoesNotExist:
            # Si no existe el perfil, crearlo
            return Customer.objects.create(user=self.request.user)

class ApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            customer = Customer.objects.get(user=self.request.user)
            return Application.objects.filter(customer=customer)
        except Customer.DoesNotExist:
            return Application.objects.none()

class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        
        # Retornar la solicitud creada con todos los detalles
        response_serializer = ApplicationSerializer(application)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class ApplicationDetailView(generics.RetrieveAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            customer = Customer.objects.get(user=self.request.user)
            return Application.objects.filter(customer=customer)
        except Customer.DoesNotExist:
            return Application.objects.none()
