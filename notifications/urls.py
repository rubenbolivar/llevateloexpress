from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notificaciones del usuario
    path('', views.UserNotificationsListView.as_view(), name='user-notifications'),
    path('stats/', views.notification_stats, name='notification-stats'),
    path('<int:notification_id>/read/', views.mark_notification_as_read, name='mark-as-read'),
    path('mark-all-read/', views.mark_all_notifications_as_read, name='mark-all-read'),
    
    # Preferencias de notificación
    path('preferences/', views.UserNotificationPreferencesView.as_view(), name='user-preferences'),
    
    # Tipos de notificaciones
    path('types/', views.NotificationTypesListView.as_view(), name='notification-types'),
    
    # Funciones de prueba y gestión
    path('test/', views.test_notification, name='test-notification'),
    path('unsubscribe/', views.unsubscribe_notifications, name='unsubscribe'),
] 