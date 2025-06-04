# Flujo de Trabajo Git para LlévateloExpress

## Buenas Prácticas de Commit

Para mantener un historial de cambios claro y útil, seguiremos estas prácticas:

1. **Commit frecuente**: Realizar un commit por cada cambio significativo o conjunto de cambios relacionados.

2. **Mensajes descriptivos**: Usar mensajes claros que expliquen QUÉ se cambió y POR QUÉ.

3. **Estructura de mensajes**:
   - Primera línea: Resumen breve (máx. 50 caracteres)
   - Líneas siguientes: Descripción detallada (si es necesario)

4. **Prefijos para los mensajes**:
   - `feat`: Nueva funcionalidad
   - `fix`: Corrección de errores
   - `docs`: Cambios en documentación
   - `style`: Cambios que no afectan el significado del código (formato, espacios en blanco)
   - `refactor`: Cambios de código que no corrigen errores ni añaden funcionalidades
   - `perf`: Cambios que mejoran el rendimiento
   - `test`: Adición de pruebas faltantes o corrección de pruebas existentes
   - `chore`: Cambios en el proceso de construcción o herramientas auxiliares

## Ejemplos de buenos commits:

```
feat: Añadir calculadora de financiamiento en la página de detalle

fix: Corregir enlaces rotos en la página Nosotros

docs: Actualizar README con instrucciones de despliegue

refactor: Reorganizar código JavaScript para mejor mantenibilidad
```

## Flujo de Ramas

Para nuevas características:
1. Crear una nueva rama: `git checkout -b feature/nombre-caracteristica`
2. Realizar commits en esa rama
3. Cuando esté lista, fusionar con main: `git checkout main && git merge feature/nombre-caracteristica`

## Antes de cada Despliegue:

1. Verificar que todos los cambios estén en commit: `git status`
2. Ejecutar pruebas (cuando estén implementadas)
3. Realizar commit con mensaje descriptivo: `git commit -m "feat: Descripción del cambio"`
4. Desplegar con el script: `./deploy.sh`

Recuerda: Un buen historial de Git es invaluable para el seguimiento y la colaboración en el proyecto.
