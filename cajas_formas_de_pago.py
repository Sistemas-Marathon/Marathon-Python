# rrhh_tem_tre.py
import streamlit as st
import pandas as pd
import pymssql
from io import BytesIO

def run():
    st.title("🔁 Consulta por formas de pago")

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
            WHERE GPE_NATUREPIECEG='FFO' AND GPE_DATEPIECE>=%s AND GPE_DATEPIECE <=%s
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
