#!/usr/bin/env python
"""
Script para configurar los tipos de notificación de reset de contraseña
en el sistema de notificaciones existente de LlévateloExpress
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/var/www/llevateloexpress')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from notifications.models import NotificationType, EmailTemplate

def setup_password_reset_notifications():
    """
    Configura los tipos de notificación y templates para reset de contraseña
    """
    print("🔐 Configurando notificaciones de reset de contraseña...")
    
    # 1. Crear tipo de notificación para solicitud de reset
    password_reset_type, created = NotificationType.objects.get_or_create(
        code='password_reset',
        defaults={
            'name': 'Recuperación de Contraseña',
            'description': 'Notificación enviada cuando un usuario solicita recuperar su contraseña',
            'is_active': True
        }
    )
    
    if created:
        print("✅ Tipo de notificación 'password_reset' creado")
    else:
        print("ℹ️  Tipo de notificación 'password_reset' ya existe")
    
    # 2. Crear template de email para reset
    reset_template, created = EmailTemplate.objects.get_or_create(
        notification_type=password_reset_type,
        defaults={
            'name': 'Template Reset de Contraseña',
            'subject': 'Recuperación de Contraseña - {{ site.name }}',
            'html_content': """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recuperación de Contraseña - {{ site.name }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }
        .content {
            padding: 30px;
        }
        .greeting {
            font-size: 18px;
            margin-bottom: 20px;
            color: #495057;
        }
        .message {
            font-size: 16px;
            margin-bottom: 30px;
            line-height: 1.7;
        }
        .reset-button {
            display: inline-block;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white !important;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            font-size: 16px;
            margin: 20px 0;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
        }
        .button-container {
            text-align: center;
            margin: 30px 0;
        }
        .security-note {
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            font-size: 14px;
        }
        .footer {
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #dee2e6;
            font-size: 14px;
            color: #6c757d;
        }
        .footer a {
            color: #007bff;
            text-decoration: none;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .alternative-link {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            font-size: 12px;
            word-break: break-all;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="font-size: 48px; margin-bottom: 20px;">🔐</div>
            <div class="logo">{{ site.name }}</div>
            <h1>Recuperación de Contraseña</h1>
        </div>
        
        <div class="content">
            <div class="greeting">
                Hola {% if user.first_name %}{{ user.first_name }}{% else %}{{ user.username }}{% endif %},
            </div>
            
            <div class="message">
                Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en {{ site.name }}. 
                Si no solicitaste este cambio, puedes ignorar este mensaje de forma segura.
            </div>
            
            <div class="message">
                Para crear una nueva contraseña, haz clic en el siguiente botón:
            </div>
            
            <div class="button-container">
                <a href="{{ reset_url }}" class="reset-button">
                    Restablecer Contraseña
                </a>
            </div>
            
            <div class="security-note">
                <strong>Importante:</strong> Este enlace es válido por {{ expires_hours }} horas por seguridad. 
                Si no cambias tu contraseña dentro de este tiempo, deberás solicitar un nuevo enlace.
            </div>
            
            <div class="message">
                Si el botón no funciona, también puedes copiar y pegar el siguiente enlace en tu navegador:
            </div>
            
            <div class="alternative-link">
                {{ reset_url }}
            </div>
            
            <div class="message">
                <strong>¿Necesitas ayuda?</strong><br>
                Si tienes problemas para restablecer tu contraseña o no solicitaste este cambio, 
                contáctanos en <a href="mailto:{{ site.contact_email }}">{{ site.contact_email }}</a> 
                o a través de WhatsApp: <a href="https://wa.me/{{ site.phone }}">{{ site.phone }}</a>
            </div>
        </div>
        
        <div class="footer">
            <p>
                Este mensaje fue enviado desde {{ site.name }}<br>
                <a href="{{ site.url }}">{{ site.url }}</a>
            </p>
            <p>
                <strong>Tu financiamiento de vehículos en Venezuela</strong><br>
                Motocicletas • Vehículos • Camiones • Maquinaria Agrícola
            </p>
            <p style="margin-top: 20px; font-size: 12px; color: #999;">
                Si no solicitaste este email, puedes ignorarlo con seguridad.
            </p>
        </div>
    </div>
</body>
</html>
            """,
            'text_content': """
Hola {% if user.first_name %}{{ user.first_name }}{% else %}{{ user.username }}{% endif %},

Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en {{ site.name }}.

Para crear una nueva contraseña, visita el siguiente enlace:
{{ reset_url }}

Este enlace es válido por {{ expires_hours }} horas.

Si no solicitaste este cambio, puedes ignorar este mensaje de forma segura.

¿Necesitas ayuda? Contáctanos:
- Email: {{ site.contact_email }}
- WhatsApp: {{ site.phone }}

--
{{ site.name }}
{{ site.url }}
            """,
            'is_active': True
        }
    )
    
    if created:
        print("✅ Template de email 'password_reset' creado")
    else:
        print("ℹ️  Template de email 'password_reset' ya existe")
    
    # 3. Crear tipo de notificación para confirmación de cambio
    password_changed_type, created = NotificationType.objects.get_or_create(
        code='password_changed',
        defaults={
            'name': 'Contraseña Cambiada',
            'description': 'Notificación enviada cuando un usuario cambia su contraseña exitosamente',
            'is_active': True
        }
    )
    
    if created:
        print("✅ Tipo de notificación 'password_changed' creado")
    else:
        print("ℹ️  Tipo de notificación 'password_changed' ya existe")
    
    # 4. Crear template para confirmación
    changed_template, created = EmailTemplate.objects.get_or_create(
        notification_type=password_changed_type,
        defaults={
            'name': 'Template Contraseña Cambiada',
            'subject': 'Contraseña actualizada exitosamente - {{ site.name }}',
            'html_content': """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Contraseña Actualizada - {{ site.name }}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #28a745; color: white; padding: 20px; text-align: center; border-radius: 5px; }
        .content { padding: 20px; background: #f9f9f9; border-radius: 5px; margin-top: 20px; }
        .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>✅ Contraseña Actualizada</h2>
        </div>
        <div class="content">
            <p>Hola {{ user_name }},</p>
            <p>Tu contraseña ha sido cambiada exitosamente en {{ site.name }}.</p>
            <p><strong>Fecha del cambio:</strong> {{ change_date|date:"d/m/Y H:i" }}</p>
            <p>Si no realizaste este cambio, contacta inmediatamente a nuestro soporte.</p>
            <p><strong>Contacto:</strong><br>
            Email: {{ site.contact_email }}<br>
            WhatsApp: {{ site.phone }}</p>
        </div>
        <div class="footer">
            <p>{{ site.name }} - {{ site.url }}</p>
        </div>
    </div>
</body>
</html>
            """,
            'text_content': """
Hola {{ user_name }},

Tu contraseña ha sido cambiada exitosamente en {{ site.name }}.

Fecha del cambio: {{ change_date|date:"d/m/Y H:i" }}

Si no realizaste este cambio, contacta inmediatamente a nuestro soporte:
- Email: {{ site.contact_email }}
- WhatsApp: {{ site.phone }}

--
{{ site.name }}
{{ site.url }}
            """,
            'is_active': True
        }
    )
    
    if created:
        print("✅ Template de email 'password_changed' creado")
    else:
        print("ℹ️  Template de email 'password_changed' ya existe")
    
    print("\n🎉 Configuración de notificaciones de reset de contraseña completada!")
    print("\n📋 Resumen:")
    print(f"- Tipo password_reset: {password_reset_type.id}")
    print(f"- Template password_reset: {reset_template.id}")
    print(f"- Tipo password_changed: {password_changed_type.id}")  
    print(f"- Template password_changed: {changed_template.id}")

if __name__ == '__main__':
    setup_password_reset_notifications() 