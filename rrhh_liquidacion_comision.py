# rrhh_liquidacion_comision.py
import streamlit as st
import pandas as pd
import pymssql
from io import BytesIO

def run():
    st.title("Liquidación de Comisiones (RRHH)")

    fecha_inicio = st.date_input("📅 Fecha de inicio")
    fecha_fin = st.date_input("📅 Fecha de fin")

    if st.button("📥 Consultar y descargar"):
        try:
            # Conexión
            conn = pymssql.connect(
                server=st.secrets["DB_SERVER"],
                port=int(st.secrets["DB_PORT"]),
                user=st.secrets["DB_USER"],
                password=st.secrets["DB_PASSWORD"],
                database=st.secrets["DB_NAME"],
            )

            # Consulta
            query = """SELECT 
    GL_DATEPIECE AS FECHA,
    GL_REPRESENTANT AS COMERCIAL,
    GCL_LIBELLE AS NOMBRE_COMERCIAL,
    GL_ETABLISSEMENT AS ESTABLECIMIENTO,
    GP_TYPECOMPTA AS TIPO_DOCUMENTO,
    GL_NUMERO AS NUMERO,
    GL_FAMILLENIV1 AS TIPO_ARTICULO,
    GL_LIBREART2 AS MARCA, 
    GL_CODEARTICLE AS CODIGO_ARTICULO,
    GL_QTEFACT AS CANTIDAD,
    GL_TOTALTTC AS PRECIO
FROM [MARAPROD24].[dbo].[GCLIGNEARTDIM] 
INNER JOIN COMMERCIAL ON GL_REPRESENTANT=GCL_COMMERCIAL
WHERE GL_DATEPIECE >= %s AND GL_DATEPIECE <= %s
AND GL_NATUREPIECEG IN ('FFO')
AND GP_TYPECOMPTA IN ('FAC','TIC')
AND GL_TYPEARTICLE IN ('MAR','NOM')
AND GP_TICKETANNULE <> 'X'
AND GL_CODEARTICLE <> 'CE001'
AND GL_CODEARTICLE <> 'NCPROMOCION'
AND GL_FAMILLENIV1 <> 'INS'
AND GL_FAMILLENIV1 <> 'LOG'
AND GL_FAMILLENIV1 <> 'REP'
AND GL_FAMILLENIV1 <> 'SER'
ORDER BY GL_DATEPIECE desc
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
