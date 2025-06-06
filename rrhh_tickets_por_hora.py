# rrhh_tickets_por_hora.py
import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO

def run():
    st.title("🕒 Tickets por Hora (RRHH)")

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
            SELECT 
                CONVERT(DATE, GP_HEURECREATION) AS Fecha,
                CONVERT(TIME, GP_HEURECREATION) AS Hora,
                GP_SOUCHE AS Establecimiento,
                FORMAT(DATEPART(HOUR, GP_HEURECREATION), '00') + ':00-' +
                FORMAT(DATEPART(HOUR, GP_HEURECREATION) + 1, '00') + ':00' AS Rango_Horario,
                1 AS Cantidad
            FROM [MARAPROD24].[dbo].[PIECE]
            WHERE GP_NATUREPIECEG = 'FFO'
              AND GP_DATECREATION >= ?
              AND GP_DATECREATION <= ?
              AND GP_TYPECOMPTA <> 'TRE'
            ORDER BY GP_HEURECREATION;
            """

            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📄 Descargar Excel", output.getvalue(), file_name="tickets_por_hora.xlsx")

        except Exception as e:
            st.error(f"❌ Error: {e}")
