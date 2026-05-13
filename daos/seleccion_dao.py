from .base_dao import BaseDAO
from database import db

class SeleccionDAO(BaseDAO):
    def __init__(self):
        super().__init__("SELECCION")

    def get_by_confederacion(self, cod_confederacion):
        sql = "SELECT * FROM Seleccion WHERE codigo_confederacion = :1"
        return db.run_query(sql, (cod_confederacion,))

    def get_by_grupo(self, cod_grupo):
        sql = "SELECT * FROM Seleccion WHERE codigo_grupo = :1"
        return db.run_query(sql, (cod_grupo,))

    def get_most_expensive_by_host_country(self):
        sql = """
            WITH costo AS (
                SELECT s.codigo_seleccion, s.nombre AS equipo,
                       NVL(SUM(j.valor),0) AS valor_total
                FROM Seleccion s
                JOIN Jugador j ON j.codigo_seleccion = s.codigo_seleccion
                GROUP BY s.codigo_seleccion, s.nombre
            ),
            por_pais AS (
                SELECT DISTINCT pa.nombre AS pais, co.equipo, co.valor_total
                FROM Detalles_Partido_Seleccion dps
                JOIN Partido    p  ON dps.codigo_partido   = p.codigo_partido
                JOIN Estadio    e  ON p.codigo_estadio     = e.codigo_estadio
                JOIN Ciudad     ci ON e.codigo_ciudad      = ci.codigo_ciudad
                JOIN Pais       pa ON ci.codigo_pais       = pa.codigo_pais
                JOIN costo      co ON dps.codigo_seleccion = co.codigo_seleccion
                WHERE pa.nombre IN ('México','USA','Canadá')
                  AND p.codigo_grupo IS NOT NULL
            )
            SELECT pp.pais AS pais_anfitrion,
                   pp.equipo AS equipo_mas_costoso,
                   pp.valor_total AS valor_plantilla_USD
            FROM por_pais pp
            WHERE pp.valor_total = (
                SELECT MAX(valor_total) FROM por_pais pp2
                WHERE pp2.pais = pp.pais
            )
            AND pp.valor_total > 0
            ORDER BY pp.pais
        """
        return db.run_query(sql)
