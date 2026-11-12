from datetime import datetime


class ItemPedido:
    """Línea de pedido: producto, cantidad y precio unitario en el momento de la compra."""

    def __init__(self, producto, cantidad):
        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario = producto.precio

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad


class Pedido:
    def __init__(self, id, cliente, items):
        self.id = id
        self.cliente = cliente
        self.items = items
        self.fecha = datetime.now()

    @property
    def total(self):
        return sum(item.subtotal for item in self.items)
