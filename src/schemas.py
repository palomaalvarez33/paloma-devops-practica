from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ---------- 1.1 Usuario ----------
class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=1)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    tipo: Literal["cliente", "administrador"]
    direccion_postal: Optional[str] = None

    @model_validator(mode="after")
    def validar_direccion(self):
        if self.tipo == "cliente" and not self.direccion_postal:
            raise ValueError("direccion_postal es obligatoria para clientes")
        return self


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    es_admin: bool


# ---------- 1.2 Producto ----------
class ProductoCreate(BaseModel):
    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str = Field(..., min_length=1)
    precio: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    meses_garantia: Optional[int] = Field(None, ge=0)
    talla: Optional[str] = None
    color: Optional[str] = None

    @model_validator(mode="after")
    def validar_atributos(self):
        if self.tipo == "electronico" and self.meses_garantia is None:
            raise ValueError("meses_garantia es obligatorio para productos electrónicos")
        if self.tipo == "ropa" and (not self.talla or not self.color):
            raise ValueError("talla y color son obligatorios para productos de ropa")
        return self


class ProductoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    nombre: str
    precio: float
    stock: int
    meses_garantia: Optional[int] = None
    talla: Optional[str] = None
    color: Optional[str] = None


# ---------- 1.3 Pedido ----------
class PedidoItemCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0)


class PedidoCreate(BaseModel):
    cliente_id: int
    items: List[PedidoItemCreate] = Field(..., min_length=1)


class PedidoItemRead(BaseModel):
    producto_id: int
    nombre: str
    cantidad: int
    precio_unitario: float
    subtotal: float


class PedidoRead(BaseModel):
    id: int
    fecha: datetime
    cliente_id: int
    total: float
    items: List[PedidoItemRead]
