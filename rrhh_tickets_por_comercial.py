# rrhh_tickets_por_hora.py
import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO

def run():
    st.title("🕒 Tickets por Comercial (RRHH)")

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
            query = """
            SELECT GP_REPRESENTANT AS [Comercial del doc.],
            GP_HEURECREATION AS [Fecha],
            GP_ETABLISSEMENT AS [Establecimiento],
            GP_CAISSE AS [Caja],
            GP_TOTALTTC AS [Total IVA inc],
            GP_TOTALHT AS [Total exc. IVA documento],
            US_LIBELLE AS [Ultimo usuario]  
            FROM [MARAPROD24].[dbo].[PIECE]
            INNER JOIN UTILISAT ON GP_CREATEUR=US_UTILISATEUR
            WHERE (GP_DATEPIECE >= ? AND GP_DATEPIECE < ? AND GP_NATUREPIECEG IN ('TEM', 'TRE')) 
            """

            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📄 Descargar Excel", output.getvalue(), file_name="tickets_por_comercial.xlsx")

        except Exception as e:
            st.error(f"❌ Error: {e}")
