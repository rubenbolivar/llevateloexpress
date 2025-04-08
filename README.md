# LlévateloExpress - Plataforma de Financiamiento

Aplicación web para LlévateloExpress.com, una plataforma para financiamiento y adquisición de vehículos, motocicletas, camiones, maquinaria agrícola y equipos industriales en Venezuela.

## Características Principales

- **Catálogo de Productos**: Amplia variedad de vehículos, motocicletas, camiones, maquinaria agrícola y equipos industriales disponibles para financiamiento.
- **Planes de Financiamiento**: Diferentes opciones adaptadas a las necesidades de cada cliente (Plan 50-50, Plan 70-30, Plan Agrícola).
- **Calculadora Interactiva**: Permite al usuario simular diferentes escenarios de financiamiento y ver las cuotas resultantes con tabla de amortización.
- **Registro de Clientes**: Sistema seguro para recolectar información de los potenciales clientes interesados en adquirir un producto.
- **Formulario de Contacto**: Integrado con WhatsApp para comunicación directa con los asesores.
- **Diseño Responsive**: Experiencia de usuario optimizada para dispositivos móviles, tablets y escritorio.
- **Despliegue Automatizado**: Script de despliegue para configuración rápida del servidor de producción.
- **Preparado para Integración con Django**: Estructura de datos diseñada para futuro backend con Django.

## Tecnologías Utilizadas

- HTML5 y CSS3 para estructuración y estilización
- JavaScript (ES6+) para funcionalidades dinámicas
- Bootstrap 5 como framework de UI
- Font Awesome para iconografía
- Servidor Nginx con configuración optimizada
- Certificados SSL vía Let's Encrypt
- API de WhatsApp para formulario de contacto
- Optimización de rendimiento para producción

## Estructura del Proyecto

```
/
├── index.html              # Página principal con catálogo
├── catalogo.html           # Catálogo completo de productos
├── detalle-producto.html   # Vista detallada de productos
├── registro.html           # Formulario de registro de clientes
├── planes.html             # Información sobre planes de financiamiento
├── calculadora.html        # Calculadora interactiva de financiamiento
├── nosotros.html           # Información sobre la empresa
├── contacto.html           # Formulario de contacto con integración WhatsApp
├── css/
│   └── styles.css          # Estilos personalizados
├── js/
│   ├── main.js             # Funcionalidades comunes
│   ├── models.js           # Modelos y estructuras para integración con Django
│   ├── products.js         # Datos y funciones del catálogo
│   ├── calculadora.js      # Lógica de la calculadora
│   ├── planes.js           # Funcionalidades página de planes
│   └── registro.js         # Validación del formulario
├── img/
│   ├── logos/              # Logos e identidad visual
│   ├── products/           # Imágenes de productos
│   └── banners/            # Banners promocionales
└── deploy.sh               # Script de despliegue automatizado
```

## Categorías de Productos

El sistema incluye las siguientes categorías de productos, cada una con su estructura de datos optimizada:

1. **Motocicletas**: Modelos de diferentes cilindradas y estilos, desde económicas hasta deportivas.
2. **Vehículos**: Automóviles, camionetas y vehículos de pasajeros.
3. **Camiones**: Unidades de carga, transporte y distribución de diferentes capacidades.
4. **Maquinaria Agrícola**: Tractores y equipos para optimizar la producción agrícola.
5. **Maquinaria y Equipos**: Equipamiento especializado para la industria y el comercio.

Cada categoría está modelada para permitir filtrado, búsqueda y presentación específica acorde a sus características particulares.

## Páginas del Sitio

### Página Principal (index.html)
Muestra el catálogo de productos destacados, categorías principales y acceso rápido a la calculadora de financiamiento.

### Catálogo (catalogo.html)
Listado completo de productos disponibles para financiamiento, con filtros por categoría, marca y precio.

### Detalle de Producto (detalle-producto.html)
Vista detallada de cada producto con especificaciones técnicas, imágenes y opciones de financiamiento.

### Registro de Clientes (registro.html)
Formulario para recolectar información de clientes interesados, con validación en tiempo real y feedback visual sobre la fortaleza de la contraseña.

### Planes de Financiamiento (planes.html)
Detalla las opciones de financiamiento disponibles, con una tabla comparativa, beneficios y requisitos.

### Calculadora de Financiamiento (calculadora.html)
Herramienta interactiva para simular diferentes escenarios de financiamiento, permitiendo ajustar monto, inicial y plazo, mostrando resultados detallados incluyendo tabla de amortización.

### Sobre Nosotros (nosotros.html)
Información sobre la empresa, misión, visión y valores, así como equipo y trayectoria.

### Contacto (contacto.html)
Formulario de contacto con integración directa a WhatsApp, información de ubicación y preguntas frecuentes.

## Integración con Django (Plan Futuro)

El proyecto está estructurado para facilitar la migración a un backend Django:

### Modelos y Estructura

- Se ha creado un archivo `js/models.js` que define la estructura de datos para los modelos de Django.
- Las categorías de productos están definidas siguiendo el patrón de modelos Django con:
  - Identificadores únicos (id)
  - Slugs para URLs amigables
  - Nombres legibles para usuarios
  - Descripciones e iconos
- La estructura de productos incluye metadatos para las relaciones y campos necesarios

### Pasos para Migración a Django

1. Crear los modelos Django basados en la estructura definida en `models.js`
2. Implementar API REST para consumo de datos
3. Adaptar el frontend para consumir datos de la API
4. Implementar panel administrativo para gestión de productos

## Despliegue a Producción

El proyecto incluye un script `deploy.sh` que automatiza:

1. Configuración de servidor Nginx
2. Transferencia de archivos al servidor
3. Configuración de permisos
4. Implementación de HTTPS con Let's Encrypt
5. Optimización para producción

### Requisitos para Despliegue

- Servidor con Ubuntu/Debian
- Acceso SSH con privilegios de administrador
- Dominio configurado apuntando al servidor
- Puertos 80 y 443 abiertos

### Instrucciones de Despliegue

1. Configurar las variables del servidor en `deploy.sh`:
   - SERVER_IP
   - USERNAME
   - PASSWORD
   - DOMAIN
   - EMAIL

2. Ejecutar el script de despliegue:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## Mantenimiento

### Actualización de Productos
Para actualizar el catálogo de productos, edite el archivo `js/products.js` siguiendo el formato establecido.

### Actualización de Categorías
Para añadir nuevas categorías o modificar las existentes, edite el archivo `js/models.js` y actualice el arreglo `PRODUCT_CATEGORIES`.

### Cambios en la Interfaz
Los estilos personalizados se encuentran en `css/styles.css`. Para modificaciones mayores, considere editar los archivos HTML correspondientes.

## Contacto y Soporte

Para consultas técnicas o soporte relacionado con la implementación:
- Email: soporte@llevateloexpress.com
- Teléfono: (0212) 555-1234
- WhatsApp: +584121010744

## Desarrollado por

LlévateloExpress © 2023-2024 - Todos los derechos reservados 