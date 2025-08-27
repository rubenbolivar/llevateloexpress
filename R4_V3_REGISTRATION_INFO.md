# 🚀 R4 CONECTA V3.0 - INFORMACIÓN PARA REGISTRO

## 📋 DATOS PARA ENVIAR AL EQUIPO R4

### 🔗 URLs de Webhooks (V3.0)
R4consulta: https://llevateloexpress.com/api/payments/webhooks/r4/consulta/
R4notifica: https://llevateloexpress.com/api/payments/webhooks/r4/notifica/

### 🔑 Token UUID de Autorización
39f97f26-b0cb-4527-a9a4-7d9acd1b0881

### 📝 Especificaciones Técnicas

#### ✅ Certificado TLS
- Protocolo: TLS 1.3
- Dominio: llevateloexpress.com
- Emisor: Lets Encrypt (R10)
- Validez: Sep 2025

#### ✅ Webhook R4consulta (Fase 1)
- Método: POST
- Content-Type: application/json
- Validación IP: 45.175.213.98, 200.74.203.91, 190.202.123.66
- Campos esperados:
  - IdCliente (requerido) - String - 8 numérico
  - TelefonoComercio (requerido) - String - 11 numérico  
  - Monto (opcional) - String - máximo 8 números y 2 decimales
- Respuesta éxito: {status: true}
- Respuesta rechazo: {status: false}

#### ✅ Webhook R4notifica (Fase 2)
- Método: POST
- Content-Type: application/json
- Validación IP: 45.175.213.98, 200.74.203.91, 190.202.123.66
- Campos esperados según V3.0:
  - IdComercio (requerido) - String - 8 numérico
  - TelefonoComercio (requerido) - String - 11 numérico
  - TelefonoEmisor (requerido) - String - 11 numérico
  - BancoEmisor (requerido) - String - 3 numérico
  - Monto (requerido) - String con decimales
  - FechaHora (requerido) - String
  - Referencia (requerido) - String
  - CodigoRed (requerido) - String
  - Concepto (opcional) - String - 30 alfanumérico
- Respuesta éxito: {abono: true}
- Respuesta rechazo: {abono: false}

### 🧪 Estado de Pruebas

#### ✅ Pruebas Internas Realizadas
- [x] Configuración Django sin errores
- [x] Servicios activos (Django + Nginx)
- [x] Endpoints respondiendo correctamente
- [x] Validación de IPs funcionando
- [x] Parseo JSON según especificaciones V3.0
- [x] Logging de eventos implementado

#### 🔄 Pendiente con R4
- [ ] Registro de URLs en sistema R4
- [ ] Configuración de Token UUID
- [ ] Pruebas controladas desde IPs oficiales
- [ ] Validación de flujo completo Pago móvil conciliado

### 📞 Contacto Técnico
- Servidor: 203.161.55.87
- Dominio: llevateloexpress.com
- Monitoreo: /var/log/llevateloexpress/
- Admin: https://llevateloexpress.com/admin/

---
WEBHOOKS R4 V3.0 LISTOS PARA PRUEBAS CONTROLADAS
