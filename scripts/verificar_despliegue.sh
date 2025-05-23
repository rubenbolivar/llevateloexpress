#!/bin/bash

# Script para verificar que el despliegue se haya realizado correctamente
# Comprueba recursos críticos en el servidor

SITE_URL="https://llevateloexpress.com"

# Recursos críticos que deben estar accesibles
RECURSOS=(
    "css/styles.css"
    "js/main.js"
    "js/products.js"
    "js/models.js"
    "js/calculadora.js"
    "templates/calculadora.html"
    "templates/catalogo.html"
    "img/products/gn125.jpg"
    "img/banners/logo.png"
)

echo "=== VERIFICACIÓN POST-DESPLIEGUE ==="
echo "Comprobando recursos críticos en $SITE_URL..."
echo ""

FALLOS=0

for recurso in "${RECURSOS[@]}"; do
    echo -n "Verificando $recurso... "
    
    # Usar curl para comprobar el código HTTP
    RESPUESTA=$(curl -s -o /dev/null -w "%{http_code}" "$SITE_URL/$recurso")
    
    if [ "$RESPUESTA" == "200" ]; then
        echo "OK (HTTP 200)"
    else
        echo "ERROR (HTTP $RESPUESTA)"
        FALLOS=$((FALLOS + 1))
    fi
done

# Comprobar si el catálogo muestra productos
echo -n "Verificando si el catálogo muestra productos... "
CATALOGO_CONTENT=$(curl -s "$SITE_URL/catalogo.html")
if [[ $CATALOGO_CONTENT == *"card-img-top"* ]]; then
    echo "OK (Se detectan tarjetas de productos)"
else
    echo "ERROR (No se detectan tarjetas de productos)"
    FALLOS=$((FALLOS + 1))
fi

# Comprobar si la calculadora funciona
echo -n "Verificando si la calculadora está disponible... "
CALCULADORA_CONTENT=$(curl -s "$SITE_URL/calculadora.html")
if [[ $CALCULADORA_CONTENT == *"calculateCredito"* ]]; then
    echo "OK (Se detecta función de cálculo)"
else
    echo "ERROR (No se detecta función de cálculo)"
    FALLOS=$((FALLOS + 1))
fi

echo ""
if [ $FALLOS -eq 0 ]; then
    echo "¡VERIFICACIÓN EXITOSA! Todos los recursos críticos están disponibles."
    exit 0
else
    echo "¡ATENCIÓN! Se encontraron $FALLOS problemas en el despliegue."
    echo "Por favor, revisa los errores y corrige los problemas."
    exit 1
fi 