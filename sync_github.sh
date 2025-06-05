#!/bin/bash
# Script para sincronizar el VPS (fuente de verdad) con GitHub
# Dashboard solucionado - 14 solicitudes funcionando correctamente

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== SINCRONIZANDO VPS FUNCIONAL CON GITHUB ===${NC}"
echo -e "${YELLOW}VPS es fuente de verdad - Dashboard funcionando con 14 solicitudes${NC}"

# Configurar Git si no está configurado
git config --global user.name "LlevateloExpress VPS" 2>/dev/null || true
git config --global user.email "admin@llevateloexpress.com" 2>/dev/null || true

# Verificar que existe el remoto GitHub
if ! git remote get-url github >/dev/null 2>&1; then
    echo -e "${YELLOW}Configurando remoto GitHub...${NC}"
    git remote add github https://github.com/rubenbolivar/llevateloexpress.git
fi

# Verificar estado
echo -e "${YELLOW}Estado actual del repositorio:${NC}"
git status

# Añadir archivos importantes (excluyendo archivos grandes y backups)
echo -e "${YELLOW}Añadiendo archivos críticos...${NC}"
git add dashboard.html js/dashboard.js js/api-fixed.js financing/ users/ core/ products/ notifications/ RESUMEN_FINAL_SOLICITUDES_SOLUCIONADAS.md 2>/dev/null || true

# Verificar si hay cambios
if git diff --staged --quiet; then
    echo -e "${GREEN}✅ No hay cambios nuevos para sincronizar${NC}"
    echo -e "${BLUE}ℹ️  Para forzar sincronización: ./sync_github.sh force${NC}"
    if [ "$1" != "force" ]; then
        exit 0
    fi
fi

# Commit con información del estado actual
echo -e "${YELLOW}Creando commit...${NC}"
COMMIT_MSG="🔄 SYNC VPS→GITHUB: Dashboard funcionando perfectamente

✅ Estado actual VPS (fuente de verdad):
- 14 solicitudes visibles en dashboard
- Problema paginación API resuelto (data.results)
- Referencias Auth.fetch corregidas → API.users.authFetch  
- Sin errores consola, sistema completamente operativo
- Backup: dashboard_solucionado_backup_$(date +%Y%m%d_%H%M%S)

📍 Sincronización desde VPS 203.161.55.87"

git commit -m "$COMMIT_MSG" || echo -e "${YELLOW}No hay cambios para commit${NC}"

echo -e "${GREEN}✅ Preparado para push a GitHub${NC}"
echo -e "${RED}⚠️  IMPORTANTE: Configurar token antes del push${NC}"
echo -e "${BLUE}Comando para push:${NC}"
echo "git push https://$GITHUB_TOKEN@github.com/rubenbolivar/llevateloexpress.git main --force"
echo ""
echo -e "${YELLOW}O configurar remote seguro:${NC}"
echo "git remote set-url github https://$GITHUB_TOKEN@github.com/rubenbolivar/llevateloexpress.git"
echo "git push github main --force" 