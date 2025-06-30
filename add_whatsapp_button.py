#!/usr/bin/env python3
import os
import re

# HTML del botón flotante oficial de WhatsApp
whatsapp_html = '''
<!-- Botón flotante oficial de WhatsApp -->
<a href="https://api.whatsapp.com/send?phone=5804128701585&text=¡Hola!%20Necesito%20información%20sobre%20financiamiento%20de%20vehículos%20en%20LlévateloExpress.%20¿Pueden%20ayudarme?" 
   class="whatsapp-float" 
   target="_blank" 
   rel="noopener noreferrer"
   aria-label="Contactar por WhatsApp"
   title="¿Necesitas ayuda? ¡Escríbenos por WhatsApp!">
    
    <!-- Logo oficial de WhatsApp SVG -->
    <svg class="whatsapp-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.465 3.085"/>
    </svg>
</a>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const whatsappButton = document.querySelector('.whatsapp-float');
    if (whatsappButton) {
        setTimeout(function() {
            whatsappButton.style.opacity = '1';
            whatsappButton.style.transform = 'scale(1)';
        }, 1000);
    }
});
</script>

'''

# Páginas principales (excluir debug, test y backup)
main_pages = [
    'index.html', 'catalogo.html', 'contacto.html', 'dashboard.html',
    'detalle-producto.html', 'login.html', 'nosotros.html', 'planes.html',
    'politicas-privacidad.html', 'realizar-pago.html', 'registro-directo.html',
    'registro.html', 'solicitud-financiamiento.html', 'terminos-condiciones.html',
    'calculadora.html'
]

print("🚀 Agregando botón flotante oficial de WhatsApp...")

for page in main_pages:
    if os.path.exists(page):
        with open(page, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si ya tiene el botón
        if 'whatsapp-float' not in content:
            # Insertar antes de </body>
            new_content = content.replace('</body>', whatsapp_html + '\n</body>')
            
            with open(page, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ {page} - Botón agregado")
        else:
            print(f"⚠️  {page} - Ya tiene botón WhatsApp")
    else:
        print(f"❌ {page} - Archivo no encontrado")

print("\n🎉 ¡Proceso completado!")
print(f"📱 Número WhatsApp: +58 412-8701585")
print(f"🌐 Páginas actualizadas con botón flotante oficial")
