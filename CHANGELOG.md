# Changelog - LlévateloExpress

Todos los cambios notables de este proyecto serán documentados en este archivo.

## [1.2.0] - 2025-10-18

### ✨ Agregado
- **Nuevo Plan de Financiamiento: CrediLlevo X 4**
  - Plan express de 4 meses (inicial + 4 cuotas mensuales)
  - Sin intereses, con precios en LLEVO
  - Entrega inmediata
  - ID de plan en base de datos: 11

#### Backend
- Campo `financing_plan` en modelo Product (ForeignKey a FinancingPlan)
- Método `get_financing_details()` en modelo Product para cálculos dinámicos
- Migración 0007: Agregado campo financing_plan
- Migración 0008: Asignación de plan default a 30 productos existentes
- Badges de colores en Django Admin para distinguir planes visualmente
- Filtro por plan de financiamiento en lista de productos (admin)
- Preview dinámico de financiamiento en admin con cálculos por plan
- Campos en serializers: `financing_plan_name`, `financing_plan_slug`, `financing_term_months`
- Método `get_financing_details()` en ProductDetailSerializer

#### Frontend
- **calculadora-credillevo.js**:
  - Sistema dinámico de lectura de planes desde API
  - Actualización automática de textos UI según plan seleccionado
  - Cálculos dinámicos basados en term_months del plan
  - Método `updatePlanTexts()` para sincronización de UI
- **calculadora.html**:
  - IDs dinámicos para elementos de texto del plan
  - Soporte para mostrar 4 o 24 meses según producto
- **planes.html**:
  - Diseño de dos columnas mostrando ambos planes
  - Tabla comparativa de características
  - Ticker actualizado con información de ambos planes
  - Eliminadas referencias a tasas de interés
- **index.html**:
  - Hero banner con ambos planes lado a lado
  - Ticker actualizado para mostrar ambos planes
  - Navegación actualizada a "Planes CrediLlevo"

### 🔄 Modificado
- Textos de "24 meses fijo" a dinámicos según plan
- Navegación de "CrediLlevo Inmediato" a "Planes CrediLlevo"
- Sistema de cálculo de cuotas ahora usa plazo dinámico
- Admin preview ahora muestra información específica del plan asignado

### 🗑️ Eliminado
- Referencias a "0% de interés" y "tasa de interés" en toda la UI
- Texto estático "sin intereses" en descripciones
- Tarjeta de "0% de Interés" de la sección de características en planes.html

### 🎨 Diseño
- **Código de colores**:
  - CrediLlevo Inmediato: Azul (#007bff)
  - CrediLlevo X 4: Verde (#28a745)
- Badges con colores distintivos en Django Admin
- Diseño responsive de dos columnas en planes.html
- Tarjetas compactas en hero banner del home

### 📊 Base de Datos
- 30 productos migrados con plan "CrediLlevo Inmediato" como default
- 2 planes activos en sistema (IDs: 10 y 11)

### 🔧 Técnico
- Relación `on_delete=PROTECT` para evitar eliminación accidental de planes
- Serialización optimizada con campos calculados
- Validación de datos de financiamiento en modelo
- Sistema de dataset HTML5 para almacenar info de planes

### 📝 Documentación
- Actualizado CLAUDE.md con información de planes
- Creado CHANGELOG.md (este archivo)
- Backup completo en `backups/credillevo_x4_complete_20251018/`
- README detallado en carpeta de backup

### 🧪 Testing
- ✅ Verificado badges en admin
- ✅ Verificado filtros por plan
- ✅ Verificado cálculos dinámicos en calculadora
- ✅ Verificado actualización de textos UI
- ✅ Verificado respuesta API con nuevos campos
- ✅ Verificado despliegue en producción

---

## [1.1.0] - 2025-06-30

### Agregado
- Sistema de pagos R4 integrado
- Dashboard de usuario con historial de pagos
- Calculadora de financiamiento CrediLlevo
- Sistema LLEVO completo con cotización en tiempo real

### Modificado
- Optimización de rendimiento del catálogo
- Mejoras en sistema de autenticación
- Actualización de información de contacto

---

## [1.0.0] - 2024-01-15

### Agregado
- Lanzamiento inicial de LlévateloExpress
- Sistema de catálogo de productos
- Plan de financiamiento CrediLlevo Inmediato (24 meses)
- Autenticación de usuarios con JWT
- Django Admin para gestión de productos
- Frontend con Bootstrap 5 y JavaScript vanilla
- Sistema de tokens LLEVO
- Integración con Soloson y R4

---

**Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/)**
