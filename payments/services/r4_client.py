import requests
import logging
from django.conf import settings
from .hmac_utils import create_consulta_pm_auth, create_c2p_auth, create_webhook_auth
from .r4_validators import R4RequestValidator

logger = logging.getLogger(__name__)

class R4Client:
    def __init__(self):
        self.base_url = getattr(settings, 'R4_BASE_URL', 'https://r4conecta.mibanco.com.ve/')
        self.commerce_token = getattr(settings, 'R4_COMMERCE_TOKEN', '')
        self.timeout = getattr(settings, 'R4_TIMEOUT', 30)
        self.debug = getattr(settings, 'R4_DEBUG', False)
        
        if not self.commerce_token:
            raise ValueError("R4_COMMERCE_TOKEN no configurado")

    def _make_request(self, endpoint, data, auth_token):
        """
        Hace request HTTP a R4 Conecta
        """
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': auth_token,
            'Commerce': self.commerce_token
        }
        
        try:
            if self.debug:
                logger.info(f"R4 Request URL: {url}")
                logger.info(f"R4 Request Data: {data}")
                logger.info(f"R4 Headers: {headers}")
            
            response = requests.post(
                url, 
                json=data, 
                headers=headers, 
                timeout=self.timeout
            )
            
            if self.debug:
                logger.info(f"R4 Response Status: {response.status_code}")
                logger.info(f"R4 Response Body: {response.text}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en request R4: {str(e)}")
            raise Exception(f"Error comunicación R4: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado R4: {str(e)}")
            raise Exception(f"Error procesando respuesta R4: {str(e)}")

    def consulta_pago_movil(self, referencia, telefono_origen):
        """
        MBconsulta_pm - Consulta pago móvil por referencia
        """
        try:
            # Validar datos de entrada según documentación oficial
            validation_result = R4RequestValidator.validate_consulta_pm_request({
                'referencia': referencia,
                'telefono_origen': telefono_origen
            })
            
            if not validation_result['valid']:
                logger.error(f"Validación fallida para consulta PM: {validation_result['errors']}")
                return {
                    'success': False,
                    'found': False,
                    'message': f'Datos inválidos: {", ".join(validation_result["errors"])}',
                    'validation_errors': validation_result['errors']
                }
            
            # Usar datos validados
            validated_data = validation_result['data']
            
            # Crear autenticación HMAC
            auth_token = create_consulta_pm_auth(validated_data['referencia'], validated_data['telefono_origen'])
            
            # Hacer request con datos validados
            response = self._make_request('MBconsulta_pm', validated_data, auth_token)
            
            # Procesar respuesta
            if response.get('code') == '00':
                return {
                    'success': True,
                    'found': True,
                    'message': 'Pago encontrado',
                    'reference': response.get('reference'),
                    'raw_response': response
                }
            elif response.get('code') == '12':
                return {
                    'success': True,
                    'found': False,
                    'message': 'Pago no encontrado',
                    'raw_response': response
                }
            else:
                return {
                    'success': False,
                    'found': False,
                    'message': response.get('message', 'Error desconocido'),
                    'error_code': response.get('code'),
                    'raw_response': response
                }
                
        except Exception as e:
            logger.error(f"Error en consulta_pago_movil: {str(e)}")
            return {
                'success': False,
                'found': False,
                'message': f"Error: {str(e)}",
                'error': str(e)
            }

    def procesar_cobro_c2p(self, telefono_destino, cedula, concepto, banco, monto, otp, ip=None):
        """
        MBc2p - Procesar cobro C2P
        """
        try:
            # Validar datos de entrada según documentación oficial
            validation_result = R4RequestValidator.validate_c2p_request({
                'TelefonoDestino': telefono_destino,
                'Cedula': cedula,
                'Concepto': concepto,
                'Banco': banco,
                'Monto': monto,
                'Otp': otp,
                'Ip': ip
            })
            
            if not validation_result['valid']:
                logger.error(f"Validación fallida para C2P: {validation_result['errors']}")
                return {
                    'success': False,
                    'approved': False,
                    'message': f'Datos inválidos: {", ".join(validation_result["errors"])}',
                    'validation_errors': validation_result['errors']
                }
            
            # Usar datos validados
            validated_data = validation_result['data']
            
            # Crear autenticación HMAC
            auth_token = create_c2p_auth(
                validated_data['TelefonoDestino'], 
                validated_data['Monto'], 
                validated_data['Banco'], 
                validated_data['Cedula']
            )
            
            # Hacer request con datos validados
            response = self._make_request('MBc2p', validated_data, auth_token)
            
            # Procesar respuesta
            if response.get('code') == '00':
                return {
                    'success': True,
                    'approved': True,
                    'message': 'Transacción exitosa',
                    'reference': response.get('reference'),
                    'raw_response': response
                }
            else:
                return {
                    'success': False,
                    'approved': False,
                    'message': response.get('message', 'Transacción rechazada'),
                    'error_code': response.get('code'),
                    'raw_response': response
                }
                
        except Exception as e:
            logger.error(f"Error en procesar_cobro_c2p: {str(e)}")
            return {
                'success': False,
                'approved': False,
                'message': f"Error: {str(e)}",
                'error': str(e)
            }

# Instancia global del cliente
r4_client = R4Client()
