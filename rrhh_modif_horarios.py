# rrhh_modif_horarios.py
import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO

def run():
    st.title("Modificaciones de Horarios (RRHH)")

    fecha_inicio = st.date_input("📅 Fecha de inicio")
    fecha_fin = st.date_input("📅 Fecha de fin")

    if st.button("📥 Consultar y descargar"):
        try:
            # Conexión
            conn_str = (
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=181.209.94.152,29433\\MARAPROD24;'
                'DATABASE=MARAPROD24;'
                'UID=BIMA;'
                'PWD=Mar2024*'
            )
            conn = pyodbc.connect(conn_str)

            # Consulta
            query = """SELECT 
                MPS_DATEMODIF AS FECHA_MODIFICACION,
                MPS_COMMERCIAL AS COMERCIAL,
                MPS_ETABLISSEMENT AS ESTABLECIMIENTO,
                MPS_DATEDEBPLAGE AS FECHA_INICIO,
                MPS_DATEFINPLAGE AS FECHA_FIN,
                US_LIBELLE AS MODIFICADOR
            FROM 
            MPLAGESALARIE
            INNER JOIN UTILISAT ON MPS_UTILISATEUR = US_UTILISATEUR
                where mps_modepla='001'	and MPS_DATEDEBPLAGE BETWEEN ? AND ?
                order by MPS_DATEDEBPLAGE desc
            """

            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📄 Descargar Excel", output.getvalue(), file_name="modificaciones_horarios.xlsx")

        except Exception as e:
            st.error(f"❌ Error: {e}")
