# rrhh_tem_tre.py
import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO

def run():
    st.title("🔁 Transferencias TEM y TRE (RRHH)")

    fecha_inicio = st.date_input("📅 Fecha de inicio")
    fecha_fin = st.date_input("📅 Fecha de fin")

    if st.button("📥 Consultar y descargar"):
        try:
            conn_str = (
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=181.209.94.152,29433\\MARAPROD24;'
                'DATABASE=MARAPROD24;'
                'UID=BIMA;'
                'PWD=Mar2024*'
            )
            conn = pyodbc.connect(conn_str)

            query = """
            SELECT 
                GL_REPRESENTANT AS [Comercial 2 (depo central)], 
                GP_REPRESENTANT2 AS [Comercial (locales)], 
                GP_NATUREPIECEG AS [Clase], 
                GL_ETABLISSEMENT AS [Establecimiento línea],
                GP_ETABLISSEMENT AS [Establecimiento doc.],
                GP_ETABLISSDEST AS [Destinatario], 
                GL_CODESDIM AS [Código artículo], 
                US_LIBELLE AS [Usuario modif], 
                GL_QTEFACT AS [Cantidad], 
                GP_DATEPIECE AS [Fecha Documento], 
                GL_LIBELLE AS [Nombre artículo]
            FROM GCLIGNEARTDIM 
            INNER JOIN UTILISAT ON GP_UTILISATEUR=US_UTILISATEUR
            WHERE (GP_DATEPIECE >= ? AND GP_DATEPIECE < ? AND GP_NATUREPIECEG IN ('TEM', 'TRE')) 
            AND GA_CODEARTICLE IS NULL
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
