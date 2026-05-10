import oracledb
import os
import re

# ============================================================
# Script de inicialización completa de la BD del Mundial 2026
# Ejecutar: python database/init_db.py
# ============================================================

DSN  = "localhost/xe"
USER = "SYSTEM"
PWD  = "ORLO"

# Ruta al archivo SQL
SQL_FILE = os.path.join(os.path.dirname(__file__), 'schema.sql')


def parse_statements(sql_content):
    """
    Parsea el contenido SQL en sentencias individuales de forma robusta.
    Maneja comentarios, bloques PL/SQL (terminados en /) y sentencias estándar (;).
    """
    import re
    statements = []
    current_stmt = []
    in_plsql = False

    for line in sql_content.splitlines():
        # 1. Limpiar espacios y comentarios de toda la línea
        raw_line = line.strip()
        if not raw_line or raw_line.startswith('--'):
            continue

        # Eliminar comentario inline para análisis lógico
        clean_line = re.sub(r"--.*$", "", raw_line).strip()
        if not clean_line and not in_plsql:
            continue

        # 2. Detectar inicio de bloque PL/SQL
        up = clean_line.upper()
        if up.startswith('CREATE OR REPLACE TRIGGER') or up.startswith('BEGIN') or up.startswith('DECLARE'):
            in_plsql = True

        # 3. Detectar fin de bloque PL/SQL (el '/' solo en una línea)
        if clean_line == '/' and in_plsql:
            if current_stmt:
                statements.append("\n".join(current_stmt))
                current_stmt = []
            in_plsql = False
            continue

        # 4. Manejar sentencias estándar (;)
        if not in_plsql and clean_line.endswith(';'):
            current_stmt.append(line.replace(';', '')) # Oracle cursor no quiere el ;
            statements.append("\n".join(current_stmt))
            current_stmt = []
        else:
            current_stmt.append(line)

    # Si quedó algo pendiente
    if current_stmt:
        stmt = "\n".join(current_stmt).strip()
        if stmt: statements.append(stmt)

    return statements


def execute_script():
    if not os.path.exists(SQL_FILE):
        print(f"[ERROR] No se encontró {SQL_FILE}")
        return

    print(f"[INFO] Leyendo {SQL_FILE}...")
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    statements = parse_statements(sql_content)
    print(f"   -> {len(statements)} sentencias encontradas\n")

    try:
        conn = oracledb.connect(user=USER, password=PWD, dsn=DSN)
        cur  = conn.cursor()
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a Oracle: {e}")
        return

    drops = creates = inserts = errors = 0

    for i, stmt in enumerate(statements, start=1):
        # Determinar el tipo de sentencia ANTES de ejecutar
        first_word = stmt.split()[0].upper()

        try:
            cur.execute(stmt)

            if first_word == "DROP":
                name = stmt.split()[2]
                print(f"   [DROP] {name}")
                drops += 1
            elif first_word == "CREATE":
                # Extraer nombre de tabla: CREATE TABLE NombreTabla (
                match = re.search(r'CREATE\s+TABLE\s+(\w+)', stmt, re.IGNORECASE)
                name = match.group(1) if match else "?"
                print(f"   [CREATE] {name}")
                creates += 1
            elif first_word == "INSERT":
                inserts += 1
            elif first_word == "COMMIT":
                conn.commit()
                print(f"\n   [COMMIT] Cambios guardados")

        except oracledb.DatabaseError as e:
            err, = e.args
            # Ignorar DROP de tablas que no existen
            if first_word == "DROP" and err.code == 942:
                continue
            # Cualquier otro error se reporta
            print(f"   [ERROR] [{first_word}] sentencia {i}: ORA-{err.code}")
            print(f"      SQL: {stmt[:70].replace(chr(10), ' ')}...")
            errors += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"\n{'='*50}")
    print(f"  Tablas eliminadas:    {drops}")
    print(f"  Tablas creadas:       {creates}")
    print(f"  Registros insertados: {inserts}")
    if errors:
        print(f"  ERRORES:              {errors}")
    else:
        print(f"  Sin errores - OK")
    print(f"{'='*50}")


if __name__ == '__main__':
    execute_script()
