import tkinter as tk
from tkinter import ttk, messagebox
from controllers.report_controller import ReportController
import pandas as pd
from logic.pdf_generator import generar_pdf_reporte
# pyrefly: ignore [missing-import]
from tkcalendar import DateEntry
from datetime import datetime

# =================================
# Módulo de Consultas y Reportes
# =================================
class ReportsWindow:
    def __init__(self, root):
        self.root = root
        self.controller = ReportController()
        
        self.root.title("📊 Consultas y Reportes — Mundial 2026")
        self.root.geometry("960x680")
        self.root.configure(bg="#1e2a3a")

        # Header
        tk.Label(root, text="📊  Módulo de Consultas y Reportes",
                 font=("Segoe UI", 15, "bold"), bg="#6f42c1", fg="white", pady=14).pack(fill=tk.X)

        nb = ttk.Notebook(root)
        nb.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        tab_c = tk.Frame(nb, bg="#f0f4f8"); nb.add(tab_c, text="🔍  Consultas")
        tab_r = tk.Frame(nb, bg="#f0f4f8"); nb.add(tab_r, text="📄  Reportes")

        self._build_consultas(tab_c)
        self._build_reportes(tab_r)

    def _scrollable(self, parent):
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
        outer = tk.Frame(parent, bg="#ffffff", bd=1, relief=tk.SOLID)
        outer.pack(fill=tk.X, padx=10, pady=6)
        hdr = tk.Frame(outer, bg="#e9ecef")
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=title, font=("Segoe UI", 10, "bold"), bg="#e9ecef", anchor="w", padx=10, pady=6).pack(fill=tk.X)
        ctrl = tk.Frame(outer, bg="#ffffff")
        ctrl.pack(fill=tk.X, padx=8, pady=4)
        tf = tk.Frame(outer, bg="#ffffff")
        tf.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        tree = ttk.Treeview(tf, height=5, show="headings")
        sb = ttk.Scrollbar(tf, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(xscrollcommand=sb.set)
        tree.pack(fill=tk.BOTH, expand=True)
        sb.pack(fill=tk.X)
        return ctrl, tree

    def _run(self, tree, report_name, params=()):
        for item in tree.get_children(): tree.delete(item)
        try:
            res = self.controller.run_report(report_name, params)
            if not res: return
            rows, cols = res
            tree["columns"] = cols
            for c in cols:
                tree.heading(c, text=c.replace("_", " ").title())
                tree.column(c, width=140, anchor="center")
            for i, row in enumerate(rows):
                tree.insert("", tk.END, values=row, tags=("even" if i%2==0 else "odd",))
            tree.tag_configure("even", background="#ffffff")
            tree.tag_configure("odd",  background="#f5f8fd")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _exec_btn(self, ctrl, tree, report_name, params_fn, title="Reporte"):
        tk.Button(ctrl, text="▶ Ejecutar", font=("Segoe UI", 9, "bold"), bg="#6f42c1", fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                  command=lambda: self._run(tree, report_name, params_fn())).pack(side=tk.RIGHT, padx=6)
        tk.Button(ctrl, text="📄 Exportar PDF", font=("Segoe UI", 9), bg="#28a745", fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                  command=lambda: self._export_pdf(title, report_name, params_fn)).pack(side=tk.RIGHT, padx=6)

    def _export_pdf(self, title, report_name, params_fn):
        params = params_fn()
        if params is None: return
        try:
            rows, cols = self.controller.run_report(report_name, params)
            df = pd.DataFrame(rows, columns=cols)
            generar_pdf_reporte(title, df, self.root)
        except Exception as e:
            messagebox.showerror("Error PDF", str(e))

    def _build_consultas(self, parent):
        frame = self._scrollable(parent)
        
        c1_ctrl, c1_tree = self._section(frame, "C1 · Jugador más costoso por confederación")
        self._exec_btn(c1_ctrl, c1_tree, "most_expensive_player", lambda: (), "Jugador más costoso")

        c2_ctrl, c2_tree = self._section(frame, "C2 · Partidos en un estadio")
        stadiums = self.controller.get_combo_data("SELECT codigo_estadio, nombre FROM Estadio ORDER BY nombre")
        cb_est = ttk.Combobox(c2_ctrl, values=stadiums, state="readonly", width=35)
        cb_est.pack(side=tk.LEFT, padx=6); 
        if stadiums: cb_est.current(0)
        self._exec_btn(c2_ctrl, c2_tree, "matches_by_stadium", lambda: (cb_est.get().split(" - ")[0],) if cb_est.get() else (), "Partidos")

        c3_ctrl, c3_tree = self._section(frame, "C3 · Equipo más costoso por país anfitrión")
        self._exec_btn(c3_ctrl, c3_tree, "most_expensive_team", lambda: (), "Equipo más costoso")

        c4_ctrl, c4_tree = self._section(frame, "C4 · Cantidad de jugadores sub-21")
        self._exec_btn(c4_ctrl, c4_tree, "sub_21_count", lambda: (), "Sub-21")

    def _build_reportes(self, parent):
        frame = self._scrollable(parent)

        r1_ctrl, r1_tree = self._section(frame, "R1 · Bitácora por fecha")
        # Selector de fecha con calendario y restricción de fechas futuras
        cal_fecha = DateEntry(r1_ctrl, width=14, background='#6f42c1', foreground='white', 
                              borderwidth=2, date_pattern='dd/mm/yyyy', 
                              maxdate=datetime.now().date())
        cal_fecha.pack(side=tk.LEFT, padx=6)
        
        self._exec_btn(r1_ctrl, r1_tree, "bitacora_by_date", lambda: (cal_fecha.get(),), "Bitácora")

        r2_ctrl, r2_tree = self._section(frame, "R2 · Jugadores por peso/estatura")
        tk.Label(r2_ctrl, text="Filtros:", bg="#ffffff").pack(side=tk.LEFT)
        e_pmin = ttk.Entry(r2_ctrl, width=4); e_pmin.insert(0,"65"); e_pmin.pack(side=tk.LEFT, padx=2)
        e_pmax = ttk.Entry(r2_ctrl, width=4); e_pmax.insert(0,"85"); e_pmax.pack(side=tk.LEFT, padx=2)
        e_emin = ttk.Entry(r2_ctrl, width=4); e_emin.insert(0,"1.70"); e_emin.pack(side=tk.LEFT, padx=2)
        e_emax = ttk.Entry(r2_ctrl, width=4); e_emax.insert(0,"1.85"); e_emax.pack(side=tk.LEFT, padx=2)
        equipos = self.controller.get_combo_data("SELECT codigo_seleccion, nombre FROM Seleccion ORDER BY nombre")
        cb_eq = ttk.Combobox(r2_ctrl, values=["Todos"] + equipos, state="readonly", width=15); cb_eq.current(0); cb_eq.pack(side=tk.LEFT, padx=4)
        
        def params_r2():
            try:
                p = (float(e_pmin.get()), float(e_pmax.get()), float(e_emin.get()), float(e_emax.get()))
                eq = cb_eq.get()
                return p if eq == "Todos" else p + (eq.split(" - ")[0],)
            except: return None
        self._exec_btn(r2_ctrl, r2_tree, "filtered_players", params_r2, "Jugadores Filtrados")

        r3_ctrl, r3_tree = self._section(frame, "R3 · Valor por equipo en confederación")
        confs = self.controller.get_combo_data("SELECT codigo_confederacion, nombre FROM Confederacion ORDER BY nombre")
        cb_conf = ttk.Combobox(r3_ctrl, values=confs, state="readonly", width=22); 
        if confs: cb_conf.current(0)
        cb_conf.pack(side=tk.LEFT, padx=6)
        self._exec_btn(r3_ctrl, r3_tree, "value_by_confed", lambda: (cb_conf.get().split(" - ")[0],) if cb_conf.get() else (), "Valor por Confed")

        r4_ctrl, r4_tree = self._section(frame, "R4 · Equipos por país anfitrión")
        paises = self.controller.get_combo_data("SELECT codigo_pais, nombre FROM Pais ORDER BY nombre")
        cb_pais = ttk.Combobox(r4_ctrl, values=["Todos"] + paises, state="readonly", width=25); cb_pais.current(0); cb_pais.pack(side=tk.LEFT, padx=6)
        self._exec_btn(r4_ctrl, r4_tree, "teams_by_host", lambda: (cb_pais.get().split(" - ")[0],) if cb_pais.get() != "Todos" else ("Todos",), "Equipos por País")
