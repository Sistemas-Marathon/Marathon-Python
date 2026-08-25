# rrhh_recepcion_proveedor.py
import streamlit as st
import pandas as pd
import pymssql
from io import BytesIO

def run():
    st.title("📦 Recepción de Proveedor (RRHH)")

    fecha_inicio = st.date_input("📅 Fecha de inicio")
    fecha_fin = st.date_input("📅 Fecha de fin")

    if st.button("📥 Consultar y descargar"):
        try:
            conn = pymssql.connect(
                server=st.secrets["DB_SERVER"],
                port=int(st.secrets["DB_PORT"]),
                user=st.secrets["DB_USER"],
                password=st.secrets["DB_PASSWORD"],
                database=st.secrets["DB_NAME"],
            )

            query = """
            SELECT
                CONVERT(DATETIME, CONVERT(VARCHAR(10), GL_DATEPIECE, 120) + ' ' + CONVERT(VARCHAR(8), GP_HEURECREATION, 108)) AS [Fecha línea],
                US_LIBELLE AS [Usuario de origen],
                GL_DEPOT AS [Almacén línea doc.],
                GL_QTEFACT AS [Cantidad línea],
                GL_FAMILLENIV1 AS [TIPO PROD línea doc],
                GL_TIERS AS [Tercero de la línea],
                T_LIBELLE AS [Razón social / nombre],
                GL_LIBELLE AS [Nombre artículo]
            FROM GCLIGNEARTDIM
            INNER JOIN UTILISAT ON GP_CREATEUR=US_UTILISATEUR
            WHERE GL_NATUREPIECEG = 'BLF'
            AND GL_DATEPIECE >= %s AND GL_DATEPIECE < DATEADD(day, 1, %s)
            AND GL_FAMILLENIV1 IS NOT NULL
            AND LTRIM(RTRIM(GL_FAMILLENIV1)) <> ''
            """

            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📄 Descargar Excel", output.getvalue(), file_name="recepcion_proveedor.xlsx")

        except Exception as e:
            st.error(f"❌ Error: {e}")