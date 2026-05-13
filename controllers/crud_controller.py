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
        # Aquí irían validaciones de negocio adicionales si fueran necesarias
        try:
            if not edit_mode:
                self.dao.insert(table_name, columns_info, vals)
            else:
                self.dao.update(table_name, columns_info, vals, original_pk_vals)
            return True, "Guardado exitosamente."
        except Exception as e:
            return False, str(e)

    def fetch_combos(self, query):
        return self.dao.fetch_combo_data(query)
