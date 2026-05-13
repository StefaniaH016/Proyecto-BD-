import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import db
import oracledb

def debug_r2():
    sql = """
            SELECT P.NOMBRE, S.NOMBRE AS EQUIPO,
                   J.PESO, J.ESTATURA, J.VALOR,
                   NVL(POS.NOMBRE, 'Sin definir') AS POSICION
            FROM JUGADOR J
            JOIN PERSONA P ON J.CODIGO_PERSONA = P.CODIGO_PERSONA
            JOIN SELECCION S ON J.CODIGO_SELECCION = S.CODIGO_SELECCION
            LEFT JOIN POSICION POS ON J.CODIGO_POSICION = POS.CODIGO_POSICION
            WHERE J.PESO BETWEEN :1 AND :2
              AND J.ESTATURA BETWEEN :3 AND :4
            ORDER BY J.VALOR DESC"""
    
    params = (50.0, 120.0, 1.50, 2.20)
    
    print(f"Probando consulta R2 con params: {params}")
    conn = db.get_connection()
    if not conn:
        print("Fallo de conexión")
        return
        
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        print(f"Filas encontradas: {len(rows)}")
        for r in rows:
            print(f" > {r}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_r2()
