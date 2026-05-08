import pandas as pd
from fpdf import FPDF
import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox
import fitz  # PyMuPDF
from PIL import Image, ImageTk

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(30, 42, 58)
        self.cell(0, 10, 'SISTEMA MUNDIAL DE FÚTBOL 2026', ln=True, align='C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Reporte Oficial de Consultas', ln=True, align='C')
        self.ln(5)
        self.set_draw_color(111, 66, 193)
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()} - Generado el {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}', align='C')

class PDFPreviewWindow:
    def __init__(self, parent, pdf_path):
        self.top = tk.Toplevel(parent)
        self.top.title("👁️ Vista Previa del Reporte")
        self.top.geometry("700x850")
        self.top.configure(bg="#2c3e50")
        self.top.grab_set()

        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.current_page = 0

        # Toolbar
        toolbar = tk.Frame(self.top, bg="#1e2a3a", pady=5)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="◀ Anterior", command=self.prev_page, bg="#6f42c1", fg="white").pack(side=tk.LEFT, padx=10)
        self.page_label = tk.Label(toolbar, text=f"Página 1 de {len(self.doc)}", bg="#1e2a3a", fg="white", font=("Segoe UI", 10, "bold"))
        self.page_label.pack(side=tk.LEFT, expand=True)
        tk.Button(toolbar, text="Siguiente ▶", command=self.next_page, bg="#6f42c1", fg="white").pack(side=tk.LEFT, padx=10)
        
        tk.Button(toolbar, text="📂 Abrir Externo", command=lambda: os.startfile(pdf_path), bg="#28a745", fg="white").pack(side=tk.RIGHT, padx=10)

        # Canvas para mostrar el PDF
        self.canvas_frame = tk.Frame(self.top, bg="#525659")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#525659")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.show_page()

    def show_page(self):
        page = self.doc.load_page(self.current_page)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) # Zoom para mejor calidad
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Redimensionar si es muy grande para la ventana
        img.thumbnail((650, 800), Image.LANCZOS)
        
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(350, 400, image=self.photo, anchor="center")
        self.page_label.config(text=f"Página {self.current_page + 1} de {len(self.doc)}")

    def next_page(self):
        if self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.show_page()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()

def generar_pdf_reporte(titulo_reporte, df, parent_window=None):
    if df.empty:
        messagebox.showwarning("Reporte Vacío", "No hay datos para exportar.")
        return

    try:
        pdf = PDFReport()
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(111, 66, 193)
        pdf.cell(0, 10, titulo_reporte.upper(), ln=True, align='L')
        pdf.ln(5)

        # Tabla
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(233, 236, 239)
        pdf.set_text_color(0)
        
        # Calcular ancho de columnas dinámico
        page_width = 190
        num_cols = len(df.columns)
        col_width = page_width / num_cols

        for col in df.columns:
            header_text = str(col).replace("_", " ").title()
            pdf.cell(col_width, 10, header_text, border=1, align='C', fill=True)
        pdf.ln()

        pdf.set_font('Arial', '', 9)
        for i, row in df.iterrows():
            fill = i % 2 == 0
            if fill: pdf.set_fill_color(248, 249, 250)
            else: pdf.set_fill_color(255, 255, 255)
            
            for item in row:
                val = str(item) if item is not None else "—"
                if len(val) > 30: val = val[:27] + "..."
                pdf.cell(col_width, 8, val, border=1, align='C', fill=True)
            pdf.ln()

        filename = f"reporte_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        
        # En lugar de solo abrirlo externo, abrimos la vista previa interna
        if parent_window:
            PDFPreviewWindow(parent_window, filename)
        else:
            # Si no hay parent, abrimos externo como antes
            if os.name == 'nt':
                os.startfile(filename)
        
    except Exception as e:
        messagebox.showerror("Error PDF", f"No se pudo generar el PDF: {str(e)}")
