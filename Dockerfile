# ---- Imagen base ligera de Python ----
FROM python:3.12-slim

# Evita ficheros .pyc y fuerza logs sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# 1) Dependencias primero (aprovecha la caché de capas de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Código fuente de la aplicación
COPY src/ ./src/

# 3) Usuario sin privilegios y permisos sobre el código
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app
USER appuser

EXPOSE 8000

# 4) Comando de inicio (PORT configurable por variable de entorno)
CMD ["sh", "-c", "uvicorn main:app --app-dir src --host 0.0.0.0 --port ${PORT}"]
