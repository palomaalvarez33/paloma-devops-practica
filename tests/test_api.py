from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_flujo_completo_pedido():
    usuario = client.post("/usuarios", json={
        "nombre": "Test", "email": "test@ejemplo.com",
        "tipo": "cliente", "direccion_postal": "Calle 1",
    })
    assert usuario.status_code == 201
    uid = usuario.json()["id"]

    producto = client.post("/productos", json={
        "tipo": "electronico", "nombre": "Ratón", "precio": 10.0,
        "stock": 5, "meses_garantia": 12,
    })
    assert producto.status_code == 201
    pid = producto.json()["id"]

    pedido = client.post("/pedidos", json={
        "cliente_id": uid, "items": [{"producto_id": pid, "cantidad": 2}],
    })
    assert pedido.status_code == 201
    assert pedido.json()["total"] == 20.0
    assert client.get(f"/productos/{pid}").json()["stock"] == 3


def test_errores():
    assert client.get("/productos/9999").status_code == 404
    assert client.post("/productos", json={"tipo": "ropa", "nombre": "X", "precio": 1, "stock": 1}).status_code == 422
    client.post("/usuarios", json={"nombre": "A", "email": "dup@ejemplo.com", "tipo": "administrador"})
    assert client.post("/usuarios", json={"nombre": "B", "email": "dup@ejemplo.com", "tipo": "administrador"}).status_code == 409
