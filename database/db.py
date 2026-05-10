import oracledb
from tkinter import messagebox

def get_connection():
    try:
        # Aquí puedes ajustar tus credenciales
        connection = oracledb.connect(user="SYSTEM", password="oracle2313", dsn="localhost/xe")
        return connection
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{e}")
        return None
