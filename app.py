# app.py
import streamlit as st
from PIL import Image
import rrhh_tem_tre
import rrhh_tickets_por_hora
import reposicion_cruzada
import min_max
import marketing_codigos_barra
import rrhh_lleg_tardes
import rrhh_modif_horarios
import rrhh_tickets_por_comercial
import rrhh_desglose_recibos
import cajas_formas_de_pago
import cajas_desc_empleado
import rrhh_liquidacion_comision
import cajas_ventas_cliente
import cajas_ventas_banco
import rrhh_desglose_recibos_dab
import lista_art
import rrhh_martin
# Configuración global
st.set_page_config(page_title="Sistema de Automatización", layout="wide", page_icon="🛠️")

# Cargar logo
logo = Image.open("descarga.jpeg")  # Asegurate que esté en la misma carpeta del proyecto

# --- SIDEBAR ---
with st.sidebar:
    st.image(logo, width=150)
    st.title("🔧 Automatizaciones")
    area = st.selectbox("Seleccioná el área", ["Inicio", "Supply Chain", "RRHH", "Marketing","Control cajas"])

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


    st.markdown("---")
    st.success("Seleccioná un área en la barra lateral para comenzar.")

elif area == "Supply Chain":
    st.title("🚚 Supply Chain")
    opcion = st.sidebar.radio("📦 Procesos disponibles:", ["Reposición Cruzada", "Minimos y Máximos", "Lista artículos"])
    if opcion == "Reposición Cruzada":
        reposicion_cruzada.run()
    elif opcion == "Minimos y Máximos":
        min_max.run()
    elif opcion == "Lista artículos":
        lista_art.run()

# En la sección "RRHH"
elif area == "RRHH":
    st.title("👩‍💼 Recursos Humanos")
    opcion = st.sidebar.radio("📋 Procesos disponibles:", [
        "Tickets por hora",
        "Transferencias TEM-TRE",
        "Llegadas Tardes y Justificaciones",
        "Modificaciones de Horarios",
        "Tickets por Comercial",
        "Desglose de Recibos",
        "Desglose de Recibos DAB",
        "Liquidación de Comisiones",
        "Reporte Martin"
    ])
    if opcion == "Tickets por hora":
        rrhh_tickets_por_hora.run()
    elif opcion == "Transferencias TEM-TRE":
        rrhh_tem_tre.run()
    elif opcion == "Llegadas Tardes y Justificaciones":
        rrhh_lleg_tardes.run()
    elif opcion == "Modificaciones de Horarios":
        rrhh_modif_horarios.run()
    elif opcion == "Tickets por Comercial":
        rrhh_tickets_por_comercial.run()
    elif opcion == "Desglose de Recibos":
        rrhh_desglose_recibos.run()
    elif opcion == "Desglose de Recibos DAB":
        rrhh_desglose_recibos_dab.run()
    elif opcion == "Liquidación de Comisiones":
        rrhh_liquidacion_comision.run()
    elif opcion == "Reporte Martin":
        rrhh_martin.run()

elif area == "Marketing":
    st.title("📈 Marketing")
    opcion = st.sidebar.radio("📋 Procesos disponibles:", [
        "Generador de Códigos de Barras"
    ])
    if opcion == "Generador de Códigos de Barras":
        marketing_codigos_barra.run()
    
elif area == "Control cajas":
    st.title("📦 Control de Cajas")
    opcion = st.sidebar.radio("📋 Procesos disponibles:", [
        "Consulta por forma de pago",
        "Consulta por descuentos empleados",
        "Consulta de clientes por venta",
        "Consulta de ventas por banco"
    ])
    if opcion == "Consulta por forma de pago":
        cajas_formas_de_pago.run()
    elif opcion == "Consulta por descuentos empleados":
        cajas_desc_empleado.run()
    elif opcion == "Consulta de clientes por venta":
        cajas_ventas_cliente.run()
    elif opcion == "Consulta de ventas por banco":
        cajas_ventas_banco.run()
    

# --- PIE DE PÁGINA ---
st.markdown("---")
st.markdown("<center>🔒 Sistema interno de uso exclusivo - Santiago Sosa</center>", unsafe_allow_html=True)



