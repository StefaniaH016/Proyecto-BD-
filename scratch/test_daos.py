import sys
import os

# Asegurar que el directorio raíz está en el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from daos import UsuarioDAO, BaseDAO
from database import db

def test_dao_implementation():
    print("=== INICIANDO PRUEBAS DE DAO ===")
    
    # 1. Probar UsuarioDAO
    print("\n1. Probando UsuarioDAO.authenticate...")
    u_dao = UsuarioDAO()
    res = u_dao.authenticate('admin', 'admin123')
    if res:
        print(f"   [OK] Autenticación exitosa. Fila: {res}")
    else:
        print("   [ERROR] No se pudo autenticar al admin.")

    # 2. Probar BaseDAO.get_schema
    print("\n2. Probando BaseDAO.get_schema('PAIS')...")
    b_dao = BaseDAO()
    schema = b_dao.get_schema('PAIS')
    if schema:
        print(f"   [OK] Esquema recuperado. Columnas: {[c['name'] for c in schema]}")
    else:
        print("   [ERROR] No se pudo recuperar el esquema de PAIS.")

    # 3. Probar BaseDAO.get_all
    print("\n3. Probando BaseDAO.get_all('CONFEDERACION')...")
    rows = b_dao.get_all('CONFEDERACION')
    if rows:
        print(f"   [OK] Datos recuperados. Filas: {len(rows[0])}")
    else:
        print("   [ERROR] No se pudieron recuperar datos de CONFEDERACION.")

    # 4. Probar Registro en Bitácora
    print("\n4. Probando UsuarioDAO.registrar_entrada...")
    try:
        u_dao.registrar_entrada(1)
        print("   [OK] Entrada registrada en bitácora.")
    except Exception as e:
        print(f"   [ERROR] Falló registro en bitácora: {e}")

    print("\n=== PRUEBAS FINALIZADAS ===")

if __name__ == "__main__":
    test_dao_implementation()
