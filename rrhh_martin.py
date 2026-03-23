# rrhh_martin.py
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
                            GCL_TCONTRAT AS MOD_HORARIA,
                            CC_LIBELLE AS ROL_COMERCIAL,
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
                        LEFT JOIN CHOIXCOD ON GCL_FONCTIONCOM=CC_CODE AND CC_TYPE='MFO'
                        WHERE GL_DATEPIECE >= ? AND GL_DATEPIECE <= ?
                        AND GL_NATUREPIECEG IN ('FFO')
                        AND GP_TYPECOMPTA IN ('FAC','TIC')
                        AND GL_TYPEARTICLE IN ('MAR','NOM')
                        AND GP_TICKETANNULE <> 'X'
                        AND GL_CODEARTICLE <> 'CE001'
                        AND GL_CODEARTICLE <> 'NCPROMOCION'
                        AND GL_FAMILLENIV1 <> 'INS'
                        ORDER BY GL_DATEPIECE desc
            """

            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📄 Descargar Excel", output.getvalue(), file_name="reporte_martin.xlsx")

        except Exception as e:
            st.error(f"❌ Error: {e}")
