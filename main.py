import oracledb
from tkinter import messagebox

try:
    connection = oracledb.connect(user="SYSTEM", password="ORLO", dsn="localhost/xe")
    messagebox.showinfo("Mensaje", "Conectado a la B.D.")
except:
    messagebox.showinfo("Mensaje", "Error de conexión")
