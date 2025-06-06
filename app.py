# app.py
import streamlit as st
import reposicion_cruzada

# ✅ Esta línea debe ir ANTES de todo
st.set_page_config(page_title="Sistema de scripts", layout="centered")

st.sidebar.title("🧭 Menú")
opcion = st.sidebar.radio("Elegí un script:", ["Reposición Cruzada"])

if opcion == "Reposición Cruzada":
    reposicion_cruzada.run()