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

WITH base AS (
  SELECT
    gp_etablissement,
    gp_tiers = UPPER(LTRIM(RTRIM(gp_tiers)))
  FROM piece
  WHERE GP_NATUREPIECEG IN ('FFO') 
    AND GP_DATEPIECE >= @desde
    AND GP_DATEPIECE < DATEADD(day, 1, @hasta)  -- inclusivo hasta @hasta
    AND GP_TYPECOMPTA IN ('FAC','TIC')
    AND (GP_SUPPRIME IS NULL OR GP_SUPPRIME <> 'X')
    -- AND GP_TIERS = 'defecto'  -- <- descomentar si querés un cliente puntual
),
conteo AS (
  SELECT
    gp_etablissement,
    gp_tiers,
    COUNT(*) AS repeticiones
  FROM base
  WHERE gp_tiers IS NOT NULL AND gp_tiers <> ''
  GROUP BY gp_etablissement, gp_tiers
),
ranked AS (
  SELECT
    gp_etablissement,
    gp_tiers,
    repeticiones,
    ROW_NUMBER() OVER (
      PARTITION BY gp_etablissement
      ORDER BY repeticiones DESC, gp_tiers
    ) AS rn
  FROM conteo
)
SELECT
  gp_etablissement,
  gp_tiers,
  repeticiones
FROM ranked
WHERE rn <= 10
ORDER BY gp_etablissement, repeticiones DESC, gp_tiers;

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
