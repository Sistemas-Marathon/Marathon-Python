import streamlit as st
import pandas as pd
import pymssql
from io import BytesIO


def run():
    st.title("💵 Consulta de ventas por banco (Cajas)")

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
            fecha_inicio_sql = fecha_inicio.strftime("%Y-%m-%d")
            fecha_fin_sql = fecha_fin.strftime("%Y-%m-%d")
            query = """
            SELECT
                G.GPE_DATEPIECE AS FECHA_TRANS,
                G.GPE_NUMERO AS NUMERO_TICKET,
                G.GPE_SOUCHE AS SUC,
                G.GPE_MODEPAIE AS COD_PAGO,
                G.GPE_CBNBVERSEMENT AS CUOTAS,
                G.GPE_MONTANTECHE AS PRECIO,
                MB.MBE_BLOCNOTE AS NRO_TARJETA
            FROM GCREGLEMENTFO G
            INNER JOIN MPIEDECHEOLE MB
                ON MB.MBE_SOUCHE = G.GPE_SOUCHE
                AND MB.MBE_NUMERO = G.GPE_NUMERO
                AND MB.MBE_INDICEG = G.GPE_INDICEG
                AND MB.MBE_NUMECHE = G.GPE_NUMECHE
            WHERE MB.MBE_BLOCNOTE IS NOT NULL
              AND G.GPE_DATEPIECE >= CONVERT(date, %s, 23)
              AND G.GPE_DATEPIECE < DATEADD(day, 1, CONVERT(date, %s, 23));
            """

            df = pd.read_sql(query, conn, params=[fecha_inicio_sql, fecha_fin_sql])
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
            
            # Agregar tipo de tarjeta si existe la columna en base.xlsx
            if "TIPO_TARJETA" in bin_df.columns:
                df.rename(columns={"TIPO_TARJETA": "TIPO_TARJETA"}, inplace=True)
                df["TIPO_TARJETA"] = df["TIPO_TARJETA"].fillna("Desconocido")

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
