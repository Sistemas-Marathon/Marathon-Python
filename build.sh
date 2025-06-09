#!/usr/bin/env bash

# Salir inmediatamente si un comando falla
set -e

echo "--- Instalando dependencias de Python ---"
pip install -r requirements.txt
echo "--- Dependencias de Python instaladas ---"

# NOTA: La instalación del driver ODBC de SQL Server (msodbcsql17 y unixodbc-dev)
# se espera que sea manejada por Render de forma automática si los archivos
# 'microsoft-prod.list' y 'microsoft.gpg' están en la raíz del repositorio,
# y/o si Render tiene una configuración de "System Packages" en su UI.
# No se pueden ejecutar comandos 'apt-get install' con permisos de root directamente aquí.
