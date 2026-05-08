import tkinter as tk
from tkinter import ttk, messagebox
import db
from crud_views import GenericCRUD, PersonaSubtypeCRUD
from reports_views import ReportsWindow

class Dashboard:
    def __init__(self, root, user_id, user_type):
        self.root = root
        self.user_id = user_id
        self.user_type = user_type.upper()
        self.root.title(f"Sistema de Gestión - Panel Principal ({self.user_type})")
        self.root.geometry("600x650")
        self.root.configure(bg="#e9ecef")
        self.root.resizable(False, False)
        
        # Registrar salida al cerrar la ventana para la bitácora
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Header
        header_frame = tk.Frame(root, bg="#343a40")
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="⚽ SISTEMA MUNDIAL DE FÚTBOL ⚽", font=("Segoe UI", 16, "bold"), fg="white", bg="#343a40", pady=15).pack()

        # Subtítulo
        tk.Label(root, text=f"Bienvenido, Rol: {self.user_type}", font=("Segoe UI", 12, "italic"), bg="#e9ecef", fg="#495057").pack(pady=10)

        # Contenedor con scroll para los botones si son muchos
        canvas = tk.Canvas(root, bg="#e9ecef", highlightthickness=0)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#e9ecef")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((300, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Permisos TRADICIONAL y ADMINISTRADOR (Pueden hacer CRUD)
        if self.user_type in ['ADMINISTRADOR', 'TRADICIONAL']:
            tk.Label(scrollable_frame, text="✏️ Gestión de Datos (CRUD)", font=("Segoe UI", 12, "bold"), bg="#e9ecef", fg="#212529").pack(pady=5)
            self.create_button(scrollable_frame, "📋 Gestionar Selecciones", "SELECCION", "#0d6efd")
            self.create_button(scrollable_frame, "🏟️ Gestionar Partidos", "PARTIDO", "#0d6efd")
            self.create_button(scrollable_frame, "🏃‍♂️ Gestionar Jugadores", "JUGADOR", "#0d6efd")
            self.create_button(scrollable_frame, "👔 Gestionar D. Técnicos", "DIRECTOR_TECNICO", "#0d6efd")
            self.create_button(scrollable_frame, "📈 Gestionar Participaciones", "PARTICIPACION", "#0d6efd")
        
        # Opciones solo para administrador
        if self.user_type == 'ADMINISTRADOR':
            ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=15, padx=40)
            tk.Label(scrollable_frame, text="🛡️ Herramientas de Administrador", font=("Segoe UI", 12, "bold"), bg="#e9ecef", fg="#212529").pack(pady=5)
            
            self.create_button(scrollable_frame, "👤 Gestionar Usuarios", "USUARIO", "#198754")
            self.create_button(scrollable_frame, "🏙️ Gestionar Ciudades", "CIUDAD", "#198754")
            self.create_button(scrollable_frame, "🗺️ Gestionar Confederaciones", "CONFEDERACION", "#198754")
            self.create_button(scrollable_frame, "🏟️ Gestionar Estadios", "ESTADIO", "#198754")
            self.create_button(scrollable_frame, "⚽ Gestionar Posiciones", "POSICION", "#198754")
            self.create_button(scrollable_frame, "🕒 Ver Bitácora de Accesos", "BITACORA", "#ffc107", text_color="black")

        # Opciones ESPORADICO y TODOS (Solo lectura / Reportes)
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=15, padx=40)
        tk.Label(scrollable_frame, text="📊 Inteligencia y Reportes", font=("Segoe UI", 12, "bold"), bg="#e9ecef", fg="#212529").pack(pady=5)
        
        btn_reports = tk.Button(scrollable_frame, text="🔍 Abrir Módulo de Consultas y Reportes", font=("Segoe UI", 10, "bold"), width=35, pady=8, bg="#6f42c1", fg="white", activebackground="#59359a", bd=0, cursor="hand2", command=self.open_reports)
        btn_reports.pack(pady=10)

        # Botón Salir
        salir_btn = tk.Button(scrollable_frame, text="🚪 Cerrar Sesión", font=("Segoe UI", 10, "bold"), command=self.on_closing, bg="#dc3545", fg="white", activebackground="#c82333", activeforeground="white", width=20, bd=0, pady=8)
        salir_btn.pack(pady=20)

    def create_button(self, parent, text, table_name, bg_color, text_color="white"):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"), width=35, pady=5, bg=bg_color, fg=text_color, activebackground=bg_color, bd=0, cursor="hand2", command=lambda: self.open_crud(table_name))
        btn.pack(pady=5)

    def open_crud(self, table_name):
        top = tk.Toplevel(self.root)
        if table_name in ['JUGADOR', 'DIRECTOR_TECNICO']:
            PersonaSubtypeCRUD(top, table_name)
        else:
            GenericCRUD(top, table_name)
        
    def open_reports(self):
        top = tk.Toplevel(self.root)
        ReportsWindow(top)

    def on_closing(self):
        conn = db.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Bitacora SET fecha_salida = CURRENT_TIMESTAMP 
                    WHERE cod_usuario = :1 AND fecha_salida IS NULL
                """, (self.user_id,))
                conn.commit()
            except Exception as e:
                print(f"Error actualizando bitácora: {e}")
            finally:
                conn.close()
        self.root.destroy()
