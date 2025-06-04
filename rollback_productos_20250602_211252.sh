#!/bin/bash
# Script de rollback automático para migración de productos
# Creado: 20250602_211252
echo "🔄 Iniciando rollback de migración de productos..."

cd /var/www/llevateloexpress

# Restaurar archivos originales
sudo cp js/products-backup-20250602_211252.js js/products.js
sudo cp catalogo-backup-20250602_211252.html catalogo.html

# Recargar servicios
sudo systemctl reload llevateloexpress
sudo systemctl reload nginx

echo "✅ Rollback completado exitosamente"
echo "📝 El sistema ha sido restaurado al estado pre-migración"
