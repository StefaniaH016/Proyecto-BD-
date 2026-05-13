from database import db
from .base_dao import BaseDAO

class UsuarioDAO(BaseDAO):
    def __init__(self):
        super().__init__("USUARIO")

    def authenticate(self, username, password):
        sql = """SELECT codigo_usuario FROM Usuario
                 WHERE nombreUsuario = :1 AND contrasena = :2"""
        res = db.run_query(sql, (username, password))
        if res and res[0] and len(res[0]) > 0:
            return res[0][0][0]
        return None

    def authenticate_with_role(self, username, password):
        sql = """SELECT codigo_usuario, tipo_usuario FROM Usuario
                 WHERE nombreUsuario = :1 AND contrasena = :2"""
        res = db.run_query(sql, (username, password))
        if res and res[0] and len(res[0]) > 0:
            return res[0][0][0], res[0][0][1] # (id, tipo)
        return None

    def registrar_entrada(self, user_id):
        sql = """INSERT INTO Bitacora (codigo_usuario, fechaHoraEntrada)
                 VALUES (:1, CURRENT_TIMESTAMP)"""
        return db.run_query(sql, (user_id,), commit=True)

    def registrar_salida(self, user_id):
        # Usamos :1 y :2 aunque sea el mismo valor para evitar ambigüedad en oracledb positional binds
        sql = """UPDATE Bitacora 
                 SET fechaHoraSalida = CURRENT_TIMESTAMP 
                 WHERE codigo_usuario = :1 AND fechaHoraSalida IS NULL
                 AND fechaHoraEntrada = (SELECT MAX(fechaHoraEntrada) 
                                         FROM Bitacora WHERE codigo_usuario = :2)"""
        return db.run_query(sql, (user_id, user_id), commit=True)

    def get_bitacora_by_fecha(self, fecha_str):
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
        return db.run_query(sql, (fecha_str,))
