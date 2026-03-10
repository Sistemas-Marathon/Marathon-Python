# generar_csv_liac.py
import streamlit as st
import pandas as pd
from io import BytesIO

def run():
    st.title("📄 Generador de CSV LIAC")

    uploaded_file = st.file_uploader(
        "📤 Subí un archivo Excel con las columnas 'codigo' y 'lista'",
        type=["xlsx"]
    )

    if uploaded_file and st.button("🎯 Generar CSV"):
        try:
            df = pd.read_excel(uploaded_file, dtype=str)

            # Normalizar nombres de columnas
            df.columns = [col.strip().lower() for col in df.columns]

            if "codigo" not in df.columns or "lista" not in df.columns:
                st.error("❌ El archivo debe tener las columnas 'codigo' y 'lista'.")
                return

            # Limpiar datos
            df["codigo"] = df["codigo"].fillna("").astype(str).str.strip()
            df["lista"] = df["lista"].fillna("").astype(str).str.strip()

            # Filtrar filas vacías
            df = df[(df["codigo"] != "") & (df["lista"] != "")]

            if df.empty:
                st.error("❌ No hay filas válidas para procesar.")
                return

            # Generar formato requerido
            df_resultado = pd.DataFrame()
            df_resultado["registro"] = "LIAC1_|" + df["codigo"] + "|" + df["lista"]

            # Convertir a CSV en memoria
            csv_buffer = BytesIO()
            csv_buffer.write(df_resultado.to_csv(index=False, header=False, encoding="utf-8").encode("utf-8"))
            csv_buffer.seek(0)

            st.success("✅ ¡CSV generado correctamente!")
            st.download_button(
                label="📥 Descargar CSV",
                data=csv_buffer,
                file_name="liac_generado.csv",
                mime="text/csv"
            )

            # Vista previa
            st.subheader("👀 Vista previa")
            st.dataframe(df_resultado)

        except Exception as e:
            st.error(f"❌ Error: {e}")
