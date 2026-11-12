class Usuario:
    es_admin = False

    def __init__(self, id, nombre, email):
        self.id = id
        self.nombre = nombre
        self.email = email


class Cliente(Usuario):
    es_admin = False

    def __init__(self, id, nombre, email, direccion_postal):
        super().__init__(id, nombre, email)
        self.direccion_postal = direccion_postal


class Administrador(Usuario):
    es_admin = True
