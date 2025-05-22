from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import Customer, Application
from products.serializers.product_serializers import ProductDetailSerializer
from financing.serializers.financing_serializers import FinancingPlanSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para obtener tokens JWT que permite iniciar sesión
    tanto con username como con email.
    """
    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        
        # Verificar si el username es un email
        if '@' in username:
            # Intentar obtener el usuario por email
            try:
                user = User.objects.get(email=username)
                # Reemplazar el username con el username real del usuario
                attrs['username'] = user.username
            except User.DoesNotExist:
                pass
        
        # Continuar con la validación normal
        return super().validate(attrs)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'user', 'phone', 'address', 'identity_document', 
                 'date_of_birth', 'occupation', 'monthly_income', 'verified']
        read_only_fields = ['id', 'verified']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    phone = serializers.CharField(required=True)
    identity_document = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone', 'identity_document']
    
    def validate(self, data):
        # Validar que las contraseñas coincidan
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        
        # Validar que el email no esté ya registrado
        email = data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Este correo electrónico ya está registrado"})
        
        # Validar que el nombre de usuario no esté ya registrado
        username = data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Este nombre de usuario ya está registrado"})
            
        # Validar que el documento de identidad no esté ya registrado
        identity_document = data.get('identity_document')
        if identity_document and Customer.objects.filter(identity_document=identity_document).exists():
            raise serializers.ValidationError({"identity_document": "Este documento de identidad ya está registrado"})
            
        # Asegurar que el username sea igual al email si no se proporciona explícitamente
        # Esto es importante para el flujo de login que usa el email como username
        if not username and email:
            data['username'] = email
            
        return data
    
    def create(self, validated_data):
        phone = validated_data.pop('phone')
        identity_document = validated_data.pop('identity_document')
        validated_data.pop('password2')
        
        # Asegurar que el email y username sean iguales (para logins consistentes)
        if 'email' in validated_data and 'username' in validated_data:
            validated_data['username'] = validated_data['email']
        
        user = User.objects.create_user(**validated_data)
        
        Customer.objects.create(
            user=user,
            phone=phone,
            identity_document=identity_document
        )
        
        return user

class ApplicationSerializer(serializers.ModelSerializer):
    customer_details = CustomerSerializer(source='customer', read_only=True)
    product_details = ProductDetailSerializer(source='product', read_only=True)
    financing_plan_details = FinancingPlanSerializer(source='financing_plan', read_only=True)
    
    class Meta:
        model = Application
        fields = ['id', 'customer', 'customer_details', 'product', 'product_details', 
                 'financing_plan', 'financing_plan_details', 'status', 'initial_amount', 
                 'monthly_payment', 'term', 'notes', 'application_date', 'approved_date']
        read_only_fields = ['id', 'application_date', 'approved_date']

class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['product', 'financing_plan', 'initial_amount', 'monthly_payment', 'term', 'notes']
    
    def create(self, validated_data):
        # Obtener el cliente a partir del usuario autenticado
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                customer = Customer.objects.get(user=request.user)
                validated_data['customer'] = customer
                return super().create(validated_data)
            except Customer.DoesNotExist:
                raise serializers.ValidationError({"customer": "Debes completar tu perfil de cliente primero"})
        raise serializers.ValidationError({"authorization": "Debes iniciar sesión para enviar una solicitud"})
