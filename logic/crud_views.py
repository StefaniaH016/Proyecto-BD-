import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from controllers.crud_controller import CRUDController
import os
from datetime import datetime

# =============================================================================
# CONSTANTES: enums y valores predeterminados del dominio del enunciado
# =============================================================================
ENUM_MAP = {
    "TIPO_USUARIO":  ["ADMINISTRADOR", "TRADICIONAL", "ESPORADICO"],
    "TIPO_PERSONA":  ["JUGADOR", "DIRECTOR_TECNICO"],
    "FASE":          ["Fase de Grupos", "Octavos de Final", "Cuartos de Final", "Semifinal", "Final"],
    "PAIS":          ["USA", "México", "Canadá"],
}

FK_COMBO_QUERY = {
    "CODIGO_CIUDAD":        "SELECT codigo_ciudad, nombre || ' (' || (SELECT p.nombre FROM Pais p WHERE p.codigo_pais = c.codigo_pais) || ')' FROM Ciudad c ORDER BY nombre",
    "CODIGO_CONFEDERACION": "SELECT codigo_confederacion, nombre FROM Confederacion ORDER BY nombre",
    "CODIGO_ESTADIO":       "SELECT codigo_estadio, nombre FROM Estadio ORDER BY nombre",
    "CODIGO_SELECCION":     "SELECT codigo_seleccion, nombre FROM Seleccion ORDER BY nombre",
    "CODIGO_POSICION":      "SELECT codigo_posicion, nombre FROM Posicion ORDER BY nombre",
    "CODIGO_GRUPO":         "SELECT codigo_grupo, 'Grupo ' || nombre FROM Grupo ORDER BY nombre",
    "CODIGO_PERSONA":       "SELECT codigo_persona, nombre FROM Persona ORDER BY nombre",
    "CODIGO_PARTIDO":       "SELECT codigo_partido, 'Partido ' || codigo_partido || ' (' || TO_CHAR(fecha,'DD/MM/YYYY') || ')' FROM Partido ORDER BY fecha",
    "CODIGO_USUARIO":       "SELECT codigo_usuario, nombreUsuario FROM Usuario ORDER BY nombreUsuario",
    "CODIGO_PAIS":          "SELECT codigo_pais, nombre FROM Pais ORDER BY nombre",
}

# =============================================================================
# Ventana de visualización + CRUD genérico
# =============================================================================
class GenericCRUD:
    def __init__(self, root, table_name, read_only=False):
        self.root = root
        self.table_name = table_name.upper()
        self.read_only = read_only
        is_bitacora = (self.table_name == "BITACORA")
        self.root.title(f"{'Vista' if read_only and not is_bitacora else 'Gestión'} — {self.table_name}")
        self.root.geometry("900x520")
        self.root.configure(bg="#f0f4f8")

        self.controller = CRUDController(self.table_name)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#4a6fa5", foreground="white")
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=24, fieldbackground="#ffffff")
        style.map("Treeview", background=[("selected", "#4a6fa5")])

        self.columns_info = self.controller.get_schema()
        self.col_names    = [c["name"] for c in self.columns_info]

        # Cabecera
        hdr = tk.Frame(root, bg="#4a6fa5")
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=f"{'📂' if read_only and not is_bitacora else '🗂️'}  {self.table_name}",
                 font=("Segoe UI", 13, "bold"), fg="white", bg="#4a6fa5", pady=10).pack(side=tk.LEFT, padx=15)

        # Tabla
        tree_frame = tk.Frame(root, bg="#f0f4f8")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10, 5))

        self.tree = ttk.Treeview(tree_frame, columns=self.col_names, show="headings")
        for col in self.col_names:
            self.tree.heading(col, text=col.replace("_", " ").upper())
            self.tree.column(col, width=130, anchor="center")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Botones
        btn_frame = tk.Frame(root, bg="#f0f4f8")
        btn_frame.pack(fill=tk.X, padx=15, pady=10)

        ttk.Button(btn_frame, text="🔄  Refrescar", command=self.load_data).pack(side=tk.LEFT, padx=4)
        
        if is_bitacora:
            # Solo borrar en bitácora
            ttk.Button(btn_frame, text="❌  Eliminar",  command=self.delete_record).pack(side=tk.LEFT, padx=4)
        elif not read_only:
            ttk.Button(btn_frame, text="➕  Añadir",    command=self.add_record).pack(side=tk.LEFT, padx=4)
            ttk.Button(btn_frame, text="✏️  Modificar", command=self.edit_record).pack(side=tk.LEFT, padx=4)
            ttk.Button(btn_frame, text="❌  Eliminar",  command=self.delete_record).pack(side=tk.LEFT, padx=4)

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        res = self.controller.get_data()
        if not res: return
        rows, _ = res

        for i, row in enumerate(rows):
            display = []
            for idx, val in enumerate(row):
                ct = self.columns_info[idx]["type"]
                if ct == "BLOB":
                    display.append("🖼️ [Imagen]" if val else "—")
                elif val is None:
                    display.append("—")
                elif ct in ("DATE", "TIMESTAMP(6)"):
                    display.append(val.strftime("%d/%m/%Y") if hasattr(val, "strftime") else str(val))
                else:
                    display.append(val)
            
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", tk.END, values=display, tags=(tag,))
        
        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("odd",  background="#f5f8fd")

    def add_record(self):
        if self.table_name == "DETALLES_PARTIDO_SELECCION":
            AddMatchDetailsWindow(self.root, self.load_data, controller=self.controller)
        else:
            AddWindow(self.root, self.table_name, self.columns_info, self.load_data, controller=self.controller)

    def edit_record(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione una fila para modificar.")
            return
        vals = self.tree.item(sel, "values")
        AddWindow(self.root, self.table_name, self.columns_info, self.load_data, edit_data=vals, controller=self.controller)

    def delete_record(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Seleccion", "Seleccione una fila primero.")
            return
        vals = self.tree.item(sel, "values")

        pk_cols = [c["name"] for c in self.columns_info if c.get("is_pk")]
        if not pk_cols: pk_cols = [self.col_names[0]]

        pk_vals = [vals[self.col_names.index(col)] for col in pk_cols]
        desc = ", ".join(f"{c}={v}" for c, v in zip(pk_cols, pk_vals))
        
        if not messagebox.askyesno("Confirmar", f"\u00bfEliminar registro ({desc})?"):
            return

        success, msg = self.controller.delete_record(self.table_name, pk_cols, pk_vals)
        if success:
            self.load_data()
            messagebox.showinfo("Exito", msg)
        else:
            messagebox.showerror("Error", msg)

# =============================================================================
# Ventana de Añadir con widgets inteligentes por tipo
# =============================================================================
class AddWindow:
    def __init__(self, parent, table_name, columns_info, on_success, edit_data=None, controller=None):
        self.top = tk.Toplevel(parent)
        self.edit_mode = edit_data is not None
        self.top.title(f"{'✏️ Modificar' if self.edit_mode else '✨ Añadir'} — {table_name}")
        self.top.geometry("520x640")
        self.top.configure(bg="#ffffff")
        self.top.grab_set()

        self.table_name   = table_name
        self.columns_info = columns_info
        self.on_success   = on_success
        self.controller   = controller or CRUDController(table_name)
        self.entries      = {}
        self.edit_data    = edit_data

        title_text = f"Modificar registro en {table_name}" if self.edit_mode else f"Nuevo registro en {table_name}"
        tk.Label(self.top, text=title_text,
                 font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#0d6efd").pack(pady=12)

        canvas = tk.Canvas(self.top, bg="#ffffff", highlightthickness=0)
        vsb    = ttk.Scrollbar(self.top, orient="vertical", command=canvas.yview)
        form   = tk.Frame(canvas, bg="#ffffff")
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=form, anchor="nw", width=500)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        vsb.pack(side="right", fill="y")

        for col in self.columns_info:
            self._build_field(form, col)

        btn_frame = tk.Frame(self.top, bg="#ffffff")
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="💾 Guardar", command=self.save).pack(side=tk.LEFT, padx=8)
        ttk.Button(btn_frame, text="Cancelar",   command=self.top.destroy).pack(side=tk.LEFT, padx=8)

    def _build_field(self, parent, col):
        col_name = col["name"]
        col_type = col["type"]
        nullable = col["nullable"]
        key      = col_name.upper()

        row = tk.Frame(parent, bg="#ffffff")
        row.pack(fill=tk.X, padx=15, pady=6)

        label = col_name.replace("_", " ").title() + (" (*)" if nullable == "N" else "")
        tk.Label(row, text=label, width=22, anchor="w", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side=tk.LEFT)

        current_val = None
        if self.edit_mode:
            col_idx = [c["name"] for c in self.columns_info].index(col_name)
            current_val = self.edit_data[col_idx]

        is_pk = col.get("is_pk", False)
        # Robustez: si el nombre es CODIGO_TABLA, suele ser la PK (por si falla la detección de constraints)
        if not is_pk and key == f"CODIGO_{self.table_name}":
            is_pk = True

        # No automatizamos PKs en tablas de relación (donde no son IDENTITY)
        is_auto = is_pk and self.table_name not in ["DETALLES_PARTIDO_SELECCION"]

        if is_auto and not self.edit_mode:
            w = ttk.Entry(row)
            w.insert(0, "(AUTO)")
            w.config(state="disabled")
            widget = w
        elif is_pk and self.edit_mode:
            w = ttk.Entry(row)
            if current_val and current_val != "—": w.insert(0, current_val)
            w.config(state="disabled")
            widget = w
        elif key in ENUM_MAP:
            vals = ENUM_MAP[key]
            w = ttk.Combobox(row, values=vals, state="readonly")
            if self.edit_mode and current_val in vals: w.set(current_val)
            else: w.current(0)
            widget = w
        elif key in FK_COMBO_QUERY:
            data = self.controller.fetch_combos(FK_COMBO_QUERY[key])
            w = ttk.Combobox(row, values=data, state="readonly")
            if self.edit_mode and current_val:
                match = [d for d in data if d.startswith(str(current_val) + " - ")]
                if match: w.set(match[0])
            elif data: w.current(0)
            widget = w
        elif col_type == "BLOB":
            sv = tk.StringVar()
            btn = ttk.Button(row, text="📁 Buscar...", command=lambda v=sv: v.set(filedialog.askopenfilename()))
            btn.pack(side=tk.LEFT)
            tk.Label(row, textvariable=sv, bg="#ffffff", font=("Segoe UI", 8)).pack(side=tk.LEFT)
            self.entries[col_name] = sv
            return
        else:
            w = ttk.Entry(row)
            if self.edit_mode and current_val and current_val != "—": w.insert(0, current_val)
            widget = w

        widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entries[col_name] = widget

    def save(self):
        vals = []
        for col in self.columns_info:
            raw = self.entries.get(col["name"])
            val = raw.get().strip() if hasattr(raw, "get") else ""
            
            if val == "(AUTO)": val = ""

            # 1. Si es un FK (Combo), extraer solo el código antes de validar numéricamente
            if col["name"].upper() in FK_COMBO_QUERY and " - " in val:
                val = val.split(" - ")[0]

            # 2. Validar si es numérico (ahora val ya es solo el código)
            if col["type"] == "NUMBER" and val:
                try: 
                    # Reemplazamos coma por punto para aceptar ambos formatos
                    val_str = str(val).replace(',', '.')
                    val_num = float(val_str)
                    # Lo guardamos como int o float nativo de Python
                    val = int(val_num) if val_num.is_integer() else val_num
                except ValueError: 
                    messagebox.showwarning("Error", f"El campo '{col['name']}' debe ser un valor numérico válido.")
                    return
                
            if col["type"] == "BLOB" and val and isinstance(val, str) and os.path.exists(val):
                with open(val, "rb") as f: val = f.read()
            
            vals.append(val if val != "" else None)

        original_pk_vals = None
        if self.edit_mode:
            pk_names = [c["name"] for c in self.columns_info if c.get("is_pk")]
            original_pk_vals = [self.edit_data[[c["name"] for c in self.columns_info].index(pk)] for pk in pk_names]

        success, msg = self.controller.validate_and_save(self.table_name, self.columns_info, vals, self.edit_mode, original_pk_vals)
        if success:
            messagebox.showinfo("Exito", msg)
            self.on_success()
            self.top.destroy()
        else:
            messagebox.showerror("Error", msg)

# =============================================================================
# Ventana especial para añadir Detalles_Partido_Seleccion (Registro Doble)
# =============================================================================
class AddMatchDetailsWindow:
    def __init__(self, parent, on_success, controller):
        self.top = tk.Toplevel(parent)
        self.top.title("✨ Añadir Resultado del Partido")
        self.top.geometry("520x450")
        self.top.configure(bg="#ffffff")
        self.top.grab_set()

        self.on_success = on_success
        self.controller = controller

        tk.Label(self.top, text="Registro Completo de Partido",
                 font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#0d6efd").pack(pady=12)

        form = tk.Frame(self.top, bg="#ffffff")
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Combo de Partido
        tk.Label(form, text="Partido (*)", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=0, column=0, sticky="w", pady=10)
        partidos_data = self.controller.fetch_combos(FK_COMBO_QUERY["CODIGO_PARTIDO"])
        self.cb_partido = ttk.Combobox(form, values=partidos_data, state="readonly", width=40)
        if partidos_data: self.cb_partido.current(0)
        self.cb_partido.grid(row=0, column=1, columnspan=2, sticky="w", pady=10)

        selecciones_data = self.controller.fetch_combos(FK_COMBO_QUERY["CODIGO_SELECCION"])

        # Equipo Local
        tk.Label(form, text="Equipo Local (*)", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=1, column=0, sticky="w", pady=5)
        self.cb_local = ttk.Combobox(form, values=selecciones_data, state="readonly", width=25)
        if selecciones_data: self.cb_local.current(0)
        self.cb_local.grid(row=1, column=1, sticky="w", pady=5, padx=(0, 10))

        tk.Label(form, text="Goles:", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=1, column=2, sticky="e", pady=5)
        self.txt_goles_local = ttk.Entry(form, width=5)
        self.txt_goles_local.insert(0, "0")
        self.txt_goles_local.grid(row=1, column=3, sticky="w", pady=5)

        # Equipo Visita
        tk.Label(form, text="Equipo Visita (*)", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=2, column=0, sticky="w", pady=5)
        self.cb_visita = ttk.Combobox(form, values=selecciones_data, state="readonly", width=25)
        if len(selecciones_data) > 1: self.cb_visita.current(1)
        elif selecciones_data: self.cb_visita.current(0)
        self.cb_visita.grid(row=2, column=1, sticky="w", pady=5, padx=(0, 10))

        tk.Label(form, text="Goles:", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=2, column=2, sticky="e", pady=5)
        self.txt_goles_visita = ttk.Entry(form, width=5)
        self.txt_goles_visita.insert(0, "0")
        self.txt_goles_visita.grid(row=2, column=3, sticky="w", pady=5)

        btn_frame = tk.Frame(self.top, bg="#ffffff")
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="💾 Guardar Partido", command=self.save).pack(side=tk.LEFT, padx=8)
        ttk.Button(btn_frame, text="Cancelar", command=self.top.destroy).pack(side=tk.LEFT, padx=8)

    def save(self):
        partido_str = self.cb_partido.get()
        local_str = self.cb_local.get()
        visita_str = self.cb_visita.get()
        goles_local_str = self.txt_goles_local.get().strip()
        goles_visita_str = self.txt_goles_visita.get().strip()

        if not partido_str or not local_str or not visita_str:
            messagebox.showwarning("Faltan Datos", "Debe seleccionar un partido y ambas selecciones.")
            return

        if local_str == visita_str:
            messagebox.showwarning("Error", "La selección local y visita no pueden ser la misma.")
            return

        try:
            partido_id = int(partido_str.split(" - ")[0])
            local_id = int(local_str.split(" - ")[0])
            visita_id = int(visita_str.split(" - ")[0])
            goles_local = int(goles_local_str)
            goles_visita = int(goles_visita_str)
        except ValueError:
            messagebox.showwarning("Error numérico", "Asegúrese de ingresar números enteros válidos para los goles.")
            return

        success, msg = self.controller.save_match_details(partido_id, local_id, visita_id, goles_local, goles_visita)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.on_success()
            self.top.destroy()
        else:
            messagebox.showerror("Error", msg)
