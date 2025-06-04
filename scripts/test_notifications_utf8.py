#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from notifications.models import NotificationType, EmailTemplate
from django.core.mail import send_mail
from django.conf import settings

def test_notifications():
    print("=== PRUEBA DEL SISTEMA DE NOTIFICACIONES CON UTF8 ===")
    print("")
    
    # 1. Verificar tipos de notificación
    print("1. Tipos de notificación en la base de datos:")
    for nt in NotificationType.objects.all():
        print(f"   - {nt.name} ({'Activo' if nt.is_active else 'Inactivo'})")
    
    print("")
    print("2. Plantillas de email:")
    templates = EmailTemplate.objects.all()
    print(f"   Total: {templates.count()}")
    
    # 2. Crear una notificación de prueba con caracteres especiales
    print("")
    print("3. Prueba de caracteres UTF8:")
    
    test_strings = [
        "Notificación con acentos: áéíóú ÁÉÍÓÚ",
        "Texto con ñ: El niño compró una motocicleta",
        "Signos especiales: ¡Felicitaciones! ¿Necesitas ayuda?",
        "Nombres venezolanos: José Pérez, María Núñez",
        "Montos en bolívares: Bs. 1.250,50",
    ]
    
    print("   Textos de prueba:")
    for text in test_strings:
        print(f"   [OK] {text}")
    
    # 3. Verificar configuración de email
    print("")
    print("4. Configuración de email:")
    print(f"   - Backend: {settings.EMAIL_BACKEND}")
    print(f"   - Host: {settings.EMAIL_HOST}")
    print(f"   - Puerto: {settings.EMAIL_PORT}")
    print(f"   - Usuario: {settings.EMAIL_HOST_USER}")
    print(f"   - From: {settings.DEFAULT_FROM_EMAIL}")
    
    # 4. Intentar enviar un email de prueba
    print("")
    print("5. Enviando email de prueba...")
    
    try:
        subject = "Prueba UTF8 - Notificación de LlévateloExpress"
        message = """
¡Hola!

Esta es una prueba del sistema de notificaciones con caracteres UTF8.

Verificación de caracteres especiales:
- Acentos: áéíóú ÁÉÍÓÚ
- Letra ñ: España, niño, año
- Signos: ¿Cómo estás? ¡Excelente!
- Nombres: José María Pérez Núñez

Si recibes este mensaje correctamente, el sistema de notificaciones está funcionando perfectamente con UTF8.

Saludos,
El equipo de LlévateloExpress
"""
        
        # Si el backend es console, se mostrará en la consola
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            print("   NOTA: Email backend configurado como 'console', el email se mostrará abajo:")
            print("-" * 50)
        
        result = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['test@example.com'],
            fail_silently=False,
        )
        
        if result:
            print("   [OK] Email enviado exitosamente")
        else:
            print("   [ERROR] Error al enviar el email")
            
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
    
    print("")
    print("=== PRUEBA COMPLETADA ===")

if __name__ == "__main__":
    test_notifications() 