import tkinter as tk
from tkinter import ttk, messagebox
from database.db import get_connection
from ui.ui_main import MainWindow

# =============================================================================
# Ventana de Login — punto de entrada de la aplicación
# =============================================================================
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Mundial de Fútbol 2026 — Ingreso")
        self.root.geometry("420x380")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e2a3a")
        self.root.bind("<Return>", lambda e: self.login())

        # Logo / Cabecera
        tk.Label(root, text="⚽", font=("Segoe UI", 42), bg="#1e2a3a", fg="#0d6efd").pack(pady=(30, 0))
        tk.Label(root, text="MUNDIAL 2026",
                 font=("Segoe UI", 18, "bold"), bg="#1e2a3a", fg="white").pack()
        tk.Label(root, text="Sistema de Gestión",
                 font=("Segoe UI", 10), bg="#1e2a3a", fg="#6c9bcf").pack(pady=(0, 20))

        # Formulario
        form = tk.Frame(root, bg="#2c3e50", padx=30, pady=25)
        form.pack(fill=tk.X, padx=40)

        tk.Label(form, text="👤  Usuario", font=("Segoe UI", 10, "bold"),
                 bg="#2c3e50", fg="#cfe2ff", anchor="w").pack(fill=tk.X)
        self.ent_usuario = ttk.Entry(form, font=("Segoe UI", 11))
        self.ent_usuario.pack(fill=tk.X, pady=(4, 14))
        self.ent_usuario.focus()

        tk.Label(form, text="🔑  Contraseña", font=("Segoe UI", 10, "bold"),
                 bg="#2c3e50", fg="#cfe2ff", anchor="w").pack(fill=tk.X)
        self.ent_pass = ttk.Entry(form, font=("Segoe UI", 11), show="●")
        self.ent_pass.pack(fill=tk.X, pady=(4, 6))

        btn = tk.Button(root, text="INGRESAR AL SISTEMA",
                        font=("Segoe UI", 11, "bold"),
                        bg="#0d6efd", fg="white",
                        activebackground="#0b5ed7", activeforeground="white",
                        bd=0, pady=12, cursor="hand2",
                        command=self.login)
        btn.pack(fill=tk.X, padx=40, pady=18)

    # ─── Lógica ────────────────────────────────────────────────
    def login(self):
        usuario  = self.ent_usuario.get().strip()
        password = self.ent_pass.get()

        if not usuario or not password:
            messagebox.showwarning("Campos vacíos", "Ingrese usuario y contraseña.")
            return

        conn = get_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()
            cur.execute("""SELECT codigo, tipo_usuario FROM Usuario
                           WHERE nombre_usuario = :1 AND contrasena = :2""",
                        (usuario, password))
            row = cur.fetchone()

            if not row:
                messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")
                return

            cod_usuario, tipo_usuario = row

            # Registrar entrada en Bitácora
            cur.execute("""INSERT INTO Bitacora (cod_usuario, fecha_entrada)
                           VALUES (:1, CURRENT_TIMESTAMP)""", (cod_usuario,))
            conn.commit()

            # Abrir ventana principal
            self.root.withdraw()
            win = tk.Toplevel(self.root)
            app = MainWindow(win, cod_usuario, tipo_usuario)

            # Cuando el usuario cierre el MainWindow vía su botón,
            # sys.exit() ya se encarga; pero si usa la X del SO:
            win.protocol("WM_DELETE_WINDOW", app.cerrar_sesion)

        except Exception as e:
            messagebox.showerror("Error", f"Error en el sistema:\n{e}")
        finally:
            conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
