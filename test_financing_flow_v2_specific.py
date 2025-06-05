#!/usr/bin/env python3
"""
Prueba específica del flujo de financiamiento V2
Usa las URLs exactas del VPS sin alterar la configuración existente
"""

import requests
import json
from datetime import datetime

# URLs exactas del VPS (según la configuración existente)
BASE_URL = "https://llevateloexpress.com"
FINANCING_API = f"{BASE_URL}/api/financing"

# Usuario de prueba existente
TEST_USER = {
    "email": "1@centrodelpan.com",
    "password": "12345678"
}

class FinancingV2Tester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
    
    def authenticate_user(self):
        """Autenticar usuario con el sistema existente"""
        try:
            # Primero obtener la página de login para posibles tokens
            login_page = self.session.get(f"{BASE_URL}/login.html")
            
            # Intentar login con el endpoint que funciona
            response = self.session.post(
                f"{BASE_URL}/login/",  # Endpoint que responde 405 (existe)
                data=TEST_USER,
                timeout=10
            )
            
            # También intentar con otros endpoints posibles
            if response.status_code not in [200, 302]:
                response = self.session.post(
                    f"{BASE_URL}/api/auth/login/",
                    json=TEST_USER,
                    timeout=10
                )
            
            if response.status_code in [200, 302]:
                # Buscar token en respuesta o cookies
                if hasattr(response, 'json'):
                    try:
                        data = response.json()
                        self.token = data.get('token') or data.get('access_token')
                    except:
                        pass
                
                # Verificar cookies de autenticación
                auth_cookies = ['sessionid', 'csrftoken', 'token']
                has_auth = any(cookie.name in auth_cookies for cookie in self.session.cookies)
                
                if self.token or has_auth:
                    self.log_test("Autenticación", True, "Usuario autenticado correctamente")
                    return True
            
            self.log_test("Autenticación", False, f"Error de autenticación: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_test("Autenticación", False, f"Error: {str(e)}")
            return False
    
    def test_financing_endpoints(self):
        """Probar endpoints específicos de financiamiento"""
        endpoints_to_test = [
            ("Plans", f"{FINANCING_API}/plans/"),
            ("Requests", f"{FINANCING_API}/requests/"),
            ("Calculator", f"{FINANCING_API}/calculator/calculate/"),
            ("Simulator", f"{FINANCING_API}/simulator/calculate/")
        ]
        
        for name, url in endpoints_to_test:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    self.log_test(f"Endpoint {name}", True, f"Disponible - Status: {response.status_code}")
                elif response.status_code == 401:
                    self.log_test(f"Endpoint {name}", True, f"Protegido correctamente - Status: {response.status_code}")
                elif response.status_code == 403:
                    self.log_test(f"Endpoint {name}", True, f"Acceso denegado (normal) - Status: {response.status_code}")
                else:
                    self.log_test(f"Endpoint {name}", False, f"Error: {response.status_code}")
            except Exception as e:
                self.log_test(f"Endpoint {name}", False, f"Error de conexión: {str(e)}")
    
    def test_financing_plans(self):
        """Probar obtención de planes de financiamiento"""
        try:
            response = self.session.get(f"{FINANCING_API}/plans/", timeout=10)
            
            if response.status_code == 200:
                plans = response.json()
                if plans:
                    plan_info = f"Planes disponibles: {len(plans)}"
                    # Mostrar los primeros planes
                    for i, plan in enumerate(plans[:3]):
                        plan_info += f"\n  Plan {i+1}: {plan.get('name', 'N/A')} - ID: {plan.get('id')}"
                    self.log_test("Planes de Financiamiento", True, plan_info)
                    return plans
                else:
                    self.log_test("Planes de Financiamiento", False, "No hay planes configurados")
                    return []
            else:
                self.log_test("Planes de Financiamiento", False, f"Error: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_test("Planes de Financiamiento", False, f"Error: {str(e)}")
            return []
    
    def test_create_financing_request(self):
        """Probar creación de solicitud de financiamiento con datos reales"""
        
        # Datos de prueba que coinciden con la estructura del VPS
        request_data = {
            "product": 1,  # ID de producto existente
            "financing_plan": 5,  # Plan Crédito Inmediato 35%
            "product_price": "4500.00",
            "down_payment_percentage": 35,
            "down_payment_amount": "1575.00",
            "financed_amount": "2925.00",
            "payment_frequency": "biweekly",
            "number_of_payments": 24,
            "payment_amount": "158.33",
            "monthly_income": "800.00",
            "employment_type": "empleado_privado"
        }
        
        try:
            response = self.session.post(
                f"{FINANCING_API}/requests/",
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 201:
                data = response.json()
                request_id = data.get('id')
                self.log_test("Crear Solicitud", True, f"Solicitud creada exitosamente - ID: {request_id}")
                return request_id
            elif response.status_code == 400:
                # Error de validación - mostrar detalles
                try:
                    error_data = response.json()
                    error_details = json.dumps(error_data, indent=2)
                    self.log_test("Crear Solicitud", False, f"Error de validación:\n{error_details}")
                except:
                    self.log_test("Crear Solicitud", False, f"Error 400: {response.text}")
            elif response.status_code == 401:
                self.log_test("Crear Solicitud", False, "Error de autenticación - revisar credenciales")
            elif response.status_code == 403:
                self.log_test("Crear Solicitud", False, "Sin permisos - posible problema de CSRF")
            else:
                self.log_test("Crear Solicitud", False, f"Error {response.status_code}: {response.text}")
                
            return None
            
        except Exception as e:
            self.log_test("Crear Solicitud", False, f"Error de conexión: {str(e)}")
            return None
    
    def test_v2_javascript_integration(self):
        """Verificar que el JavaScript V2 se carga correctamente"""
        try:
            response = requests.get(f"{BASE_URL}/solicitud-financiamiento.html", timeout=10)
            if response.status_code == 200:
                html_content = response.text
                
                # Verificar que usa V2
                if "solicitud-financiamiento-v2" in html_content:
                    self.log_test("Integración V2", True, "HTML referencia JavaScript V2")
                    
                    # Verificar que el JS V2 se carga
                    js_response = requests.get(f"{BASE_URL}/js/solicitud-financiamiento-v2-part2.js", timeout=10)
                    if js_response.status_code == 200:
                        js_content = js_response.text
                        if "FinancingRequestV2" in js_content:
                            self.log_test("JavaScript V2", True, "Archivo V2 cargado correctamente")
                        else:
                            self.log_test("JavaScript V2", False, "Archivo V2 no contiene la clase esperada")
                    else:
                        self.log_test("JavaScript V2", False, f"Error cargando JS V2: {js_response.status_code}")
                else:
                    self.log_test("Integración V2", False, "HTML aún usa JavaScript V1")
            else:
                self.log_test("Integración V2", False, f"Error cargando página: {response.status_code}")
                
        except Exception as e:
            self.log_test("Integración V2", False, f"Error: {str(e)}")
    
    def run_financing_flow_test(self):
        """Ejecutar prueba completa del flujo de financiamiento V2"""
        print("🔧 PRUEBA ESPECÍFICA DEL FLUJO DE FINANCIAMIENTO V2")
        print("=" * 60)
        print("🎯 Objetivo: Verificar que el V2 funciona con la infraestructura existente")
        print("⚠️  Sin alterar configuraciones que ya funcionan")
        print("=" * 60)
        
        # 1. Verificar integración V2
        self.test_v2_javascript_integration()
        
        # 2. Probar endpoints de financiamiento
        self.test_financing_endpoints()
        
        # 3. Autenticar usuario
        if self.authenticate_user():
            
            # 4. Obtener planes de financiamiento
            plans = self.test_financing_plans()
            
            # 5. Probar creación de solicitud
            request_id = self.test_create_financing_request()
            
            if request_id:
                print(f"\n🎉 ¡SOLICITUD CREADA EXITOSAMENTE! ID: {request_id}")
        
        # Resumen
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS DEL FLUJO V2")
        print("=" * 60)
        
        successful_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"✅ Pruebas exitosas: {len(successful_tests)}")
        print(f"❌ Pruebas fallidas: {len(failed_tests)}")
        print(f"📈 Tasa de éxito: {len(successful_tests)}/{len(self.test_results)} ({len(successful_tests)/len(self.test_results)*100:.1f}%)")
        
        if failed_tests:
            print("\n❌ Pruebas que necesitan ajuste:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        # Guardar resultados
        with open("test_financing_v2_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📁 Resultados guardados en: test_financing_v2_results.json")
        
        # Recomendaciones específicas
        if len(failed_tests) > 0:
            print(f"\n🔧 RECOMENDACIONES PARA AJUSTAR V2:")
            print("  1. Verificar URLs exactas del API en el JavaScript V2")
            print("  2. Adaptar formato de datos a lo que espera el backend")
            print("  3. Asegurar compatibilidad con autenticación existente")
            print("  4. Verificar que el V2 use los endpoints correctos")
        
        return len(failed_tests) == 0

if __name__ == "__main__":
    tester = FinancingV2Tester()
    success = tester.run_financing_flow_test()
    
    if success:
        print("\n🎉 ¡FLUJO V2 FUNCIONA CORRECTAMENTE!")
        print("   El sistema está listo para solicitudes de financiamiento.")
    else:
        print("\n🔧 AJUSTES NECESARIOS EN V2")
        print("   Revisar los puntos indicados para completar la integración.")
    
    exit(0 if success else 1) 