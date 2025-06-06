import streamlit as st
import pandas as pd
import requests
from io import BytesIO

def run():
    st.title("🕒 Tickets por Hora (RRHH)")

    fecha_inicio = st.date_input("📅 Fecha de inicio")
    fecha_fin = st.date_input("📅 Fecha de fin")

    if st.button("📥 Consultar y descargar"):
        try:
            url = "http://192.168.1.111:5000/tickets-por-hora"  # reemplazá con la IP real
            response = requests.post(url, json={
                "fecha_inicio": str(fecha_inicio),
                "fecha_fin": str(fecha_fin)
            })

            if response.status_code != 200:
                st.error(f"❌ Error en la API: {response.text}")
                return

            df = pd.DataFrame(response.json())
            st.success(f"✅ {len(df)} registros encontrados")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📄 Descargar Excel", output.getvalue(), file_name="tickets_por_hora.xlsx")

        except Exception as e:
            st.error(f"❌ Error: {e}")
