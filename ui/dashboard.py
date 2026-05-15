import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from logic.crud_views import GenericCRUD
from logic.reports_views import ReportsWindow
from controllers.dashboard_controller import DashboardController

class Dashboard:
    def __init__(self, user_id, user_type="TRADICIONAL"):
        self.root = tk.Tk()
        self.user_id = user_id
        self.user_type = user_type.upper()
        self.controller = DashboardController()
        
        self.root.title(f"Sistema de Gestión - Panel Principal ({self.user_type})")
        self.root.geometry("600x650")
        self.root.configure(bg="#e9ecef")
        self.root.resizable(False, False)
        
        # Registrar salida al cerrar la ventana para la bitácora
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_sesion)

        # Header
        header_frame = tk.Frame(self.root, bg="#343a40")
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="⚽ SISTEMA MUNDIAL DE FÚTBOL ⚽", font=("Segoe UI", 16, "bold"), fg="white", bg="#343a40", pady=15).pack()

        # Subtítulo
        tk.Label(self.root, text=f"Bienvenido, Rol: {self.user_type}", font=("Segoe UI", 12, "italic"), bg="#e9ecef", fg="#495057").pack(pady=10)

        # Contenedor con scroll
        canvas = tk.Canvas(self.root, bg="#e9ecef", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#e9ecef")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((300, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # CRUDs
        if self.user_type in ['ADMINISTRADOR', 'TRADICIONAL']:
            tk.Label(scrollable_frame, text="✏️ Gestión de Datos (CRUD)", font=("Segoe UI", 12, "bold"), bg="#e9ecef", fg="#212529").pack(pady=5)
            self.create_button(scrollable_frame, "📋 Gestionar Selecciones", "SELECCION", "#0d6efd")
            self.create_button(scrollable_frame, "🏟️ Gestionar Partidos", "PARTIDO", "#0d6efd")
            self.create_button(scrollable_frame, "🏃‍♂️ Gestionar Jugadores", "JUGADOR", "#0d6efd")
            self.create_button(scrollable_frame, "👔 Gestionar D. Técnicos", "DIRECTOR_TECNICO", "#0d6efd")
            self.create_button(scrollable_frame, "📈 Gestionar Detalles Partido", "DETALLES_PARTIDO_SELECCION", "#0d6efd")
        
        if self.user_type == 'ADMINISTRADOR':
            ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=15, padx=40)
            tk.Label(scrollable_frame, text="🛡️ Herramientas de Administrador", font=("Segoe UI", 12, "bold"), bg="#e9ecef", fg="#212529").pack(pady=5)
            self.create_button(scrollable_frame, "👤 Gestionar Usuarios", "USUARIO", "#198754")
            self.create_button(scrollable_frame, "🏙️ Gestionar Ciudades", "CIUDAD", "#198754")
            self.create_button(scrollable_frame, "🌎 Gestionar Países", "PAIS", "#198754")
            self.create_button(scrollable_frame, "🗺️ Gestionar Confederaciones", "CONFEDERACION", "#198754")
            self.create_button(scrollable_frame, "🏟️ Gestionar Estadios", "ESTADIO", "#198754")
            self.create_button(scrollable_frame, "⚽ Gestionar Posiciones", "POSICION", "#198754")
            self.create_button(scrollable_frame, "🕒 Ver Bitácora de Accesos", "BITACORA", "#ffc107", text_color="black")

        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=15, padx=40)
        tk.Label(scrollable_frame, text="📊 Inteligencia y Reportes", font=("Segoe UI", 12, "bold"), bg="#e9ecef", fg="#212529").pack(pady=5)
        
        btn_reports = tk.Button(scrollable_frame, text="🔍 Abrir Módulo de Consultas y Reportes", font=("Segoe UI", 10, "bold"), width=35, pady=8, bg="#6f42c1", fg="white", activebackground="#59359a", bd=0, cursor="hand2", command=self.open_reports)
        btn_reports.pack(pady=10)

        salir_btn = tk.Button(scrollable_frame, text="🚪 Cerrar Sesión", font=("Segoe UI", 10, "bold"), command=self.cerrar_sesion, bg="#dc3545", fg="white", activebackground="#c82333", activeforeground="white", width=20, bd=0, pady=8)
        salir_btn.pack(pady=20)
        
        self.root.mainloop()

    def create_button(self, parent, text, table_name, bg_color, text_color="white"):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"), width=35, pady=5, bg=bg_color, fg=text_color, activebackground=bg_color, bd=0, cursor="hand2", command=lambda: self.open_crud(table_name))
        btn.pack(pady=5)

    def open_crud(self, table_name):
        top = tk.Toplevel(self.root)
        GenericCRUD(top, table_name)
        
    def open_reports(self):
        top = tk.Toplevel(self.root)
        ReportsWindow(top)

    def cerrar_sesion(self):
        if messagebox.askyesno("Salir", "¿Desea cerrar sesión?"):
            success, msg = self.controller.cerrar_sesion(self.user_id)
            if not success:
                print(f"[ERROR] No se pudo registrar salida: {msg}")
            self.root.destroy()
            # Reiniciar login
            import os
            import sys
            os.execv(sys.executable, ['python'] + sys.argv)
