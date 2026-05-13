from .base_dao import BaseDAO
from database import db

class PaisDAO(BaseDAO):
    def __init__(self):
        super().__init__("PAIS")

class ConfederacionDAO(BaseDAO):
    def __init__(self):
        super().__init__("CONFEDERACION")

    def get_valor_por_equipo_en_confederacion(self, cod_confederacion):
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
        return db.run_query(sql, (cod_confederacion,))

class PosicionDAO(BaseDAO):
    def __init__(self):
        super().__init__("POSICION")

class GrupoDAO(BaseDAO):
    def __init__(self):
        super().__init__("GRUPO")

class CiudadDAO(BaseDAO):
    def __init__(self):
        super().__init__("CIUDAD")

class EstadioDAO(BaseDAO):
    def __init__(self):
        super().__init__("ESTADIO")
