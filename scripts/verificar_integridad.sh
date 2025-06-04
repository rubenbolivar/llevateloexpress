#!/bin/bash

# Script para verificar la integridad de los recursos críticos en el entorno local
# Debe ejecutarse antes de desplegar cambios al servidor

echo "Verificando integridad de recursos críticos en entorno local..."

# Directorios críticos que deben existir
DIRECTORIOS=(
    "css"
    "js"
    "img"
    "img/products"
    "img/banners"
    "templates"
)

# Archivos críticos que deben existir
ARCHIVOS=(
    "css/styles.css"
    "js/main.js"
    "js/products.js"
    "js/models.js"
    "js/calculadora.js"
    "js/planes.js"
    "js/registro.js"
    "templates/calculadora.html"
    "templates/catalogo.html"
    "index.html"
)

# Verificar directorios
echo "Verificando directorios..."
for dir in "${DIRECTORIOS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "ERROR: El directorio '$dir' no existe!"
        exit 1
    else
        echo "OK: Directorio $dir"
    fi
done

# Verificar archivos
echo "Verificando archivos..."
for archivo in "${ARCHIVOS[@]}"; do
    if [ ! -f "$archivo" ]; then
        echo "ERROR: El archivo '$archivo' no existe!"
        exit 1
    else
        echo "OK: Archivo $archivo"
    fi
done

# Verificar imágenes de productos (debe haber al menos algunas)
PRODUCTOS=$(ls img/products/ | grep -E "\.jpg|\.png" | wc -l)
if [ "$PRODUCTOS" -lt 3 ]; then
    echo "ADVERTENCIA: Hay muy pocas imágenes de productos ($PRODUCTOS). Verifica que no falten imágenes."
else
    echo "OK: Hay $PRODUCTOS imágenes de productos."
fi

echo "Verificación completada con éxito. El entorno local parece tener todos los recursos críticos."
echo "Puedes proceder con el despliegue."
exit 0 