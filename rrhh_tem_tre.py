# rrhh_tem_tre.py
import streamlit as st
import pandas as pd
import pymssql
from io import BytesIO

def run():
    st.title("🔁 Transferencias TEM y TRE (RRHH)")

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
                CONVERT(DATETIME, CONVERT(VARCHAR(10), GP_DATEPIECE, 120) + ' ' + CONVERT(VARCHAR(8), GP_HEURECREATION, 108)) AS [Fecha Documento],
                GP_NATUREPIECEG AS [Clase],
                GL_ETABLISSEMENT AS [Establecimiento línea],
                US_LIBELLE AS [Usuario modif],
                GL_QTEFACT AS [Cantidad],
                GL_FAMILLENIV1 AS [Tipo producto línea]
            FROM GCLIGNEARTDIM
            INNER JOIN UTILISAT ON GP_UTILISATEUR=US_UTILISATEUR
            WHERE (GP_DATEPIECE >= %s AND GP_DATEPIECE < DATEADD(day, 1, %s) AND GP_NATUREPIECEG IN ('TEM', 'TRE'))
            AND GA_CODEARTICLE IS NOT NULL
            AND GL_FAMILLENIV1!='INS'
            """

            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            df['Clase'] = df['Clase'].map({'TEM': 'Transferencia emitida', 'TRE': 'Transferencia recibida'})

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📄 Descargar Excel", output.getvalue(), file_name="transferencias_tem_tre.xlsx")

        except Exception as e:
            st.error(f"❌ Error: {e}")
