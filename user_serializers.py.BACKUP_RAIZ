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
    is_profile_complete = serializers.BooleanField(default=False, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone', 'identity_document', 'is_profile_complete']
    
    def validate(self, data):
        print("RegisterSerializer.validate() - Datos recibidos:", {**data, 'password': '********', 'password2': '********'})
        
        # Validar que las contraseñas coincidan
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
            
        # Validar que el email no esté ya registrado
        email = data.get('email')
        if not email:
            raise serializers.ValidationError({"email": "El correo electrónico es obligatorio"})
            
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Este correo electrónico ya está registrado"})
        
        # Asegurar que el username sea el mismo que el email
        data['username'] = email
        
        # Validar que el documento de identidad no esté ya registrado
        identity_document = data.get('identity_document')
        if identity_document and Customer.objects.filter(identity_document=identity_document).exists():
            raise serializers.ValidationError({"identity_document": "Este documento de identidad ya está registrado"})
            
        return data
    
    def create(self, validated_data):
        print("RegisterSerializer.create() - Datos validados:", {**validated_data, 'password': '********'})
        
        phone = validated_data.pop('phone')
        identity_document = validated_data.pop('identity_document')
        validated_data.pop('password2')
        is_profile_complete = validated_data.pop('is_profile_complete', False)
        
        # Asegurar que el email y username sean iguales (para logins consistentes)
        validated_data['username'] = validated_data['email']
        
        # Crear el usuario
        user = User.objects.create_user(**validated_data)
        print(f"Usuario creado: ID={user.id}, username={user.username}, email={user.email}")
        
        # Crear un perfil básico de cliente
        customer = Customer.objects.create(
            user=user,
            phone=phone,
            identity_document=identity_document,
            is_profile_complete=is_profile_complete
        )
        print(f"Cliente creado: ID={customer.id}, usuario_id={user.id}")
        
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
