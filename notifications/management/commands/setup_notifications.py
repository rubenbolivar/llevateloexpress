from django.core.management.base import BaseCommand
from notifications.models import NotificationType, EmailTemplate


class Command(BaseCommand):
    help = 'Inicializa los tipos de notificaciones y plantillas básicas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Sobrescribir plantillas existentes'
        )
    
    def handle(self, *args, **options):
        overwrite = options['overwrite']
        
        self.stdout.write(
            self.style.SUCCESS('Iniciando configuración del sistema de notificaciones...')
        )
        
        # Crear tipos de notificaciones
        self.create_notification_types()
        
        # Crear plantillas básicas
        self.create_email_templates(overwrite)
        
        self.stdout.write(
            self.style.SUCCESS('✓ Configuración completada exitosamente')
        )
    
    def create_notification_types(self):
        """Crea los tipos de notificaciones básicos"""
        self.stdout.write('Creando tipos de notificaciones...')
        
        notification_types = [
            ('welcome', 'Bienvenida', 'Email de bienvenida para nuevos usuarios'),
            ('registration_confirmation', 'Confirmación de Registro', 'Confirmación de que la cuenta fue creada'),
            ('financing_application', 'Solicitud de Financiamiento', 'Notificación de nueva solicitud de financiamiento'),
            ('application_approved', 'Solicitud Aprobada', 'Notificación de solicitud de financiamiento aprobada'),
            ('application_rejected', 'Solicitud Rechazada', 'Notificación de solicitud de financiamiento rechazada'),
            ('application_pending', 'Solicitud Pendiente', 'Notificación de solicitud en proceso de revisión'),
            ('payment_reminder', 'Recordatorio de Pago', 'Recordatorio de cuota pendiente de pago'),
            ('payment_confirmation', 'Confirmación de Pago', 'Confirmación de pago recibido'),
            ('document_request', 'Solicitud de Documentos', 'Solicitud de documentos adicionales'),
            ('newsletter', 'Boletín Informativo', 'Boletín con novedades y promociones'),
            ('promotion', 'Promoción Especial', 'Promociones especiales y ofertas'),
            ('system_maintenance', 'Mantenimiento del Sistema', 'Notificaciones de mantenimiento programado'),
        ]
        
        created_count = 0
        for code, name, description in notification_types:
            notification_type, created = NotificationType.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': description,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Creado: {name}')
            else:
                self.stdout.write(f'  - Ya existe: {name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Tipos de notificaciones: {created_count} creados')
        )
    
    def create_email_templates(self, overwrite=False):
        """Crea las plantillas de email básicas"""
        self.stdout.write('Creando plantillas de email...')
        
        templates = [
            {
                'code': 'welcome',
                'subject': '¡Bienvenido a LlévateloExpress, {{user.first_name}}!',
                'html_content': self.get_welcome_template(),
                'text_content': self.get_welcome_text_template(),
                'variables': {
                    'user.first_name': 'Nombre del usuario',
                    'user.full_name': 'Nombre completo del usuario',
                    'site.name': 'Nombre del sitio',
                    'site.url': 'URL del sitio'
                }
            },
            {
                'code': 'registration_confirmation',
                'subject': 'Confirmación de registro en LlévateloExpress',
                'html_content': self.get_registration_confirmation_template(),
                'text_content': self.get_registration_confirmation_text_template(),
                'variables': {
                    'user.first_name': 'Nombre del usuario',
                    'confirmation_message': 'Mensaje de confirmación',
                    'login_url': 'URL de inicio de sesión'
                }
            },
            {
                'code': 'financing_application',
                'subject': 'Tu solicitud de financiamiento ha sido recibida',
                'html_content': self.get_financing_application_template(),
                'text_content': self.get_financing_application_text_template(),
                'variables': {
                    'user.first_name': 'Nombre del usuario',
                    'application_id': 'ID de la solicitud',
                    'product_name': 'Nombre del producto',
                    'amount': 'Monto solicitado',
                    'plan': 'Plan de financiamiento'
                }
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for template_data in templates:
            try:
                notification_type = NotificationType.objects.get(code=template_data['code'])
                
                template, created = EmailTemplate.objects.get_or_create(
                    notification_type=notification_type,
                    defaults={
                        'subject': template_data['subject'],
                        'html_content': template_data['html_content'],
                        'text_content': template_data['text_content'],
                        'available_variables': template_data['variables'],
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'  ✓ Creada: {notification_type.name}')
                elif overwrite:
                    template.subject = template_data['subject']
                    template.html_content = template_data['html_content']
                    template.text_content = template_data['text_content']
                    template.available_variables = template_data['variables']
                    template.save()
                    updated_count += 1
                    self.stdout.write(f'  ↻ Actualizada: {notification_type.name}')
                else:
                    self.stdout.write(f'  - Ya existe: {notification_type.name}')
                    
            except NotificationType.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Tipo de notificación no encontrado: {template_data["code"]}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Plantillas: {created_count} creadas, {updated_count} actualizadas')
        )
    
    def get_welcome_template(self):
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bienvenido a LlévateloExpress</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
        .button { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>¡Bienvenido a LlévateloExpress!</h1>
        </div>
        <div class="content">
            <h2>Hola {{user.first_name}},</h2>
            <p>{{welcome_message|default:"¡Gracias por unirte a LlévateloExpress!"}}</p>
            
            <p>Ahora puedes:</p>
            <ul>
                {% for step in next_steps %}
                <li>{{step}}</li>
                {% empty %}
                <li>Explorar nuestro catálogo de vehículos</li>
                <li>Conocer nuestros planes de financiamiento</li>
                <li>Simular tu financiamiento</li>
                {% endfor %}
            </ul>
            
            <a href="{{site.url}}" class="button">Explorar Catálogo</a>
        </div>
        <div class="footer">
            <p>{{site.name}} - {{current_year}}</p>
            <p>Contacto: {{site.contact_email}} | {{site.phone}}</p>
        </div>
    </div>
</body>
</html>
        """
    
    def get_welcome_text_template(self):
        return """
¡Bienvenido a LlévateloExpress, {{user.first_name}}!

{{welcome_message|default:"¡Gracias por unirte a LlévateloExpress!"}}

Ahora puedes:
{% for step in next_steps %}
- {{step}}
{% empty %}
- Explorar nuestro catálogo de vehículos
- Conocer nuestros planes de financiamiento
- Simular tu financiamiento
{% endfor %}

Visita nuestro sitio: {{site.url}}

{{site.name}} - {{current_year}}
Contacto: {{site.contact_email}} | {{site.phone}}
        """
    
    def get_registration_confirmation_template(self):
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirmación de Registro</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #28a745; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
        .button { background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>¡Registro Exitoso!</h1>
        </div>
        <div class="content">
            <h2>Hola {{user.first_name}},</h2>
            <p>{{confirmation_message|default:"Tu cuenta ha sido creada exitosamente"}}</p>
            
            <p>Ya puedes iniciar sesión y comenzar a explorar nuestros productos y servicios.</p>
            
            <a href="{{login_url|default:'https://llevateloexpress.com/login.html'}}" class="button">Iniciar Sesión</a>
        </div>
        <div class="footer">
            <p>{{site.name}} - {{current_year}}</p>
            <p>Contacto: {{site.contact_email}} | {{site.phone}}</p>
        </div>
    </div>
</body>
</html>
        """
    
    def get_registration_confirmation_text_template(self):
        return """
¡Registro Exitoso!

Hola {{user.first_name}},

{{confirmation_message|default:"Tu cuenta ha sido creada exitosamente"}}

Ya puedes iniciar sesión y comenzar a explorar nuestros productos y servicios.

Iniciar sesión: {{login_url|default:'https://llevateloexpress.com/login.html'}}

{{site.name}} - {{current_year}}
Contacto: {{site.contact_email}} | {{site.phone}}
        """
    
    def get_financing_application_template(self):
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solicitud de Financiamiento Recibida</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #17a2b8; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
        .details { background: white; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Solicitud Recibida</h1>
        </div>
        <div class="content">
            <h2>Hola {{user.first_name}},</h2>
            <p>Hemos recibido tu solicitud de financiamiento. La revisaremos y te contactaremos pronto.</p>
            
            <div class="details">
                <h3>Detalles de tu solicitud:</h3>
                <p><strong>ID de Solicitud:</strong> {{application_id}}</p>
                <p><strong>Producto:</strong> {{product_name}}</p>
                <p><strong>Monto:</strong> {{amount}}</p>
                <p><strong>Plan:</strong> {{plan}}</p>
                <p><strong>Fecha:</strong> {{application_date}}</p>
            </div>
            
            <p>Te contactaremos en las próximas 24-48 horas para continuar con el proceso.</p>
        </div>
        <div class="footer">
            <p>{{site.name}} - {{current_year}}</p>
            <p>Contacto: {{site.contact_email}} | {{site.phone}}</p>
        </div>
    </div>
</body>
</html>
        """
    
    def get_financing_application_text_template(self):
        return """
Solicitud de Financiamiento Recibida

Hola {{user.first_name}},

Hemos recibido tu solicitud de financiamiento. La revisaremos y te contactaremos pronto.

Detalles de tu solicitud:
- ID de Solicitud: {{application_id}}
- Producto: {{product_name}}
- Monto: {{amount}}
- Plan: {{plan}}
- Fecha: {{application_date}}

Te contactaremos en las próximas 24-48 horas para continuar con el proceso.

{{site.name}} - {{current_year}}
Contacto: {{site.contact_email}} | {{site.phone}}
        """ 