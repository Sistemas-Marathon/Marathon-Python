#!/usr/bin/env bash

set -e

echo "--- Installing ODBC Driver for SQL Server ---"

curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
# ^^^^ REVISA ESTA LÍNEA DE DEBIAN/UBUNTU ^^^^

apt-get update
ACCEPT_EULA=Y apt-get install -y unixodbc-dev msodbcsql17

echo "--- ODBC Driver installation complete ---"

echo "--- Installing Python dependencies ---"
pip install -r requirements.txt
echo "--- Python dependencies installed ---"
