#!/bin/bash

# Script para verificar cambios sin commit antes del despliegue
echo "=== Verificación de cambios sin commit ==="

# Obtener el estado de Git
CHANGES=$(git status --porcelain)

if [ -n "$CHANGES" ]; then
    echo "⚠️  ATENCIÓN: Hay cambios que no se han guardado en commit:"
    echo "$CHANGES"
    echo ""
    echo "Por favor, realiza un commit antes de continuar:"
    echo "  git add ."
    echo "  git commit -m \"feat: Descripción de los cambios\""
    exit 1
else
    echo "✅ No hay cambios pendientes."
    echo "Puedes proceder con el despliegue: ./deploy.sh"
fi
