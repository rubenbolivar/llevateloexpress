#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para sincronizar cambios del sistema de financiamiento con producción
SOLUCIÓN INTELIGENTE: Relación directa entre CalculatorMode y FinancingPlan
"""

import os
import subprocess

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n🔄 {description}")
    print(f"Comando: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Éxito: {description}")
        if result.stdout:
            print(f"Output: {result.stdout}")
    else:
        print(f"❌ Error en: {description}")
        print(f"Error: {result.stderr}")
        return False
    return True

def main():
    print("🚀 SINCRONIZACIÓN: Sistema de Financiamiento Inteligente")
    print("=" * 60)
    
    # 1. Transferir archivos modificados
    files_to_sync = [
        "financing/models.py",
        "financing/admin.py", 
        "financing/views.py",
        "js/solicitud-financiamiento.js",
        "js/api.js"
    ]
    
    print("\n📁 TRANSFERIR ARCHIVOS MODIFICADOS")
    for file in files_to_sync:
        if not run_command(f"scp {file} root@203.161.55.87:/var/www/llevateloexpress/{file}", f"Transferir {file}"):
            return False
    
    # 2. Crear y aplicar migración
    print("\n🗃️ CREAR Y APLICAR MIGRACIÓN")
    migration_commands = [
        "cd /var/www/llevateloexpress",
        "source backend_env/bin/activate",
        "python manage.py makemigrations financing --name='add_financing_plans_relation'",
        "python manage.py migrate"
    ]
    
    command = " && ".join(migration_commands)
    if not run_command(f'ssh root@203.161.55.87 "{command}"', "Crear y aplicar migración"):
        return False
    
    # 3. Configurar relaciones iniciales
    print("\n⚙️ CONFIGURAR RELACIONES INICIALES")
    setup_script = '''
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llevateloexpress_backend.settings")
django.setup()

from financing.models import CalculatorMode, FinancingPlan

# Obtener modalidad de crédito inmediato
try:
    credito_mode = CalculatorMode.objects.get(mode_type="credito", is_active=True)
    print(f"✅ Modalidad encontrada: {credito_mode.name}")
    
    # Obtener planes activos con porcentajes que coincidan
    planes_30 = FinancingPlan.objects.filter(min_down_payment_percentage=30, is_active=True)
    planes_40 = FinancingPlan.objects.filter(min_down_payment_percentage=40, is_active=True)
    planes_50 = FinancingPlan.objects.filter(min_down_payment_percentage=50, is_active=True)
    planes_60 = FinancingPlan.objects.filter(min_down_payment_percentage=60, is_active=True)
    
    # Mostrar planes disponibles
    all_plans = FinancingPlan.objects.filter(is_active=True).order_by("min_down_payment_percentage")
    print("📋 Planes disponibles:")
    for plan in all_plans:
        print(f"  ID:{plan.id} - {plan.name} - {plan.min_down_payment_percentage}%")
    
    # Asociar planes a la modalidad (si existen)
    plans_to_associate = []
    if planes_30.exists():
        plans_to_associate.extend(planes_30)
    if planes_40.exists():
        plans_to_associate.extend(planes_40)
    if planes_50.exists():
        plans_to_associate.extend(planes_50)
    if planes_60.exists():
        plans_to_associate.extend(planes_60)
    
    if plans_to_associate:
        credito_mode.available_financing_plans.set(plans_to_associate)
        print(f"✅ Asociados {len(plans_to_associate)} planes a la modalidad")
        
        # Verificar asociación
        associated = credito_mode.available_financing_plans.all()
        print("🔗 Planes asociados:")
        for plan in associated:
            print(f"  ✓ {plan.name} - {plan.min_down_payment_percentage}%")
    else:
        print("⚠️ No se encontraron planes con porcentajes 30, 40, 50, 60")
        print("💡 Recomendación: Crear planes o ajustar porcentajes existentes")
    
    # Actualizar configuración de la modalidad
    credito_mode.available_down_payments = "30,40,50,60"  # Backup para compatibilidad
    credito_mode.save()
    
    print("✅ Configuración completada")
    
except CalculatorMode.DoesNotExist:
    print("❌ No se encontró modalidad de crédito inmediato")
except Exception as e:
    print(f"❌ Error en configuración: {e}")
'''
    
    # Crear archivo temporal
    with open("temp_setup.py", "w") as f:
        f.write(setup_script)
    
    # Transferir y ejecutar
    if not run_command("scp temp_setup.py root@203.161.55.87:/var/www/llevateloexpress/", "Transferir script de configuración"):
        return False
    
    setup_command = "cd /var/www/llevateloexpress && source backend_env/bin/activate && python temp_setup.py"
    if not run_command(f'ssh root@203.161.55.87 "{setup_command}"', "Ejecutar configuración inicial"):
        return False
    
    # Limpiar archivo temporal
    os.remove("temp_setup.py")
    
    # 4. Reiniciar servicios
    print("\n🔄 REINICIAR SERVICIOS")
    if not run_command("ssh root@203.161.55.87 'systemctl reload llevateloexpress'", "Recargar servicio"):
        return False
    
    # 5. Verificar funcionamiento
    print("\n✅ VERIFICAR FUNCIONAMIENTO")
    test_commands = [
        "cd /var/www/llevateloexpress",
        "source backend_env/bin/activate", 
        "python manage.py shell -c \"from financing.models import CalculatorMode; mode = CalculatorMode.objects.get(mode_type='credito'); print('Opciones disponibles:', mode.get_down_payment_options()); print('Planes asociados:', mode.available_financing_plans.count())\""
    ]
    
    test_command = " && ".join(test_commands)
    if not run_command(f'ssh root@203.161.55.87 "{test_command}"', "Verificar configuración"):
        return False
    
    print("\n🎉 SINCRONIZACIÓN COMPLETADA")
    print("=" * 60)
    print("✅ Sistema de financiamiento actualizado con arquitectura inteligente")
    print("✅ CalculatorMode ahora usa FinancingPlan directamente")
    print("✅ Configurable desde Django Admin")
    print("✅ Frontend usa financing_plan_id correcto")
    print("\n🔧 PRÓXIMOS PASOS:")
    print("1. Verificar calculadora en frontend")
    print("2. Probar formulario de solicitud")
    print("3. Configurar planes desde Admin si es necesario")

if __name__ == "__main__":
    main() 