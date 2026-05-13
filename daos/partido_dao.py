from .base_dao import BaseDAO
from database import db

class PartidoDAO(BaseDAO):
    def __init__(self):
        super().__init__("PARTIDO")

    def get_by_estadio(self, cod_estadio):
        sql = """
            SELECT p.codigo_partido,
                   TO_CHAR(p.fecha,'DD/MM/YYYY') AS fecha,
                   p.hora,
                   e.nombre AS estadio,
                   c.nombre || ', ' || pa.nombre AS ciudad_pais
            FROM Partido  p
            JOIN Estadio  e  ON p.codigo_estadio = e.codigo_estadio
            JOIN Ciudad   c  ON e.codigo_ciudad  = c.codigo_ciudad
            JOIN Pais     pa ON c.codigo_pais    = pa.codigo_pais
            WHERE e.codigo_estadio = :1
            ORDER BY p.fecha
        """
        return db.run_query(sql, (cod_estadio,))

    def get_equipos_por_pais_anfitrion(self, cod_pais=None):
        sql_base = """
            SELECT DISTINCT pa.nombre AS pais_anfitrion, s.nombre AS seleccion
            FROM Detalles_Partido_Seleccion dps
            JOIN Partido    p  ON dps.codigo_partido   = p.codigo_partido
            JOIN Estadio    e  ON p.codigo_estadio     = e.codigo_estadio
            JOIN Ciudad     ci ON e.codigo_ciudad      = ci.codigo_ciudad
            JOIN Pais       pa ON ci.codigo_pais       = pa.codigo_pais
            JOIN Seleccion  s  ON dps.codigo_seleccion = s.nombre
        """
        # Wait, the original query had s.nombre in the last JOIN? 
        # Let me check the original query in reports_views.py.
        # It was JOIN Seleccion s ON dps.codigo_seleccion = s.codigo_seleccion
        
        sql_base = """
            SELECT DISTINCT pa.nombre AS pais_anfitrion, s.nombre AS seleccion
            FROM Detalles_Partido_Seleccion dps
            JOIN Partido    p  ON dps.codigo_partido   = p.codigo_partido
            JOIN Estadio    e  ON p.codigo_estadio     = e.codigo_estadio
            JOIN Ciudad     ci ON e.codigo_ciudad      = ci.codigo_ciudad
            JOIN Pais       pa ON ci.codigo_pais       = pa.codigo_pais
            JOIN Seleccion  s  ON dps.codigo_seleccion = s.codigo_seleccion
        """
        params = []
        if cod_pais and cod_pais != "Todos":
            sql_base += " WHERE pa.codigo_pais = :1"
            params.append(cod_pais)
            
        sql_base += " ORDER BY pa.nombre, s.nombre"
        return db.run_query(sql_base, tuple(params))
