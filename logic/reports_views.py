import tkinter as tk
from tkinter import ttk, messagebox
from database import db
import pandas as pd
from logic.pdf_generator import generar_pdf_reporte

# =============================================================================
# Módulo de Consultas y Reportes — Cumple exactamente el enunciado del proyecto
# =============================================================================
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
        for item in tree.get_children():
            tree.delete(item)
        conn = db.get_connection()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            cols = [d[0].replace("_", " ").title() for d in cur.description]
            tree["columns"] = [d[0] for d in cur.description]
            for c in cur.description:
                tree.heading(c[0], text=c[0].replace("_", " ").title())
                tree.column( c[0], width=140, anchor="center")
            for i, row in enumerate(cur.fetchall()):
                tree.insert("", tk.END, values=row, tags=("even" if i%2==0 else "odd",))
            tree.tag_configure("even", background="#ffffff")
            tree.tag_configure("odd",  background="#f5f8fd")
        except Exception as e:
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
                  command=lambda: self._run(tree, sql, params_fn())).pack(side=tk.RIGHT, padx=6)
        
        # Botón PDF (Exportación)
        tk.Button(ctrl, text="📄 Exportar PDF", font=("Segoe UI", 9),
                  bg="#28a745", fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                  command=lambda: self._export_pdf(title, sql, params_fn)).pack(side=tk.RIGHT, padx=6)

    def _export_pdf(self, title, sql, params_fn):
        """Ejecuta la consulta con Pandas y genera el PDF."""
        params = params_fn()
        conn = db.get_connection()
        if not conn: return
        try:
            # Reemplazar placeholders :1, :2... por :idx para pandas si fuera necesario, 
            # pero oracledb + pandas suelen manejar bien los posicionales.
            df = pd.read_sql(sql, conn, params=params)
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
            JOIN Persona     p  ON j.cod_persona      = p.codigo
            JOIN Seleccion   s  ON p.cod_seleccion     = s.codigo
            JOIN Confederacion c ON s.cod_confederacion = c.codigo
            WHERE j.valor = (
                SELECT MAX(j2.valor) FROM Jugador j2
                JOIN Persona   p2 ON j2.cod_persona    = p2.codigo
                JOIN Seleccion s2 ON p2.cod_seleccion  = s2.codigo
                WHERE s2.cod_confederacion = c.codigo
            )
            ORDER BY j.valor DESC
        """
        self._exec_btn(ctrl, tree, sql, lambda: (), "Jugador más costoso por confederación")

        # ─ C2: Partidos en un estadio elegido ────────────────────
        ctrl, tree = self._section(frame,
            "C2 · Partidos que se llevarán a cabo en un estadio")
        stadiums = self._combo_from_db("SELECT codigo, nombre FROM Estadio ORDER BY nombre")
        tk.Label(ctrl, text="Estadio:", bg="#ffffff").pack(side=tk.LEFT)
        cb_est = ttk.Combobox(ctrl, values=stadiums, state="readonly", width=35)
        cb_est.pack(side=tk.LEFT, padx=6)
        if stadiums: cb_est.current(0)
        sql = """
            SELECT p.codigo,
                   p.fase,
                   TO_CHAR(p.fecha,'DD/MM/YYYY') AS fecha,
                   p.hora,
                   e.nombre AS estadio,
                   c.nombre || ', ' || c.pais AS ciudad
            FROM Partido p
            JOIN Estadio e ON p.cod_estadio = e.codigo
            JOIN Ciudad  c ON e.cod_ciudad  = c.codigo
            WHERE e.codigo = :1
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
                SELECT s.codigo, s.nombre AS equipo,
                       NVL(SUM(j.valor),0) AS valor_total
                FROM Seleccion s
                LEFT JOIN Persona p ON p.cod_seleccion = s.codigo AND p.tipo_persona = 'JUGADOR'
                LEFT JOIN Jugador j ON j.cod_persona = p.codigo
                GROUP BY s.codigo, s.nombre
            ),
            por_pais AS (
                SELECT DISTINCT ci.pais, co.equipo, co.valor_total
                FROM Participacion pt
                JOIN Partido    pa ON pt.cod_partido   = pa.codigo
                JOIN Estadio    e  ON pa.cod_estadio   = e.codigo
                JOIN Ciudad     ci ON e.cod_ciudad     = ci.codigo
                JOIN costo      co ON pt.cod_seleccion = co.codigo
                WHERE ci.pais IN ('México','USA','Canadá')
                  AND UPPER(pa.fase) LIKE '%GRUPO%'
            )
            SELECT pp.pais AS pais_anfitrion,
                   pp.equipo AS equipo_mas_costoso,
                   pp.valor_total AS valor_plantilla_USD
            FROM por_pais pp
            WHERE pp.valor_total = (
                SELECT MAX(valor_total) FROM por_pais pp2
                WHERE pp2.pais = pp.pais
            )
            ORDER BY pp.pais
        """
        self._exec_btn(ctrl, tree, sql, lambda: (), "Equipo más costoso por país")

        # ─ C4: Cantidad de jugadores sub-21 por equipo ───────────
        ctrl, tree = self._section(frame,
            "C4 · Cantidad de jugadores por equipo con menos de 21 años")
        sql = """
            SELECT s.nombre AS equipo,
                   COUNT(p.codigo) AS cant_sub_21
            FROM Seleccion s
            JOIN Persona p ON p.cod_seleccion = s.codigo
            WHERE p.tipo_persona = 'JUGADOR'
              AND TRUNC(MONTHS_BETWEEN(SYSDATE, p.fecha_nacimiento)/12) < 21
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
            SELECT u.nombre_usuario,
                   u.tipo_usuario,
                   TO_CHAR(b.fecha_entrada,'DD/MM/YYYY HH24:MI:SS') AS entrada,
                   TO_CHAR(b.fecha_salida, 'DD/MM/YYYY HH24:MI:SS') AS salida
            FROM Bitacora b
            JOIN Usuario u ON b.cod_usuario = u.codigo
            WHERE TRUNC(b.fecha_entrada) = TO_DATE(:1,'DD/MM/YYYY')
            ORDER BY b.fecha_entrada
        """
        self._exec_btn(ctrl, tree, sql, lambda: (ent_fecha.get(),), "Bitácora de Accesos")

        # ─ R2: Jugadores por peso, estatura y equipo ─────────────
        ctrl, tree = self._section(frame,
            "R2 · Jugadores filtrados por peso, estatura y equipo")

        tk.Label(ctrl, text="Peso min:", bg="#ffffff").pack(side=tk.LEFT)
        e_pmin = ttk.Entry(ctrl, width=5); e_pmin.insert(0,"50"); e_pmin.pack(side=tk.LEFT, padx=2)
        tk.Label(ctrl, text="max:", bg="#ffffff").pack(side=tk.LEFT)
        e_pmax = ttk.Entry(ctrl, width=5); e_pmax.insert(0,"120"); e_pmax.pack(side=tk.LEFT, padx=(2,10))

        tk.Label(ctrl, text="Est. min:", bg="#ffffff").pack(side=tk.LEFT)
        e_emin = ttk.Entry(ctrl, width=5); e_emin.insert(0,"1.50"); e_emin.pack(side=tk.LEFT, padx=2)
        tk.Label(ctrl, text="max:", bg="#ffffff").pack(side=tk.LEFT)
        e_emax = ttk.Entry(ctrl, width=5); e_emax.insert(0,"2.20"); e_emax.pack(side=tk.LEFT, padx=(2,10))

        equipos = self._combo_from_db("SELECT codigo, nombre FROM Seleccion ORDER BY nombre")
        tk.Label(ctrl, text="Equipo:", bg="#ffffff").pack(side=tk.LEFT)
        cb_eq = ttk.Combobox(ctrl, values=["Todos"] + equipos, state="readonly", width=20)
        cb_eq.current(0); cb_eq.pack(side=tk.LEFT, padx=6)

        sql_all  = """
            SELECT p.nombre, s.nombre AS equipo,
                   j.peso, j.estatura, j.valor,
                   pos.nombre AS posicion
            FROM Jugador j
            JOIN Persona   p   ON j.cod_persona    = p.codigo
            JOIN Seleccion s   ON p.cod_seleccion  = s.codigo
            JOIN Posicion  pos ON j.cod_posicion   = pos.codigo
            WHERE j.peso     BETWEEN :1 AND :2
              AND j.estatura BETWEEN :3 AND :4
            ORDER BY j.valor DESC"""
        sql_eq   = sql_all.replace("ORDER BY", "AND s.codigo = :5 ORDER BY")

        def run_r2():
            try:
                pm, px = float(e_pmin.get()), float(e_pmax.get())
                em, ex = float(e_emin.get()), float(e_emax.get())
            except ValueError:
                messagebox.showwarning("Valores", "Ingrese números válidos."); return
            eq_val = cb_eq.get()
            if eq_val == "Todos":
                self._run(tree, sql_all, (pm, px, em, ex))
            else:
                eq_id = eq_val.split(" - ")[0]
                self._run(tree, sql_eq, (pm, px, em, ex, eq_id))

        tk.Button(ctrl, text="▶ Ejecutar", font=("Segoe UI", 9, "bold"),
                  bg="#6f42c1", fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                  command=run_r2).pack(side=tk.RIGHT, padx=6)
        
        tk.Button(ctrl, text="📄 Exportar PDF", font=("Segoe UI", 9),
                  bg="#28a745", fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                  command=lambda: self._export_pdf("Jugadores por Físico", 
                                                   sql_eq if cb_eq.get() != "Todos" else sql_all,
                                                   lambda: (float(e_pmin.get()), float(e_pmax.get()), 
                                                            float(e_emin.get()), float(e_emax.get())) + 
                                                           ((cb_eq.get().split(" - ")[0],) if cb_eq.get() != "Todos" else ())
                                                  )).pack(side=tk.RIGHT, padx=6)

        # ─ R3: Valor total de plantilla por confederación ────────
        ctrl, tree = self._section(frame,
            "R3 · Valor total de jugadores por equipo de una confederación")
        confs = self._combo_from_db("SELECT codigo, nombre FROM Confederacion ORDER BY nombre")
        tk.Label(ctrl, text="Confederación:", bg="#ffffff").pack(side=tk.LEFT)
        cb_conf = ttk.Combobox(ctrl, values=confs, state="readonly", width=22)
        if confs: cb_conf.current(0)
        cb_conf.pack(side=tk.LEFT, padx=6)
        sql = """
            SELECT s.nombre AS equipo,
                   NVL(SUM(j.valor),0) AS valor_total_USD
            FROM Seleccion s
            LEFT JOIN Persona p ON p.cod_seleccion = s.codigo AND p.tipo_persona = 'JUGADOR'
            LEFT JOIN Jugador j ON j.cod_persona   = p.codigo
            WHERE s.cod_confederacion = :1
            GROUP BY s.nombre
            ORDER BY valor_total_USD DESC
        """
        self._exec_btn(ctrl, tree, sql,
                       lambda: (cb_conf.get().split(" - ")[0],) if cb_conf.get() else (),
                       "Valor Plantilla por Confederación")

        # ─ R4: Selecciones que juegan en cada país anfitrión ─────
        ctrl, tree = self._section(frame,
            "R4 · Equipos que jugarán en cada país anfitrión")
        paises = ["Todos", "México", "USA", "Canadá"]
        tk.Label(ctrl, text="País anfitrión:", bg="#ffffff").pack(side=tk.LEFT)
        cb_pais = ttk.Combobox(ctrl, values=paises, state="readonly", width=15)
        cb_pais.current(0); cb_pais.pack(side=tk.LEFT, padx=6)

        sql_all4 = """
            SELECT DISTINCT ci.pais AS pais_anfitrion, s.nombre AS seleccion
            FROM Participacion pt
            JOIN Partido    pa ON pt.cod_partido   = pa.codigo
            JOIN Estadio    e  ON pa.cod_estadio   = e.codigo
            JOIN Ciudad     ci ON e.cod_ciudad     = ci.codigo
            JOIN Seleccion  s  ON pt.cod_seleccion = s.codigo
            WHERE ci.pais IN ('México','USA','Canadá')
            ORDER BY ci.pais, s.nombre
        """
        sql_pais4 = """
            SELECT DISTINCT ci.pais AS pais_anfitrion, s.nombre AS seleccion
            FROM Participacion pt
            JOIN Partido    pa ON pt.cod_partido   = pa.codigo
            JOIN Estadio    e  ON pa.cod_estadio   = e.codigo
            JOIN Ciudad     ci ON e.cod_ciudad     = ci.codigo
            JOIN Seleccion  s  ON pt.cod_seleccion = s.codigo
            WHERE ci.pais = :1
            ORDER BY s.nombre
        """

        def run_r4():
            p = cb_pais.get()
            if p == "Todos":
                self._run(tree, sql_all4)
            else:
                self._run(tree, sql_pais4, (p,))

        tk.Button(ctrl, text="▶ Ejecutar", font=("Segoe UI", 9, "bold"),
                  bg="#6f42c1", fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                  command=run_r4).pack(side=tk.RIGHT, padx=6)

        tk.Button(ctrl, text="📄 Exportar PDF", font=("Segoe UI", 9),
                  bg="#28a745", fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                  command=lambda: self._export_pdf("Equipos por País Anfitrión",
                                                   sql_pais4 if cb_pais.get() != "Todos" else sql_all4,
                                                   lambda: (cb_pais.get(),) if cb_pais.get() != "Todos" else ()
                                                  )).pack(side=tk.RIGHT, padx=6)
