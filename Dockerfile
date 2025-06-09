# Usar una imagen base de Debian o Ubuntu que ya tenga Python
# python:3.11-slim-bookworm es una excelente opción ya que sabemos que Render usa Debian 12.
FROM python:3.11-slim-bookworm

# Instalar dependencias del sistema operativo (incluido el driver ODBC)
# Los comandos RUN en un Dockerfile se ejecutan como root por defecto.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Añadir el repositorio de Microsoft para el driver ODBC
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list

# Instalar el driver ODBC de SQL Server
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de requisitos de Python e instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de tu aplicación
COPY . .

# Comando para ejecutar la aplicación cuando el contenedor se inicie
CMD streamlit run app.py --server.port $PORT --server.address 0.0.0.0
