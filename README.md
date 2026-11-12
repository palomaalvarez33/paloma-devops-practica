# Tienda online API – Práctica DevOps

**Autora:** Paloma Álvarez

## Descripción
API REST desarrollada en Python con **FastAPI** que simula una tienda online:
gestión de usuarios (clientes y administradores), productos (genéricos, electrónicos y ropa)
y pedidos con control de stock. Incluye un cliente Python (`requests`) y un frontend
HTML/JavaScript que consumen la API. La aplicación está contenerizada con **Docker**.

## Estructura
```
.
├── src/                   # Código de la API (Práctica 2)
│   ├── main.py            #   endpoints FastAPI
│   ├── schemas.py         #   modelos Pydantic
│   ├── models/            #   Usuario, Producto, Pedido
│   └── Services/          #   lógica de negocio (TiendaService)
├── tests/                 # Tests con pytest
├── cliente_python/        # Cliente de prueba (requests)
├── frontend/              # index.html + Dockerfile (nginx)
├── Dockerfile             # Imagen de la API
├── .dockerignore
├── docker-compose.yml     # API + frontend
├── requirements.txt       # Dependencias de la API (versiones fijadas)
└── requirements-dev.txt   # Dependencias para tests
```

---

## 1. Ejecución sin Docker (local)
```bash
pip install -r requirements.txt
uvicorn main:app --app-dir src --reload
```
Documentación interactiva: http://localhost:8000/docs

Tests:
```bash
pip install -r requirements-dev.txt
pytest tests
```

---

## 2. Docker

### 2.1 Dockerfile (resumen)
- Imagen base `python:3.12-slim`.
- Copia primero `requirements.txt` y ejecuta `pip install --no-cache-dir` (aprovecha la caché de capas).
- Copia el código fuente con `COPY src/ ./src/`.
- Crea el usuario sin privilegios `appuser`, le da la propiedad y permisos de `/app` (`chown`/`chmod`) y ejecuta la app con él (`USER appuser`).
- Arranca con `CMD` → `uvicorn main:app --app-dir src --host 0.0.0.0 --port ${PORT}`.

El fichero `.dockerignore` excluye `.git`, cachés de Python, entornos virtuales, `tests/`, etc. para que la imagen sea pequeña (~136 MB).

### 2.2 Construir la imagen
```bash
docker build -t tienda-api:1.0.0 -t tienda-api:latest .
```

### 2.3 Ejecutar el contenedor
```bash
# En primer plano
docker run --rm -p 8000:8000 tienda-api:1.0.0

# En segundo plano, con nombre
docker run -d --name tienda-api -p 8000:8000 tienda-api:1.0.0

# Cambiando el puerto interno con la variable de entorno PORT
docker run -d --name tienda-api -e PORT=9000 -p 9000:9000 tienda-api:1.0.0
```
Ver logs y parar:
```bash
docker logs -f tienda-api
docker stop tienda-api && docker rm tienda-api
```

### 2.4 Variables de entorno soportadas
| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `PORT`   | `8000`            | Puerto en el que escucha uvicorn dentro del contenedor |

La aplicación no usa secretos ni claves.

### 2.5 Pruebas / salida esperada
Al arrancar, los logs muestran:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Endpoints para probar:
| Método | Endpoint | Resultado esperado |
|--------|----------|--------------------|
| GET  | `/health` | `200` → `{"status":"ok"}` |
| GET  | `/docs` | Documentación Swagger |
| POST | `/usuarios` | `201` usuario creado |
| GET  | `/usuarios` | `200` lista de usuarios |
| POST | `/productos` | `201` producto creado |
| GET  | `/productos` | `200` lista de productos |
| DELETE | `/productos/{id}` | `204` producto eliminado |
| POST | `/pedidos` | `201` pedido creado (descuenta stock) |
| GET  | `/usuarios/{id}/pedidos` | `200` pedidos del usuario |

Ejemplos con `curl`:
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/productos -H "Content-Type: application/json" \
     -d '{"tipo":"generico","nombre":"Libreta","precio":3.5,"stock":50}'
curl http://localhost:8000/productos
```

Prueba completa con el cliente Python (contenedor en marcha):
```bash
pip install -r cliente_python/requirements.txt
python cliente_python/cliente.py http://localhost:8000
```
Debe terminar con `Flujo completado correctamente.`

Códigos HTTP: 201 creado · 204 borrado · 400 datos/stock inválidos · 404 no encontrado · 409 email duplicado · 422 validación.

### 2.6 Publicar la imagen en Docker Hub (push)
Imagen publicada: https://hub.docker.com/r/paalomalvarez/tienda-api

```bash
docker login
docker tag tienda-api:1.0.0 paalomalvarez/tienda-api:1.0.0
docker tag tienda-api:1.0.0 paalomalvarez/tienda-api:latest
docker push paalomalvarez/tienda-api:1.0.0
docker push paalomalvarez/tienda-api:latest
```

### 2.7 Descargar y ejecutar la imagen publicada (pull)
```bash
docker pull paalomalvarez/tienda-api:1.0.0
docker run -d -p 8000:8000 paalomalvarez/tienda-api:1.0.0
```

---

## 3. Extra: API + frontend con docker-compose
`frontend/Dockerfile` sirve `index.html` con `nginx:1.27-alpine`. `docker-compose.yml`
levanta los dos contenedores; el frontend espera a que la API esté sana (`healthcheck` sobre `/health`).

```bash
docker compose up -d --build
```
- API: http://localhost:8000/docs
- Frontend: http://localhost:8080 (la URL de la API por defecto es `http://localhost:8000`)

```bash
docker compose ps
docker compose logs -f
docker compose down
```

---

## 4. Flujo de trabajo Git
- `main`: rama principal y estable.
- `feature/docker`: contenerización de la aplicación; se integra en `main` mediante Pull Request.
- Commits pequeños con prefijos (`feat`, `docs`, `build`, `test`, `chore`).
