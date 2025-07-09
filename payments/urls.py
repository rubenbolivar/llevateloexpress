from django.urls import path
from . import api_views
from .webhooks import r4_webhooks

app_name = 'payments'

urlpatterns = [
    path('verify-mobile/', api_views.verify_mobile_payment, name='verify_mobile_payment'),
    path('methods/', api_views.payment_methods, name='payment_methods'),
    path('schedule/', api_views.user_payment_schedule, name='user_payment_schedule'),
    path('r4/', api_views.r4_system_status, name='r4_status'),
    path('r4/simulate/', api_views.r4_simulate, name='r4_simulate'),
    path('r4/mobile-query/', api_views.r4_mobile_query, name='r4_mobile_query'),
    path('r4/dispersion/', api_views.r4_dispersion, name='r4_dispersion'),
    path('webhooks/r4/notify/', r4_webhooks.r4_notification_webhook, name='r4_notify_webhook'),
    path('webhooks/r4/validate-client/', r4_webhooks.r4_client_validation_webhook,
name='r4_validate_client_webhook'),
]
