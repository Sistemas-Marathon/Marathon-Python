# rrhh_liquidacion_comision.py
import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO

def run():
    st.title("Liquidación de Comisiones (RRHH)")

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
                    GL_DATEPIECE AS FECHA,
                    GL_REPRESENTANT AS COMERCIAL,
                    GCL_LIBELLE AS NOMBRE_COMERCIAL,
                    GL_ETABLISSEMENT AS ESTABLECIMIENTO,
                    GL_FAMILLENIV1 AS TIPO_ARTICULO,
                    GL_LIBREART2 AS MARCA, 
                    GL_CODEARTICLE AS CODIGO_ARTICULO,
                    GL_QTEFACT AS CANTIDAD,
                    GL_MONTANTTTC AS PRECIO
                FROM [MARAPROD24].[dbo].[GCLIGNEARTDIM] 
                INNER JOIN COMMERCIAL ON GL_REPRESENTANT=GCL_COMMERCIAL
                WHERE GL_DATEPIECE >= ? AND GL_DATEPIECE <= ?
                AND GL_NATUREPIECEG IN ('FFO','FAC','AVC')
            """

            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📄 Descargar Excel", output.getvalue(), file_name="liquidacion_comision.xlsx")

        except Exception as e:
            st.error(f"❌ Error: {e}")
