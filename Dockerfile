FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Puerto para Cloud Run (health check)
ENV PORT=8080
EXPOSE 8080

# Ejecutar el servidor HTTP (Cloud Run) o el CLI
CMD ["python", "server.py"]
