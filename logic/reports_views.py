import tkinter as tk
from tkinter import ttk, messagebox
from database import db
import pandas as pd
from logic.pdf_generator import generar_pdf_reporte

# =================================
# Módulo de Consultas y Reportes
# =================================
class ReportsWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Consultas y Reportes — Mundial 2026")
        self.root.geometry("960x680")
        self.root.configure(bg="#1e2a3a")

        # Header
        tk.Label(root, text="📊  Módulo de Consultas y Reportes",
                 font=("Segoe UI", 15, "bold"), bg="#6f42c1", fg="white", pady=14).pack(fill=tk.X)

        # Notebook
        style = ttk.Style()
        style.configure("TNotebook",     background="#1e2a3a", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[14, 6],
                        background="#2c3e50", foreground="#adb5bd")
        style.map("TNotebook.Tab",
                  background=[("selected", "#6f42c1")],
                  foreground=[("selected", "white")])

        nb = ttk.Notebook(root)
        nb.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        tab_c = tk.Frame(nb, bg="#f0f4f8"); nb.add(tab_c, text="🔍  Consultas")
        tab_r = tk.Frame(nb, bg="#f0f4f8"); nb.add(tab_r, text="📄  Reportes")

        self._build_consultas(tab_c)
        self._build_reportes(tab_r)

    # ── Utilidades ───────────────────────────────────────────────

    def _scrollable(self, parent):
        """Devuelve un Frame scrollable dentro del parent."""
        canvas = tk.Canvas(parent, bg="#f0f4f8", highlightthickness=0)
        vsb    = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame  = tk.Frame(canvas, bg="#f0f4f8")
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        return frame

    def _section(self, parent, title):
        """Crea un bloque visual con título y devuelve (controles_frame, tree)."""
        outer = tk.Frame(parent, bg="#ffffff", bd=1, relief=tk.SOLID)
        outer.pack(fill=tk.X, padx=10, pady=6)

        hdr = tk.Frame(outer, bg="#e9ecef")
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=title, font=("Segoe UI", 10, "bold"),
                 bg="#e9ecef", anchor="w", padx=10, pady=6).pack(fill=tk.X)

        ctrl = tk.Frame(outer, bg="#ffffff")
        ctrl.pack(fill=tk.X, padx=8, pady=4)

        tf   = tk.Frame(outer, bg="#ffffff")
        tf.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        tree = ttk.Treeview(tf, height=5, show="headings")
        sb   = ttk.Scrollbar(tf, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(xscrollcommand=sb.set)
        tree.pack(fill=tk.BOTH, expand=True)
        sb.pack(fill=tk.X)

        return ctrl, tree

    def _run(self, tree, sql, params=()):
        """Ejecuta query y llena el tree dinámicamente."""
        print(f"[DEBUG SQL] Ejecutando: {sql[:100]}...")
        for item in tree.get_children():
            tree.delete(item)
        conn = db.get_connection()
        if not conn: 
            print("[DEBUG SQL] Error: No se pudo obtener conexión")
            return
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            
            if not cur.description:
                print("[DEBUG SQL] Error: No hay descripción de columnas")
                return

            cols = [d[0] for d in cur.description]
            print(f"[DEBUG SQL] Columnas detectadas: {cols}")
            
            tree["columns"] = cols
            for c in cur.description:
                tree.heading(c[0], text=c[0].replace("_", " ").title())
                tree.column( c[0], width=140, anchor="center")
            
            rows = cur.fetchall()
            print(f"[DEBUG SQL] Filas encontradas: {len(rows)}")
            
            for i, row in enumerate(rows):
                tree.insert("", tk.END, values=row, tags=("even" if i%2==0 else "odd",))
            
            tree.tag_configure("even", background="#ffffff")
            tree.tag_configure("odd",  background="#f5f8fd")
        except Exception as e:
            print(f"[DEBUG SQL] EXCEPCIÓN: {str(e)}")
            messagebox.showerror("Error en consulta", str(e))
        finally:
            conn.close()

    def _combo_from_db(self, query):
        conn = db.get_connection()
        data = []
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(query)
                data = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
            except: pass
            finally: conn.close()
        return data

    def _exec_btn(self, ctrl, tree, sql, params_fn, title="Reporte"):
        # Botón Ejecutar (Vista en tabla)
        tk.Button(ctrl, text="▶ Ejecutar", font=("Segoe UI", 9, "bold"),
                  bg="#6f42c1", fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                  command=lambda t=tree, s=sql: self._run(t, s() if callable(s) else s, params_fn())).pack(side=tk.RIGHT, padx=6)
        
        # Botón PDF (Exportación)
        tk.Button(ctrl, text="📄 Exportar PDF", font=("Segoe UI", 9),
                  bg="#28a745", fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                  command=lambda: self._export_pdf(title, sql, params_fn)).pack(side=tk.RIGHT, padx=6)

    def _export_pdf(self, title, sql, params_fn):
        """Ejecuta la consulta con Pandas y genera el PDF."""
        params = params_fn()
        if params is None: return
        query = sql() if callable(sql) else sql
        conn = db.get_connection()
        if not conn: return
        try:
            df = pd.read_sql(query, conn, params=params)
            generar_pdf_reporte(title, df, self.root)
        except Exception as e:
            messagebox.showerror("Error de Datos", f"No se pudieron obtener los datos para el PDF: {e}")
        finally:
            conn.close()

    # ── CONSULTAS ────────────────────────────────────────────────
    def _build_consultas(self, parent):
        frame = self._scrollable(parent)

        # ─ C1: Jugador más costoso por confederación ─────────────
        ctrl, tree = self._section(frame,
            "C1 · Jugador más costoso por confederación")
        sql = """
            SELECT c.nombre AS confederacion,
                   p.nombre AS jugador,
                   j.valor  AS valor_USD
            FROM Jugador j
            JOIN Persona      p  ON j.codigo_persona      = p.codigo_persona
            JOIN Seleccion    s  ON j.codigo_seleccion    = s.codigo_seleccion
            JOIN Confederacion c ON s.codigo_confederacion = c.codigo_confederacion
            WHERE j.valor = (
                SELECT MAX(j2.valor) FROM Jugador j2
                JOIN Seleccion s2 ON j2.codigo_seleccion = s2.codigo_seleccion
                WHERE s2.codigo_confederacion = c.codigo_confederacion
            )
            ORDER BY j.valor DESC
        """
        self._exec_btn(ctrl, tree, sql, lambda: (), "Jugador más costoso por confederación")

        # ─ C2: Partidos en un estadio elegido ────────────────────
        ctrl, tree = self._section(frame,
            "C2 · Partidos que se llevarán a cabo en un estadio")
        stadiums = self._combo_from_db("SELECT codigo_estadio, nombre FROM Estadio ORDER BY nombre")
        tk.Label(ctrl, text="Estadio:", bg="#ffffff").pack(side=tk.LEFT)
        cb_est = ttk.Combobox(ctrl, values=stadiums, state="readonly", width=35)
        cb_est.pack(side=tk.LEFT, padx=6)
        if stadiums: cb_est.current(0)
        sql = """
            SELECT p.codigo_partido,
                   TO_CHAR(p.fecha,'DD/MM/YYYY') AS fecha,
                   p.hora,
                   e.nombre AS estadio,
                   c.nombre || ', ' || pa.nombre AS ciudad_pais
            FROM Partido  p
            JOIN Estadio  e  ON p.codigo_estadio = e.codigo_estadio
            JOIN Ciudad   c  ON e.codigo_ciudad  = c.codigo_ciudad
            JOIN Pais     pa ON c.codigo_pais    = pa.codigo_pais
            WHERE e.codigo_estadio = :1
            ORDER BY p.fecha
        """
        self._exec_btn(ctrl, tree, sql,
                       lambda: (cb_est.get().split(" - ")[0],) if cb_est.get() else (),
                       "Partidos en Estadio")

        # ─ C3: Equipo más costoso por país anfitrión ─────────────
        ctrl, tree = self._section(frame,
            "C3 · Equipo más costoso jugando en cada país anfitrión (Fase de Grupos)")
        sql = """
            WITH costo AS (
                SELECT s.codigo_seleccion, s.nombre AS equipo,
                       NVL(SUM(j.valor),0) AS valor_total
                FROM Seleccion s
                JOIN Jugador j ON j.codigo_seleccion = s.codigo_seleccion
                GROUP BY s.codigo_seleccion, s.nombre
            ),
            por_pais AS (
                SELECT DISTINCT pa.nombre AS pais, co.equipo, co.valor_total
                FROM Detalles_Partido_Seleccion dps
                JOIN Partido    p  ON dps.codigo_partido   = p.codigo_partido
                JOIN Estadio    e  ON p.codigo_estadio     = e.codigo_estadio
                JOIN Ciudad     ci ON e.codigo_ciudad      = ci.codigo_ciudad
                JOIN Pais       pa ON ci.codigo_pais       = pa.codigo_pais
                JOIN costo      co ON dps.codigo_seleccion = co.codigo_seleccion
                WHERE pa.nombre IN ('México','USA','Canadá')
                  AND p.codigo_grupo IS NOT NULL
            )
            SELECT pp.pais AS pais_anfitrion,
                   pp.equipo AS equipo_mas_costoso,
                   pp.valor_total AS valor_plantilla_USD
            FROM por_pais pp
            WHERE pp.valor_total = (
                SELECT MAX(valor_total) FROM por_pais pp2
                WHERE pp2.pais = pp.pais
            )
            AND pp.valor_total > 0
            ORDER BY pp.pais
        """
        self._exec_btn(ctrl, tree, sql, lambda: (), "Equipo más costoso por país")

        # ─ C4: Cantidad de jugadores sub-21 por equipo ───────────
        ctrl, tree = self._section(frame,
            "C4 · Cantidad de jugadores por equipo con menos de 21 años")
        sql = """
            SELECT s.nombre AS equipo,
                   COUNT(p.codigo_persona) AS cant_sub_21
            FROM Jugador j
            JOIN Persona   p ON j.codigo_persona    = p.codigo_persona
            JOIN Seleccion s ON j.codigo_seleccion  = s.codigo_seleccion
            WHERE TRUNC(MONTHS_BETWEEN(SYSDATE, p.fecha_nacimiento)/12) < 21
            GROUP BY s.nombre
            ORDER BY cant_sub_21 DESC
        """
        self._exec_btn(ctrl, tree, sql, lambda: (), "Jugadores Sub-21 por equipo")

    # ── REPORTES ─────────────────────────────────────────────────
    def _build_reportes(self, parent):
        frame = self._scrollable(parent)

        # ─ R1: Bitácora por fecha ─────────────────────────────────
        ctrl, tree = self._section(frame,
            "R1 · Usuarios que ingresaron y salieron en una fecha específica")
        tk.Label(ctrl, text="Fecha (DD/MM/YYYY):", bg="#ffffff").pack(side=tk.LEFT)
        ent_fecha = ttk.Entry(ctrl, width=14)
        ent_fecha.insert(0, "01/06/2026")
        ent_fecha.pack(side=tk.LEFT, padx=6)
        sql = """
            SELECT u.nombreUsuario,
                   u.tipo_usuario,
                   TO_CHAR(b.fechaHoraEntrada,'DD/MM/YYYY HH24:MI:SS') AS entrada,
                   TO_CHAR(b.fechaHoraSalida, 'DD/MM/YYYY HH24:MI:SS') AS salida
            FROM Bitacora b
            JOIN Usuario u ON b.codigo_usuario = u.codigo_usuario
            WHERE TRUNC(b.fechaHoraEntrada) = TO_DATE(:1,'DD/MM/YYYY')
            ORDER BY b.fechaHoraEntrada
        """
        self._exec_btn(ctrl, tree, sql, lambda: (ent_fecha.get(),), "Bitácora de Accesos")

        # ─ R2: Jugadores por peso, estatura y equipo ─────────────
        ctrl, tree = self._section(frame,
            "R2 · Jugadores filtrados por peso, estatura y equipo")

        tk.Label(ctrl, text="Peso min (kg):", bg="#ffffff").pack(side=tk.LEFT)
        e_pmin = ttk.Entry(ctrl, width=5); e_pmin.insert(0,"65"); e_pmin.pack(side=tk.LEFT, padx=2)
        tk.Label(ctrl, text="max:", bg="#ffffff").pack(side=tk.LEFT)
        e_pmax = ttk.Entry(ctrl, width=5); e_pmax.insert(0,"85"); e_pmax.pack(side=tk.LEFT, padx=(2,10))

        tk.Label(ctrl, text="Est. min (m):", bg="#ffffff").pack(side=tk.LEFT)
        e_emin = ttk.Entry(ctrl, width=5); e_emin.insert(0,"1.70"); e_emin.pack(side=tk.LEFT, padx=2)
        tk.Label(ctrl, text="max:", bg="#ffffff").pack(side=tk.LEFT)
        e_emax = ttk.Entry(ctrl, width=5); e_emax.insert(0,"1.85"); e_emax.pack(side=tk.LEFT, padx=(2,10))

        equipos = self._combo_from_db("SELECT codigo_seleccion, nombre FROM Seleccion ORDER BY nombre")
        tk.Label(ctrl, text="Equipo:", bg="#ffffff").pack(side=tk.LEFT)
        cb_eq = ttk.Combobox(ctrl, values=["Todos"] + equipos, state="readonly", width=20)
        cb_eq.current(0); cb_eq.pack(side=tk.LEFT, padx=6)

        sql_all = """
            SELECT P.NOMBRE, S.NOMBRE AS EQUIPO,
                   J.PESO, J.ESTATURA, J.VALOR,
                   NVL(POS.NOMBRE, 'Sin definir') AS POSICION
            FROM JUGADOR J
            JOIN PERSONA P ON J.CODIGO_PERSONA = P.CODIGO_PERSONA
            JOIN SELECCION S ON J.CODIGO_SELECCION = S.CODIGO_SELECCION
            LEFT JOIN POSICION POS ON J.CODIGO_POSICION = POS.CODIGO_POSICION
            WHERE J.PESO BETWEEN :1 AND :2
              AND J.ESTATURA BETWEEN :3 AND :4
            ORDER BY J.VALOR DESC"""

        sql_eq = sql_all.replace("ORDER BY", "AND S.CODIGO_SELECCION = :5 ORDER BY")

        def params_r2():
            try:
                pm, px = float(e_pmin.get()), float(e_pmax.get())
                em, ex = float(e_emin.get()), float(e_emax.get())
            except ValueError:
                messagebox.showwarning("Valores", "Ingrese números válidos."); return None
            
            eq_val = cb_eq.get()
            print(f"[DEBUG R2] Filtros: Peso {pm}-{px}, Estatura {em}-{ex}, Equipo: {eq_val}")
            
            if eq_val == "Todos":
                return (pm, px, em, ex)
            else:
                return (pm, px, em, ex, eq_val.split(" - ")[0])

        def sql_r2():
            return sql_eq if cb_eq.get() != "Todos" else sql_all

        self._exec_btn(ctrl, tree, sql_r2, params_r2, "Jugadores por Físico")

        # ─ R3: Valor total de plantilla por confederación ────────
        ctrl, tree = self._section(frame,
            "R3 · Valor total de jugadores por equipo de una confederación")
        confs = self._combo_from_db("SELECT codigo_confederacion, nombre FROM Confederacion ORDER BY nombre")
        tk.Label(ctrl, text="Confederación:", bg="#ffffff").pack(side=tk.LEFT)
        cb_conf = ttk.Combobox(ctrl, values=confs, state="readonly", width=22)
        if confs: cb_conf.current(0)
        cb_conf.pack(side=tk.LEFT, padx=6)
        sql = """
            SELECT s.nombre AS equipo,
                   SUM(j.valor) AS valor_total_USD
            FROM Seleccion s
            JOIN Jugador j ON j.codigo_seleccion = s.codigo_seleccion
            WHERE s.codigo_confederacion = :1
            GROUP BY s.nombre
            HAVING SUM(j.valor) > 0
            ORDER BY valor_total_USD DESC
        """
        self._exec_btn(ctrl, tree, sql,
                       lambda: (cb_conf.get().split(" - ")[0],) if cb_conf.get() else (),
                       "Valor Plantilla por Confederación")

        # ─ R4: Selecciones que juegan en cada país anfitrión ─────
        ctrl, tree = self._section(frame,
            "R4 · Equipos que jugarán en cada país anfitrión")
        
        # Cargar países dinámicamente
        paises_db = self._combo_from_db("SELECT codigo_pais, nombre FROM Pais ORDER BY nombre")
        paises_opciones = ["Todos"] + paises_db

        tk.Label(ctrl, text="País anfitrión:", bg="#ffffff").pack(side=tk.LEFT)
        cb_pais = ttk.Combobox(ctrl, values=paises_opciones, state="readonly", width=25)
        cb_pais.current(0)
        cb_pais.pack(side=tk.LEFT, padx=6)

        sql_all4 = """
            SELECT DISTINCT pa.nombre AS pais_anfitrion, s.nombre AS seleccion
            FROM Detalles_Partido_Seleccion dps
            JOIN Partido    p  ON dps.codigo_partido   = p.codigo_partido
            JOIN Estadio    e  ON p.codigo_estadio     = e.codigo_estadio
            JOIN Ciudad     ci ON e.codigo_ciudad      = ci.codigo_ciudad
            JOIN Pais       pa ON ci.codigo_pais       = pa.codigo_pais
            JOIN Seleccion  s  ON dps.codigo_seleccion = s.codigo_seleccion
            ORDER BY pa.nombre, s.nombre
        """
        sql_pais4 = """
            SELECT DISTINCT pa.nombre AS pais_anfitrion, s.nombre AS seleccion
            FROM Detalles_Partido_Seleccion dps
            JOIN Partido    p  ON dps.codigo_partido   = p.codigo_partido
            JOIN Estadio    e  ON p.codigo_estadio     = e.codigo_estadio
            JOIN Ciudad     ci ON e.codigo_ciudad      = ci.codigo_ciudad
            JOIN Pais       pa ON ci.codigo_pais       = pa.codigo_pais
            JOIN Seleccion  s  ON dps.codigo_seleccion = s.codigo_seleccion
            WHERE pa.codigo_pais = :1
            ORDER BY s.nombre
        """

        def run_r4(t=tree):
            val = cb_pais.get()
            if val == "Todos":
                self._run(t, sql_all4)
            else:
                pais_id = val.split(" - ")[0]
                self._run(t, sql_pais4, (pais_id,))

        tk.Button(ctrl, text="▶ Ejecutar", font=("Segoe UI", 9, "bold"),
                  bg="#6f42c1", fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                  command=run_r4).pack(side=tk.RIGHT, padx=6)

        tk.Button(ctrl, text="📄 Exportar PDF", font=("Segoe UI", 9),
                  bg="#28a745", fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                  command=lambda: self._export_pdf(
                      "Equipos por Pais Anfitrion",
                      sql_pais4 if cb_pais.get() != "Todos" else sql_all4,
                      lambda: (cb_pais.get().split(" - ")[0],) if cb_pais.get() != "Todos" else ()
                  )).pack(side=tk.RIGHT, padx=6)
