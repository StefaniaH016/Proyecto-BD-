
try:
    import pandas
    print("pandas OK")
except ImportError:
    print("pandas MISSING")

try:
    import fpdf
    print("fpdf OK")
except ImportError:
    print("fpdf MISSING")

try:
    import fitz
    print("pymupdf OK")
except ImportError:
    print("pymupdf MISSING")

try:
    from PIL import Image
    print("Pillow OK")
except ImportError:
    print("Pillow MISSING")
