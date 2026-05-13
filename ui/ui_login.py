import tkinter as tk
from tkinter import ttk, messagebox
from ui.dashboard import Dashboard
from controllers.login_controller import LoginController

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
        
        self.controller = LoginController(self)

    # ─── Lógica ────────────────────────────────────────────────
    def login(self):
        user = self.ent_usuario.get().strip()
        pw   = self.ent_pass.get().strip()
        
        success, result = self.controller.intentar_login(user, pw)
        
        if success:
            user_id, user_type = result
            messagebox.showinfo("Acceso", f"Bienvenido, {user_type}")
            self.root.destroy() # Destruir login para que Dashboard sea la principal
            Dashboard(user_id, user_type)
        else:
            messagebox.showwarning("Acceso denegado", result)

if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
