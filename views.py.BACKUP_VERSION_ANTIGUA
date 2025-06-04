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
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
import logging

# Configuración de logging
logger = logging.getLogger(__name__)

# Vista personalizada para tokens JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Create your views here.

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        return Response({"success": "CSRF cookie set"})

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def post(self, request, *args, **kwargs):
        logger.info(f"Datos de registro recibidos: {request.data}")
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error en registro: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class PublicRegisterView(APIView):
    """
    Vista alternativa para registro público sin restricciones CSRF
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        logger.info(f"Datos de registro público recibidos: {request.data}")
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"Usuario creado con éxito: {user.id} - {user.username}")
            return Response({
                "success": True,
                "message": "Usuario creado exitosamente",
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
