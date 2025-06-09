#!/usr/bin/env bash

set -e

echo "--- Installing Python dependencies ---"
pip install -r requirements.txt
echo "--- Python dependencies installed ---"

echo "--- Installing ODBC Driver for SQL Server (via Render's APT config) ---"
# Render gestionará automáticamente la adición del repositorio de Microsoft
# si los archivos 'microsoft-prod.list' y 'microsoft.gpg'
# están en la raíz de tu repositorio.

# Ahora sí, podemos instalar los paquetes que dependen de ese repositorio.
# Render ya habrá hecho el 'apt-get update' después de configurar los repositorios,
# pero lo repetimos aquí por si acaso, para asegurar que la lista de paquetes esté actualizada.
apt-get update
ACCEPT_EULA=Y apt-get install -y unixodbc-dev msodbcsql17

echo "--- ODBC Driver installation complete ---"

# Cualquier otro paso de construcción para tu aplicación puede ir aquí.
