import oracledb
import os
import re

# ============================================================
# Script de inicialización completa de la BD del Mundial 2026
# Ejecutar: python database/init_db.py
# ============================================================

DSN  = "localhost/xe"
USER = "SYSTEM"
PWD  = "oracle2313"

SQL_FILE = os.path.join(os.path.dirname(__file__), 'schema.sql')


def parse_statements(sql_content):
    """
    Parsea el contenido SQL en sentencias individuales.
    Acumula líneas hasta encontrar ';' (ignorando comentarios inline -- ...)
    antes de decidir si la sentencia está completa.
    """
    statements = []
    current = []

    for line in sql_content.splitlines():
        stripped = line.strip()

        # Ignorar líneas vacías o solo comentarios fuera de un bloque activo
        if not stripped or stripped.startswith('--'):
            continue

        current.append(line)

        # Eliminar comentario inline (-- ...) para detectar correctamente el ';'
        # Ej: "  VALUES (3, 'México');   -- comentario"  → termina en ';'
        stripped_no_comment = re.sub(r"--[^\n]*$", "", stripped).strip()

        # Si la línea (sin comentario) termina con ';', la sentencia está completa
        if stripped_no_comment.endswith(';'):
            stmt = '\n'.join(current).strip()
            # Quitar comentarios inline de cada línea antes de ejecutar
            stmt = re.sub(r"--[^\n]*", "", stmt).strip()
            # Quitar el ';' final (Oracle cursor.execute no lo necesita)
            if stmt.endswith(';'):
                stmt = stmt[:-1].strip()
            if stmt:
                statements.append(stmt)
            current = []

    # Si queda algo sin ';' al final (no debería), lo incluimos igual
    if current:
        stmt = '\n'.join(current).strip()
        if stmt:
            statements.append(stmt)

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
