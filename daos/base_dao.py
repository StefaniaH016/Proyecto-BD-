from database import db

class BaseDAO:
    def __init__(self, table_name=None):
        self.table_name = table_name.upper() if table_name else None

    def get_schema(self, table_name=None):
        target_table = (table_name or self.table_name).upper()
        cols = []
        # 1. Obtener todas las columnas
        sql_cols = """SELECT column_name, data_type, data_length, nullable 
                      FROM user_tab_columns WHERE table_name = :1 ORDER BY column_id"""
        res_cols = db.run_query(sql_cols, (target_table,))
        if res_cols:
            for r in res_cols[0]:
                cols.append({"name": r[0], "type": r[1], "length": r[2], "nullable": r[3], "is_pk": False})

        # 2. Marcar las PKs
        sql_pks = """SELECT cols.column_name FROM user_constraints cons 
                     JOIN user_cons_columns cols ON cons.constraint_name = cols.constraint_name
                     WHERE cons.constraint_type = 'P' AND cons.table_name = :1"""
        res_pks = db.run_query(sql_pks, (target_table,))
        if res_pks:
            pk_names = {r[0] for r in res_pks[0]}
            for c in cols:
                if c["name"] in pk_names: c["is_pk"] = True
        return cols

    def get_pk_cols(self, table_name=None):
        target_table = (table_name or self.table_name).upper()
        sql = """SELECT cols.column_name FROM user_constraints cons 
                 JOIN user_cons_columns cols ON cons.constraint_name = cols.constraint_name 
                 AND cons.owner = cols.owner 
                 WHERE cons.constraint_type = 'P' AND cons.table_name = :1 ORDER BY cols.position"""
        res = db.run_query(sql, (target_table,))
        return [r[0] for r in res[0]] if res else []

    def get_all(self, table_name=None):
        target_table = (table_name or self.table_name).upper()
        return db.run_query(f"SELECT * FROM {target_table}")

    def insert(self, table_name, columns_info, vals):
        target_table = table_name.upper()
        ph = [f"TO_DATE(:{i+1}, 'DD/MM/YYYY')" if c["type"] in ("DATE", "TIMESTAMP(6)") and vals[i] is not None else f":{i+1}" 
              for i, c in enumerate(columns_info)]
        cols_str = ", ".join(c["name"] for c in columns_info)
        sql = f"INSERT INTO {target_table} ({cols_str}) VALUES ({', '.join(ph)})"
        return db.run_query(sql, vals, commit=True)

    def update(self, table_name, columns_info, vals, original_pk_vals):
        target_table = table_name.upper()
        pk_names = [c["name"] for c in columns_info if c.get("is_pk")]
        if not pk_names: pk_names = [columns_info[0]["name"]] # Fallback
        
        set_parts = []
        final_vals = []
        idx = 1
        for i, c in enumerate(columns_info):
            col_name = c["name"]
            if col_name in pk_names: continue
            
            if c["type"] in ("DATE", "TIMESTAMP(6)") and vals[i] is not None:
                set_parts.append(f"{col_name} = TO_DATE(:{idx}, 'DD/MM/YYYY')")
            else:
                set_parts.append(f"{col_name} = :{idx}")
            final_vals.append(vals[i])
            idx += 1
        
        where_parts = []
        for i, pk in enumerate(pk_names):
            where_parts.append(f"{pk} = :{idx}")
            final_vals.append(original_pk_vals[i])
            idx += 1
        
        sql = f"UPDATE {target_table} SET {', '.join(set_parts)} WHERE {' AND '.join(where_parts)}"
        return db.run_query(sql, final_vals, commit=True)

    def delete(self, table_name, pk_cols, pk_vals):
        target_table = table_name.upper()
        where_parts = [f"{col} = :{i+1}" for i, col in enumerate(pk_cols)]
        where_clause = " AND ".join(where_parts)
        return db.run_query(f"DELETE FROM {target_table} WHERE {where_clause}", pk_vals, commit=True)

    def fetch_combo_data(self, query):
        res = db.run_query(query)
        if res:
            rows, _ = res
            return [f"{r[0]} - {r[1]}" for r in rows]
        return []
