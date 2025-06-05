#!/usr/bin/env python
"""
Script para crear templates de email para password reset
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/var/www/llevateloexpress')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from notifications.models import NotificationType, EmailTemplate

def create_password_reset_templates():
    """
    Crear templates de email para password reset
    """
    print("🔐 Creando templates de email para password reset...")
    
    # Template 1: Password Reset Request
    try:
        nt_reset = NotificationType.objects.get(code='password_reset')
        
        template_reset = EmailTemplate.objects.create(
            notification_type=nt_reset,
            subject='Recuperación de Contraseña - LlévateloExpress',
            text_content='''Hola {{ user.first_name|default:user.username }},

Hemos recibido una solicitud para restablecer tu contraseña en LlévateloExpress.

Para crear una nueva contraseña, visita el siguiente enlace:
{{ reset_url }}

Este enlace es válido por {{ expires_hours }} horas.

Si no solicitaste este cambio, puedes ignorar este mensaje.

¿Necesitas ayuda? Contáctanos:
- WhatsApp: +58 414-123-4567
- Email: soporte@llevateloexpress.com

--
LlévateloExpress
Tu financiamiento de vehículos en Venezuela''',
            html_content='''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Recuperación de Contraseña</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
        <h2>🔐 Recuperación de Contraseña</h2>
    </div>
    
    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
        <p>Hola <strong>{{ user.first_name|default:user.username }}</strong>,</p>
        
        <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en LlévateloExpress.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{ reset_url }}" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; display: inline-block;">
                Restablecer Contraseña
            </a>
        </div>
        
        <p><strong>Importante:</strong> Este enlace es válido por {{ expires_hours }} horas.</p>
        
        <p>Si no solicitaste este cambio, puedes ignorar este mensaje de forma segura.</p>
        
        <hr style="margin: 20px 0;">
        
        <p><strong>¿Necesitas ayuda?</strong><br>
        WhatsApp: +58 414-123-4567<br>
        Email: soporte@llevateloexpress.com</p>
        
        <p style="text-align: center; color: #666; font-size: 12px;">
            LlévateloExpress - Tu financiamiento de vehículos en Venezuela
        </p>
    </div>
</body>
</html>''',
            available_variables='user, reset_url, reset_token, expires_hours, site_name',
            is_active=True
        )
        print(f"✅ Template password_reset creado: ID {template_reset.id}")
        
    except Exception as e:
        print(f"❌ Error creando template password_reset: {e}")
    
    # Template 2: Password Changed Confirmation
    try:
        nt_changed = NotificationType.objects.get(code='password_changed')
        
        template_changed = EmailTemplate.objects.create(
            notification_type=nt_changed,
            subject='Contraseña actualizada exitosamente - LlévateloExpress',
            text_content='''Hola {{ user_name }},

Tu contraseña ha sido cambiada exitosamente en LlévateloExpress.

Fecha del cambio: {{ change_date|date:"d/m/Y H:i" }}

Si no realizaste este cambio, contacta inmediatamente a nuestro soporte:
- WhatsApp: +58 414-123-4567  
- Email: soporte@llevateloexpress.com

--
LlévateloExpress
llevateloexpress.com''',
            html_content='''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Contraseña Actualizada</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
        <h2>✅ Contraseña Actualizada</h2>
    </div>
    
    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
        <p>Hola <strong>{{ user_name }}</strong>,</p>
        
        <p>Tu contraseña ha sido cambiada exitosamente en LlévateloExpress.</p>
        
        <p><strong>Fecha del cambio:</strong> {{ change_date|date:"d/m/Y H:i" }}</p>
        
        <div style="background: #fff3cd; border: 1px solid #ffeeba; border-radius: 8px; padding: 15px; margin: 20px 0;">
            <p><strong>⚠️ Importante:</strong> Si no realizaste este cambio, contacta inmediatamente a nuestro soporte.</p>
        </div>
        
        <hr style="margin: 20px 0;">
        
        <p><strong>¿Necesitas ayuda?</strong><br>
        WhatsApp: +58 414-123-4567<br>
        Email: soporte@llevateloexpress.com</p>
        
        <p style="text-align: center; color: #666; font-size: 12px;">
            LlévateloExpress - llevateloexpress.com
        </p>
    </div>
</body>
</html>''',
            available_variables='user_name, change_date',
            is_active=True
        )
        print(f"✅ Template password_changed creado: ID {template_changed.id}")
        
    except Exception as e:
        print(f"❌ Error creando template password_changed: {e}")
    
    print("\n🎉 Templates de email creados exitosamente!")

if __name__ == '__main__':
    create_password_reset_templates() 