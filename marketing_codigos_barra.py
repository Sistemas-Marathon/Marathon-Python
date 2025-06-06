# marketing_codigos_barra.py
import streamlit as st
import pandas as pd
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import zipfile
import os

def run():
    st.title("🏷️ Generador de Códigos de Barras (Marketing)")

    uploaded_file = st.file_uploader("📤 Subí un archivo Excel con la columna 'Codigo'", type=["xlsx"])

    if uploaded_file and st.button("🎯 Generar códigos"):
        try:
            df = pd.read_excel(uploaded_file, dtype=str)
            if "Codigo" not in df.columns:
                st.error("❌ El archivo debe tener una columna llamada 'Codigo'.")
                return

            # Crear ZIP en memoria
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zipf:
                for codigo in df["Codigo"].dropna():
                    codigo = str(codigo).strip()
                    if not codigo:
                        continue

                    code128 = barcode.get("code128", codigo, writer=ImageWriter())
                    buffer_img = BytesIO()
                    code128.write(buffer_img, {
                        'font_size': 16,
                        'text_distance': 6,
                        'quiet_zone': 10,
                        'module_height': 40,
                        'module_width': 0.4,
                        'write_text': True,
                        'background': 'white'
                    })
                    zipf.writestr(f"{codigo}.png", buffer_img.getvalue())

            st.success("✅ ¡Códigos generados correctamente!")
            st.download_button(
                label="📥 Descargar ZIP con imágenes",
                data=zip_buffer.getvalue(),
                file_name="codigos_barra.zip",
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
