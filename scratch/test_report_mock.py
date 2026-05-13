
import sys
import os
import pandas as pd
from unittest.mock import MagicMock

# Añadir el directorio raíz al path para poder importar logic
sys.path.append(os.getcwd())

from logic.pdf_generator import generar_pdf_reporte

def test_mock_report():
    print("Iniciando prueba de reporte con datos mock...")
    
    # 1. Crear datos de prueba
    data = {
        "Nombre": ["Lionel Messi", "Cristiano Ronaldo", "Kylian Mbappé", "Erling Haaland"],
        "Equipo": ["Argentina", "Portugal", "Francia", "Noruega"],
        "Valor_USD": [100000000, 80000000, 180000000, 170000000],
        "Posicion": ["Delantero", "Delantero", "Delantero", "Delantero"]
    }
    df = pd.DataFrame(data)
    
    # 2. Mockear Tkinter messagebox para evitar bloqueos en el test
    import tkinter.messagebox
    tkinter.messagebox.showwarning = MagicMock()
    tkinter.messagebox.showerror = MagicMock()
    
    # 3. Generar el reporte
    titulo = "Reporte de Prueba (Mock)"
    try:
        generar_pdf_reporte(titulo, df, parent_window=None)
        print("Llamada a generar_pdf_reporte completada.")
    except Exception as e:
        print(f"Error durante la generación: {e}")
        return False

    # 4. Verificar si se creó un archivo PDF recientemente
    files = [f for f in os.listdir('.') if f.startswith("reporte_") and f.endswith(".pdf")]
    if files:
        latest_file = max(files, key=os.path.getctime)
        print(f"ÉXITO: Reporte generado correctamente -> {latest_file}")
        return True
    else:
        print("FALLO: No se encontró el archivo PDF generado.")
        return False

if __name__ == "__main__":
    if test_mock_report():
        sys.exit(0)
    else:
        sys.exit(1)
