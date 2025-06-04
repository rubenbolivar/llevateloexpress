#!/usr/bin/env python3
"""
Script para migrar imágenes de productos a media/products/ (ubicación estándar Django)
"""
import os
import sys
import django
import shutil

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llevateloexpress_backend.settings')
django.setup()

from products.models import Product

def migrate_product_images():
    print('=== MIGRACIÓN DE IMÁGENES A MEDIA/PRODUCTS/ ===')
    
    # Rutas base
    img_products_dir = '/var/www/llevateloexpress/img/products'
    media_products_dir = '/var/www/llevateloexpress/media/products'
    
    # Crear directorio media/products si no existe
    os.makedirs(media_products_dir, exist_ok=True)
    print(f'✅ Directorio {media_products_dir} verificado')
    
    # Mapeo de productos tradicionales (archivos a mover)
    traditional_images = {
        'Suzuki DR 650': 'dr650.jpg',
        'Suzuki GN 125': 'gn125.jpg', 
        'Suzuki V-Strom 250': 'vstrom.jpg',
        'Voge 525 DSX': '525dsx.jpg',
        'Voge AC 525 X': 'ac525.jpg',
        'Voge Rally 300': '300.jpg',
        'Voge SR4': 'sr4.jpg'
    }
    
    moved_files = 0
    updated_records = 0
    
    # Procesar cada producto
    for product in Product.objects.all():
        old_image = str(product.image)
        
        if product.name in traditional_images:
            filename = traditional_images[product.name]
            source_path = os.path.join(img_products_dir, filename)
            dest_path = os.path.join(media_products_dir, filename)
            
            # Mover archivo físico si existe
            if os.path.exists(source_path):
                if not os.path.exists(dest_path):
                    shutil.copy2(source_path, dest_path)
                    print(f'📁 Movido: {filename} → media/products/')
                    moved_files += 1
                else:
                    print(f'📁 Ya existe: {filename} en media/products/')
            
            # Actualizar base de datos
            new_image_path = f'products/{filename}'
            product.image = new_image_path
            product.save()
            print(f'✅ {product.name}: {old_image} → {new_image_path}')
            updated_records += 1
            
        elif 'WhatsApp' in old_image:
            # Las imágenes de WhatsApp ya están en media/products/
            # Solo ajustar la ruta en BD si es necesario
            if old_image.startswith('products/'):
                print(f'📱 {product.name}: {product.image} (ya correcto)')
            else:
                # Corregir ruta
                if 'products/' not in old_image:
                    product.image = f'products/{os.path.basename(old_image)}'
                else:
                    product.image = old_image
                product.save()
                print(f'📱 {product.name}: {old_image} → {product.image}')
                updated_records += 1
        else:
            print(f'⚠️  {product.name}: {product.image} (revisar manualmente)')
    
    print(f'\n=== RESUMEN DE MIGRACIÓN ===')
    print(f'Archivos movidos: {moved_files}')
    print(f'Registros actualizados: {updated_records}')
    
    # Verificar resultado final
    print('\n=== ESTADO FINAL ===')
    for product in Product.objects.all():
        print(f'ID: {product.id} | {product.name} | Imagen: {product.image}')
        
        # Verificar que el archivo existe
        if product.image:
            file_path = os.path.join('/var/www/llevateloexpress/media', str(product.image))
            exists = os.path.exists(file_path)
            print(f'   Archivo existe: {"✅" if exists else "❌"} {file_path}')
    
    print('\n✅ Migración completada!')

if __name__ == '__main__':
    migrate_product_images() 