from models.Producto import Producto, ProductoElectronico, ProductoRopa
from models.Usuario import Cliente, Administrador
from models.Pedido import Pedido, ItemPedido


# Errores de negocio: main.py los traduce a códigos HTTP
class NoEncontradoError(Exception):
    pass


class DatosInvalidosError(Exception):
    pass


class ConflictoError(Exception):
    pass


class StockInsuficienteError(Exception):
    pass


class TiendaService:
    def __init__(self):
        self.usuarios = {}
        self.productos = {}
        self.pedidos = {}
        self._sig_usuario = 1
        self._sig_producto = 1
        self._sig_pedido = 1

    # ---------- Usuarios ----------
    def crear_usuario(self, nombre, email, tipo, direccion_postal=None):
        if any(u.email == email for u in self.usuarios.values()):
            raise ConflictoError(f"Ya existe un usuario con el email {email}")
        if tipo == "cliente":
            if not direccion_postal:
                raise DatosInvalidosError("Un cliente necesita dirección postal")
            usuario = Cliente(self._sig_usuario, nombre, email, direccion_postal)
        elif tipo == "administrador":
            usuario = Administrador(self._sig_usuario, nombre, email)
        else:
            raise DatosInvalidosError("El tipo de usuario debe ser 'cliente' o 'administrador'")
        self.usuarios[usuario.id] = usuario
        self._sig_usuario += 1
        return usuario

    def obtener_usuario(self, usuario_id):
        if usuario_id not in self.usuarios:
            raise NoEncontradoError(f"Usuario {usuario_id} no encontrado")
        return self.usuarios[usuario_id]

    def listar_usuarios(self):
        return list(self.usuarios.values())

    # ---------- Productos ----------
    def crear_producto(self, tipo, nombre, precio, stock, meses_garantia=None, talla=None, color=None):
        if tipo == "generico":
            producto = Producto(self._sig_producto, nombre, precio, stock)
        elif tipo == "electronico":
            if meses_garantia is None:
                raise DatosInvalidosError("Un producto electrónico necesita meses_garantia")
            producto = ProductoElectronico(self._sig_producto, nombre, precio, stock, meses_garantia)
        elif tipo == "ropa":
            if not talla or not color:
                raise DatosInvalidosError("Un producto de ropa necesita talla y color")
            producto = ProductoRopa(self._sig_producto, nombre, precio, stock, talla, color)
        else:
            raise DatosInvalidosError("Tipo de producto no válido")
        self.productos[producto.id] = producto
        self._sig_producto += 1
        return producto

    def listar_productos(self):
        return list(self.productos.values())

    def obtener_producto(self, producto_id):
        if producto_id not in self.productos:
            raise NoEncontradoError(f"Producto {producto_id} no encontrado")
        return self.productos[producto_id]

    def eliminar_producto(self, producto_id):
        self.obtener_producto(producto_id)
        del self.productos[producto_id]

    # ---------- Pedidos ----------
    def crear_pedido(self, cliente_id, lineas):
        """lineas: lista de tuplas (producto_id, cantidad)."""
        cliente = self.obtener_usuario(cliente_id)
        if cliente.es_admin:
            raise DatosInvalidosError("Un administrador no puede realizar pedidos")

        # 1) Validar todo antes de tocar el stock
        items = []
        pedido_por_producto = {}
        for producto_id, cantidad in lineas:
            producto = self.obtener_producto(producto_id)
            pedido_por_producto[producto_id] = pedido_por_producto.get(producto_id, 0) + cantidad
            if not producto.hay_stock(pedido_por_producto[producto_id]):
                raise StockInsuficienteError(
                    f"Stock insuficiente para '{producto.nombre}' (disponible: {producto.stock})"
                )
            items.append(ItemPedido(producto, cantidad))

        # 2) Descontar stock y registrar el pedido
        for item in items:
            item.producto.reducir_stock(item.cantidad)
        pedido = Pedido(self._sig_pedido, cliente, items)
        self.pedidos[pedido.id] = pedido
        self._sig_pedido += 1
        return pedido

    def pedidos_de_cliente(self, cliente_id):
        self.obtener_usuario(cliente_id)
        return [p for p in self.pedidos.values() if p.cliente.id == cliente_id]
