# rrhh_desglose_recibos.py
import streamlit as st
import fitz  # PyMuPDF
import re
from io import BytesIO
import zipfile

def extraer_legajo_y_descripcion(texto):
    """
    Extrae el legajo y la descripción del pago del bloque de texto.
    """
    legajo_match = re.search(r"Legajo\s+(\d+)", texto)
    desc_match = re.search(r"Descripción del pago\s+(\w+\s+\d{4})", texto)

    legajo = legajo_match.group(1) if legajo_match else "sin_legajo"
    descripcion = desc_match.group(1) if desc_match else "sin_descripcion"
    return legajo, descripcion

def dividir_pdf_streamlit(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
        for i, pagina in enumerate(doc):
            texto = pagina.get_text()
            legajo, descripcion = extraer_legajo_y_descripcion(texto)
            nombre_archivo = f"{legajo} - {descripcion}.pdf"
            nombre_archivo = nombre_archivo.replace("/", "-").replace("\\", "-").strip()
            nuevo_pdf = fitz.open()
            nuevo_pdf.insert_pdf(doc, from_page=i, to_page=i)
            pdf_bytes_individual = nuevo_pdf.write()
            zipf.writestr(nombre_archivo, pdf_bytes_individual)
            nuevo_pdf.close()
    doc.close()
    zip_buffer.seek(0)
    return zip_buffer

def run():
    st.title("📄 Desglose de Recibos PDF")
    uploaded_pdf = st.file_uploader("Subí el PDF con los recibos", type=["pdf"])
    if uploaded_pdf:
        st.info("Procesando el PDF...")
        zip_buffer = dividir_pdf_streamlit(uploaded_pdf.read())
        st.success("¡Listo! Descargá los recibos individuales en un ZIP.")
        st.download_button(
            label="📥 Descargar ZIP",
            data=zip_buffer.getvalue(),
            file_name="recibos_individuales.zip",
            mime="application/zip"
        )
