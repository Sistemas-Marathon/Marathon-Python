# rrhh_tem_tre.py
import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO

def run():
    st.title("🔁 Consulta por descuentos empleados")

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
            -- Rango de fechas (inclusive)
DECLARE @desde date = ?;
DECLARE @hasta date = ?;

WITH conteo AS (
  SELECT
    GL_ETABLISSEMENT,
    GL_TIERS,
    COUNT(*) AS repeticiones
  FROM [MARAPROD24].[dbo].[LIGNE]
  WHERE GL_NATUREPIECEG IN ('FFO', 'TIC')
    AND GL_DATEPIECE >= @desde
    AND GL_DATEPIECE < DATEADD(day, 1, @hasta)  -- inclusivo hasta @hasta
    -- AND GL_TIERS IS NOT NULL  -- (descomentá si querés omitir nulos)
  GROUP BY GL_ETABLISSEMENT, GL_TIERS
),
top10 AS (
  SELECT
    GL_ETABLISSEMENT,
    GL_TIERS,
    repeticiones,
    ROW_NUMBER() OVER (
      PARTITION BY GL_ETABLISSEMENT
      ORDER BY repeticiones DESC, GL_TIERS
    ) AS rn
  FROM conteo
)
SELECT
  GL_ETABLISSEMENT,
  GL_TIERS,
  repeticiones
FROM top10
WHERE rn <= 10
ORDER BY GL_ETABLISSEMENT, repeticiones DESC, GL_TIERS;

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
