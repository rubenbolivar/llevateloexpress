# ALTERNATIVA 4: Propiedad @customer robusta con caché inteligente
# Agregar al modelo User en users/models.py

from django.core.cache import cache
from django.db import models
import logging

logger = logging.getLogger(__name__)

# Agregar esta propiedad al modelo User existente
@property
def customer(self):
    """
    Propiedad robusta para acceder al Customer asociado con caché inteligente.
    
    Beneficios:
    1. Caché automático para evitar consultas repetidas
    2. Manejo de errores robusto
    3. Logging para debugging
    4. Creación automática de Customer si no existe (opcional)
    5. Invalidación inteligente del caché
    """
    # Clave de caché única por usuario
    cache_key = f"user_customer_{self.id}"
    
    # Intentar obtener del caché primero
    cached_customer = cache.get(cache_key)
    if cached_customer is not None:
        logger.debug(f"Customer para User {self.id} obtenido del caché")
        return cached_customer
    
    try:
        # Buscar Customer en la base de datos
        from users.models import Customer  # Import local para evitar circular
        customer_obj = Customer.objects.select_related('user').get(user=self)
        
        # Guardar en caché por 15 minutos
        cache.set(cache_key, customer_obj, 900)
        logger.debug(f"Customer {customer_obj.id} para User {self.id} cacheado")
        
        return customer_obj
        
    except Customer.DoesNotExist:
        logger.warning(f"Customer no existe para User {self.id} ({self.username})")
        
        # OPCIÓN A: Retornar None (comportamiento actual)
        cache.set(cache_key, None, 300)  # Caché por 5 minutos
        return None
        
        # OPCIÓN B: Crear Customer automáticamente (descomentear si se desea)
        # try:
        #     customer_obj = Customer.objects.create(
        #         user=self,
        #         first_name=self.first_name or '',
        #         last_name=self.last_name or '',
        #         email=self.email,
        #         verified=False,
        #         is_profile_complete=False
        #     )
        #     cache.set(cache_key, customer_obj, 900)
        #     logger.info(f"Customer {customer_obj.id} creado automáticamente para User {self.id}")
        #     return customer_obj
        # except Exception as create_error:
        #     logger.error(f"Error creando Customer para User {self.id}: {create_error}")
        #     return None
        
    except Exception as e:
        logger.error(f"Error accediendo Customer para User {self.id}: {e}")
        return None

# Método para invalidar caché cuando se modifica el Customer
def invalidate_user_customer_cache(user_id):
    """
    Invalida el caché del customer para un usuario específico.
    Llamar cuando se modifica/crea/elimina un Customer.
    """
    cache_key = f"user_customer_{user_id}"
    cache.delete(cache_key)
    logger.debug(f"Caché de Customer invalidado para User {user_id}")

# Signal para invalidar caché automáticamente
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver([post_save, post_delete], sender='users.Customer')
def invalidate_customer_cache(sender, instance, **kwargs):
    """
    Signal que invalida automáticamente el caché cuando se modifica un Customer.
    """
    if hasattr(instance, 'user_id') and instance.user_id:
        invalidate_user_customer_cache(instance.user_id)

# Método adicional para el modelo User
def get_customer_safe(self):
    """
    Método alternativo que siempre retorna un Customer válido o None.
    Útil para casos donde se necesita garantía de existencia.
    """
    customer = self.customer
    if customer and hasattr(customer, 'id'):
        return customer
    return None

# Método para verificar si el usuario tiene customer completo
def has_complete_customer(self):
    """
    Verifica si el usuario tiene un Customer con perfil completo.
    """
    customer = self.customer
    return customer and getattr(customer, 'is_profile_complete', False) 