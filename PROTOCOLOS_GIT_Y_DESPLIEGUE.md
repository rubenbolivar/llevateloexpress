# Protocolos de Gestión de Repositorio y Despliegue para LlévateloExpress

Este documento describe los procedimientos estándar para la gestión del código fuente y el despliegue del sitio web LlévateloExpress.com.

## Tabla de Contenidos

1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Gestión del Repositorio Git](#gestión-del-repositorio-git)
3. [Flujo de Trabajo para Cambios](#flujo-de-trabajo-para-cambios)
4. [Procedimiento de Despliegue](#procedimiento-de-despliegue)
5. [Gestión de Archivos Estáticos](#gestión-de-archivos-estáticos)
6. [Solución de Problemas Comunes](#solución-de-problemas-comunes)

## Estructura del Proyecto

El proyecto LlévateloExpress tiene la siguiente estructura principal:

```
/
├── css/                    # Estilos CSS del frontend
├── js/                     # Scripts JavaScript del frontend
├── img/                    # Imágenes y recursos visuales
│   ├── banners/            # Imágenes de banners y logos
│   ├── products/           # Imágenes de productos
│   └── partners/           # Logos de marcas y aliados
├── templates/              # Plantillas HTML para Django
├── static/                 # Archivos estáticos para Django
├── media/                  # Archivos subidos por usuarios
├── llevateloexpress_backend/ # Configuración principal de Django
├── products/               # App de Django para gestión de productos
├── financing/              # App de Django para financiamiento
├── users/                  # App de Django para gestión de usuarios
├── core/                   # Funcionalidades centrales
├── scripts/                # Scripts de utilidad y despliegue
├── *.html                  # Archivos HTML del frontend
├── README.md               # Documentación general
├── requirements.txt        # Dependencias de Python
└── llevateloexpress_nginx.conf # Configuración de Nginx
```

## Gestión del Repositorio Git

### Configuración del Repositorio

El proyecto utiliza Git para el control de versiones. Hay dos repositorios principales:

1. **Repositorio Local**: En la máquina del desarrollador
2. **Repositorio Remoto**: En el servidor de producción (VPS)

El repositorio remoto se considera la fuente de verdad, ya que refleja lo que está actualmente en producción.

### Configuración Inicial

Para configurar un nuevo entorno de desarrollo:

```bash
# Clonar el repositorio del servidor (asumiendo que tienes acceso SSH)
git clone ssh://root@203.161.55.87/var/www/llevateloexpress

# Configurar tu información de usuario
git config user.name "Tu Nombre"
git config user.email "tu.email@example.com"
```

## Flujo de Trabajo para Cambios

### Principio Fundamental

> **El servidor de producción siempre tiene prioridad.**

Esto significa que cualquier cambio local debe sincronizarse primero con el servidor antes de comenzar a trabajar, y el estado final del repositorio local debe reflejar exactamente el estado del servidor de producción.

### Antes de Comenzar Cualquier Cambio

1. Obtener los cambios más recientes del servidor:

```bash
git fetch origin
git reset --hard origin/main
```

Esto asegura que estás comenzando desde el estado actual del servidor de producción.

### Para Cambios Pequeños y Rápidos

1. Edita los archivos localmente
2. Sube los archivos al servidor:
   ```bash
   scp archivo.extensión root@203.161.55.87:/var/www/llevateloexpress/
   ```
3. Haz commit en el servidor:
   ```bash
   ssh root@203.161.55.87 "cd /var/www/llevateloexpress && git add archivo.extensión && git commit -m 'descripción del cambio'"
   ```
4. Sincroniza tu repositorio local:
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```

### Para Cambios Complejos

1. Sincroniza tu repositorio local con el servidor:
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```

2. Crea una rama local para tus cambios:
   ```bash
   git checkout -b feature/nombre-funcionalidad
   ```

3. Realiza y prueba tus cambios localmente

4. Una vez satisfecho, aplica los cambios en producción:
   ```bash
   # Transfiere archivos modificados al servidor
   scp archivo1 archivo2 directorio/* root@203.161.55.87:/var/www/llevateloexpress/

   # Haz commit en el servidor
   ssh root@203.161.55.87 "cd /var/www/llevateloexpress && git add . && git commit -m 'descripción del cambio'"
   
   # Sincroniza tu repositorio local
   git fetch origin
   git reset --hard origin/main
   ```

5. Limpia tus ramas locales:
   ```bash
   git branch -D feature/nombre-funcionalidad
   ```

### Convenciones para Mensajes de Commit

Usar prefijos que indiquen el tipo de cambio:

- `feat:` Nueva funcionalidad
- `fix:` Corrección de errores
- `style:` Cambios de estilo o formato
- `refactor:` Refactorización de código
- `docs:` Documentación
- `perf:` Mejoras de rendimiento
- `test:` Adición o corrección de pruebas

Ejemplo: `feat: Agregar carrusel de marcas oficiales en home`

## Procedimiento de Despliegue

### Requisitos

- Acceso SSH al servidor (root@203.161.55.87)
- Certificados SSL configurados en el servidor
- Cuenta con permisos suficientes para reiniciar servicios

### Despliegue de Cambios Frontend

1. Transfiere los archivos modificados al servidor:
   ```bash
   scp -r archivos/* root@203.161.55.87:/var/www/llevateloexpress/
   ```

2. Asegúrate de que los permisos son correctos:
   ```bash
   ssh root@203.161.55.87 "chmod 644 /var/www/llevateloexpress/*.html /var/www/llevateloexpress/css/*.css /var/www/llevateloexpress/js/*.js"
   ```

3. Haz commit de los cambios en el servidor:
   ```bash
   ssh root@203.161.55.87 "cd /var/www/llevateloexpress && git add . && git commit -m 'descripción del cambio'"
   ```

4. Recarga Nginx (solo si es necesario):
   ```bash
   ssh root@203.161.55.87 "systemctl reload nginx"
   ```

### Despliegue de Cambios Backend (Django)

1. Transfiere los archivos modificados:
   ```bash
   scp -r archivos_python/* root@203.161.55.87:/var/www/llevateloexpress/
   ```

2. Aplica migraciones y recolecta archivos estáticos:
   ```bash
   ssh root@203.161.55.87 "cd /var/www/llevateloexpress && source backend_env/bin/activate && python manage.py migrate && python manage.py collectstatic --noinput"
   ```

3. Haz commit de los cambios:
   ```bash
   ssh root@203.161.55.87 "cd /var/www/llevateloexpress && git add . && git commit -m 'descripción del cambio'"
   ```

4. Reinicia el servicio Django:
   ```bash
   ssh root@203.161.55.87 "systemctl restart llevateloexpress"
   ```

### Despliegue Completo (Grandes Actualizaciones)

Para actualizaciones mayores que requieren reinicio completo:

```bash
# Transferir todos los archivos
scp -r * root@203.161.55.87:/tmp/llevateloexpress-update/

# Ejecutar script de despliegue
ssh root@203.161.55.87 "cd /var/www/llevateloexpress && ./scripts/deploy_full.sh /tmp/llevateloexpress-update"
```

## Gestión de Archivos Estáticos

### Imágenes y Recursos Visuales

1. Las imágenes deben estar en formato optimizado (JPG/PNG con compresión)
2. Colocar en la carpeta correspondiente:
   - Imágenes de productos: `img/products/`
   - Banners y logos: `img/banners/`
   - Logos de partners: `img/partners/`

3. Asegurarse de que tengan los permisos correctos:
   ```bash
   chmod 644 img/*/*.jpg img/*/*.png
   ```

### CSS y JavaScript

1. Los archivos CSS van en la carpeta `css/`
2. Los archivos JavaScript van en la carpeta `js/`
3. Para actualizar:
   ```bash
   scp css/styles.css root@203.161.55.87:/var/www/llevateloexpress/css/
   scp js/main.js root@203.161.55.87:/var/www/llevateloexpress/js/
   ```

## Solución de Problemas Comunes

### Problema: Los cambios no se ven reflejados en el sitio

1. Verificar que los archivos se han transferido correctamente:
   ```bash
   ssh root@203.161.55.87 "ls -la /var/www/llevateloexpress/archivo_modificado"
   ```

2. Limpiar la caché del navegador con Ctrl+F5 o Cmd+Shift+R

3. Verificar permisos de archivos:
   ```bash
   ssh root@203.161.55.87 "ls -la /var/www/llevateloexpress/archivo_modificado"
   ```

4. Recargar Nginx:
   ```bash
   ssh root@203.161.55.87 "systemctl reload nginx"
   ```

### Problema: Errores en el Backend Django

1. Revisar los logs:
   ```bash
   ssh root@203.161.55.87 "tail -n 100 /var/log/llevateloexpress/error.log"
   ```

2. Verificar estado del servicio:
   ```bash
   ssh root@203.161.55.87 "systemctl status llevateloexpress"
   ```

3. Reiniciar el servicio Django:
   ```bash
   ssh root@203.161.55.87 "systemctl restart llevateloexpress"
   ```

### Problema: Conflictos en Git

Si encuentras errores al sincronizar o hacer push al servidor:

1. Guardar tus cambios locales:
   ```bash
   git stash
   ```

2. Actualizar desde el servidor:
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```

3. Aplicar tus cambios de nuevo:
   ```bash
   git stash pop
   ```

4. Resolver conflictos manualmente y repetir el proceso de despliegue

---

**Nota importante:** Siempre hacer una copia de seguridad antes de realizar cambios significativos en el servidor de producción. Para esto:

```bash
ssh root@203.161.55.87 "cd /var/www && tar -czf llevateloexpress-backup-$(date +%Y%m%d).tar.gz llevateloexpress"
```

Este documento debe actualizarse regularmente para reflejar cualquier cambio en los procesos de gestión y despliegue del proyecto.

Última actualización: Abril 2025 