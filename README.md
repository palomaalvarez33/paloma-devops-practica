# Tienda online API – Práctica DevOps

**Autora:** Paloma Álvarez

## Descripción
API REST desarrollada en Python con **FastAPI** que simula una tienda online:
gestión de usuarios (clientes y administradores), productos (genéricos, electrónicos y ropa)
y pedidos con control de stock. Incluye además un cliente Python (`requests`) y un
frontend HTML/JavaScript que consumen la API.

## Estructura
```
src/               -> código de la API (main.py, schemas.py, models/, Services/)
cliente_python/    -> cliente de prueba con requests
frontend/          -> index.html (fetch)
requirements.txt   -> dependencias
```

## Ejecución en local
```bash
pip install -r requirements.txt
cd src
uvicorn main:app --reload
```
Documentación interactiva: http://localhost:8000/docs

## Flujo de trabajo Git
- `main`: rama principal y estable.
- `feature/<nombre>`: una rama por funcionalidad, que se integra en `main` mediante Pull Request.
