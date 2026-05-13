
import oracledb
import sys

try:
    connection = oracledb.connect(user="SYSTEM", password="ORLO", dsn="localhost/xe")
    print("Connection SUCCESS")
    connection.close()
except Exception as e:
    print(f"Connection FAILED: {e}")
