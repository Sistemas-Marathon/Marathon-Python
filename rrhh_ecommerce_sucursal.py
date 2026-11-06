# rrhh_ecommerce_sucursal.py
import streamlit as st
import pandas as pd
import pymssql
from io import BytesIO


def run():
    st.title("🛒 Ventas E-commerce por Sucursal (RRHH)")

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

            query = """SELECT
    'ticket' AS [Clase],
    GL_DATEPIECE AS [Fecha],
    GL_REPRESENTANT AS [Comercial del doc.],
    GCL_LIBELLE AS NOMBRE_COMERCIAL,
    GL_ETABLISSEMENT AS [Establecimiento],
    GP_TYPECOMPTA AS TIPO_DOCUMENTO,
    GL_NUMERO AS [Número],
    GP_REFINTERNE AS [Referencia interna doc..],
    GP_NUMPIECE AS [Referencia fiscal del documento],
    GP_REFSUIVI AS [Ref. de seguimiento doc.],
    GP_NUMZCAISSE AS [Número de "ticket Z" de caja doc],
    GP_TIERS AS [Código NIF],
    GP_TYPEFISCAL AS [Código del tipo fiscal],
    GP_CAISSE AS [Caja],
    UM.US_LIBELLE AS [Usuario de modif. doc..],
    GP_DATEMODIF AS [Fecha modificación doc.],
    UO.US_LIBELLE AS [Usuario de origen],
    GP_TIERSFACTURE AS [Tercero facturado],
    GL_FAMILLENIV1 AS TIPO_ARTICULO,
    GL_LIBREART2 AS MARCA,
    GL_CODEARTICLE AS CODIGO_ARTICULO,
    GL_QTEFACT AS CANTIDAD,
    GP_TOTALHT AS [Total exc. IVA documento],
    GP_TOTALTTC AS PRECIO,
    CAST(GP_HEURECREATION AS TIME) AS [Hora de creación],
    GP_TYPEPROVENANCE AS TIPO,
    CASE WHEN GL_ETABLISSEMENT = '249999' OR GP_TYPEPROVENANCE = 'ECO' THEN 'ECO' ELSE 'LOCAL' END AS ECO,
    GL.GL_LIBELLE AS NOMBRE_ARTICULO,
    CCFN7.CC_LIBELLE AS CLASIFICACION
FROM [MARAPROD24].[dbo].[GCLIGNEARTDIM] GL
LEFT JOIN COMMERCIAL ON GL_REPRESENTANT=GCL_COMMERCIAL
LEFT JOIN ARTICLE_COMPL AC
    ON GL.GL_ARTICLE = AC.GA_ARTICLE
LEFT JOIN CHOIXCOD CCFN7
    ON AC.GA2_FAMILLENIV7 = CCFN7.CC_CODE
   AND CCFN7.CC_TYPE = 'FN7'
LEFT JOIN UTILISAT UM ON GP_UTILISATEUR = UM.US_UTILISATEUR
LEFT JOIN UTILISAT UO ON GP_CREATEUR = UO.US_UTILISATEUR
WHERE GL_DATEPIECE >= %s AND GL_DATEPIECE <= %s
AND GL_NATUREPIECEG IN ('FFO')
AND GP_TYPECOMPTA IN ('FAC','TIC')
AND GL_TYPEARTICLE IN ('MAR','NOM')
AND GP_TICKETANNULE <> 'X'
AND GL_CODEARTICLE <> 'CE001'
AND GL_CODEARTICLE <> 'NCPROMOCION'
AND GL_CODEARTICLE IS NOT NULL
AND LTRIM(RTRIM(GL_CODEARTICLE)) <> ''
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
            st.download_button(
                "📄 Descargar Excel",
                output.getvalue(),
                file_name="ecommerce_por_sucursal.xlsx",
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
