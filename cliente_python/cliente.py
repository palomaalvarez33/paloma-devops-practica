"""Cliente Python de la API de la tienda online (solo usa peticiones HTTP con requests).

Uso:
    python cliente.py                          -> usa BASE_URL (localhost)
    python cliente.py http://192.168.1.34:8000 -> usa la IP del equipo servidor
"""
import sys
import time

import requests

BASE_URL = "http://localhost:8000"  # Cambiar por la IP del equipo servidor para la prueba entre equipos
if len(sys.argv) > 1:
    BASE_URL = sys.argv[1].rstrip("/")


def peticion(metodo, ruta, codigo_esperado, **kwargs):
    """Hace la petición, comprueba el código de estado y devuelve el JSON de la respuesta."""
    url = BASE_URL + ruta
    try:
        respuesta = requests.request(metodo, url, timeout=10, **kwargs)
    except requests.exceptions.RequestException as error:
        print(f"No se pudo conectar con {url}: {error}")
        sys.exit(1)

    print(f"{metodo} {ruta} -> {respuesta.status_code}")
    if respuesta.status_code != codigo_esperado:
        print(f"  Error: se esperaba {codigo_esperado}. Respuesta: {respuesta.text}")
        sys.exit(1)
    return respuesta.json() if respuesta.content else None


def main():
    print(f"API: {BASE_URL}\n")

    # 1. Crear un usuario (email único para poder repetir el script)
    email = f"cliente{int(time.time())}@ejemplo.com"
    usuario = peticion("POST", "/usuarios", 201, json={
        "nombre": "Ana García",
        "email": email,
        "tipo": "cliente",
        "direccion_postal": "Calle Mayor 1, Madrid",
    })
    print("  Usuario creado:", usuario)

    # 2. Consultar la lista de usuarios
    usuarios = peticion("GET", "/usuarios", 200)
    print(f"  Usuarios registrados: {len(usuarios)}")
    for u in usuarios:
        print("   -", u)

    # 3. Crear uno o varios productos
    productos_nuevos = [
        {"tipo": "generico", "nombre": "Libreta", "precio": 3.5, "stock": 50},
        {"tipo": "electronico", "nombre": "Auriculares", "precio": 59.9, "stock": 10, "meses_garantia": 24},
        {"tipo": "ropa", "nombre": "Camiseta", "precio": 15.0, "stock": 20, "talla": "M", "color": "azul"},
    ]
    creados = [peticion("POST", "/productos", 201, json=p) for p in productos_nuevos]
    for p in creados:
        print("  Producto creado:", p)

    # 4. Consultar la lista de productos
    productos = peticion("GET", "/productos", 200)
    print(f"  Productos disponibles: {len(productos)}")
    for p in productos:
        print("   -", p)

    # 5. Crear un pedido para el usuario
    pedido = peticion("POST", "/pedidos", 201, json={
        "cliente_id": usuario["id"],
        "items": [
            {"producto_id": creados[0]["id"], "cantidad": 2},
            {"producto_id": creados[1]["id"], "cantidad": 1},
        ],
    })
    print("  Pedido creado:", pedido)

    # 6. Consultar los pedidos del usuario
    pedidos = peticion("GET", f"/usuarios/{usuario['id']}/pedidos", 200)
    print(f"  Pedidos del usuario {usuario['id']}: {len(pedidos)}")
    for p in pedidos:
        print(f"   - Pedido {p['id']} | total {p['total']} | {len(p['items'])} líneas")

    print("\nFlujo completado correctamente.")


if __name__ == "__main__":
    main()
