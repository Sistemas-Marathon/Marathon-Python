import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO


def run():
    st.title("Reporte para Martin (RRHH)")

    fecha_inicio = st.date_input("📅 Fecha de inicio")
    fecha_fin = st.date_input("📅 Fecha de fin")

    if st.button("📥 Consultar y descargar"):
        try:
            conn_str = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=181.209.94.152,29433\\MARAPROD24;"
                "DATABASE=MARAPROD24;"
                "UID=BIMA;"
                "PWD=Mar2024*"
            )

            conn = pyodbc.connect(conn_str)

            query = """
SELECT 
    GL.GL_DATEPIECE AS FECHA,
    GL.GL_REPRESENTANT AS COMERCIAL,
    C.GCL_LIBELLE AS NOMBRE_COMERCIAL,
    C.GCL_TCONTRAT AS MOD_HORARIA,
    CCMFO.CC_LIBELLE AS ROL_COMERCIAL,
    GL.GL_ETABLISSEMENT AS ESTABLECIMIENTO,
    GL.GP_TYPECOMPTA AS TIPO_DOCUMENTO,
    GL.GL_NUMERO AS NUMERO,
    GL.GL_FAMILLENIV1 AS TIPO_ARTICULO,
    GL.GL_LIBREART2 AS MARCA, 
    GL.GL_CODEARTICLE AS CODIGO_ARTICULO,
    GL.GL_LIBELLE AS NOMBRE_ARTICULO,
    CCFN7.CC_LIBELLE AS CLASIFICACION,
    GL.GL_QTEFACT AS CANTIDAD,
    GL.GL_TOTALTTC AS PRECIO
FROM [MARAPROD24].[dbo].[GCLIGNEARTDIM] GL
INNER JOIN COMMERCIAL C
    ON GL.GL_REPRESENTANT = C.GCL_COMMERCIAL
LEFT JOIN CHOIXCOD CCMFO
    ON C.GCL_FONCTIONCOM = CCMFO.CC_CODE
   AND CCMFO.CC_TYPE = 'MFO'
LEFT JOIN ARTICLE_COMPL AC
    ON GL.GL_ARTICLE = AC.GA_ARTICLE
LEFT JOIN CHOIXCOD CCFN7
    ON AC.GA2_FAMILLENIV7 = CCFN7.CC_CODE
   AND CCFN7.CC_TYPE = 'FN7'
WHERE GL.GL_DATEPIECE >= ?
  AND GL.GL_DATEPIECE <= ?
  AND GL.GL_NATUREPIECEG IN ('FFO')
  AND GL.GP_TYPECOMPTA IN ('FAC', 'TIC')
  AND GL.GL_TYPEARTICLE IN ('MAR', 'NOM')
  AND GL.GP_TICKETANNULE <> 'X'
  AND GL.GL_CODEARTICLE <> 'CE001'
  AND GL.GL_CODEARTICLE <> 'NCPROMOCION'
  AND GL.GL_FAMILLENIV1 <> 'INS'
  AND GL_FAMILLENIV1 <> 'LOG'
  AND GL_FAMILLENIV1 <> 'REP'
  AND GL_FAMILLENIV1 <> 'SER'
ORDER BY GL.GL_DATEPIECE DESC;
            """

            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)

            st.download_button(
                "📄 Descargar Excel",
                data=output.getvalue(),
                file_name="reporte_martin.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
