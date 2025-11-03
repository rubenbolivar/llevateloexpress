# Script para actualizar admin.py con los cambios necesarios

with open('admin.py', 'r') as f:
    lines = f.readlines()

# Nueva versión del archivo
new_lines = []
skip_until = None

for i, line in enumerate(lines):
    # 1. Actualizar list_display
    if 'list_display = ' in line and 'ProductAdmin' in ''.join(lines[max(0,i-10):i]):
        new_lines.append("    list_display = (\n")
        new_lines.append("        'name', 'category', 'brand', 'price_llevo_formatted', \n")
        new_lines.append("        'financing_plan_display', 'inicial_llevos_formatted', \n")
        new_lines.append("        'cuota_mensual_formatted', 'stock', 'out_of_stock', 'featured', 'thumbnail'\n")
        new_lines.append("    )\n")
        continue
    
    # 2. Actualizar list_filter
    if 'list_filter = ' in line and 'ProductAdmin' in ''.join(lines[max(0,i-15):i]):
        new_lines.append("    list_filter = ('category', 'brand', 'featured', 'financing_plan')\n")
        continue
    
    # 3. Actualizar fieldsets - encontrar y reemplazar sección de Precios
    if "('Precios y Financiamiento'" in line:
        new_lines.append("        ('Plan de Financiamiento', {\n")
        # Saltar hasta encontrar el cierre de esta sección
        skip_until = "description"
        continue
    
    if skip_until == "description" and "'description'" in line:
        new_lines.append("            'fields': ('financing_plan', 'price_llevo', 'inicial_llevos', 'cuota_mensual_llevos', 'price', 'price_conversion_preview', 'financing_preview'),\n")
        new_lines.append("            'description': 'Selecciona el plan de financiamiento y configura inicial y cuota mensual.'\n")
        new_lines.append("        }),\n")
        skip_until = None
        continue
    
    if skip_until:
        continue
    
    # 4. Agregar método financing_plan_display después de inicial_llevos_formatted
    if "inicial_llevos_formatted.short_description = 'Inicial'" in line:
        new_lines.append(line)
        new_lines.append("\n")
        new_lines.append("    def financing_plan_display(self, obj):\n")
        new_lines.append("        \"\"\"Muestra el plan asignado con badge de color\"\"\"\n")
        new_lines.append("        if obj.financing_plan:\n")
        new_lines.append("            colors = {\n")
        new_lines.append("                'credillevo-inmediato': '#007bff',\n")
        new_lines.append("                'credillevo-x4': '#28a745',\n")
        new_lines.append("            }\n")
        new_lines.append("            color = colors.get(obj.financing_plan.slug, '#6c757d')\n")
        new_lines.append("            return format_html(\n")
        new_lines.append("                '<span style=\"background: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;\">{}</span>',\n")
        new_lines.append("                color,\n")
        new_lines.append("                obj.financing_plan.name\n")
        new_lines.append("            )\n")
        new_lines.append("        return format_html('<span style=\"color: #dc3545;\">Sin plan</span>')\n")
        new_lines.append("    financing_plan_display.short_description = 'Plan Asignado'\n")
        continue
    
    # 5. Reemplazar método financing_preview completo
    if "def financing_preview(self, obj):" in line:
        # Saltar el método antiguo hasta encontrar el próximo def o @
        skip_until = "next_method"
        new_lines.append("    def financing_preview(self, obj):\n")
        new_lines.append("        \"\"\"Vista previa del plan de financiamiento asignado\"\"\"\n")
        new_lines.append("        if not obj.financing_plan:\n")
        new_lines.append("            return format_html(\n")
        new_lines.append("                '<div style=\"background: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;\">'" \n")
        new_lines.append("                '<strong>⚠️ Sin plan asignado</strong><br>'\n")
        new_lines.append("                '<small>Selecciona un plan de financiamiento para este producto</small>'\n")
        new_lines.append("                '</div>'\n")
        new_lines.append("            )\n")
        new_lines.append("        \n")
        new_lines.append("        if not obj.price_llevo or not obj.inicial_llevos:\n")
        new_lines.append("            return format_html(\n")
        new_lines.append("                '<div style=\"background: #f8d7da; padding: 10px; border-radius: 5px; border-left: 4px solid #dc3545;\">'" \n")
        new_lines.append("                '<strong>❌ Configuración incompleta</strong><br>'\n")
        new_lines.append("                '<small>Configura precio e inicial en LLEVO</small>'\n")
        new_lines.append("                '</div>'\n")
        new_lines.append("            )\n")
        new_lines.append("        \n")
        new_lines.append("        monto_financiado = obj.price_llevo - obj.inicial_llevos\n")
        new_lines.append("        term_months = obj.financing_plan.max_term_months\n")
        new_lines.append("        \n")
        new_lines.append("        if obj.cuota_mensual_llevos and obj.cuota_mensual_llevos > 0:\n")
        new_lines.append("            cuota_mensual = obj.cuota_mensual_llevos\n")
        new_lines.append("            cuota_type = 'Manual'\n")
        new_lines.append("        else:\n")
        new_lines.append("            cuota_mensual = monto_financiado / term_months\n")
        new_lines.append("            cuota_type = 'Automática'\n")
        new_lines.append("        \n")
        new_lines.append("        total_cuotas = cuota_mensual * term_months\n")
        new_lines.append("        total_pagar = obj.inicial_llevos + total_cuotas\n")
        new_lines.append("        \n")
        new_lines.append("        plan_colors = {'credillevo-inmediato': '#007bff', 'credillevo-x4': '#28a745'}\n")
        new_lines.append("        plan_color = plan_colors.get(obj.financing_plan.slug, '#6c757d')\n")
        new_lines.append("        \n")
        new_lines.append("        content = f'<div style=\"background: #e3f2fd; padding: 12px; border-radius: 5px; border-left: 4px solid {plan_color};\">' \n")
        new_lines.append("        content += f'<strong style=\"color: {plan_color};\">📋 {obj.financing_plan.name}</strong><br><br>' \n")
        new_lines.append("        content += f'<strong>Precio:</strong> {obj.price_llevo} LLEVO<br>' \n")
        new_lines.append("        content += f'<strong>Inicial:</strong> {obj.inicial_llevos} LLEVO<br>' \n")
        new_lines.append("        content += f'<strong>A financiar:</strong> {monto_financiado} LLEVO<br>' \n")
        new_lines.append("        content += f'<strong>Cuota mensual:</strong> {cuota_mensual:.0f} LLEVO x {term_months} meses<br>' \n")
        new_lines.append("        content += f'<strong>Total a pagar:</strong> {total_pagar:.0f} LLEVO<br>' \n")
        new_lines.append("        content += f'<small class=\"text-muted\">Sin intereses • Plazo fijo {term_months} meses • Cuota {cuota_type}</small>' \n")
        new_lines.append("        content += '</div>' \n")
        new_lines.append("        \n")
        new_lines.append("        return format_html(content)\n")
        continue
    
    if skip_until == "next_method" and (line.strip().startswith('def ') or line.strip().startswith('@')):
        skip_until = None
        new_lines.append("    financing_preview.short_description = 'Vista previa del Plan'\n")
        new_lines.append("\n")
        new_lines.append(line)
        continue
    
    if skip_until == "next_method":
        continue
    
    new_lines.append(line)

# Guardar archivo actualizado
with open('admin.py', 'w') as f:
    f.writelines(new_lines)

print('✅ Admin actualizado')
