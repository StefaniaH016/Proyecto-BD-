import oracledb
from contextlib import contextmanager
from tkinter import messagebox

def get_connection():
    try:
        # Aquí puedes ajustar tus credenciales
        connection = oracledb.connect(user="SYSTEM", password="ORLO", dsn="localhost/xe")
        return connection
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{e}")
        return None

@contextmanager
def db_session():
    """Manejador de contexto para asegurar el cierre de la conexión."""
    conn = get_connection()
    try:
        yield conn
    finally:
        if conn:
            conn.close()

def run_query(sql, params=(), commit=False):
    """
    Ejecuta una consulta SQL. 
    Si commit=True, guarda cambios. Si commit=False, retorna (filas, columnas).
    """
    with db_session() as conn:
        if not conn: return None
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            if commit:
                conn.commit()
                return True
            else:
                rows = cur.fetchall()
                cols = [d[0] for d in cur.description] if cur.description else []
                return rows, cols
        except Exception as e:
            raise e # Dejar que el llamador lo maneje o lo pase a messagebox
