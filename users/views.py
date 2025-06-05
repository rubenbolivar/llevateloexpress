from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .models import Customer, Application, PasswordResetToken
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
from notifications.services import send_welcome_email, send_registration_confirmation, send_password_reset_email, send_password_changed_email
from django.contrib.auth import authenticate
from django.conf import settings
import logging
import uuid
import json

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

@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetRequestView(APIView):
    """
    Vista para solicitar recuperación de contraseña
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Parsear datos JSON del request
            if hasattr(request, 'data'):
                # Si es una request de DRF
                email = request.data.get('email')
            else:
                # Si es una request estándar de Django
                data = json.loads(request.body.decode('utf-8'))
                email = data.get('email')
        except (json.JSONDecodeError, UnicodeDecodeError):
            return Response({
                'success': False,
                'message': 'Datos JSON inválidos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Invalidar tokens anteriores del usuario
            PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Crear nuevo token
            reset_token = PasswordResetToken.objects.create(user=user)
            logger.info(f"Token de reset generado para {email}: {reset_token.token}")
            
            # Enviar notificación usando la función que sigue el patrón que funciona
            try:
                success = send_password_reset_email(user, str(reset_token.token))
                if success:
                    logger.info(f"Email de reset enviado exitosamente a {email}")
                else:
                    logger.warning(f"No se pudo enviar email de reset a {email} pero token creado")
            except Exception as email_error:
                logger.warning(f"Error enviando email de reset a {email}: {str(email_error)} - Token creado exitosamente")
                # No fallar la solicitud si hay error en emails
            
            # SIEMPRE devolver éxito por seguridad (aunque el email falle)
            return Response({
                'success': True,
                'message': 'Se ha enviado un enlace de recuperación a tu email'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Por seguridad, devolvemos el mismo mensaje aunque el usuario no exista
            logger.info(f"Intento de reset para email inexistente: {email}")
            return Response({
                'success': True,
                'message': 'Se ha enviado un enlace de recuperación a tu email'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error crítico en reset de contraseña: {str(e)}")
            return Response({
                'success': False,
                'message': 'Error interno. Intenta nuevamente más tarde.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetConfirmView(APIView):
    """
    Vista para confirmar el reset de contraseña con el token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Parsear datos JSON del request
            if hasattr(request, 'data'):
                # Si es una request de DRF
                token = request.data.get('token')
                new_password = request.data.get('new_password')
                confirm_password = request.data.get('confirm_password')
            else:
                # Si es una request estándar de Django
                data = json.loads(request.body.decode('utf-8'))
                token = data.get('token')
                new_password = data.get('new_password')
                confirm_password = data.get('confirm_password')
        except (json.JSONDecodeError, UnicodeDecodeError):
            return Response({
                'success': False,
                'message': 'Datos JSON inválidos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not all([token, new_password, confirm_password]):
            return Response({
                'success': False,
                'message': 'Token y contraseñas son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({
                'success': False,
                'message': 'Las contraseñas no coinciden'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 8:
            return Response({
                'success': False,
                'message': 'La contraseña debe tener al menos 8 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            
            if not reset_token.is_valid():
                return Response({
                    'success': False,
                    'message': 'Token inválido o expirado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Cambiar contraseña
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            # Marcar token como usado
            reset_token.mark_as_used()
            
            # Enviar notificación de confirmación
            send_password_changed_email(user)
            
            logger.info(f"Contraseña cambiada exitosamente para {user.email}")
            
            return Response({
                'success': True,
                'message': 'Contraseña cambiada exitosamente'
            }, status=status.HTTP_200_OK)
            
        except PasswordResetToken.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Token inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Error confirmando reset: {str(e)}")
            return Response({
                'success': False,
                'message': 'Error interno. Intenta nuevamente más tarde.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
