# Documentación de Migración a UTF8 - LlévateloExpress

**Fecha de migración:** 26 de Mayo de 2025  
**Realizada por:** Equipo de desarrollo  
**Base de datos:** PostgreSQL 12

## 📋 Resumen Ejecutivo

Se realizó exitosamente la migración de la base de datos de **LATIN1** a **UTF8** para garantizar el soporte completo de caracteres especiales del español (acentos, ñ, signos de interrogación/exclamación, etc.).

## 🔄 Proceso de Migración Realizado

### 1. **Preparación**
```bash
# Detener servicios
sudo systemctl stop llevateloexpress
sudo systemctl stop nginx
```

### 2. **Backup de la base de datos original**
```bash
cd /var/www/llevateloexpress
source backend_env/bin/activate
export $(grep -v '^#' .env.production | xargs)
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h $DB_HOST -d $DB_NAME > backups/backup_latin1_20250526_020443.sql
```

### 3. **Creación de nueva base de datos UTF8**
```bash
# Conectar con las credenciales de la aplicación
PGPASSWORD=llevateloexpress_pass psql -U llevateloexpress_user -h localhost -d postgres

# Dentro de psql:
CREATE DATABASE llevateloexpress_utf8 WITH ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE=template0;
\q
```

### 4. **Conversión y restauración de datos**
```bash
# Convertir el backup de LATIN1 a UTF8
iconv -f LATIN1 -t UTF8 backups/backup_latin1_20250526_020443.sql -o backups/backup_utf8.sql

# Restaurar en la nueva base de datos
PGPASSWORD=llevateloexpress_pass psql -U llevateloexpress_user -h localhost -d llevateloexpress_utf8 < backups/backup_utf8.sql
```

### 5. **Actualización de configuración**
```bash
# Backup de configuración
cp .env.production .env.production.backup_latin1

# Actualizar nombre de base de datos
sed -i 's/DB_NAME=llevateloexpress/DB_NAME=llevateloexpress_utf8/' .env.production
```

### 6. **Reinicio de servicios**
```bash
systemctl start llevateloexpress
systemctl start nginx
```

## 🗄️ Acceso a la Base de Datos

### Credenciales de Producción
```
Base de datos: llevateloexpress_utf8
Usuario: llevateloexpress_user
Contraseña: llevateloexpress_pass
Host: localhost
Puerto: 5432
Encoding: UTF8
```

### Métodos de Acceso

#### 1. **Desde la línea de comandos (psql)**
```bash
# Método 1: Con variable de entorno
PGPASSWORD=llevateloexpress_pass psql -U llevateloexpress_user -h localhost -d llevateloexpress_utf8

# Método 2: Interactivo (pedirá contraseña)
psql -U llevateloexpress_user -h localhost -d llevateloexpress_utf8
```

#### 2. **Desde Django Shell**
```bash
cd /var/www/llevateloexpress
source backend_env/bin/activate
python manage.py shell

# Dentro del shell:
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT version()")
print(cursor.fetchone())
```

#### 3. **Desde scripts Python**
```python
import psycopg2

conn = psycopg2.connect(
    dbname="llevateloexpress_utf8",
    user="llevateloexpress_user",
    password="llevateloexpress_pass",
    host="localhost",
    port="5432"
)
```

### Configuración de PostgreSQL

**Archivo de configuración de autenticación:**
```
/etc/postgresql/12/main/pg_hba.conf
```

**Configuración actual:**
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

## 📁 Archivos de Backup

### Ubicación de backups
```
/var/www/llevateloexpress/backups/
```

### Archivos creados durante la migración
- `backup_latin1_20250526_020443.sql` - Backup original en LATIN1
- `backup_latin1_20250526_020443.sql.gz` - Backup comprimido
- `backup_utf8.sql` - Backup convertido a UTF8
- `.env.production.backup_latin1` - Configuración anterior

## ✅ Verificaciones Post-Migración

### 1. **Verificar encoding de la base de datos**
```sql
SELECT datname, pg_encoding_to_char(encoding) 
FROM pg_database 
WHERE datname = 'llevateloexpress_utf8';
```

### 2. **Verificar datos migrados**
```bash
python manage.py shell -c "
from products.models import Product, Category
from financing.models import FinancingPlan
print(f'Categorías: {Category.objects.count()}')
print(f'Productos: {Product.objects.count()}')
print(f'Planes: {FinancingPlan.objects.count()}')
"
```

### 3. **Probar caracteres especiales**
```sql
-- En psql
SELECT name FROM products_product WHERE name LIKE '%ñ%' OR name LIKE '%á%';
```

## 🚨 Procedimiento de Rollback (si fuera necesario)

En caso de necesitar volver a la base de datos anterior:

```bash
# 1. Detener servicios
sudo systemctl stop llevateloexpress

# 2. Restaurar configuración
cp .env.production.backup_latin1 .env.production

# 3. Reiniciar servicios
sudo systemctl start llevateloexpress
```

## 📝 Notas Importantes

1. **Encoding UTF8**: La base de datos ahora soporta todos los caracteres Unicode, incluyendo:
   - Acentos: á, é, í, ó, ú, Á, É, Í, Ó, Ú
   - Letra ñ/Ñ
   - Signos: ¿? ¡!
   - Emojis y símbolos especiales

2. **Sistema de Notificaciones**: Verificado y funcionando correctamente con UTF8

3. **APIs**: Todas las respuestas JSON ahora manejan correctamente caracteres especiales

4. **Backups futuros**: Todos los backups nuevos serán en UTF8

## 🔧 Scripts Útiles

### Script de backup automatizado
```bash
/var/www/llevateloexpress/scripts/backup_db.sh
```

### Script de prueba de notificaciones
```bash
python scripts/test_notifications_utf8.py
```

## 📞 Soporte

En caso de problemas con la base de datos:
1. Verificar logs: `/var/log/postgresql/postgresql-12-main.log`
2. Verificar conexión: `pg_isready -h localhost -p 5432`
3. Verificar servicios: `systemctl status postgresql`

---

**Última actualización:** 26 de Mayo de 2025 