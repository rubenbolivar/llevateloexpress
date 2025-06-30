import hmac
import hashlib
from django.conf import settings

def generate_hmac_signature(data_string, secret_key):
    """
    Genera firma HMAC-SHA256 para autenticación R4 Conecta
    """
    try:
        # Convertir a bytes si es necesario
        if isinstance(data_string, str):
            data_string = data_string.encode('utf-8')
        if isinstance(secret_key, str):
            secret_key = secret_key.encode('utf-8')
        
        # Generar HMAC-SHA256
        signature = hmac.new(
            secret_key,
            data_string,
            hashlib.sha256
        ).hexdigest()
        
        return signature.upper()  # R4 requiere mayúsculas
    except Exception as e:
        raise Exception(f"Error generando HMAC: {str(e)}")

def create_consulta_pm_auth(referencia, telefono_origen):
    """
    Crea autenticación para MBconsulta_pm
    Format: referencia + telefono_origen
    """
    data_string = f"{referencia}{telefono_origen}"
    return generate_hmac_signature(data_string, settings.R4_COMMERCE_TOKEN)

def create_c2p_auth(telefono_destino, monto, banco, cedula):
    """
    Crea autenticación para MBc2p
    Format: TelefonoDestino + Monto + Banco + Cedula
    """
    data_string = f"{telefono_destino}{monto}{banco}{cedula}"
    return generate_hmac_signature(data_string, settings.R4_COMMERCE_TOKEN)

def create_webhook_auth(banco):
    """
    Crea autenticación para webhooks
    Format: Banco
    """
    return generate_hmac_signature(banco, settings.R4_COMMERCE_TOKEN)
