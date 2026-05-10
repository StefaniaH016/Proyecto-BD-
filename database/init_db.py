import oracledb
import os

# ============================================================
# Script de inicialización completa de la BD del Mundial 2026
# Ejecutar: python init_db.py
# ============================================================

DSN  = "localhost/xe"
USER = "SYSTEM"
PWD  = "oracle2313"

# Ruta al archivo SQL
SQL_FILE = os.path.join(os.path.dirname(__file__), 'schema.sql')

def execute_script():
    if not os.path.exists(SQL_FILE):
        print(f"❌ Error: No se encontró el archivo {SQL_FILE}")
        return

    try:
        conn = oracledb.connect(user=USER, password=PWD, dsn=DSN)
        cur  = conn.cursor()

        print(f"📖 Leyendo {SQL_FILE}...")
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Separar los comandos por ';'
        # Nota: Esto es una división simple. 
        # Si hubiera ';' dentro de strings o triggers, fallaría, 
        # pero para este esquema estándar funciona bien.
        statements = sql_content.split(';')

        print("🚀 Ejecutando comandos...")
        for i, sql in enumerate(statements):
            command = sql.strip()
            if not command or command.startswith('--'):
                continue

            try:
                cur.execute(command)
                # Extraer el nombre de la tabla o acción para el log
                first_word = command.split()[0].upper()
                if first_word == "CREATE":
                    name = command.split("TABLE")[1].split("(")[0].strip()
                    print(f"   ✓ Tabla creada: {name}")
                elif first_word == "DROP":
                    name = command.split("TABLE")[1].split("CASCADE")[0].strip()
                    print(f"   ✓ Tabla eliminada: {name}")
                elif first_word == "INSERT":
                    pass # No logueamos cada insert para no saturar la consola
                elif first_word == "COMMIT":
                    print(f"   ✓ Cambios guardados (COMMIT)")

            except oracledb.DatabaseError as e:
                err, = e.args
                # Ignorar error "table or view does not exist" al borrar
                if "DROP" in command.upper() and err.code == 942:
                    continue
                print(f"   ✗ Error en comando {i+1}: {e}")
                print(f"     SQL: {command[:50]}...")

        conn.commit()
        cur.close()
        conn.close()
        print("\n✅ ¡Base de datos inicializada exitosamente desde schema.sql!")

    except Exception as e:
        print(f"\n❌ Error general: {e}")

if __name__ == '__main__':
    execute_script()
