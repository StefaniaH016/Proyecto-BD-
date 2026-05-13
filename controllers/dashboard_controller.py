from daos import UsuarioDAO

class DashboardController:
    def __init__(self):
        self.dao = UsuarioDAO()

    def cerrar_sesion(self, user_id):
        try:
            self.dao.registrar_salida(user_id)
            return True, "Sesión cerrada correctamente."
        except Exception as e:
            return False, str(e)

    def get_user_role(self, user_id):
        # Podríamos expandir el UsuarioDAO para obtener el rol por ID
        # Por ahora, el dashboard ya lo recibe o lo puede consultar
        res = self.dao.get_by_id(user_id)
        if res:
            # Según el schema, la columna tipo_usuario es la 4 (index 3)
            # user_id (0), nombre (1), pass (2), tipo (3)
            return res[3]
        return "TRADICIONAL"
