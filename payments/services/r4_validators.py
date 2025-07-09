import re
from django.core.exceptions import ValidationError

def validate_referencia_r4(referencia):
    """Valida que la referencia tenga el formato correcto para R4"""
    if not referencia:
        raise ValidationError("La referencia es requerida")
    
    # Referencia debe ser numérica de 8-9 dígitos
    if not re.match(r"^[0-9]{8,9}$", str(referencia)):
        raise ValidationError("La referencia debe ser numérica de 8-9 dígitos")
    
    return str(referencia)

def validate_telefono_venezuela(telefono):
    """Valida formato de teléfono venezolano"""
    if not telefono:
        raise ValidationError("El teléfono es requerido")
    
    # Remover espacios y caracteres especiales
    telefono_limpio = re.sub(r"[^0-9]", "", str(telefono))
    
    # Debe tener 11 dígitos y empezar con 04
    if not re.match(r"^04[0-9]{9}$", telefono_limpio):
        raise ValidationError("El teléfono debe tener formato venezolano 04XXXXXXXXX")
    
    return telefono_limpio

def validate_cedula_venezuela(cedula):
    """Valida formato de cédula venezolana"""
    if not cedula:
        raise ValidationError("La cédula es requerida")
    
    cedula_str = str(cedula).upper().strip()
    
    # Formato: V12345678 o E12345678
    if not re.match(r"^[VE][0-9]{6,9}$", cedula_str):
        raise ValidationError("La cédula debe tener formato venezolano (V/E + 6-9 dígitos)")
    
    return cedula_str

def validate_monto_r4(monto):
    """Valida que el monto sea válido para R4"""
    try:
        monto_float = float(monto)
        if monto_float <= 0:
            raise ValidationError("El monto debe ser mayor a 0")
        if monto_float > 999999.99:
            raise ValidationError("El monto excede el límite máximo")
        return round(monto_float, 2)
    except (ValueError, TypeError):
        raise ValidationError("El monto debe ser un número válido")

def validate_banco_r4(codigo_banco):
    """Valida código de banco venezolano"""
    bancos_validos = [
        "0001", "0102", "0104", "0105", "0108", "0114", "0115", "0128", 
        "0134", "0137", "0138", "0151", "0156", "0157", "0163", "0166", 
        "0168", "0169", "0171", "0172", "0174", "0175", "0177", "0191"
    ]
    
    if str(codigo_banco) not in bancos_validos:
        raise ValidationError(f"Código de banco no válido: {codigo_banco}")
    
    return str(codigo_banco)

def validate_otp_r4(otp):
    """Valida formato de OTP para R4"""
    if not otp:
        raise ValidationError("El OTP es requerido")
    
    # OTP debe ser numérico de 4-6 dígitos
    if not re.match(r"^[0-9]{4,6}$", str(otp)):
        raise ValidationError("El OTP debe ser numérico de 4-6 dígitos")
    
    return str(otp)

class R4FieldValidator:
    """Validador de campos individuales según documentación R4"""
    
    @staticmethod
    def validate_referencia(referencia):
        return validate_referencia_r4(referencia)
    
    @staticmethod
    def validate_telefono(telefono):
        return validate_telefono_venezuela(telefono)
    
    @staticmethod
    def validate_cedula(cedula):
        return validate_cedula_venezuela(cedula)
    
    @staticmethod
    def validate_monto(monto):
        return validate_monto_r4(monto)
    
    @staticmethod
    def validate_banco(banco):
        return validate_banco_r4(banco)
    
    @staticmethod
    def validate_otp(otp):
        return validate_otp_r4(otp)

class R4RequestValidator:
    """Validador de requests completos según documentación oficial R4"""
    
    def __init__(self):
        self.field_validator = R4FieldValidator()
    
    def validate_consulta_pm_request(self, data):
        """Valida request MBconsulta_pm según doc oficial"""
        required_fields = ["telefono", "cedula", "referencia", "banco", "monto"]
        errors = []
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Campo requerido faltante: {field}")
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        # Validar cada campo individualmente
        try:
            self.field_validator.validate_telefono(data["telefono"])
            self.field_validator.validate_cedula(data["cedula"])
            self.field_validator.validate_referencia(data["referencia"])
            self.field_validator.validate_banco(data["banco"])
            self.field_validator.validate_monto(data["monto"])
        except ValidationError as e:
            raise ValidationError(f"Error de validación: {str(e)}")
        
        return True
    
    def validate_c2p_request(self, data):
        """Valida request MBc2p según documentación oficial"""
        required_fields = ["telefono", "cedula", "referencia", "banco", "monto", "otp"]
        errors = []
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Campo requerido faltante: {field}")
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        # Validar campos según documentación R4
        try:
            self.field_validator.validate_telefono(data["telefono"])
            self.field_validator.validate_cedula(data["cedula"])
            self.field_validator.validate_referencia(data["referencia"])
            self.field_validator.validate_banco(data["banco"])
            self.field_validator.validate_monto(data["monto"])
            self.field_validator.validate_otp(data["otp"])
        except ValidationError as e:
            raise ValidationError(f"Error de validación: {str(e)}")
        
        return True
    
    def validate_webhook_notification(self, data):
        """Valida webhook MBnotifica según documentación oficial"""
        required_fields = [
            "IdComercio", "TelefonoComercio", "TelefonoEmisor", 
            "BancoEmisor", "Monto", "FechaHora", "Referencia", "CodigoRed"
        ]
        
        errors = []
        for field in required_fields:
            if field not in data:
                errors.append(f"Campo requerido faltante: {field}")
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        return True

class R4FieldValidator:
    """Validador de campos individuales según documentación oficial R4 V2.0"""
    
    @staticmethod
    def validate_referencia(referencia):
        return validate_referencia_r4(referencia)
    
    @staticmethod
    def validate_telefono(telefono):
        return validate_telefono_venezuela(telefono)
    
    @staticmethod
    def validate_cedula(cedula):
        return validate_cedula_venezuela(cedula)
    
    @staticmethod
    def validate_monto(monto):
        return validate_monto_r4(monto)
    
    @staticmethod
    def validate_banco(banco):
        return validate_banco_r4(banco)
    
    @staticmethod
    def validate_otp(otp):
        return validate_otp_r4(otp)

class R4RequestValidator:
    """Validador de requests completos según documentación oficial R4 V2.0"""
    
    def __init__(self):
        self.field_validator = R4FieldValidator()
    
    def validate_mbnotifica_request(self, data):
        """Valida webhook MBnotifica según documentación oficial R4 V2.0 página 18"""
        # Campos requeridos según doc oficial: página 18
        required_fields = [
            "IdComercio",           # Cédula o RIF del Comercio (requerido) - String - 8 numérico
            "TelefonoComercio",     # Teléfono del comercio (requerido) - String - 11 numérico  
            "TelefonoEmisor",       # Teléfono de origen del pago (requerido) - String - 11 numérico
            "BancoEmisor",          # Código del banco del pago (requerido) - String - 3 numérico
            "Monto",                # Monto con decimales separados por punto (requerido) - String
            "FechaHora",            # (requerido) - String
            "Referencia",           # Referencia interbancaria (requerido) - String
            "CodigoRed"             # Código de respuesta de la red interbancaria (requerido) - String
        ]
        
        # Campos opcionales según doc oficial
        optional_fields = ["Concepto"]  # Motivo del pago (opcional) String - 30 alfanumérico
        
        errors = []
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Campo requerido faltante: {field}")
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        return True
    
    def validate_mbconsulta_request(self, data):
        """Valida request MBconsulta según documentación oficial R4 V2.0 página 16"""
        # Campos requeridos según doc oficial
        required_fields = [
            "IdCliente",            # Identificación del cliente (requerido) - String - 8 numérico
            "Monto",                # Monto de la operación - String - máximo 8 números y 2 decimales
            "TelefonoComercio"      # Teléfono del comercio - String - 11 numérico
        ]
        
        errors = []
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Campo requerido faltante: {field}")
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        return True
