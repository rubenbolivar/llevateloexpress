from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .models import EmailNotification, UserNotificationPreference, NotificationType
from .services import notification_service
from .serializers import (
    EmailNotificationSerializer, 
    UserNotificationPreferenceSerializer,
    NotificationTypeSerializer
)
from django.utils import timezone


class UserNotificationsListView(generics.ListAPIView):
    """
    Vista para obtener las notificaciones del usuario autenticado
    """
    serializer_class = EmailNotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EmailNotification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Paginación
        page = request.GET.get('page', 1)
        per_page = min(int(request.GET.get('per_page', 20)), 50)  # Máximo 50 por página
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        serializer = self.get_serializer(page_obj.object_list, many=True)
        
        return Response({
            'success': True,
            'notifications': serializer.data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })


class UserNotificationPreferencesView(generics.RetrieveUpdateAPIView):
    """
    Vista para obtener y actualizar las preferencias de notificación del usuario
    """
    serializer_class = UserNotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        preferences, created = UserNotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Preferencias actualizadas correctamente',
                    'preferences': serializer.data
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Error en los datos proporcionados',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error actualizando preferencias: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationTypesListView(generics.ListAPIView):
    """
    Vista para obtener la lista de tipos de notificaciones disponibles
    """
    serializer_class = NotificationTypeSerializer
    permission_classes = [IsAuthenticated]
    queryset = NotificationType.objects.filter(is_active=True).order_by('name')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, notification_id):
    """
    Marca una notificación específica como leída
    """
    try:
        notification = EmailNotification.objects.get(
            id=notification_id,
            user=request.user
        )
        
        # Si está en estado 'sent', marcarla como 'opened'
        if notification.status == 'sent':
            notification.mark_as_opened()
            
        return Response({
            'success': True,
            'message': 'Notificación marcada como leída'
        })
        
    except EmailNotification.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Notificación no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_as_read(request):
    """
    Marca todas las notificaciones del usuario como leídas
    """
    try:
        updated_count = EmailNotification.objects.filter(
            user=request.user,
            status='sent'
        ).update(status='opened')
        
        return Response({
            'success': True,
            'message': f'{updated_count} notificaciones marcadas como leídas'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_stats(request):
    """
    Obtiene estadísticas de notificaciones del usuario
    """
    try:
        user_notifications = EmailNotification.objects.filter(user=request.user)
        
        stats = {
            'total': user_notifications.count(),
            'unread': user_notifications.filter(status='sent').count(),
            'failed': user_notifications.filter(status='failed').count(),
            'by_type': {}
        }
        
        # Estadísticas por tipo de notificación
        for notification_type in NotificationType.objects.filter(is_active=True):
            count = user_notifications.filter(notification_type=notification_type).count()
            if count > 0:
                stats['by_type'][notification_type.code] = {
                    'name': notification_type.name,
                    'count': count
                }
        
        return Response({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error obteniendo estadísticas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_notification(request):
    """
    Envía una notificación de prueba al usuario autenticado
    """
    try:
        notification_type = request.data.get('type', 'welcome')
        
        success = notification_service.send_notification(
            user=request.user,
            notification_type_code=notification_type,
            context={
                'test_message': 'Esta es una notificación de prueba',
                'timestamp': str(timezone.now())
            }
        )
        
        if success:
            return Response({
                'success': True,
                'message': f'Notificación de prueba ({notification_type}) enviada correctamente'
            })
        else:
            return Response({
                'success': False,
                'message': 'Error enviando notificación de prueba'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def unsubscribe_notifications(request):
    """
    Permite desuscribirse de todas las notificaciones por email
    """
    try:
        email = request.data.get('email')
        token = request.data.get('token')  # Para verificación de seguridad
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            preferences, created = UserNotificationPreference.objects.get_or_create(
                user=user
            )
            preferences.email_notifications_enabled = False
            preferences.save()
            
            return Response({
                'success': True,
                'message': 'Te has desuscrito exitosamente de todas las notificaciones por email'
            })
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
