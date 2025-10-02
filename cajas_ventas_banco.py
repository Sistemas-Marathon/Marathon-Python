import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO

def run():
    st.title("🔁 Consulta de ventas por banco")

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
            SET DATEFORMAT dmy;
            SELECT
                GPE_DATEPIECE AS FECHA_TRANS,
                GPE_NUMERO AS NUMERO_TICKET,
                GPE_SOUCHE AS SUC,
                GPE_MODEPAIE AS COD_PAGO,
                MP_LIBELLE AS TARJETA,
                GPE_CBNBVERSEMENT AS CUOTAS,
                GPE_MONTANTECHE AS PRECIO,
                GPE_CBNUMTRANSAC AS NRO_TARJETA
            FROM GCREGLEMENTFO
            WHERE GPE_CBNUMTRANSAC <> ''
            AND GPE_DATEPIECE BETWEEN ? AND ?;

            """

            df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
            conn.close()

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📄 Descargar Excel", output.getvalue(), file_name="consulta_ventas_banco.xlsx")

        except Exception as e:
            st.error(f"❌ Error: {e}")
