import sys
import os

# Asegurar que el directorio raíz está en el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controllers.login_controller import LoginController
from controllers.crud_controller import CRUDController
from controllers.report_controller import ReportController
from controllers.dashboard_controller import DashboardController

def test_controllers():
    print("=== INICIANDO PRUEBAS DE CONTROLADORES ===")

    # 1. Probar LoginController
    print("\n1. Probando LoginController.intentar_login...")
    login_ctrl = LoginController(None)
    success, res = login_ctrl.intentar_login('admin', 'admin123')
    if success:
        print(f"   [OK] Login exitoso. User ID: {res}")
    else:
        print(f"   [ERROR] Falló login: {res}")

    # 2. Probar CRUDController
    print("\n2. Probando CRUDController (Tabla PAIS)...")
    crud_ctrl = CRUDController("PAIS")
    schema = crud_ctrl.get_schema()
    if schema:
        print(f"   [OK] Esquema recuperado: {[c['name'] for c in schema]}")
    data = crud_ctrl.get_data()
    if data:
        print(f"   [OK] Datos recuperados: {len(data[0])} filas")

    # 3. Probar ReportController
    print("\n3. Probando ReportController (Reporte: sub_21_count)...")
    rep_ctrl = ReportController()
    try:
        res = rep_ctrl.run_report("sub_21_count")
        if res:
            print(f"   [OK] Reporte ejecutado. Columnas: {res[1]}")
    except Exception as e:
        print(f"   [ERROR] Falló reporte: {e}")

    # 4. Probar DashboardController
    print("\n4. Probando DashboardController...")
    dash_ctrl = DashboardController()
    # Asumiendo que el ID 1 existe (el admin que probamos antes)
    success, msg = dash_ctrl.cerrar_sesion(1)
    if success:
        print(f"   [OK] Cierre de sesión registrado: {msg}")
    else:
        print(f"   [ERROR] Falló cierre de sesión: {msg}")

    print("\n=== PRUEBAS DE CONTROLADORES FINALIZADAS ===")

if __name__ == "__main__":
    test_controllers()
