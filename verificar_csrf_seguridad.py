#!/usr/bin/env python3
"""
Script para verificar la implementación de protección CSRF en LlévateloExpress
Verifica configuración de Django, tokens en formularios y JavaScript
"""

import requests
import re
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = "https://llevateloexpress.com"
API_BASE = f"{BASE_URL}/api"

class CSRFSecurityTester:
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
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
        severity = "🔴 CRÍTICO" if not success and "CSRF" in test_name else ""
        print(f"{status} {severity} {test_name}: {details}")
    
    def test_csrf_token_in_pages(self):
        """Verificar que las páginas incluyan tokens CSRF"""
        pages_to_test = [
            ("Solicitud de Financiamiento", f"{BASE_URL}/solicitud-financiamiento.html"),
            ("Registro", f"{BASE_URL}/registro.html"),
            ("Login", f"{BASE_URL}/login.html")
        ]
        
        csrf_patterns = [
            r'csrfmiddlewaretoken',
            r'csrf_token',
            r'{% csrf_token %}',
            r'name=["\']csrfmiddlewaretoken["\']',
            r'data-csrf-token',
            r'X-CSRFToken'
        ]
        
        for page_name, url in pages_to_test:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    found_csrf = []
                    
                    for pattern in csrf_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found_csrf.append(pattern)
                    
                    if found_csrf:
                        self.log_test(f"CSRF Token - {page_name}", True, f"Patrones encontrados: {', '.join(found_csrf)}")
                    else:
                        self.log_test(f"CSRF Token - {page_name}", False, "NO se encontraron tokens CSRF")
                else:
                    self.log_test(f"CSRF Token - {page_name}", False, f"Error al cargar página: {response.status_code}")
            except Exception as e:
                self.log_test(f"CSRF Token - {page_name}", False, f"Error: {str(e)}")
    
    def test_csrf_javascript_implementation(self):
        """Verificar implementación de CSRF en JavaScript"""
        js_files_to_check = [
            "js/solicitud-financiamiento-v2-part2.js",
            "js/solicitud-financiamiento.js",
            "js/api.js",
            "js/login.js"
        ]
        
        csrf_js_patterns = [
            r'X-CSRFToken',
            r'csrfmiddlewaretoken',
            r'getCookie.*csrf',
            r'csrf.*token',
            r'beforeSend.*csrf',
            r'headers.*csrf'
        ]
        
        for js_file in js_files_to_check:
            try:
                response = requests.get(f"{BASE_URL}/{js_file}", timeout=10)
                if response.status_code == 200:
                    js_content = response.text
                    found_csrf = []
                    
                    for pattern in csrf_js_patterns:
                        matches = re.findall(pattern, js_content, re.IGNORECASE)
                        if matches:
                            found_csrf.extend(matches)
                    
                    if found_csrf:
                        self.log_test(f"CSRF JavaScript - {js_file}", True, f"Implementaciones encontradas: {len(found_csrf)}")
                    else:
                        self.log_test(f"CSRF JavaScript - {js_file}", False, "NO se encontró manejo de CSRF")
                elif response.status_code == 404:
                    self.log_test(f"CSRF JavaScript - {js_file}", False, "Archivo no encontrado")
                else:
                    self.log_test(f"CSRF JavaScript - {js_file}", False, f"Error: {response.status_code}")
            except Exception as e:
                self.log_test(f"CSRF JavaScript - {js_file}", False, f"Error: {str(e)}")
    
    def test_csrf_meta_tag(self):
        """Verificar que exista meta tag con CSRF token"""
        try:
            response = requests.get(f"{BASE_URL}/solicitud-financiamiento.html", timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Buscar meta tag de CSRF
                meta_csrf_pattern = r'<meta\s+name=["\']csrf-token["\'][^>]*content=["\']([^"\']+)["\']'
                meta_match = re.search(meta_csrf_pattern, content, re.IGNORECASE)
                
                if meta_match:
                    csrf_token = meta_match.group(1)
                    self.csrf_token = csrf_token
                    self.log_test("CSRF Meta Tag", True, f"Token encontrado en meta tag (longitud: {len(csrf_token)})")
                else:
                    # Buscar otras variantes
                    csrf_variants = [
                        r'name=["\']_token["\']',
                        r'name=["\']csrf_token["\']',
                        r'data-csrf-token'
                    ]
                    
                    found_variants = []
                    for variant in csrf_variants:
                        if re.search(variant, content, re.IGNORECASE):
                            found_variants.append(variant)
                    
                    if found_variants:
                        self.log_test("CSRF Meta Tag", True, f"Variantes encontradas: {', '.join(found_variants)}")
                    else:
                        self.log_test("CSRF Meta Tag", False, "NO se encontró meta tag de CSRF")
        except Exception as e:
            self.log_test("CSRF Meta Tag", False, f"Error: {str(e)}")
    
    def test_csrf_api_protection(self):
        """Probar protección CSRF en endpoints del API"""
        test_endpoints = [
            f"{API_BASE}/financing/requests/",
            f"{API_BASE}/users/login/",
            f"{BASE_URL}/login/"
        ]
        
        test_data = {
            "test": "csrf_verification",
            "email": "test@test.com"
        }
        
        for endpoint in test_endpoints:
            try:
                # Intentar POST sin CSRF token
                response = requests.post(endpoint, json=test_data, timeout=10)
                
                if response.status_code == 403:
                    self.log_test(f"CSRF Protection - {endpoint}", True, "Endpoint rechaza peticiones sin CSRF (403)")
                elif response.status_code == 405:
                    self.log_test(f"CSRF Protection - {endpoint}", True, "Método no permitido (405) - endpoint existe")
                elif response.status_code == 404:
                    self.log_test(f"CSRF Protection - {endpoint}", False, "Endpoint no encontrado (404)")
                elif response.status_code in [400, 401]:
                    self.log_test(f"CSRF Protection - {endpoint}", True, f"Endpoint rechaza petición inválida ({response.status_code})")
                else:
                    # Verificar si la respuesta menciona CSRF
                    if "csrf" in response.text.lower() or "forbidden" in response.text.lower():
                        self.log_test(f"CSRF Protection - {endpoint}", True, f"Protección activa (Status: {response.status_code})")
                    else:
                        self.log_test(f"CSRF Protection - {endpoint}", False, f"Respuesta inesperada: {response.status_code}")
                        
            except Exception as e:
                self.log_test(f"CSRF Protection - {endpoint}", False, f"Error: {str(e)}")
    
    def test_django_csrf_settings(self):
        """Verificar configuración de CSRF en Django mediante headers y cookies"""
        try:
            response = requests.get(f"{BASE_URL}/solicitud-financiamiento.html", timeout=10)
            
            # Verificar headers de seguridad
            security_headers = {
                'X-Frame-Options': 'Protección contra clickjacking',
                'X-Content-Type-Options': 'Protección MIME type sniffing',
                'Strict-Transport-Security': 'HTTPS forzado',
                'Set-Cookie': 'Configuración de cookies'
            }
            
            found_headers = []
            for header, description in security_headers.items():
                if header in response.headers:
                    found_headers.append(f"{header}: {description}")
            
            if found_headers:
                self.log_test("Django Security Headers", True, f"Headers encontrados: {len(found_headers)}")
            else:
                self.log_test("Django Security Headers", False, "No se encontraron headers de seguridad")
            
            # Verificar cookies de CSRF
            csrf_cookies = []
            for cookie in response.cookies:
                if 'csrf' in cookie.name.lower():
                    csrf_cookies.append(cookie.name)
            
            if csrf_cookies:
                self.log_test("CSRF Cookies", True, f"Cookies CSRF encontradas: {', '.join(csrf_cookies)}")
            else:
                self.log_test("CSRF Cookies", False, "No se encontraron cookies CSRF")
                
        except Exception as e:
            self.log_test("Django Security Config", False, f"Error: {str(e)}")
    
    def test_v2_csrf_compliance(self):
        """Verificar que el JavaScript V2 implemente correctamente CSRF"""
        try:
            response = requests.get(f"{BASE_URL}/js/solicitud-financiamiento-v2-part2.js", timeout=10)
            if response.status_code == 200:
                v2_content = response.text
                
                # Verificar implementaciones específicas de CSRF en V2
                v2_csrf_checks = [
                    ("getCsrfToken function", r'getCsrfToken\s*\(\s*\)'),
                    ("CSRF headers setup", r'X-CSRFToken.*headers'),
                    ("CSRF cookie handling", r'getCookie.*csrf'),
                    ("beforeSend CSRF", r'beforeSend.*csrf'),
                    ("CSRF meta tag reading", r'meta.*csrf.*content')
                ]
                
                found_implementations = []
                for check_name, pattern in v2_csrf_checks:
                    if re.search(pattern, v2_content, re.IGNORECASE):
                        found_implementations.append(check_name)
                
                if found_implementations:
                    self.log_test("V2 CSRF Compliance", True, f"Implementaciones: {', '.join(found_implementations)}")
                else:
                    self.log_test("V2 CSRF Compliance", False, "V2 NO implementa manejo de CSRF")
            else:
                self.log_test("V2 CSRF Compliance", False, "No se pudo cargar JavaScript V2")
        except Exception as e:
            self.log_test("V2 CSRF Compliance", False, f"Error: {str(e)}")
    
    def run_csrf_security_audit(self):
        """Ejecutar auditoría completa de seguridad CSRF"""
        print("🔒 INICIANDO AUDITORÍA DE SEGURIDAD CSRF")
        print("=" * 60)
        print("⚠️  Esta auditoría verifica la protección contra ataques CSRF")
        print("   La falta de protección CSRF es un riesgo de seguridad CRÍTICO")
        print("=" * 60)
        
        # 1. Verificar tokens CSRF en páginas
        self.test_csrf_token_in_pages()
        
        # 2. Verificar implementación JavaScript
        self.test_csrf_javascript_implementation()
        
        # 3. Verificar meta tags
        self.test_csrf_meta_tag()
        
        # 4. Verificar protección en API
        self.test_csrf_api_protection()
        
        # 5. Verificar configuración Django
        self.test_django_csrf_settings()
        
        # 6. Verificar compliance del V2
        self.test_v2_csrf_compliance()
        
        # Resumen de resultados
        print("\n" + "=" * 60)
        print("🔒 RESUMEN DE AUDITORÍA CSRF")
        print("=" * 60)
        
        successful_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        critical_failures = [r for r in failed_tests if "CSRF" in r["test"]]
        
        print(f"✅ Verificaciones exitosas: {len(successful_tests)}")
        print(f"❌ Verificaciones fallidas: {len(failed_tests)}")
        print(f"🔴 Fallas críticas de CSRF: {len(critical_failures)}")
        print(f"📈 Nivel de seguridad: {len(successful_tests)}/{len(self.test_results)} ({len(successful_tests)/len(self.test_results)*100:.1f}%)")
        
        if critical_failures:
            print(f"\n🔴 FALLAS CRÍTICAS DE SEGURIDAD:")
            for failure in critical_failures:
                print(f"  - {failure['test']}: {failure['details']}")
        
        if failed_tests:
            print(f"\n❌ Otras verificaciones fallidas:")
            for failure in failed_tests:
                if failure not in critical_failures:
                    print(f"  - {failure['test']}: {failure['details']}")
        
        # Recomendaciones de seguridad
        if len(critical_failures) > 0:
            print(f"\n🚨 RECOMENDACIONES CRÍTICAS:")
            print("  1. Implementar tokens CSRF en todos los formularios")
            print("  2. Configurar X-CSRFToken en peticiones AJAX")
            print("  3. Verificar middleware CSRF en Django settings")
            print("  4. Añadir meta tags CSRF en templates")
        
        # Guardar resultados
        with open("csrf_audit_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📁 Resultados de auditoría guardados en: csrf_audit_results.json")
        
        # Evaluar nivel de seguridad
        security_level = len(successful_tests) / len(self.test_results)
        if security_level >= 0.9:
            print(f"\n🛡️  NIVEL DE SEGURIDAD: EXCELENTE")
        elif security_level >= 0.75:
            print(f"\n🟡 NIVEL DE SEGURIDAD: BUENO (mejorar fallas menores)")
        elif security_level >= 0.5:
            print(f"\n🟠 NIVEL DE SEGURIDAD: REGULAR (atender fallas)")
        else:
            print(f"\n🔴 NIVEL DE SEGURIDAD: CRÍTICO (corregir inmediatamente)")
        
        return len(critical_failures) == 0

if __name__ == "__main__":
    auditor = CSRFSecurityTester()
    is_secure = auditor.run_csrf_security_audit()
    
    if is_secure:
        print("\n🎉 ¡SISTEMA SEGURO CONTRA CSRF!")
    else:
        print("\n⚠️  SISTEMA VULNERABLE - CORREGIR INMEDIATAMENTE")
    
    exit(0 if is_secure else 1) 