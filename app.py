# app.py
import streamlit as st
from PIL import Image
import reposicion_cruzada
import otroscript

# Configuración global
st.set_page_config(page_title="Sistema de Automatización", layout="wide", page_icon="🛠️")

# Cargar logo
logo = Image.open("descarga.jpeg")  # Asegurate que esté en la misma carpeta del proyecto

# --- SIDEBAR ---
with st.sidebar:
    st.image(logo, width=150)
    st.title("🔧 Automatizaciones")
    area = st.selectbox("📂 Seleccioná el área", ["Inicio", "Supply Chain", "RRHH"])

# --- CONTENIDO PRINCIPAL ---
if area == "Inicio":
    st.title("📊 Dashboard General")
    st.markdown("Bienvenido al sistema interno de automatización de procesos.")
    st.markdown("### ✅ ¿Qué podés hacer acá?")
    st.markdown("""
    - Ejecutar scripts de forma autónoma.
    - Cargar archivos Excel y obtener resultados inmediatos.
    - Evitar depender del equipo de IT para tareas repetitivas.
    """)

    # Ejemplo de métricas
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🗂️ Scripts disponibles", 2)
    with col2:
        st.metric("👥 Áreas integradas", 2)

    st.markdown("---")
    st.success("Seleccioná un área en la barra lateral para comenzar.")

elif area == "Supply Chain":
    st.title("🚚 Supply Chain")
    opcion = st.sidebar.radio("📦 Procesos disponibles:", ["Reposición Cruzada"])
    if opcion == "Reposición Cruzada":
        reposicion_cruzada.run()

elif area == "RRHH":
    st.title("👩‍💼 Recursos Humanos")
    opcion = st.sidebar.radio("📋 Procesos disponibles:", ["Otro Script"])
    if opcion == "Otro Script":
        otroscript.run()

# --- PIE DE PÁGINA ---
st.markdown("---")
st.markdown("<center>🔒 Sistema interno de uso exclusivo - Contacto: IT@tuempresa.com</center>", unsafe_allow_html=True)
