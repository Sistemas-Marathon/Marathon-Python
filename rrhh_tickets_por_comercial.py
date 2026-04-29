# rrhh_tickets_por_comercial.py
import streamlit as st
import pandas as pd
import pymssql
from io import BytesIO

def run():
    st.title("🕒 Tickets por Comercial (RRHH)")

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
            query = """
           SELECT
                GP_REPRESENTANT AS [Comercial del doc.],
                CAST(GP_HEURECREATION AS DATE) AS [Fecha],         -- Extrae solo la parte de la fecha
                CAST(GP_HEURECREATION AS TIME) AS [Hora],          -- Extrae solo la parte de la hora
                GP_ETABLISSEMENT AS [Establecimiento],
                GP_CAISSE AS [Caja],
                GP_TOTALTTC AS [Total IVA inc],
                GP_TOTALHT AS [Total exc. IVA documento],
                US_LIBELLE AS [Ultimo usuario]
            FROM    
                [MARAPROD24].[dbo].[PIECE]
            INNER JOIN
                UTILISAT ON GP_CREATEUR = US_UTILISATEUR
            WHERE
                (GP_DATEPIECE >= %s AND GP_DATEPIECE < %s 
                AND GP_NATUREPIECEG IN ('FFO') 
                AND GP_TYPECOMPTA IN ('FAC','TIC'));
            """

            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📄 Descargar Excel", output.getvalue(), file_name="tickets_por_comercial.xlsx")

        except Exception as e:
            st.error(f"❌ Error: {e}")
