#!/usr/bin/env bash

set -e

echo "--- Installing Python dependencies ---"
pip install -r requirements.txt
echo "--- Python dependencies installed ---"

echo "--- Installing ODBC Driver for SQL Server (attempting with temporary APT paths) ---"

# Crear un directorio temporal para APT si el predeterminado es de solo lectura
# Esto es una suposición de que /tmp es escribible
export APT_LISTS_PATH=/tmp/apt_lists
export APT_STATE_DIR=/tmp/apt_state
mkdir -p "$APT_LISTS_PATH"
mkdir -p "$APT_STATE_DIR"

# Ahora sí, podemos instalar los paquetes.
# Primero el apt-get update
apt-get update -o Dir::Etc::sourcelist="etc/apt/sources.list" -o Dir::State="$APT_STATE_DIR" -o Dir::Cache="$APT_STATE_DIR/cache" -o Dir::Lists="$APT_LISTS_PATH" -o Dir::Parts="$APT_LISTS_PATH/parts"

# Luego la instalación
ACCEPT_EULA=Y apt-get install -y \
    -o Dir::Etc::sourcelist="etc/apt/sources.list" \
    -o Dir::State="$APT_STATE_DIR" \
    -o Dir::Cache="$APT_STATE_DIR/cache" \
    -o Dir::Lists="$APT_LISTS_PATH" \
    -o Dir::Parts="$APT_LISTS_PATH/parts" \
    unixodbc-dev msodbcsql17

echo "--- ODBC Driver installation complete ---"
