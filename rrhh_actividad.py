import streamlit as st
import pandas as pd
import pymssql
from io import BytesIO


def run():
    st.title("Reporte para Actividad en Masa (RRHH)")

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
  p.MPS_IDPLAGE,
  p.MPS_ETABLISSEMENT as Establecimiento,
  g.MTY_LIBELLE as Gama,
  p.MPS_COMMERCIAL as Legajo,
  c.GCL_LIBELLE as Apellido,
  c.GCL_PRENOM as Nombre,
  CONVERT(VARCHAR(10), p.MPS_DATEDEBPLAGE, 103) AS Fecha,
  CONVERT(VARCHAR(5), p.MPS_DATEDEBPLAGE, 108) + ' - ' + CONVERT(VARCHAR(5), p.MPS_DATEFINPLAGE, 108) AS Horario_planificado,
  p.MPS_DUREEPLAGE AS Horas_Planificadas,
  CONVERT(VARCHAR(5), r.MPS_DATEDEBPLAGE, 108) + ' - ' + CONVERT(VARCHAR(5), r.MPS_DATEFINPLAGE, 108) AS Horario_realizada,
  r.MPS_DUREEPLAGE AS Horas_Realizadas
FROM MPLAGESALARIE p
LEFT JOIN MPLAGESALARIE r
  ON r.MPS_IDPLAGEPREV = p.MPS_IDPLAGE
  AND r.MPS_COMMERCIAL = p.MPS_COMMERCIAL
  AND r.MPS_MODEPLA = '002'
LEFT JOIN COMMERCIAL c
  ON p.MPS_COMMERCIAL = c.GCL_COMMERCIAL
LEFT JOIN MTYPEPLAGE g
  ON p.MPS_TYPEPLAGE = g.MTY_TYPEPLAGE
WHERE p.MPS_MODEPLA = '001'
  AND CAST(p.MPS_DATEDEBPLAGE AS DATE) >= ?
  AND CAST(p.MPS_DATEDEBPLAGE AS DATE) <=  ?
ORDER BY p.MPS_DATEDEBPLAGE DESC

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
                file_name="reporte_activadad_masa.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
