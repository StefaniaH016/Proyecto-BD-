from daos import UsuarioDAO

class LoginController:
    def __init__(self, view):
        self.view = view
        self.dao = UsuarioDAO()

    def intentar_login(self, username, password):
        if not username or not password:
            return False, "Por favor ingrese usuario y contraseña."

        try:
            # Ahora UsuarioDAO.authenticate debería devolver (id, tipo)
            res = self.dao.authenticate_with_role(username, password)
            if res:
                user_id, user_type = res
                # Registrar entrada en bitácora
                self.dao.registrar_entrada(user_id)
                return True, (user_id, user_type)
            else:
                return False, "Usuario o contraseña incorrectos."
        except Exception as e:
            return False, f"Error de conexión: {e}"
