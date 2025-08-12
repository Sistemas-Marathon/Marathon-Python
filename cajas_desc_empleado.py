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
            SELECT 
                MLR_DATEPIECE,
                MP_LIBELLE,
                MLR_SOUCHE,
                MLR_MONTANTTTC,
                MLR_NUMERO,
                GA_CODEARTICLE,
                GA_LIBELLE,
                GL_TIERS,
                T_EMAIL,
                MLR_CODECOND
            FROM LIGNEREMISE LEFT JOIN LIGNE 
            ON (MLR_NATUREPIECEG=GL_NATUREPIECEG AND MLR_SOUCHE=GL_SOUCHE AND MLR_NUMERO=GL_NUMERO AND MLR_INDICEG=GL_INDICEG AND MLR_NUMLIGNE=GL_NUMLIGNE)
            LEFT JOIN ARTICLE ON GA_ARTICLE=GL_ARTICLE
            LEFT JOIN TIERS ON GL_TIERS = T_TIERS AND T_NATUREAUXI='CLI'
            LEFT JOIN GCREGLEMENTFO ON MLR_SOUCHE=GPE_SOUCHE AND MLR_NUMERO=GPE_NUMERO AND MLR_NATUREPIECEG=GPE_NATUREPIECEG
            WHERE MLR_NUMLIGNE>0 AND MLR_NUMORDRE>0 AND MLR_CODECOND='EMPLEADO' AND MLR_DATEPIECE>= ? AND MLR_DATEPIECE <= ?
            """

            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📄 Descargar Excel", output.getvalue(), file_name="consulta_desc_emp.xlsx")

        except Exception as e:
            st.error(f"❌ Error: {e}")
