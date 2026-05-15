from daos import BaseDAO
import os
from datetime import datetime

class CRUDController:
    def __init__(self, table_name=None):
        self.dao = BaseDAO(table_name)

    def get_data(self):
        return self.dao.get_all()

    def get_schema(self):
        return self.dao.get_schema()

    def delete_record(self, table_name, pk_cols, pk_vals):
        try:
            self.dao.delete(table_name, pk_cols, pk_vals)
            return True, "Registro eliminado correctamente."
        except Exception as e:
            return False, str(e)

    def validate_and_save(self, table_name, columns_info, vals, edit_mode=False, original_pk_vals=None):
        table_name_up = table_name.upper()
        if table_name_up == "BITACORA":
            return False, "No se permite la creación o modificación manual de registros en la Bitácora."
            
        try:
            if table_name_up in ("JUGADOR", "DIRECTOR_TECNICO"):
                # Caso especial: Especialización de Persona
                nombre = vals[0]
                # Para insertar/actualizar la tabla especializada, quitamos el nombre de la lista
                # y ajustamos columns_info para que coincida con la tabla real
                specialized_vals = vals[1:]
                specialized_cols = columns_info[1:]

                if not edit_mode:
                    # 1. Crear Persona
                    new_id = self.dao.insert_persona(nombre)
                    # 2. Asignar el ID a la tabla especializada (está en la pos 0 de specialized_vals)
                    specialized_vals[0] = new_id
                    # 3. Insertar en tabla especializada
                    self.dao.insert(table_name_up, specialized_cols, specialized_vals)
                else:
                    # 1. Actualizar Persona
                    codigo_persona = original_pk_vals[0]
                    self.dao.update_persona(codigo_persona, nombre)
                    # 2. Actualizar tabla especializada
                    self.dao.update(table_name_up, specialized_cols, specialized_vals, original_pk_vals)
            else:
                # Caso genérico
                if not edit_mode:
                    self.dao.insert(table_name_up, columns_info, vals)
                else:
                    self.dao.update(table_name_up, columns_info, vals, original_pk_vals)
            
            return True, "Guardado exitosamente."
        except Exception as e:
            return False, f"Error al guardar: {e}"

    def fetch_combos(self, query):
        return self.dao.fetch_combo_data(query)

    def save_match_details(self, partido_id, local_id, visita_id, goles_local, goles_visita):
        try:
            self.dao.insert_match_details(partido_id, local_id, visita_id, goles_local, goles_visita)
            return True, "Registro doble guardado exitosamente."
        except Exception as e:
            # Capturamos si hay duplicados (ORA-00001) u otro error
            return False, f"Error al guardar detalles de partido: {e}"
