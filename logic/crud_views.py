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
    "COD_CIUDAD":       "SELECT codigo, nombre || ' (' || pais || ')' FROM Ciudad ORDER BY nombre",
    "COD_CONFEDERACION":"SELECT codigo, nombre FROM Confederacion ORDER BY nombre",
    "COD_ESTADIO":      "SELECT codigo, nombre FROM Estadio ORDER BY nombre",
    "COD_SELECCION":    "SELECT codigo, nombre FROM Seleccion ORDER BY nombre",
    "COD_POSICION":     "SELECT codigo, nombre FROM Posicion ORDER BY nombre",
    "COD_GRUPO":        "SELECT codigo, 'Grupo ' || letra FROM Grupo ORDER BY letra",
    "COD_PERSONA":      "SELECT codigo, nombre FROM Persona ORDER BY nombre",
    "COD_PARTIDO":      "SELECT codigo, 'Partido ' || codigo || ' - ' || fase || ' (' || TO_CHAR(fecha,''DD/MM/YYYY'') || ')' FROM Partido ORDER BY fecha",
    "COD_USUARIO":      "SELECT codigo, nombre_usuario FROM Usuario ORDER BY nombre_usuario",
}

def fetch_combo(query: str):
    """Retorna lista ['id - etiqueta', ...] para poblar Comboboxes FK."""
    conn = db.get_connection()
    data = []
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(query)
            data = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        except Exception as e:
            print(f"Error fetch_combo: {e}")
        finally:
            conn.close()
    return data


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
            ttk.Button(btn_frame, text="➕  Añadir",   command=self.add_record).pack(side=tk.LEFT, padx=4)
            ttk.Button(btn_frame, text="❌  Eliminar", command=self.delete_record).pack(side=tk.LEFT, padx=4)

        self.load_data()

    # ---- helpers ----

    def _get_schema(self):
        conn = db.get_connection()
        cols = []
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""SELECT column_name, data_type, data_length, nullable
                               FROM user_tab_columns
                               WHERE table_name = :1
                               ORDER BY column_id""", (self.table_name,))
                for r in cur.fetchall():
                    cols.append({"name": r[0], "type": r[1], "length": r[2], "nullable": r[3]})
            except Exception as e:
                messagebox.showerror("Error de esquema", str(e))
            finally:
                conn.close()
        return cols

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = db.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {self.table_name}")
            for i, row in enumerate(cur.fetchall()):
                display = []
                for idx, val in enumerate(row):
                    ct = self.columns_info[idx]["type"]
                    if ct == "BLOB":
                        display.append("🖼️ [Imagen]" if val else "—")
                    elif val is None:
                        display.append("—")
                    elif ct in ("DATE", "TIMESTAMP(6)"):
                        try:
                            display.append(val.strftime("%d/%m/%Y"))
                        except:
                            display.append(str(val))
                    else:
                        display.append(val)
                tag = "even" if i % 2 == 0 else "odd"
                self.tree.insert("", tk.END, values=display, tags=(tag,))
            self.tree.tag_configure("even", background="#ffffff")
            self.tree.tag_configure("odd",  background="#f5f8fd")
        except Exception as e:
            messagebox.showerror("Error al cargar", str(e))
        finally:
            conn.close()

    def add_record(self):
        AddWindow(self.root, self.table_name, self.columns_info, self.load_data)

    def delete_record(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione una fila primero.")
            return
        vals = self.tree.item(sel, "values")
        pk_val = vals[0]
        pk_col = self.col_names[0]
        if not messagebox.askyesno("Confirmar", f"¿Eliminar registro {pk_col}={pk_val}?"):
            return
        conn = db.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(f"DELETE FROM {self.table_name} WHERE {pk_col} = :1", (pk_val,))
                conn.commit()
                self.load_data()
                messagebox.showinfo("Éxito", "Registro eliminado.")
            except Exception as e:
                err = str(e).upper()
                if "CHILD RECORD FOUND" in err:
                    messagebox.showerror("Integridad", "No puede eliminar: otro registro depende de éste.")
                else:
                    messagebox.showerror("Error", str(e))
            finally:
                conn.close()


# =============================================================================
# Ventana de Añadir con widgets inteligentes por tipo
# =============================================================================
class AddWindow:
    def __init__(self, parent, table_name, columns_info, on_success):
        self.top = tk.Toplevel(parent)
        self.top.title(f"✨ Añadir — {table_name}")
        self.top.geometry("520x640")
        self.top.configure(bg="#ffffff")
        self.top.grab_set()

        self.table_name   = table_name
        self.columns_info = columns_info
        self.on_success   = on_success
        self.entries      = {}

        tk.Label(self.top, text=f"Nuevo registro en {table_name}",
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

        # 1. Enum conocido del dominio
        if key in ENUM_MAP:
            w = ttk.Combobox(row, values=ENUM_MAP[key], state="readonly", font=("Segoe UI", 9))
            w.current(0)
            widget = w

        # 2. FK con datos de BD
        elif key in FK_COMBO_QUERY:
            data = fetch_combo(FK_COMBO_QUERY[key])
            w = ttk.Combobox(row, values=data, state="readonly", font=("Segoe UI", 9))
            if data:
                w.current(0)
            widget = w

        # 3. BLOB (imagen)
        elif col_type == "BLOB":
            sv = tk.StringVar(value="")
            btn = ttk.Button(row, text="📁 Buscar imagen…",
                             command=lambda v=sv: v.set(
                                 filedialog.askopenfilename(
                                     title="Seleccionar imagen",
                                     filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif")])))
            btn.pack(side=tk.LEFT, padx=4)
            tk.Label(row, textvariable=sv, font=("Segoe UI", 8, "italic"),
                     bg="#ffffff", fg="#555", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.entries[col_name] = sv
            return  # ya configurado

        # 4. Fecha
        elif col_type in ("DATE", "TIMESTAMP(6)"):
            w = ttk.Entry(row, font=("Segoe UI", 9))
            w.insert(0, "DD/MM/YYYY")
            widget = w

        # 5. Campo genérico
        else:
            w = ttk.Entry(row, font=("Segoe UI", 9))
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

        conn = db.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            ph  = []
            for idx, col in enumerate(self.columns_info):
                if col["type"] in ("DATE", "TIMESTAMP(6)") and vals[idx] is not None:
                    ph.append(f"TO_DATE(:{idx+1}, 'DD/MM/YYYY')")
                else:
                    ph.append(f":{idx+1}")
            cols_str = ", ".join(c["name"] for c in self.columns_info)
            sql = f"INSERT INTO {self.table_name} ({cols_str}) VALUES ({', '.join(ph)})"
            cur.execute(sql, vals)
            conn.commit()
            messagebox.showinfo("Éxito", "Registro añadido correctamente.")
            self.on_success()
            self.top.destroy()
        except Exception as e:
            err = str(e).upper()
            if "UNIQUE CONSTRAINT" in err:
                messagebox.showerror("Duplicado", "Ya existe un registro con esa clave única.")
            elif "PARENT KEY NOT FOUND" in err:
                messagebox.showerror("Referencia", "El código de la FK no existe en la tabla padre.")
            elif "CHECK CONSTRAINT" in err:
                messagebox.showerror("Valor inválido", "El valor ingresado no es válido para este campo.")
            else:
                messagebox.showerror("Error BD", str(e))
        finally:
            conn.close()
