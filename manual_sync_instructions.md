# INSTRUCCIONES DE SINCRONIZACIÓN MANUAL - V2 FINAL DEFINITIVA

## 🎯 OBJETIVO
Aplicar la versión que soluciona el error: `FinancingRequestV2.nextStep is not a function`

## 📁 ARCHIVO A SUBIR
- **Origen**: `solicitud-financiamiento-v2-final-fixed.js` (34KB)
- **Destino VPS**: `/var/www/llevateloexpress/js/solicitud-financiamiento-v2-part2.js`

## 🔧 MÉTODOS DE SINCRONIZACIÓN

### MÉTODO 1: SCP (Terminal)
```bash
scp solicitud-financiamiento-v2-final-fixed.js llevateloexpress@server1.llevateloexpress.com:/var/www/llevateloexpress/js/solicitud-financiamiento-v2-part2.js
```

### MÉTODO 2: Panel de Control
1. Acceder al panel de control del VPS
2. Ir a File Manager
3. Navegar a `/var/www/llevateloexpress/js/`
4. Subir `solicitud-financiamiento-v2-final-fixed.js`
5. Renombrar a `solicitud-financiamiento-v2-part2.js`

### MÉTODO 3: FTP/SFTP
```bash
sftp llevateloexpress@server1.llevateloexpress.com
cd /var/www/llevateloexpress/js/
put solicitud-financiamiento-v2-final-fixed.js solicitud-financiamiento-v2-part2.js
exit
```

## ✅ VERIFICACIÓN POST-SINCRONIZACIÓN

### 1. Verificar archivo en VPS
```bash
ssh llevateloexpress@server1.llevateloexpress.com "ls -la /var/www/llevateloexpress/js/solicitud-financiamiento-v2-part2.js"
```

### 2. Verificar contenido
```bash
ssh llevateloexpress@server1.llevateloexpress.com "head -n 10 /var/www/llevateloexpress/js/solicitud-financiamiento-v2-part2.js"
```

Debería mostrar:
```javascript
/**
 * SOLICITUD DE FINANCIAMIENTO V2 - VERSIÓN FINAL DEFINITIVA
 * Compatible con llamadas directas desde HTML y funciones globales
 */
```

### 3. Configurar permisos
```bash
ssh llevateloexpress@server1.llevateloexpress.com "
    cd /var/www/llevateloexpress &&
    chown llevateloexpress:www-data js/solicitud-financiamiento-v2-part2.js &&
    chmod 644 js/solicitud-financiamiento-v2-part2.js
"
```

## 🧪 PRUEBA DE FUNCIONAMIENTO

Después de la sincronización, recargar la página:
https://llevateloexpress.com/solicitud-financiamiento.html?mode=credito&calculation=[...]

### Logs esperados:
```
🎯 FinancingRequestV2 - Versión Final Definitiva inicializada correctamente
[...] [FinancingRequestV2-Definitiva] [INFO] Métodos expuestos globalmente con compatibilidad total
```

### Prueba de navegación:
1. Hacer clic en "Continuar" - NO debería dar error
2. Verificar que navega al paso 2
3. Hacer clic en "Anterior" - debería volver al paso 1

## 🎯 LO QUE RESUELVE ESTA VERSIÓN

✅ **ERROR PRINCIPAL**: `FinancingRequestV2.nextStep is not a function`
✅ **COMPATIBILIDAD**: Funciona con llamadas directas desde HTML
✅ **NAVEGACIÓN**: Botones Continuar/Anterior funcionan correctamente
✅ **DATOS**: Parseo correcto desde calculadora (ya funcionaba)
✅ **RENDERIZADO**: Valores mostrados correctamente (ya funcionaba)

## 🚨 DIFERENCIAS CLAVE

**ANTES** (versión actual en VPS):
```javascript
// Sólo funciones globales
window.nextStep = () => this.nextStep();
```

**DESPUÉS** (versión definitiva):
```javascript
// Compatibilidad total
window.FinancingRequestV2 = this;
FinancingRequestV2.nextStep = () => this.nextStep();  // ← ESTO ES LO NUEVO
```

## 📞 CONFIRMACIÓN DE ÉXITO

Una vez aplicado, deberías ver:
- ✅ Navegación funcional entre pasos
- ✅ No más errores en consola al hacer clic en "Continuar"
- ✅ Log: "FinancingRequestV2-Definitiva" en lugar de "FinancingRequestV2-Final" 