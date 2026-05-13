
import fitz
import sys

try:
    doc = fitz.open("reporte_20260509_204241.pdf")
    print(f"PDF abierto correctamente con fitz. Páginas: {len(doc)}")
    doc.close()
    sys.exit(0)
except Exception as e:
    print(f"Error al abrir PDF con fitz: {e}")
    sys.exit(1)
