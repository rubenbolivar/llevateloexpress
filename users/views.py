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

# Vista personalizada para tokens JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

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
