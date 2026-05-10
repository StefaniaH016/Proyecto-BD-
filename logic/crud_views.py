import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import db
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

# Para columnas cuyo nombre termina en un FK conocido, llenamos con datos de BD
FK_COMBO_QUERY = {
    # Nuevos nombres de columnas según el esquema actualizado
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

def fetch_combo(query: str):
    """Retorna lista ['id - etiqueta', ...] para poblar Comboboxes FK."""
    res = db.run_query(query)
    if res:
        rows, _ = res
        return [f"{r[0]} - {r[1]}" for r in rows]
    return []


# =============================================================================
# Ventana de visualización + CRUD genérico
# =============================================================================
class GenericCRUD:
    def __init__(self, root, table_name, read_only=False):
        self.root = root
        self.table_name = table_name.upper()
        self.read_only = read_only
        self.root.title(f"{'Vista' if read_only else 'Gestión'} — {self.table_name}")
        self.root.geometry("900x520")
        self.root.configure(bg="#f0f4f8")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#4a6fa5", foreground="white")
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=24, fieldbackground="#ffffff")
        style.map("Treeview", background=[("selected", "#4a6fa5")])

        self.columns_info = self._get_schema()
        self.col_names    = [c["name"] for c in self.columns_info]

        # Cabecera
        hdr = tk.Frame(root, bg="#4a6fa5")
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=f"{'📂' if read_only else '🗂️'}  {self.table_name}",
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
        if not read_only:
            ttk.Button(btn_frame, text="➕  Añadir",    command=self.add_record).pack(side=tk.LEFT, padx=4)
            ttk.Button(btn_frame, text="✏️  Modificar", command=self.edit_record).pack(side=tk.LEFT, padx=4)
            ttk.Button(btn_frame, text="❌  Eliminar",  command=self.delete_record).pack(side=tk.LEFT, padx=4)

        self.load_data()

    # ---- helpers ----

    def _get_schema(self):
        cols = []
        try:
            # 1. Obtener todas las columnas
            sql_cols = """SELECT column_name, data_type, data_length, nullable 
                          FROM user_tab_columns WHERE table_name = :1 ORDER BY column_id"""
            res_cols = db.run_query(sql_cols, (self.table_name,))
            if res_cols:
                for r in res_cols[0]:
                    cols.append({"name": r[0], "type": r[1], "length": r[2], "nullable": r[3], "is_pk": False})

            # 2. Marcar las PKs
            sql_pks = """SELECT cols.column_name FROM user_constraints cons 
                         JOIN user_cons_columns cols ON cons.constraint_name = cols.constraint_name
                         WHERE cons.constraint_type = 'P' AND cons.table_name = :1"""
            res_pks = db.run_query(sql_pks, (self.table_name,))
            if res_pks:
                pk_names = {r[0] for r in res_pks[0]}
                for c in cols:
                    if c["name"] in pk_names: c["is_pk"] = True
        except Exception as e:
            messagebox.showerror("Error de esquema", str(e))
        return cols

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        res = db.run_query(f"SELECT * FROM {self.table_name}")
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
        AddWindow(self.root, self.table_name, self.columns_info, self.load_data)

    def edit_record(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione una fila para modificar.")
            return
        vals = self.tree.item(sel, "values")
        # vals contiene los valores mostrados (strings). 
        # AddWindow se encargará de convertirlos si es necesario.
        AddWindow(self.root, self.table_name, self.columns_info, self.load_data, edit_data=vals)

    def delete_record(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Seleccion", "Seleccione una fila primero.")
            return
        vals = self.tree.item(sel, "values")

        # Detectar columnas PK consultando user_constraints
        pk_cols = self._get_pk_cols()
        if not pk_cols:
            # Fallback: usar primera columna
            pk_cols = [self.col_names[0]]

        # Construir WHERE con todas las columnas PK
        where_parts = [f"{col} = :{i+1}" for i, col in enumerate(pk_cols)]
        where_clause = " AND ".join(where_parts)
        pk_vals = [vals[self.col_names.index(col)] for col in pk_cols]

        desc = ", ".join(f"{c}={v}" for c, v in zip(pk_cols, pk_vals))
        if not messagebox.askyesno("Confirmar", f"\u00bfEliminar registro ({desc})?"):
            return

        try:
            db.run_query(f"DELETE FROM {self.table_name} WHERE {where_clause}", pk_vals, commit=True)
            self.load_data()
            messagebox.showinfo("Exito", "Registro eliminado.")
        except Exception as e:
            self._handle_db_error(e)

    def _get_pk_cols(self):
        """Retorna lista de columnas que conforman la PK de la tabla."""
        sql = """SELECT cols.column_name FROM user_constraints cons 
                 JOIN user_cons_columns cols ON cons.constraint_name = cols.constraint_name 
                 AND cons.owner = cols.owner 
                 WHERE cons.constraint_type = 'P' AND cons.table_name = :1 ORDER BY cols.position"""
        res = db.run_query(sql, (self.table_name,))
        return [r[0] for r in res[0]] if res else []

    @staticmethod
    def _handle_db_error(e):
        """Traduce errores Oracle comunes a mensajes amigables en espanol."""
        import oracledb
        if isinstance(e, oracledb.DatabaseError):
            err, = e.args
            code = err.code
            if code == 2292:   # ORA-02292: registro hijo encontrado
                messagebox.showerror("Integridad",
                    "No se puede eliminar: otro registro depende de este.\n"
                    "Elimine primero los registros relacionados.")
            elif code == 2291: # ORA-02291: clave padre no encontrada
                messagebox.showerror("Referencia",
                    "El codigo de FK no existe en la tabla padre.")
            elif code == 1:    # ORA-00001: restriccion UNIQUE
                messagebox.showerror("Duplicado",
                    "Ya existe un registro con esa clave unica.")
            elif code == 2290: # ORA-02290: CHECK constraint
                messagebox.showerror("Valor invalido",
                    "El valor ingresado no cumple las restricciones del campo.")
            else:
                messagebox.showerror("Error BD", f"ORA-{code:05d}: {err.message.strip()}")
        else:
            messagebox.showerror("Error", str(e))


# =============================================================================
# Ventana de Añadir con widgets inteligentes por tipo
# =============================================================================
class AddWindow:
    def __init__(self, parent, table_name, columns_info, on_success, edit_data=None):
        self.top = tk.Toplevel(parent)
        self.edit_mode = edit_data is not None
        self.top.title(f"{'✏️ Modificar' if self.edit_mode else '✨ Añadir'} — {table_name}")
        self.top.geometry("520x640")
        self.top.configure(bg="#ffffff")
        self.top.grab_set()

        self.table_name   = table_name
        self.columns_info = columns_info
        self.on_success   = on_success
        self.entries      = {}
        self.edit_data    = edit_data

        title_text = f"Modificar registro en {table_name}" if self.edit_mode else f"Nuevo registro en {table_name}"
        tk.Label(self.top, text=title_text,
                 font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#0d6efd").pack(pady=12)
        tk.Label(self.top, text="Campos obligatorios marcados con  (*)",
                 font=("Segoe UI", 8, "italic"), bg="#ffffff", fg="#888").pack()

        # Canvas scrollable
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

        row = tk.Frame(parent, bg="#ffffff")
        row.pack(fill=tk.X, padx=15, pady=6)

        label = col_name.replace("_", " ").title()
        if nullable == "N":
            label += "  (*)"
        tk.Label(row, text=label, width=22, anchor="w",
                 font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side=tk.LEFT)

        widget = None
        key    = col_name.upper()
        is_pk  = col.get("is_pk", False)
        
        # Valor actual si estamos editando
        current_val = None
        if self.edit_mode:
            col_idx = [c["name"] for c in self.columns_info].index(col_name)
            current_val = self.edit_data[col_idx]

        # 1. Enum conocido del dominio
        if key in ENUM_MAP:
            vals = ENUM_MAP[key]
            w = ttk.Combobox(row, values=vals, state="readonly", font=("Segoe UI", 9))
            if self.edit_mode and current_val in vals:
                w.set(current_val)
            else:
                w.current(0)
            widget = w

        # 2. FK con datos de BD
        elif key in FK_COMBO_QUERY and not is_pk:
            data = fetch_combo(FK_COMBO_QUERY[key])
            w = ttk.Combobox(row, values=data, state="readonly", font=("Segoe UI", 9))
            if self.edit_mode and current_val and current_val != "—":
                # Buscar en data el que empiece por el ID de current_val
                # current_val suele ser el ID en el Treeview si es FK
                match = [d for d in data if d.startswith(str(current_val) + " - ")]
                if match: w.set(match[0])
                else: w.set(current_val)
            elif data:
                w.current(0)
            widget = w

        # 3. BLOB (imagen)
        elif col_type == "BLOB":
            sv = tk.StringVar(value="")
            lbl_text = "🖼️ [Imagen actual]" if (self.edit_mode and current_val and current_val != "—") else ""
            btn = ttk.Button(row, text="📁 Cambiar imagen…" if self.edit_mode else "📁 Buscar imagen…",
                             command=lambda v=sv: v.set(
                                 filedialog.askopenfilename(
                                     title="Seleccionar imagen",
                                     filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif")])))
            btn.pack(side=tk.LEFT, padx=4)
            tk.Label(row, textvariable=sv if not sv.get() else sv, text=lbl_text if not sv.get() else "",
                     font=("Segoe UI", 8, "italic"),
                     bg="#ffffff", fg="#555", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.entries[col_name] = sv
            return

        # 4. Fecha
        elif col_type in ("DATE", "TIMESTAMP(6)"):
            w = ttk.Entry(row, font=("Segoe UI", 9))
            if self.edit_mode and current_val and current_val != "—":
                w.insert(0, current_val)
            else:
                w.insert(0, "DD/MM/YYYY")
            widget = w

        # 5. Campo genérico
        else:
            w = ttk.Entry(row, font=("Segoe UI", 9))
            if self.edit_mode and current_val and current_val != "—":
                w.insert(0, current_val)
            widget = w

        widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entries[col_name] = widget

    # ---- guardar ----

    def save(self):
        vals = []
        for col in self.columns_info:
            col_name = col["name"]
            col_type = col["type"]
            col_len  = col["length"]
            nullable = col["nullable"]

            raw = self.entries.get(col_name)
            if raw is None:
                vals.append(None); continue

            val = raw.get().strip() if hasattr(raw, "get") else ""

            if col_type in ("DATE", "TIMESTAMP(6)") and val == "DD/MM/YYYY":
                val = ""

            # Obligatorio
            if val == "" and nullable == "N":
                messagebox.showwarning("Campo obligatorio", f"El campo '{col_name}' no puede estar vacío.")
                return

            if val == "":
                vals.append(None); continue

            # FK combo → extraer id
            if col_name.upper() in FK_COMBO_QUERY and " - " in val:
                val = val.split(" - ")[0]
            # Also handle old-style FK column names (without prefix)
            elif "COD_" + col_name.upper().replace("CODIGO_","") in FK_COMBO_QUERY and " - " in val:
                val = val.split(" - ")[0]

            # Número
            if col_type == "NUMBER":
                try:
                    float(val)
                except ValueError:
                    messagebox.showwarning("Tipo inválido", f"'{col_name}' debe ser numérico.")
                    return

            # Longitud varchar
            if "VARCHAR" in col_type and col_len and len(val) > col_len:
                messagebox.showwarning("Exceso", f"'{col_name}' máx {col_len} caracteres (actual {len(val)}).")
                return

            # Fecha
            if col_type in ("DATE", "TIMESTAMP(6)"):
                try:
                    datetime.strptime(val, "%d/%m/%Y")
                except ValueError:
                    messagebox.showwarning("Fecha inválida", f"'{col_name}' debe tener formato DD/MM/YYYY.")
                    return

            # BLOB
            if col_type == "BLOB":
                if not os.path.exists(val):
                    messagebox.showwarning("Archivo", f"No se encontró el archivo para '{col_name}'.")
                    return
                try:
                    with open(val, "rb") as f:
                        val = f.read()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo leer la imagen: {e}"); return

            vals.append(val)

        try:
            if not self.edit_mode:
                # MODO INSERT
                ph = [f"TO_DATE(:{i+1}, 'DD/MM/YYYY')" if c["type"] in ("DATE", "TIMESTAMP(6)") and vals[i] is not None else f":{i+1}" 
                      for i, c in enumerate(self.columns_info)]
                cols_str = ", ".join(c["name"] for c in self.columns_info)
                sql = f"INSERT INTO {self.table_name} ({cols_str}) VALUES ({', '.join(ph)})"
                db.run_query(sql, vals, commit=True)
                messagebox.showinfo("Exito", "Registro añadido correctamente.")
            else:
                # MODO UPDATE
                # Necesitamos identificar las PKs para el WHERE
                pk_names = [c["name"] for c in self.columns_info if c.get("is_pk")]
                if not pk_names: pk_names = [self.columns_info[0]["name"]] # Fallback
                
                set_parts = []
                final_vals = []
                idx = 1
                for i, c in enumerate(self.columns_info):
                    # Solo actualizamos columnas que NO son PK o si el usuario quiere (pero es peligroso)
                    # En este caso actualizamos todas excepto las PK del WHERE
                    col_name = c["name"]
                    if col_name in pk_names: continue
                    
                    if c["type"] in ("DATE", "TIMESTAMP(6)") and vals[i] is not None:
                        set_parts.append(f"{col_name} = TO_DATE(:{idx}, 'DD/MM/YYYY')")
                    else:
                        set_parts.append(f"{col_name} = :{idx}")
                    final_vals.append(vals[i])
                    idx += 1
                
                where_parts = []
                for pk in pk_names:
                    col_idx = [c["name"] for c in self.columns_info].index(pk)
                    where_parts.append(f"{pk} = :{idx}")
                    # Usamos el valor original de la PK que vino en edit_data
                    final_vals.append(self.edit_data[col_idx])
                    idx += 1
                
                sql = f"UPDATE {self.table_name} SET {', '.join(set_parts)} WHERE {' AND '.join(where_parts)}"
                db.run_query(sql, final_vals, commit=True)
                messagebox.showinfo("Exito", "Registro actualizado correctamente.")

            self.on_success()
            self.top.destroy()
        except Exception as e:
            GenericCRUD._handle_db_error(e)
