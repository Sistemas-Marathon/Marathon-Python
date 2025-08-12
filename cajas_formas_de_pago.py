# rrhh_tem_tre.py
import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO

def run():
    st.title("🔁 Consulta por formas de pago")

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
            SELECT GPE_DATEPIECE AS FECHA_DOCUMENTO,
                GPE_ETABLISSEMENT AS ESTABLECIMIENTO, 
                GPE_NUMERO AS NUMERO_TICKET,	
                GL_MONTANTTTC AS MONTO, 
                US_LIBELLE AS USUARIO_CREADOR, 
                MP_MODEPAIE AS CODIGO_FORMA_PAGO,
                MP_LIBELLE AS DESCRIPCION_FORMA_PAGO, 
                GL_CODEARTICLE AS CODIGO_ARTICULO, 
                GL_LIBREART2 AS MARCA,
                GL_LIBREART6 AS PROMO
            FROM GCREGLEMENTFO 
            INNER JOIN UTILISAT ON US_UTILISATEUR = GPE_CREATEUR
            INNER JOIN LIGNE ON GL_NUMERO=GPE_NUMERO AND GL_DATEPIECE=GPE_DATEPIECE AND GL_ETABLISSEMENT=GPE_ETABLISSEMENT
            WHERE GPE_NATUREPIECEG='FFO' AND GPE_DATEPIECE>=? AND GPE_DATEPIECE <=?
            ORDER BY GPE_DATEPIECE DESC

            """

            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📄 Descargar Excel", output.getvalue(), file_name="consulta_formas_pago.xlsx")

        except Exception as e:
            st.error(f"❌ Error: {e}")
