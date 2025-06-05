# 📋 MÉTODO DE CARGA DE PRODUCTOS - LlévateloExpress

## 🎯 **OBJETIVO**
Documentar el método exitoso para agregar motocicletas y productos al sistema LlévateloExpress usando Django Shell en el VPS de producción.

---

## 🚀 **MÉTODO EXITOSO VALIDADO**

### **Comando Base Funcional**
```bash
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"[CÓDIGO_PYTHON]\" | python manage.py shell'"
```

### **Estructura de Conexión**
- **Usuario SSH**: `root@llevateloexpress.com`
- **Usuario Django**: `llevateloexpress` (via sudo -u)
- **Directorio**: `/var/www/llevateloexpress`
- **Entorno virtual**: `backend_env/bin/activate`
- **Método ejecución**: Django shell con pipe

---

## 📊 **FORMATO DE DATOS REQUERIDO**

### **1. Campos Obligatorios del Modelo Product**
```python
name           # Nombre del producto (único)
category       # FK a Category (id="motocicletas")
brand          # Marca del producto
price          # Precio en USD (float)
description    # Descripción del producto
image          # Ruta de imagen (USAR: "products/default.jpg")
features       # JSON string con lista de características
specs_general  # JSON string con especificaciones generales
specs_engine   # JSON string con especificaciones de motor
specs_comfort  # JSON string con especificaciones de confort
specs_safety   # JSON string con especificaciones de seguridad
stock          # Stock disponible (int)
featured       # Producto destacado (boolean)
```

### **2. Formato Correcto de Especificaciones**
Las especificaciones deben guardarse como JSON string con formato label/value:

```json
[
  {"label": "Cilindrada", "value": "999.8 cc"},
  {"label": "Potencia máxima", "value": "199+ HP @ 13,200 rpm"},
  {"label": "Velocidad máxima", "value": "299+ km/h"}
]
```

**❌ FORMATO INCORRECTO:**
```json
{
  "Cilindrada": "999.8 cc",
  "Potencia máxima": "199+ HP @ 13,200 rpm"
}
```

---

## 🛠️ **COMANDOS EXITOSOS VALIDADOS**

### **1. Comando Completo para Producto Simple**
```bash
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"from products.models import Product, Category; import json; category = Category.objects.get(id=\\\"motocicletas\\\"); product, created = Product.objects.update_or_create(name=\\\"NOMBRE_PRODUCTO\\\", defaults={\\\"category\\\": category, \\\"brand\\\": \\\"MARCA\\\", \\\"price\\\": PRECIO, \\\"description\\\": \\\"DESCRIPCION\\\", \\\"image\\\": \\\"products/default.jpg\\\", \\\"features\\\": \\\"[]\\\", \\\"specs_general\\\": \\\"[]\\\", \\\"specs_engine\\\": \\\"[]\\\", \\\"specs_comfort\\\": \\\"[]\\\", \\\"specs_safety\\\": \\\"[]\\\", \\\"stock\\\": STOCK, \\\"featured\\\": DESTACADO}); print(\\\"✅ Creado:\\\", created, \\\"- Producto:\\\", product.name, \\\"- Precio: \$\\\", product.price)\" | python manage.py shell'"
```

### **2. Comando para Verificar Productos**
```bash
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"from products.models import Product; products = Product.objects.filter(brand=\\\"MARCA\\\"); print(\\\"Productos MARCA:\\\", products.count()); [print(p.name, p.price, p.stock) for p in products]\" | python manage.py shell'"
```

### **3. Comando para Corregir Especificaciones**
```bash
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"from products.models import Product; import json; producto = Product.objects.get(name=\\\"NOMBRE_PRODUCTO\\\"); producto.specs_general = json.dumps([{\\\"label\\\": \\\"ETIQUETA\\\", \\\"value\\\": \\\"VALOR\\\"}], ensure_ascii=False); producto.save(); print(\\\"✅ Especificaciones corregidas\\\")\" | python manage.py shell'"
```

---

## ⚠️ **ERRORES COMUNES Y SOLUCIONES**

### **Error 1: Problema con Comillas Anidadas**
**Síntoma:**
```
bash: -c: line 0: syntax error near unexpected token `)'
```

**Solución:**
- Usar triple escape para comillas dentro del JSON: `\\\"`
- Verificar balance de comillas en todo el comando
- Mantener consistencia en el escape de caracteres

### **Error 2: Especificaciones No Se Muestran**
**Síntoma:**
- Producto se crea pero especificaciones aparecen vacías
- Errores RENDER_SPECS en consola del navegador

**Causa:**
```python
# ❌ INCORRECTO - formato diccionario
specs_general = '{"Cilindrada": "999.8 cc"}'

# ✅ CORRECTO - formato label/value array
specs_general = '[{"label": "Cilindrada", "value": "999.8 cc"}]'
```

**Solución:**
Usar el comando de corrección de especificaciones mostrado arriba.

### **Error 3: Campo features null no permitido**
**Síntoma:**
```
IntegrityError: NOT NULL constraint failed: products_product.features
```

**Solución:**
Siempre inicializar campos JSON como string vacío:
```python
"features": "[]",
"specs_general": "[]",
"specs_engine": "[]",
"specs_comfort": "[]", 
"specs_safety": "[]"
```

### **Error 4: Categoría no encontrada**
**Síntoma:**
```
Category.DoesNotExist: Category matching query does not exist
```

**Solución:**
Verificar que existe la categoría "motocicletas":
```bash
echo "from products.models import Category; print(Category.objects.all())" | python manage.py shell
```

### **Error 5: SSH pide contraseña**
**Síntoma:**
```
llevateloexpress@203.161.55.87's password:
```

**Causa:**
- Intentar conectar como usuario `llevateloexpress` directamente
- No usar el usuario `root` correcto

**Solución:**
- Siempre usar `ssh root@llevateloexpress.com`
- No usar `ssh llevateloexpress@llevateloexpress.com`

### **Error 6: Errores 404 en imágenes (Temblor de página)**
**Síntoma:**
- Consola del navegador muestra errores 404 para imágenes de productos
- La página "tiembla" o se comporta de manera errática
- Bucles de carga infinitos

**Causa:**
- Productos con rutas de imágenes que no existen físicamente
- Nombres de imagen específicos antes de cargar imagen real

**Solución:**
- **SIEMPRE usar `"products/default.jpg"` como imagen inicial**
- La imagen default.jpg existe y previene errores 404
- Cambiar imagen específica después vía Django admin

---

## 📝 **PLANTILLAS DE COMANDOS**

### **Plantilla 1: Producto Simple**
```bash
# Reemplazar: NOMBRE, MARCA, PRECIO, DESCRIPCION, STOCK, true/false
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"from products.models import Product, Category; category = Category.objects.get(id=\\\"motocicletas\\\"); product, created = Product.objects.update_or_create(name=\\\"NOMBRE\\\", defaults={\\\"category\\\": category, \\\"brand\\\": \\\"MARCA\\\", \\\"price\\\": PRECIO, \\\"description\\\": \\\"DESCRIPCION\\\", \\\"image\\\": \\\"products/default.jpg\\\", \\\"features\\\": \\\"[]\\\", \\\"specs_general\\\": \\\"[]\\\", \\\"specs_engine\\\": \\\"[]\\\", \\\"specs_comfort\\\": \\\"[]\\\", \\\"specs_safety\\\": \\\"[]\\\", \\\"stock\\\": STOCK, \\\"featured\\\": DESTACADO}); print(\\\"✅ Creado:\\\", created, \\\"Producto:\\\", product.name)\" | python manage.py shell'"
```

### **Plantilla 2: Agregar Especificación General**
```bash
# Reemplazar: NOMBRE_PRODUCTO, ETIQUETA, VALOR
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"from products.models import Product; import json; producto = Product.objects.get(name=\\\"NOMBRE_PRODUCTO\\\"); specs = json.loads(producto.specs_general); specs.append({\\\"label\\\": \\\"ETIQUETA\\\", \\\"value\\\": \\\"VALOR\\\"}); producto.specs_general = json.dumps(specs, ensure_ascii=False); producto.save(); print(\\\"✅ Especificación agregada\\\")\" | python manage.py shell'"
```

---

## 🏍️ **EJEMPLOS PRÁCTICOS EXITOSOS**

### **Ejemplo 1: Suzuki GSX-R1000RZ (Validado)**
```bash
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"from products.models import Product, Category; category = Category.objects.get(id=\\\"motocicletas\\\"); product, created = Product.objects.update_or_create(name=\\\"Suzuki GSX-R1000RZ\\\", defaults={\\\"category\\\": category, \\\"brand\\\": \\\"Suzuki\\\", \\\"price\\\": 18500, \\\"description\\\": \\\"Superbike de alta performance con tecnología MotoGP\\\", \\\"image\\\": \\\"products/default.jpg\\\", \\\"features\\\": \\\"[]\\\", \\\"specs_general\\\": \\\"[]\\\", \\\"specs_engine\\\": \\\"[]\\\", \\\"specs_comfort\\\": \\\"[]\\\", \\\"specs_safety\\\": \\\"[]\\\", \\\"stock\\\": 3, \\\"featured\\\": True}); print(\\\"✅ Creada:\\\", created, \\\"Suzuki GSX-R1000RZ\\\")\" | python manage.py shell'"
```

### **Ejemplo 2: Haojue DL160 (Validado)**
```bash
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"from products.models import Product, Category; category = Category.objects.get(id=\\\"motocicletas\\\"); product, created = Product.objects.update_or_create(name=\\\"Haojue DL160\\\", defaults={\\\"category\\\": category, \\\"brand\\\": \\\"Haojue\\\", \\\"price\\\": 3800, \\\"description\\\": \\\"Motocicleta doble propósito 162cc\\\", \\\"image\\\": \\\"products/default.jpg\\\", \\\"features\\\": \\\"[]\\\", \\\"specs_general\\\": \\\"[]\\\", \\\"specs_engine\\\": \\\"[]\\\", \\\"specs_comfort\\\": \\\"[]\\\", \\\"specs_safety\\\": \\\"[]\\\", \\\"stock\\\": 6, \\\"featured\\\": True}); print(\\\"✅ Creada:\\\", created, \\\"Haojue DL160\\\")\" | python manage.py shell'"
```

---

## 🔍 **COMANDOS DE VERIFICACIÓN**

### **1. Verificar Productos por Marca**
```bash
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"from products.models import Product; [print(f\\\"{p.name} - \${p.price} - Stock: {p.stock}\\\") for p in Product.objects.filter(brand=\\\"MARCA\\\")]\" | python manage.py shell'"
```

### **2. Verificar Especificaciones**
```bash
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"from products.models import Product; import json; p = Product.objects.get(name=\\\"NOMBRE\\\"); print(\\\"Features:\\\", len(json.loads(p.features))); print(\\\"General:\\\", len(json.loads(p.specs_general)))\" | python manage.py shell'"
```

### **3. Verificar Categorías Disponibles**
```bash
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"from products.models import Category; [print(f\\\"{c.id}: {c.name}\\\") for c in Category.objects.all()]\" | python manage.py shell'"
```

---

## 📋 **CHECKLIST PRE-CARGA**

### **Antes de Agregar Productos:**
- [ ] Verificar conexión SSH como root
- [ ] Confirmar que existe categoría "motocicletas"
- [ ] Preparar datos con formato correcto
- [ ] Validar que el nombre del producto es único
- [ ] **VERIFICAR que exists `/media/products/default.jpg`**

### **Durante la Carga:**
- [ ] Usar triple escape `\\\"`para comillas en JSON
- [ ] Inicializar todos los campos JSON como `"[]"`
- [ ] **USAR SIEMPRE `"products/default.jpg"` como imagen**
- [ ] Usar `update_or_create` para evitar duplicados
- [ ] Verificar mensaje de confirmación

### **Después de la Carga:**
- [ ] Verificar que el producto se creó
- [ ] Confirmar que aparece en el catálogo web
- [ ] **Verificar que NO hay errores 404 en consola del navegador**
- [ ] Agregar especificaciones técnicas detalladas
- [ ] Cambiar imagen a específica vía Django admin

---

## 🎯 **MEJORES PRÁCTICAS**

### **1. ⭐ SISTEMA DE IMÁGENES VALIDADO**

#### **🔹 Imagen Placeholder Obligatoria:**
```python
"image": "products/default.jpg"  # ✅ SIEMPRE usar esta ruta
```

#### **🔹 Ubicación Física:**
- **Ruta en servidor:** `/var/www/llevateloexpress/media/products/default.jpg`
- **URL web:** `https://llevateloexpress.com/media/products/default.jpg`
- **Permisos:** `llevateloexpress:www-data` con permisos de lectura

#### **🔹 Origen de default.jpg:**
- **Fuente:** Copia de `gn125.jpg` existente (imagen válida)
- **Propósito:** Prevenir errores 404 que causan parpadeo de página
- **Resultado:** Catálogo estable sin errores de consola

#### **🔹 Proceso de Imágenes:**
1. **Carga inicial:** Todos los productos usan `products/default.jpg`
2. **Sin errores 404:** Página funciona perfectamente 
3. **Cambio posterior:** Admin Django → subir imagen específica
4. **Resultado final:** Producto con imagen personalizada

#### **🔹 Nomenclatura Recomendada para Imágenes Finales:**
```
products/suzuki_gsxr1000rz.jpg     # Marca_modelo.jpg
products/haojue_dl160.jpg          # Marca_modelo.jpg  
products/yamaha_mt09.jpg           # Marca_modelo.jpg
```

### **2. Precios y Stock**
- Usar precios en USD como float (ej: 18500.00)
- Stock inicial conservador para pruebas
- Marcar como destacado (`featured: True`) productos premium

### **3. Descripciones**
- Mantener descripciones concisas pero informativas
- Incluir características principales en descripción
- Usar terminología técnica apropiada

### **4. Especificaciones Técnicas**
- Agregar especificaciones después de crear el producto base
- Usar datos técnicos reales y verificados
- Organizar en categorías: general, motor, confort, seguridad

---

## 📈 **HISTORIAL DE ÉXITOS**

### **Productos Agregados Exitosamente:**
1. **Haojue DK150** - $3,200 - ✅ Funcionando con default.jpg
2. **Haojue DL160** - $3,800 - ✅ Funcionando con default.jpg  
3. **Haojue HJ150-8** - $3,400 - ✅ Funcionando con default.jpg
4. **Haojue NK150** - $3,600 - ✅ Funcionando con default.jpg
5. **Suzuki GSX-R1000RZ** - $18,500 - ✅ Funcionando con default.jpg

### **Especificaciones Técnicas Completas:**
- ✅ 31+ especificaciones por producto
- ✅ 4 categorías de specs (general, motor, confort, seguridad)
- ✅ Formato label/value validado
- ✅ Renderización correcta en frontend

### **Sistema de Imágenes Validado:**
- ✅ **Imagen default.jpg creada y funcionando**
- ✅ **Eliminación total de errores 404**
- ✅ **Catálogo estable sin parpadeos**
- ✅ **Permisos correctos configurados**

---

## 🚨 **COMANDOS DE EMERGENCIA**

### **Eliminar Producto (Usar con Precaución)**
```bash
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"from products.models import Product; Product.objects.filter(name=\\\"NOMBRE_PRODUCTO\\\").delete(); print(\\\"✅ Producto eliminado\\\")\" | python manage.py shell'"
```

### **Resetear Especificaciones**
```bash
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"from products.models import Product; p = Product.objects.get(name=\\\"NOMBRE\\\"); p.specs_general=\\\"[]\\\"; p.specs_engine=\\\"[]\\\"; p.specs_comfort=\\\"[]\\\"; p.specs_safety=\\\"[]\\\"; p.save(); print(\\\"✅ Specs reseteadas\\\")\" | python manage.py shell'"
```

### **Corregir Imagen a Default (Solución de Emergencia para 404s)**
```bash
ssh root@llevateloexpress.com "cd /var/www/llevateloexpress && sudo -u llevateloexpress bash -c 'source backend_env/bin/activate && echo \"from products.models import Product; productos = Product.objects.filter(brand=\\\"MARCA\\\"); [setattr(p, \\\"image\\\", \\\"products/default.jpg\\\") or p.save() for p in productos]; print(\\\"✅ Imágenes corregidas a default.jpg\\\")\" | python manage.py shell'"
```

---

## 📞 **CONTACTO Y SOPORTE**
- **Sistema:** LlévateloExpress - Django Backend
- **VPS:** llevateloexpress.com (IP: 203.161.55.87)
- **Método validado:** SSH + Django Shell + JSON specs + default.jpg
- **Imagen placeholder:** `/media/products/default.jpg` (VALIDADA)
- **Última actualización:** Enero 2025

---

**🎉 Este método ha sido validado exitosamente con múltiples productos, especificaciones técnicas completas y sistema de imágenes estable sin errores 404.** 