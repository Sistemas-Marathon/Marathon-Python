# rrhh_tem_tre.py
import streamlit as st
import pandas as pd
import pymssql
from io import BytesIO


def run():
    st.title("🔁 Consulta por descuentos empleados")

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
            FROM LIGNEREMISE 
            LEFT JOIN LIGNE 
                ON MLR_NATUREPIECEG = GL_NATUREPIECEG 
                AND MLR_SOUCHE = GL_SOUCHE 
                AND MLR_NUMERO = GL_NUMERO 
                AND MLR_INDICEG = GL_INDICEG 
                AND MLR_NUMLIGNE = GL_NUMLIGNE
            LEFT JOIN ARTICLE 
                ON GA_ARTICLE = GL_ARTICLE
            LEFT JOIN TIERS 
                ON GL_TIERS = T_TIERS 
                AND T_NATUREAUXI = 'CLI'
            LEFT JOIN GCREGLEMENTFO 
                ON MLR_SOUCHE = GPE_SOUCHE 
                AND MLR_NUMERO = GPE_NUMERO 
                AND MLR_NATUREPIECEG = GPE_NATUREPIECEG
            WHERE 
                MLR_NUMLIGNE > 0 
                AND MLR_NUMORDRE > 0 
                AND MLR_CODECOND = 'EMPLEADO' 
                AND MLR_DATEPIECE >= %s 
                AND MLR_DATEPIECE <= %s
            """

            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)

            st.download_button(
                "📄 Descargar Excel",
                output.getvalue(),
                file_name="consulta_desc_emp.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
