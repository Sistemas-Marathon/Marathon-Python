# rrhh_lleg_tardes.py
import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO


def run():
    st.title("🕒 Llegadas Tardes y Justificaciones (RRHH)")

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
            query = """
            SELECT DISTINCT PL.MPS_ETABLISSEMENT AS ETABLISSEMENT, ET_LIBELLE AS LIBELLE, PL.MPS_COMMERCIAL AS CODECOMMERCIAL, 
            GCL_PRENOM + ' ' + GCL_LIBELLE AS COMMERCIAL, 
            PL.MPS_DATEDEBPLAGE AS DATEHEUREPLANNING, PO.MPS_DATEDEBPLAGE AS DATEHEUREPOINTAGE, 
            (CAST((PO.MPS_DATEDEBPLAGE - PL.MPS_DATEDEBPLAGE) AS FLOAT) - CAST((PO.MPS_DATEDEBPLAGE - PL.MPS_DATEDEBPLAGE) AS INTEGER)) / 
            (CAST(CAST('01/01/1900 00:01:00' AS DATETIME) AS FLOAT)) AS NBMINUTES 
            FROM MPLAGESALARIE PL 
            LEFT OUTER JOIN MPLAGESALARIE PO ON PL.MPS_IDPLAGE = PO.MPS_IDPLAGEPREV 
            LEFT OUTER JOIN COMMERCIAL ON PL.MPS_COMMERCIAL = GCL_COMMERCIAL 
            LEFT OUTER JOIN ETABLISS ON PL.MPS_ETABLISSEMENT = ET_ETABLISSEMENT 
            WHERE PO.MPS_DATEDEBPLAGE IS NOT NULL
            AND pl.MPS_DATEDEBPLAGE >= ? AND pl.MPS_DATEDEBPLAGE <= ?
            ORDER BY PL.MPS_DATEDEBPLAGE
            """
            
            query1= """SELECT DISTINCT
                p.MPS_COMMERCIAL as Comercial, 
                C.GCL_LIBELLE AS Apellido,
                C.GCL_PRENOM AS Nombre,
                c.gcl_tcontrat as Contrato,
                p.MPS_ETABLISSEMENT as Establecimiento, 
                e.ET_LIBELLE AS Nombre_Establecimiento,
                CONVERT(VARCHAR(10), r.MPS_DATEDEBPLAGE, 103) AS Fecha,
                CONVERT(VARCHAR(5), p.MPS_DATEDEBPLAGE, 108) + ' - ' + CONVERT(VARCHAR(5), p.MPS_DATEFINPLAGE, 108) AS Horario_planificado,
                CONVERT(VARCHAR(5), r.MPS_DATEDEBPLAGE, 108) + ' - ' + CONVERT(VARCHAR(5), r.MPS_DATEFINPLAGE, 108) AS Horario_realizada,
                p.MPS_DUREEPLAGE AS Horas_Planificadas,
                r.MPS_DUREEPLAGE AS Horas_Realizadas,
                ISNULL(j1.CC_LIBELLE, r.MPS_JUSTIF1) AS Nombre_Justificacion1,
                ISNULL(j2.CC_LIBELLE, r.MPS_JUSTIF2) AS Nombre_Justificacion2,
                ISNULL(j3.CC_LIBELLE, r.MPS_JUSTIF3) AS Nombre_Justificacion3,
                CONVERT(NVARCHAR(MAX), r.MPS_BLOCNOTE) AS Notas
                
            FROM 
                MPLAGESALARIE r
            JOIN 
                MPLAGESALARIE p 
            ON 
                r.MPS_IDPLAGEPREV = p.MPS_IDPLAGE
            LEFT JOIN 
                CHOIXCOD j1 ON r.MPS_JUSTIF1 = j1.CC_CODE AND j1.CC_TYPE='MJP'
            -- Join para obtener el nombre de MPS_JUSTIF2
            LEFT JOIN 
                CHOIXCOD j2 ON r.MPS_JUSTIF2 = j2.CC_CODE AND j1.CC_TYPE='MJP'
            -- Join para obtener el nombre de MPS_JUSTIF3
            LEFT JOIN 
                CHOIXCOD j3 ON r.MPS_JUSTIF3 = j3.CC_CODE AND j1.CC_TYPE='MJP'

            INNER JOIN COMMERCIAL C ON P.MPS_COMMERCIAL=C.GCL_COMMERCIAL
            INNER JOIN etabliss e ON  P.MPS_ETABLISSEMENT = E.ET_ETABLISSEMENT

            WHERE 
                r.MPS_IDPLAGEPREV IS NOT NULL AND 
                CONVERT(VARCHAR(10), r.MPS_DATEDEBPLAGE, 103) >= ? AND 
                CONVERT(VARCHAR(10), r.MPS_DATEDEBPLAGE, 103) <= ? AND

            """


            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            df1 = pd.read_sql(query1,conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)
            st.dataframe(df1)
            output = BytesIO()
            output1 = BytesIO()
            df.to_excel(output, index=False)
            df1.to_excel(output1, index=False)
            st.download_button("📄 Descargar Excel", output.getvalue(), file_name="llegadas_tardes.xlsx")
            st.download_button("📄 Descargar Excel", output1.getvalue(), file_name="justificaciones_llegadas_tardes.xlsx")


        except Exception as e:
            st.error(f"❌ Error: {e}")

