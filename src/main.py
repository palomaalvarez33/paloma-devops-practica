from typing import List

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas import (
    UsuarioCreate, UsuarioRead,
    ProductoCreate, ProductoRead,
    PedidoCreate, PedidoRead, PedidoItemRead,
)
from Services.Tienda_service import (
    TiendaService, NoEncontradoError, DatosInvalidosError,
    ConflictoError, StockInsuficienteError,
)

app = FastAPI(title="Tienda online API")

# CORS: permite que el frontend (abierto desde otro origen) consuma la API desde el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

tienda = TiendaService()


# ---------- Manejo de errores (formato consistente: {"detail": "..."}) ----------
def _error(codigo, exc):
    return JSONResponse(status_code=codigo, content={"detail": str(exc)})


@app.exception_handler(NoEncontradoError)
async def no_encontrado_handler(request: Request, exc: NoEncontradoError):
    return _error(status.HTTP_404_NOT_FOUND, exc)


@app.exception_handler(DatosInvalidosError)
async def datos_invalidos_handler(request: Request, exc: DatosInvalidosError):
    return _error(status.HTTP_400_BAD_REQUEST, exc)


@app.exception_handler(StockInsuficienteError)
async def stock_handler(request: Request, exc: StockInsuficienteError):
    return _error(status.HTTP_400_BAD_REQUEST, exc)


@app.exception_handler(ConflictoError)
async def conflicto_handler(request: Request, exc: ConflictoError):
    return _error(status.HTTP_409_CONFLICT, exc)


# ---------- Salud (útil para comprobar el contenedor) ----------
@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Usuarios ----------
@app.post("/usuarios", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCreate):
    return tienda.crear_usuario(datos.nombre, datos.email, datos.tipo, datos.direccion_postal)


@app.get("/usuarios", response_model=List[UsuarioRead])
def listar_usuarios():
    return tienda.listar_usuarios()


@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: int):
    return tienda.obtener_usuario(usuario_id)


# ---------- Productos ----------
@app.post("/productos", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate):
    return tienda.crear_producto(
        datos.tipo, datos.nombre, datos.precio, datos.stock,
        datos.meses_garantia, datos.talla, datos.color,
    )


@app.get("/productos", response_model=List[ProductoRead])
def listar_productos():
    return tienda.listar_productos()


@app.get("/productos/{producto_id}", response_model=ProductoRead)
def obtener_producto(producto_id: int):
    return tienda.obtener_producto(producto_id)


@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int):
    tienda.eliminar_producto(producto_id)


# ---------- Pedidos ----------
def pedido_a_read(pedido) -> PedidoRead:
    return PedidoRead(
        id=pedido.id,
        fecha=pedido.fecha,
        cliente_id=pedido.cliente.id,
        total=pedido.total,
        items=[
            PedidoItemRead(
                producto_id=i.producto.id,
                nombre=i.producto.nombre,
                cantidad=i.cantidad,
                precio_unitario=i.precio_unitario,
                subtotal=i.subtotal,
            )
            for i in pedido.items
        ],
    )


@app.post("/pedidos", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
def crear_pedido(datos: PedidoCreate):
    lineas = [(i.producto_id, i.cantidad) for i in datos.items]
    return pedido_a_read(tienda.crear_pedido(datos.cliente_id, lineas))


@app.get("/usuarios/{cliente_id}/pedidos", response_model=List[PedidoRead])
def pedidos_del_cliente(cliente_id: int):
    return [pedido_a_read(p) for p in tienda.pedidos_de_cliente(cliente_id)]
