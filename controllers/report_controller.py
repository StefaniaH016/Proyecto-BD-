from daos import (UsuarioDAO, SeleccionDAO, JugadorDAO, PartidoDAO, 
                  PaisDAO, ConfederacionDAO, EstadioDAO)
import pandas as pd

class ReportController:
    def __init__(self):
        self.dao_usr  = UsuarioDAO()
        self.dao_sel  = SeleccionDAO()
        self.dao_jug  = JugadorDAO()
        self.dao_par  = PartidoDAO()
        self.dao_est  = EstadioDAO()
        self.dao_pai  = PaisDAO()
        self.dao_conf = ConfederacionDAO()

    def run_report(self, report_name, params=()):
        # Mapeo de nombre de reporte a método de DAO
        mapping = {
            "most_expensive_player": self.dao_jug.get_most_expensive_by_confederacion,
            "matches_by_stadium":   self.dao_par.get_by_estadio,
            "most_expensive_team":  self.dao_sel.get_most_expensive_by_host_country,
            "sub_21_count":         self.dao_jug.get_sub_21_count_by_team,
            "bitacora_by_date":     self.dao_usr.get_bitacora_by_fecha,
            "filtered_players":     self.dao_jug.get_filtrados,
            "value_by_confed":      self.dao_conf.get_valor_por_equipo_en_confederacion,
            "teams_by_host":        self.dao_par.get_equipos_por_pais_anfitrion
        }
        
        func = mapping.get(report_name)
        if not func:
            raise ValueError(f"Reporte {report_name} no reconocido.")
        
        return func(*params)

    def get_combo_data(self, query):
        # Usamos cualquier DAO para fetch_combo_data ya que es de BaseDAO
        return self.dao_usr.fetch_combo_data(query)
