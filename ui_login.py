import tkinter as tk
from tkinter import messagebox
from db import get_connection
from datetime import datetime
from ui_main import MainWindow

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Sistema Mundial")
        self.root.geometry("300x250")
        
        tk.Label(root, text="Usuario:").pack(pady=10)
        self.entry_usuario = tk.Entry(root)
        self.entry_usuario.pack(pady=5)
        
        tk.Label(root, text="Contraseña:").pack(pady=10)
        self.entry_password = tk.Entry(root, show="*")
        self.entry_password.pack(pady=5)
        
        tk.Button(root, text="Ingresar", command=self.login).pack(pady=20)

    def login(self):
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()
        
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            # Consultar si el usuario existe y la contraseña es correcta
            try:
                cursor.execute("""
                    SELECT codigo, tipo_usuario FROM Usuario 
                    WHERE nombre_usuario = :1 AND contrasena = :2
                """, (usuario, password))
                user_data = cursor.fetchone()
                
                if user_data:
                    cod_usuario, tipo_usuario = user_data
                    self.registrar_entrada(conn, cod_usuario)
                    messagebox.showinfo("Éxito", f"Bienvenido {usuario} ({tipo_usuario})")
                    # Aquí abriremos la ventana principal dependiendo del tipo de usuario
                    self.abrir_ventana_principal(tipo_usuario, cod_usuario)
                else:
                    messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            except Exception as e:
                messagebox.showerror("Error", f"Error en la consulta:\n{e}")
            finally:
                cursor.close()
                conn.close()

    def registrar_entrada(self, conn, cod_usuario):
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Bitacora (cod_usuario, fecha_entrada) 
                VALUES (:1, CURRENT_TIMESTAMP)
            """, (cod_usuario,))
            conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error al registrar bitácora: {e}")

    def abrir_ventana_principal(self, tipo_usuario, cod_usuario):
        # Ocultar ventana de login
        self.root.withdraw()
        
        # Crear la nueva ventana Toplevel que servirá como root para el Dashboard
        dashboard_window = tk.Toplevel(self.root)
        
        # Instanciar el MainWindow
        self.app_main = MainWindow(dashboard_window, cod_usuario, tipo_usuario)


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
