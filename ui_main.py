import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
import sys

class MainWindow:
    def __init__(self, root, cod_usuario, tipo_usuario):
        self.root = root
        self.root.title(f"Sistema Mundial 2026 - Rol: {tipo_usuario}")
        self.root.geometry("800x600")
        
        self.cod_usuario = cod_usuario
        self.tipo_usuario = tipo_usuario
        
        # Manejar el evento de cerrar ventana (X)
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_sesion)
        
        # Barra superior con botón de salir
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(top_frame, text=f"Panel Principal - {tipo_usuario}", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        tk.Button(top_frame, text="Cerrar Sesión", command=self.cerrar_sesion, bg="#ff4c4c", fg="white", font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
        
        # Sistema de pestañas (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Según el rol, mostramos unas pestañas u otras
        if self.tipo_usuario in ['ADMINISTRADOR', 'TRADICIONAL']:
            self.tab_crud = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_crud, text='Gestión de Datos (CRUD)')
            self.construir_tab_crud()
            
        if self.tipo_usuario == 'ADMINISTRADOR':
            self.tab_usuarios = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_usuarios, text='Gestión de Usuarios')
            self.construir_tab_usuarios()
            
        self.tab_consultas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_consultas, text='Consultas')
        self.construir_tab_consultas()
        
        self.tab_reportes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reportes, text='Reportes')
        self.construir_tab_reportes()

    def construir_tab_crud(self):
        # TODO: Implementaremos la lógica de inserción, actualización y borrado pronto.
        tk.Label(self.tab_crud, text="Módulo para gestionar Equipos, Partidos, Jugadores, etc.", font=("Arial", 12)).pack(pady=50)

    def construir_tab_usuarios(self):
        # TODO: Solo para administrador.
        tk.Label(self.tab_usuarios, text="Módulo para crear nuevos usuarios Administradores, Tradicionales o Esporádicos.", font=("Arial", 12)).pack(pady=50)

    def construir_tab_consultas(self):
        # TODO: Las consultas específicas.
        tk.Label(self.tab_consultas, text="Módulo de las 4 consultas solicitadas (Solo lectura).", font=("Arial", 12)).pack(pady=50)

    def construir_tab_reportes(self):
        # TODO: Los reportes específicos.
        tk.Label(self.tab_reportes, text="Módulo de Reportes.", font=("Arial", 12)).pack(pady=50)

    def cerrar_sesion(self):
        if messagebox.askyesno("Salir", "¿Deseas cerrar sesión y salir del sistema?"):
            conn = get_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    # Actualizamos la fecha de salida en la Bitácora
                    cursor.execute("""
                        UPDATE Bitacora 
                        SET fecha_salida = CURRENT_TIMESTAMP 
                        WHERE cod_usuario = :1 AND fecha_salida IS NULL
                    """, (self.cod_usuario,))
                    conn.commit()
                    cursor.close()
                    conn.close()
                except Exception as e:
                    print(f"Error al cerrar bitácora: {e}")
            
            self.root.destroy()
            sys.exit()

if __name__ == "__main__":
    # Para probar la ventana directamente sin pasar por el login
    root = tk.Tk()
    app = MainWindow(root, 1, "ADMINISTRADOR")
    root.mainloop()
