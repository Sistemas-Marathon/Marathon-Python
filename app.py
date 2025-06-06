# app.py
import streamlit as st
import reposicion_cruzada
import otroscript

st.sidebar.title("🧭 Menú")
opcion = st.sidebar.radio("Elegí un script:", ["Reposición Cruzada", "Otro Script"])

if opcion == "Reposición Cruzada":
    reposicion_cruzada.run()
elif opcion == "Otro Script":
    otroscript.run()
