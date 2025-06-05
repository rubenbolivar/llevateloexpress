#!/usr/bin/env python3
"""
Script de prueba completa del flujo V2 de solicitud de financiamiento
Simula las peticiones del frontend V2 al backend
"""

import requests
import json
import time
from datetime import datetime

# Configuración del servidor
BASE_URL = "https://llevateloexpress.com"
API_BASE = f"{BASE_URL}/api"

# Datos de prueba (usuario existente)
TEST_USER = {
    "email": "1@centrodelpan.com",
    "password": "12345678"
}

# Datos de solicitud de prueba (simulando datos de calculadora)
TEST_REQUEST_DATA = {
    "vehicle_price": 4500.00,
    "down_payment": 1575.00,  # 35%
    "financed_amount": 2925.00,
    "payment_frequency": "quincenal",  # Será convertido a "biweekly"
    "payment_amount": 158.333,  # 3 decimales - será redondeado
    "financing_plan": 1,  # Será mapeado dinámicamente
    "monthly_income": 800.00,
    "work_type": "empleado",
    "phone": "+507 6999-9999",
    "address": "Panamá, Panamá"
}

class FinancingFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Registrar resultado de prueba"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        
    def test_authentication(self):
        """Probar autenticación de usuario"""
        # Probar diferentes URLs de autenticación
        auth_urls = [
            f"{API_BASE}/users/auth/login/",
            f"{API_BASE}/users/login/", 
            f"{API_BASE}/auth/login/",
            f"{BASE_URL}/login/"
        ]
        
        for auth_url in auth_urls:
            try:
                response = self.session.post(
                    auth_url,
                    json=TEST_USER,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get('token')
                    if self.token:
                        self.session.headers.update({
                            'Authorization': f'Token {self.token}',
                            'Content-Type': 'application/json'
                        })
                        self.log_test("Autenticación", True, f"Exitosa en {auth_url} - Token: {self.token[:20]}...")
                        return True
                    else:
                        self.log_test("Autenticación", False, f"Sin token en {auth_url}")
                elif response.status_code == 404:
                    continue  # Probar siguiente URL
                else:
                    self.log_test("Autenticación", False, f"Error en {auth_url}: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Autenticación", False, f"Error en {auth_url}: {str(e)}")
                continue
        
        self.log_test("Autenticación", False, "Todas las URLs fallaron")
        return False
    
    def test_user_profile(self):
        """Verificar perfil de usuario"""
        profile_urls = [
            f"{API_BASE}/users/profile/",
            f"{API_BASE}/users/me/",
            f"{API_BASE}/auth/user/"
        ]
        
        for profile_url in profile_urls:
            try:
                response = self.session.get(profile_url, timeout=10)
                
                if response.status_code == 200:
                    user_data = response.json()
                    self.log_test("Perfil de Usuario", True, f"Usuario: {user_data.get('email')} desde {profile_url}")
                    return True
                elif response.status_code == 404:
                    continue
                    
            except Exception as e:
                continue
                
        self.log_test("Perfil de Usuario", False, "No se pudo obtener el perfil")
        return False
    
    def test_financing_plans(self):
        """Verificar planes de financiamiento disponibles"""
        try:
            response = self.session.get(f"{API_BASE}/financing/plans/", timeout=10)
            
            if response.status_code == 200:
                plans = response.json()
                if plans:
                    plan_info = f"Planes encontrados: {len(plans)}"
                    for plan in plans[:3]:  # Mostrar primeros 3
                        plan_info += f"\n  - Plan {plan.get('id')}: {plan.get('name')} ({plan.get('down_payment_percentage')}%)"
                    self.log_test("Planes de Financiamiento", True, plan_info)
                    return True
                else:
                    self.log_test("Planes de Financiamiento", False, "No se encontraron planes")
                    return False
            else:
                self.log_test("Planes de Financiamiento", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Planes de Financiamiento", False, f"Error: {str(e)}")
            return False
    
    def test_data_normalization(self):
        """Probar normalización de datos (simulando FinancingDataFixer)"""
        normalized_data = TEST_REQUEST_DATA.copy()
        
        # Simular normalización
        frequency_map = {
            "quincenal": "biweekly",
            "semanal": "weekly", 
            "mensual": "monthly"
        }
        
        # Normalizar frecuencia de pago
        if normalized_data["payment_frequency"] in frequency_map:
            normalized_data["payment_frequency"] = frequency_map[normalized_data["payment_frequency"]]
        
        # Redondear cantidad de pago a 2 decimales
        normalized_data["payment_amount"] = round(normalized_data["payment_amount"], 2)
        
        # Mapear plan de financiamiento basado en down payment percentage
        down_payment_percentage = (normalized_data["down_payment"] / normalized_data["vehicle_price"]) * 100
        plan_mapping = {
            35: 5, 45: 6, 55: 7, 65: 8
        }
        closest_percentage = min(plan_mapping.keys(), key=lambda x: abs(x - down_payment_percentage))
        normalized_data["financing_plan"] = plan_mapping[closest_percentage]
        
        changes = []
        for key in ["payment_frequency", "payment_amount", "financing_plan"]:
            if normalized_data[key] != TEST_REQUEST_DATA[key]:
                changes.append(f"{key}: {TEST_REQUEST_DATA[key]} → {normalized_data[key]}")
        
        self.log_test("Normalización de Datos", True, f"Cambios aplicados: {', '.join(changes)}")
        return normalized_data
    
    def test_financing_request_creation(self, normalized_data):
        """Probar creación de solicitud de financiamiento"""
        try:
            response = self.session.post(
                f"{API_BASE}/financing/requests/",
                json=normalized_data,
                timeout=15
            )
            
            if response.status_code == 201:
                request_data = response.json()
                request_id = request_data.get('id')
                self.log_test("Creación de Solicitud", True, f"Solicitud creada con ID: {request_id}")
                return request_id
            else:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = json.dumps(error_json, indent=2)
                except:
                    pass
                self.log_test("Creación de Solicitud", False, f"Status: {response.status_code}\nDetalles: {error_detail}")
                return None
                
        except Exception as e:
            self.log_test("Creación de Solicitud", False, f"Error: {str(e)}")
            return None
    
    def test_frontend_access(self):
        """Probar acceso a las páginas del frontend"""
        pages_to_test = [
            ("Página Principal", f"{BASE_URL}/"),
            ("Calculadora", f"{BASE_URL}/calculadora.html"),
            ("Solicitud de Financiamiento", f"{BASE_URL}/solicitud-financiamiento.html")
        ]
        
        for page_name, url in pages_to_test:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Verificar que el contenido no esté vacío
                    if len(response.text) > 1000:
                        self.log_test(f"Frontend - {page_name}", True, f"Página cargada correctamente ({len(response.text)} bytes)")
                    else:
                        self.log_test(f"Frontend - {page_name}", False, "Contenido sospechosamente pequeño")
                else:
                    self.log_test(f"Frontend - {page_name}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Frontend - {page_name}", False, f"Error: {str(e)}")
    
    def test_v2_javascript_loading(self):
        """Verificar que el JavaScript V2 se carga correctamente"""
        try:
            response = requests.get(f"{BASE_URL}/js/solicitud-financiamiento-v2-part2.js", timeout=10)
            if response.status_code == 200:
                js_content = response.text
                # Verificar contenido clave del V2
                v2_indicators = [
                    "class FinancingRequestApp",
                    "constructor()",
                    "initializeApp()",
                    "normalizeFinancingData"
                ]
                
                found_indicators = [indicator for indicator in v2_indicators if indicator in js_content]
                
                if len(found_indicators) >= 3:
                    self.log_test("JavaScript V2", True, f"V2 cargado correctamente. Indicadores encontrados: {len(found_indicators)}/4")
                else:
                    self.log_test("JavaScript V2", False, f"Solo se encontraron {len(found_indicators)} indicadores V2")
            else:
                self.log_test("JavaScript V2", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("JavaScript V2", False, f"Error: {str(e)}")
    
    def test_api_endpoints_discovery(self):
        """Descubrir los endpoints disponibles del API"""
        endpoints_to_test = [
            f"{BASE_URL}/api/",
            f"{BASE_URL}/api/users/",
            f"{BASE_URL}/api/financing/",
            f"{BASE_URL}/api/products/"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(endpoint, timeout=5)
                self.log_test(f"Endpoint Discovery", True, f"{endpoint} -> Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Endpoint Discovery", False, f"{endpoint} -> Error: {str(e)}")
    
    def run_complete_test(self):
        """Ejecutar prueba completa del flujo"""
        print("🚀 Iniciando prueba completa del flujo V2 de LlévateloExpress")
        print("=" * 60)
        
        # 0. Descubrir endpoints disponibles
        self.test_api_endpoints_discovery()
        
        # 1. Probar acceso al frontend
        self.test_frontend_access()
        
        # 2. Verificar carga del JavaScript V2
        self.test_v2_javascript_loading()
        
        # 3. Probar autenticación
        if not self.test_authentication():
            print("\n❌ Autenticación falló, pero continuando con otras pruebas...")
        
        # 4. Si tenemos token, verificar perfil de usuario
        if self.token:
            self.test_user_profile()
        
        # 5. Verificar planes de financiamiento
        self.test_financing_plans()
        
        # 6. Probar normalización de datos
        normalized_data = self.test_data_normalization()
        
        # 7. Si tenemos autenticación, probar creación de solicitud
        request_id = None
        if self.token:
            request_id = self.test_financing_request_creation(normalized_data)
        
        # Resumen de resultados
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 60)
        
        successful_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"✅ Pruebas exitosas: {len(successful_tests)}")
        print(f"❌ Pruebas fallidas: {len(failed_tests)}")
        print(f"📈 Tasa de éxito: {len(successful_tests)}/{len(self.test_results)} ({len(successful_tests)/len(self.test_results)*100:.1f}%)")
        
        if failed_tests:
            print("\n❌ Pruebas fallidas:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        if request_id:
            print(f"\n🎉 SOLICITUD DE FINANCIAMIENTO CREADA EXITOSAMENTE: ID {request_id}")
        
        # Guardar resultados
        with open("test_results_v2.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📁 Resultados guardados en: test_results_v2.json")
        return len(failed_tests) == 0

if __name__ == "__main__":
    tester = FinancingFlowTester()
    success = tester.run_complete_test()
    
    if success:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        print("   El sistema V2 está funcionando correctamente.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisar los detalles arriba.")
    
    exit(0 if success else 1) 