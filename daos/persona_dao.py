from .base_dao import BaseDAO
from database import db

class PersonaDAO(BaseDAO):
    def __init__(self, table_name="PERSONA"):
        super().__init__(table_name)

class JugadorDAO(PersonaDAO):
    def __init__(self):
        super().__init__("JUGADOR")

    def get_filtrados(self, peso_min, peso_max, estatura_min, estatura_max, cod_seleccion=None):
        sql_base = """
            SELECT P.NOMBRE, S.NOMBRE AS EQUIPO,
                   J.PESO, J.ESTATURA, J.VALOR,
                   NVL(POS.NOMBRE, 'Sin definir') AS POSICION
            FROM JUGADOR J
            JOIN PERSONA P ON J.CODIGO_PERSONA = P.CODIGO_PERSONA
            JOIN SELECCION S ON J.CODIGO_SELECCION = S.CODIGO_SELECCION
            LEFT JOIN POSICION POS ON J.CODIGO_POSICION = POS.CODIGO_POSICION
            WHERE J.PESO BETWEEN :1 AND :2
              AND J.ESTATURA BETWEEN :3 AND :4
        """
        params = [peso_min, peso_max, estatura_min, estatura_max]
        
        if cod_seleccion and cod_seleccion != "Todos":
            sql_base += " AND S.CODIGO_SELECCION = :5"
            params.append(cod_seleccion)
            
        sql_base += " ORDER BY J.VALOR DESC"
        return db.run_query(sql_base, tuple(params))

    def get_sub_21_count_by_team(self):
        sql = """
            SELECT s.nombre AS equipo,
                   COUNT(p.codigo_persona) AS cant_sub_21
            FROM Jugador j
            JOIN Persona   p ON j.codigo_persona    = p.codigo_persona
            JOIN Seleccion s ON j.codigo_seleccion  = s.codigo_seleccion
            WHERE TRUNC(MONTHS_BETWEEN(SYSDATE, p.fecha_nacimiento)/12) < 21
            GROUP BY s.nombre
            ORDER BY cant_sub_21 DESC
        """
        return db.run_query(sql)

    def get_most_expensive_by_confederacion(self):
        sql = """
            SELECT p.nombre AS jugador, s.nombre AS equipo, c.nombre AS confederacion, j.valor
            FROM Jugador      j
            JOIN Persona      p  ON j.codigo_persona       = p.codigo_persona
            JOIN Seleccion    s  ON j.codigo_seleccion    = s.codigo_seleccion
            JOIN Confederacion c ON s.codigo_confederacion = c.codigo_confederacion
            WHERE j.valor = (
                SELECT MAX(j2.valor) FROM Jugador j2
                JOIN Seleccion s2 ON j2.codigo_seleccion = s2.codigo_seleccion
                WHERE s2.codigo_confederacion = c.codigo_confederacion
            )
            ORDER BY j.valor DESC
        """
        return db.run_query(sql)
