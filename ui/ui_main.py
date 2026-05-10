import tkinter as tk
from tkinter import ttk, messagebox
import sys
from database.db import get_connection
from logic.crud_views import GenericCRUD
from logic.reports_views import ReportsWindow

# =============================================================================
# Ventana principal del sistema — usa ttk.Notebook con pestañas por rol
# =============================================================================
class MainWindow:
    def __init__(self, root, cod_usuario, tipo_usuario, login_win=None):
        self.root        = root
        self.cod_usuario = cod_usuario
        self.tipo_usuario = tipo_usuario.upper()
        self.login_win = login_win

        self.root.title(f"Sistema Mundial de Fútbol 2026  —  {self.tipo_usuario}")
        self.root.geometry("960x680")
        self.root.configure(bg="#1e2a3a")
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_sesion)

        # ── Header ──────────────────────────────────────────────
        hdr = tk.Frame(root, bg="#0d6efd", pady=0)
        hdr.pack(fill=tk.X)

        tk.Label(hdr, text="⚽  MUNDIAL DE FÚTBOL 2026",
                 font=("Segoe UI", 17, "bold"), fg="white", bg="#0d6efd", pady=14).pack(side=tk.LEFT, padx=20)

        info_frame = tk.Frame(hdr, bg="#0d6efd")
        info_frame.pack(side=tk.RIGHT, padx=15)
        tk.Label(info_frame, text=f"Rol: {self.tipo_usuario}",
                 font=("Segoe UI", 10), fg="#cfe2ff", bg="#0d6efd").pack()
        tk.Button(info_frame, text="🚪 Cerrar Sesión",
                  font=("Segoe UI", 9, "bold"), bg="#dc3545", fg="white",
                  activebackground="#c82333", bd=0, padx=8, pady=4,
                  cursor="hand2", command=self.cerrar_sesion).pack(pady=4)

        # ── Notebook de pestañas ─────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",          background="#1e2a3a", borderwidth=0)
        style.configure("TNotebook.Tab",      font=("Segoe UI", 10, "bold"),
                        padding=[14, 6], background="#2c3e50", foreground="#adb5bd")
        style.map("TNotebook.Tab",
                  background=[("selected", "#0d6efd")],
                  foreground=[("selected", "white")])

        self.nb = ttk.Notebook(root)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Pestaña CRUD  (ADMINISTRADOR + TRADICIONAL)
        if self.tipo_usuario in ("ADMINISTRADOR", "TRADICIONAL"):
            self._build_tab_crud()

        # Pestaña Administración (solo ADMINISTRADOR)
        if self.tipo_usuario == "ADMINISTRADOR":
            self._build_tab_admin()

        # Consultas y Reportes  (todos los roles)
        self._build_tab_reportes()

    # ── Pestaña CRUD ────────────────────────────────────────────
    def _build_tab_crud(self):
        tab = tk.Frame(self.nb, bg="#f0f4f8")
        self.nb.add(tab, text="✏️  Gestión de Datos")

        tk.Label(tab, text="Selecciona la tabla que deseas gestionar:",
                 font=("Segoe UI", 11), bg="#f0f4f8", fg="#333").pack(pady=(20, 8))

        tables = [
            ("📋 Selecciones",              "SELECCION"),
            ("🗓️ Partidos",                 "PARTIDO"),
            ("👤 Personas",                 "PERSONA"),
            ("🏃 Jugadores",                "JUGADOR"),
            ("👔 Directores Técnicos",      "DIRECTOR_TECNICO"),
            ("⚡ Detalles Partido-Selección","DETALLES_PARTIDO_SELECCION"),
        ]
        grid = tk.Frame(tab, bg="#f0f4f8")
        grid.pack(pady=10)

        for i, (label, tbl) in enumerate(tables):
            r, c = divmod(i, 3)
            btn = tk.Button(grid, text=label,
                            font=("Segoe UI", 10, "bold"),
                            width=24, pady=12,
                            bg="#0d6efd", fg="white",
                            activebackground="#0b5ed7",
                            bd=0, cursor="hand2",
                            command=lambda t=tbl: self._open_crud(t))
            btn.grid(row=r, column=c, padx=8, pady=8)

    # ── Pestaña Administración ────────────────────────────────────
    def _build_tab_admin(self):
        tab = tk.Frame(self.nb, bg="#f0f4f8")
        self.nb.add(tab, text="🛡️  Administración")

        tk.Label(tab, text="Herramientas exclusivas del Administrador:",
                 font=("Segoe UI", 11), bg="#f0f4f8", fg="#333").pack(pady=(20, 8))

        admin_tables = [
            ("👥 Usuarios",         "USUARIO"),
            ("🌍 Países",           "PAIS"),
            ("🏙️ Ciudades",         "CIUDAD"),
            ("🗺️ Confederaciones",  "CONFEDERACION"),
            ("🏟️ Estadios",         "ESTADIO"),
            ("⚽ Posiciones",       "POSICION"),
            ("📦 Grupos (A-L)",     "GRUPO"),
            ("🕒 Bitácora",         "BITACORA"),
        ]
        grid = tk.Frame(tab, bg="#f0f4f8")
        grid.pack(pady=10)
        for i, (label, tbl) in enumerate(admin_tables):
            r, c = divmod(i, 3)
            color = "#198754" if tbl != "BITACORA" else "#6f42c1"
            btn = tk.Button(grid, text=label,
                            font=("Segoe UI", 10, "bold"),
                            width=24, pady=12,
                            bg=color, fg="white",
                            activebackground=color,
                            bd=0, cursor="hand2",
                            command=lambda t=tbl: self._open_crud(t))
            btn.grid(row=r, column=c, padx=8, pady=8)

    # ── Pestaña Consultas y Reportes (todos los roles) ───────────
    def _build_tab_reportes(self):
        tab = tk.Frame(self.nb, bg="#f0f4f8")
        self.nb.add(tab, text="📊  Consultas y Reportes")

        tk.Label(tab,
                 text="Módulo de inteligencia: 4 consultas + 4 reportes del enunciado",
                 font=("Segoe UI", 11), bg="#f0f4f8", fg="#333").pack(pady=(20, 8))

        btn = tk.Button(tab, text="🔍  Abrir Módulo de Consultas y Reportes",
                        font=("Segoe UI", 12, "bold"),
                        pady=14, padx=30,
                        bg="#6f42c1", fg="white",
                        activebackground="#59359a",
                        bd=0, cursor="hand2",
                        command=self._open_reports)
        btn.pack(pady=20)

    # ── Helpers ──────────────────────────────────────────────────
    def _open_crud(self, table_name):
        top = tk.Toplevel(self.root)
        # Bitácora es solo lectura para todos
        ro = (table_name == "BITACORA")
        GenericCRUD(top, table_name, read_only=ro)

    def _open_reports(self):
        top = tk.Toplevel(self.root)
        ReportsWindow(top)

    def cerrar_sesion(self):
        if messagebox.askyesno("Salir", "¿Deseas cerrar sesión y salir del sistema?"):
            conn = get_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("""UPDATE Bitacora
                                   SET fechaHoraSalida = CURRENT_TIMESTAMP
                                   WHERE codigo_usuario = :1 AND fechaHoraSalida IS NULL""",
                                (self.cod_usuario,))
                    conn.commit()
                    cur.close()
                    conn.close()
                except Exception as e:
                    print(f"Error bitácora: {e}")
            self.root.destroy()
            if self.login_win:
                self.login_win.deiconify()
            else:
                import sys
                sys.exit()


if __name__ == "__main__":
    root = tk.Tk()
    MainWindow(root, 1, "ADMINISTRADOR")
    root.mainloop()
