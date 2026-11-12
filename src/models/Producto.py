class Producto:
    """Producto genérico."""
    tipo = "generico"
    meses_garantia = None
    talla = None
    color = None

    def __init__(self, id, nombre, precio, stock):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def hay_stock(self, cantidad):
        return self.stock >= cantidad

    def reducir_stock(self, cantidad):
        self.stock -= cantidad


class ProductoElectronico(Producto):
    tipo = "electronico"

    def __init__(self, id, nombre, precio, stock, meses_garantia):
        super().__init__(id, nombre, precio, stock)
        self.meses_garantia = meses_garantia


class ProductoRopa(Producto):
    tipo = "ropa"

    def __init__(self, id, nombre, precio, stock, talla, color):
        super().__init__(id, nombre, precio, stock)
        self.talla = talla
        self.color = color
