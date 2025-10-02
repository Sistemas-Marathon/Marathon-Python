import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO


def run():
    st.title("💵 Consulta de ventas por banco (Cajas)")

    fecha_inicio = st.date_input("📅 Fecha de inicio")
    fecha_fin = st.date_input("📅 Fecha de fin")

    if st.button("📥 Consultar y descargar"):
        try:
            conn_str = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=181.209.94.152,29433;"
                "DATABASE=MARAPROD24;"
                "UID=BIMA;"
                "PWD=Mar2024*;"
                "TrustServerCertificate=yes;"
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

            # Agregamos mapeo de BIN → Banco
            try:
                bin_df = pd.read_excel("./base.xlsx", dtype={"BIN": str})
                bin_df["BIN"] = bin_df["BIN"].astype(str).str.strip()
            except Exception:
                st.warning("⚠️ No se encontró base.xlsx; los bancos se mostrarán como Desconocido.")
                bin_df = pd.DataFrame(columns=["BIN", "Issuer"])

            def get_bin(nro):
                if not isinstance(nro, str):
                    return ""
                return nro.split("-")[0].strip()

            df["BIN"] = df["NRO_TARJETA"].apply(get_bin)
            df = df.merge(bin_df, on="BIN", how="left")
            df.rename(columns={"Issuer": "BANCO"}, inplace=True)
            df["BANCO"] = df["BANCO"].fillna("Desconocido")

            st.success(f"✅ Consulta exitosa: {len(df)} registros")
            st.dataframe(df)

            # Descargar
            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button(
                "📄 Descargar Excel",
                output.getvalue(),
                file_name=f"cajas_ventas_banco_{fecha_inicio}_{fecha_fin}.xlsx"
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
