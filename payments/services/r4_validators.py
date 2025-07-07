"""
Validadores para campos R4 Conecta según documentación oficial
"""
import re
from typing import Optional, Dict, Any

class R4FieldValidator:
    """
    Validador de campos según especificaciones oficiales R4 Conecta
    """
    
    @staticmethod
    def validate_referencia(referencia: str) -> Dict[str, Any]:
        """
        Valida referencia de pago móvil
        Formato oficial: 8-9 numérico
        """
        if not referencia:
            return {'valid': False, 'error': 'Referencia es requerida'}
        
        if not isinstance(referencia, str):
            referencia = str(referencia)
        
        # Remover espacios
        referencia = referencia.strip()
        
        # Validar que sea numérico
        if not referencia.isdigit():
            return {'valid': False, 'error': 'Referencia debe ser numérico'}
        
        # Validar longitud
        if len(referencia) < 8 or len(referencia) > 9:
            return {'valid': False, 'error': 'Referencia debe tener 8-9 dígitos'}
        
        return {'valid': True, 'value': referencia}
    
    @staticmethod
    def validate_telefono(telefono: str) -> Dict[str, Any]:
        """
        Valida número de teléfono venezolano
        Formato oficial: 11 numérico (584XXXXXXXXX)
        """
        if not telefono:
            return {'valid': False, 'error': 'Teléfono es requerido'}
        
        if not isinstance(telefono, str):
            telefono = str(telefono)
        
        # Remover espacios y guiones
        telefono = re.sub(r'[\s\-]', '', telefono)
        
        # Validar que sea numérico
        if not telefono.isdigit():
            return {'valid': False, 'error': 'Teléfono debe ser numérico'}
        
        # Validar longitud
        if len(telefono) != 11:
            return {'valid': False, 'error': 'Teléfono debe tener 11 dígitos'}
        
        # Validar formato venezolano (58XXXXXXXXX)
        if not telefono.startswith('58'):
            return {'valid': False, 'error': 'Teléfono debe comenzar con 58 (Venezuela)'}
        
        # Validar código de operadora (4to dígito)
        operadora = telefono[2]
        if operadora not in ['4', '2', '1']:  # 04XX, 02XX, 01XX
            return {'valid': False, 'error': 'Código de operadora inválido'}
        
        return {'valid': True, 'value': telefono}
    
    @staticmethod
    def validate_cedula(cedula: str) -> Dict[str, Any]:
        """
        Valida cédula venezolana
        Formato oficial: 9 alfanumérico (V/E + 8 dígitos)
        """
        if not cedula:
            return {'valid': False, 'error': 'Cédula es requerida'}
        
        if not isinstance(cedula, str):
            cedula = str(cedula)
        
        # Remover espacios
        cedula = cedula.strip().upper()
        
        # Validar longitud
        if len(cedula) != 9:
            return {'valid': False, 'error': 'Cédula debe tener 9 caracteres'}
        
        # Validar formato (V/E + 8 dígitos)
        if not re.match(r'^[VE]\d{8}$', cedula):
            return {'valid': False, 'error': 'Cédula debe tener formato V12345678 o E12345678'}
        
        return {'valid': True, 'value': cedula}
    
    @staticmethod
    def validate_monto(monto: str) -> Dict[str, Any]:
        """
        Valida monto de transacción
        Formato oficial: máximo 8 números + 2 decimales
        """
        if not monto:
            return {'valid': False, 'error': 'Monto es requerido'}
        
        if not isinstance(monto, str):
            monto = str(monto)
        
        # Remover espacios
        monto = monto.strip()
        
        try:
            monto_float = float(monto)
        except ValueError:
            return {'valid': False, 'error': 'Monto debe ser un número válido'}
        
        # Validar que sea positivo
        if monto_float <= 0:
            return {'valid': False, 'error': 'Monto debe ser mayor a 0'}
        
        # Validar formato decimal
        if '.' in monto:
            partes = monto.split('.')
            if len(partes[1]) > 2:
                return {'valid': False, 'error': 'Monto debe tener máximo 2 decimales'}
            
            # Validar longitud total (máximo 8 dígitos antes del punto)
            if len(partes[0]) > 8:
                return {'valid': False, 'error': 'Monto debe tener máximo 8 dígitos enteros'}
        else:
            # Sin decimales, validar longitud
            if len(monto) > 8:
                return {'valid': False, 'error': 'Monto debe tener máximo 8 dígitos'}
        
        # Validar rango (máximo 99,999,999.99)
        if monto_float > 99999999.99:
            return {'valid': False, 'error': 'Monto excede el límite máximo'}
        
        return {'valid': True, 'value': f"{monto_float:.2f}"}
    
    @staticmethod
    def validate_banco(banco: str) -> Dict[str, Any]:
        """
        Valida código de banco
        Formato oficial: 3-4 numérico
        """
        if not banco:
            return {'valid': False, 'error': 'Código de banco es requerido'}
        
        if not isinstance(banco, str):
            banco = str(banco)
        
        # Remover espacios
        banco = banco.strip()
        
        # Validar que sea numérico
        if not banco.isdigit():
            return {'valid': False, 'error': 'Código de banco debe ser numérico'}
        
        # Validar longitud
        if len(banco) < 3 or len(banco) > 4:
            return {'valid': False, 'error': 'Código de banco debe tener 3-4 dígitos'}
        
        # Formatear a 4 dígitos si es necesario
        banco_formatted = banco.zfill(4)
        
        return {'valid': True, 'value': banco_formatted}
    
    @staticmethod
    def validate_otp(otp: str) -> Dict[str, Any]:
        """
        Valida código OTP
        Formato oficial: 8 numérico
        """
        if not otp:
            return {'valid': False, 'error': 'OTP es requerido'}
        
        if not isinstance(otp, str):
            otp = str(otp)
        
        # Remover espacios
        otp = otp.strip()
        
        # Validar que sea numérico
        if not otp.isdigit():
            return {'valid': False, 'error': 'OTP debe ser numérico'}
        
        # Validar longitud
        if len(otp) != 8:
            return {'valid': False, 'error': 'OTP debe tener 8 dígitos'}
        
        return {'valid': True, 'value': otp}
    
    @staticmethod
    def validate_concepto(concepto: Optional[str]) -> Dict[str, Any]:
        """
        Valida concepto de pago (opcional)
        Formato oficial: 30 alfanumérico
        """
        if not concepto:
            return {'valid': True, 'value': ''}
        
        if not isinstance(concepto, str):
            concepto = str(concepto)
        
        # Remover espacios extras
        concepto = concepto.strip()
        
        # Validar longitud
        if len(concepto) > 30:
            return {'valid': False, 'error': 'Concepto debe tener máximo 30 caracteres'}
        
        # Validar caracteres alfanuméricos y espacios
        if not re.match(r'^[a-zA-Z0-9\s]*$', concepto):
            return {'valid': False, 'error': 'Concepto debe contener solo letras, números y espacios'}
        
        return {'valid': True, 'value': concepto}
    
    @staticmethod
    def validate_ip(ip: Optional[str]) -> Dict[str, Any]:
        """
        Valida dirección IP (opcional)
        """
        if not ip:
            return {'valid': True, 'value': None}
        
        if not isinstance(ip, str):
            ip = str(ip)
        
        # Remover espacios
        ip = ip.strip()
        
        # Validar formato IP
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return {'valid': False, 'error': 'IP debe tener formato válido (x.x.x.x)'}
        
        # Validar rangos
        parts = ip.split('.')
        for part in parts:
            if int(part) > 255:
                return {'valid': False, 'error': 'IP contiene octetos inválidos'}
        
        return {'valid': True, 'value': ip}

class R4RequestValidator:
    """
    Validador completo de requests R4
    """
    
    @staticmethod
    def validate_consulta_pm_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida request completo para MBconsulta_pm
        """
        errors = []
        validated_data = {}
        
        # Validar referencia
        ref_result = R4FieldValidator.validate_referencia(data.get('referencia', ''))
        if not ref_result['valid']:
            errors.append(f"Referencia: {ref_result['error']}")
        else:
            validated_data['referencia'] = ref_result['value']
        
        # Validar teléfono
        tel_result = R4FieldValidator.validate_telefono(data.get('telefono_origen', ''))
        if not tel_result['valid']:
            errors.append(f"Teléfono: {tel_result['error']}")
        else:
            validated_data['telefono_origen'] = tel_result['value']
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'data': validated_data if len(errors) == 0 else None
        }
    
    @staticmethod
    def validate_c2p_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida request completo para MBc2p
        """
        errors = []
        validated_data = {}
        
        # Validar teléfono destino
        tel_result = R4FieldValidator.validate_telefono(data.get('TelefonoDestino', ''))
        if not tel_result['valid']:
            errors.append(f"TelefonoDestino: {tel_result['error']}")
        else:
            validated_data['TelefonoDestino'] = tel_result['value']
        
        # Validar cédula
        ced_result = R4FieldValidator.validate_cedula(data.get('Cedula', ''))
        if not ced_result['valid']:
            errors.append(f"Cedula: {ced_result['error']}")
        else:
            validated_data['Cedula'] = ced_result['value']
        
        # Validar banco
        banco_result = R4FieldValidator.validate_banco(data.get('Banco', ''))
        if not banco_result['valid']:
            errors.append(f"Banco: {banco_result['error']}")
        else:
            validated_data['Banco'] = banco_result['value']
        
        # Validar monto
        monto_result = R4FieldValidator.validate_monto(data.get('Monto', ''))
        if not monto_result['valid']:
            errors.append(f"Monto: {monto_result['error']}")
        else:
            validated_data['Monto'] = monto_result['value']
        
        # Validar OTP
        otp_result = R4FieldValidator.validate_otp(data.get('Otp', ''))
        if not otp_result['valid']:
            errors.append(f"Otp: {otp_result['error']}")
        else:
            validated_data['Otp'] = otp_result['value']
        
        # Validar concepto (opcional)
        concepto_result = R4FieldValidator.validate_concepto(data.get('Concepto'))
        if not concepto_result['valid']:
            errors.append(f"Concepto: {concepto_result['error']}")
        else:
            validated_data['Concepto'] = concepto_result['value']
        
        # Validar IP (opcional)
        ip_result = R4FieldValidator.validate_ip(data.get('Ip'))
        if not ip_result['valid']:
            errors.append(f"Ip: {ip_result['error']}")
        else:
            if ip_result['value']:
                validated_data['Ip'] = ip_result['value']
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'data': validated_data if len(errors) == 0 else None
        }