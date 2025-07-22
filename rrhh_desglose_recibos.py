# rrhh_desglose_recibos.py
import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
import zipfile
import os

def buscar_dato_abajo(pagina, palabra_clave, delta_y=15):
    """
    Busca la palabra_clave en el PDF y retorna el texto que esté justo debajo.
    """
    bloques = pagina.get_text("dict")["blocks"]
    for bloque in bloques:
        for linea in bloque.get("lines", []):
            for span in linea["spans"]:
                if palabra_clave.lower() in span["text"].lower():
                    x0, y0 = span["bbox"][0], span["bbox"][1]
                    # Buscar texto cercano hacia abajo
                    for otro_bloque in bloques:
                        for otra_linea in otro_bloque.get("lines", []):
                            for otro_span in otra_linea["spans"]:
                                x1, y1 = otro_span["bbox"][0], otro_span["bbox"][1]
                                if abs(x0 - x1) < 30 and y1 > y0 and y1 - y0 < delta_y * 2:
                                    return otro_span["text"].strip()
    return None

def dividir_pdf_streamlit(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
        for i, pagina in enumerate(doc):
            legajo = buscar_dato_abajo(pagina, "Legajo") or f"desconocido_{i+1}"
            descripcion = buscar_dato_abajo(pagina, "Descripción del pago") or "sin_descripcion"

            # Sanitizar nombre del archivo
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
    st.set_page_config(page_title="Desglose de Recibos", page_icon="📄")
    st.title("📄 Desglose de Recibos de Sueldo")
    uploaded_pdf = st.file_uploader("Subí el PDF con los recibos", type=["pdf"])
    if uploaded_pdf:
        st.info("Procesando el PDF, por favor esperá...")
        zip_buffer = dividir_pdf_streamlit(uploaded_pdf.read())
        st.success("¡Listo! Descargá los recibos individuales.")
        st.download_button(
            label="📥 Descargar ZIP",
            data=zip_buffer.getvalue(),
            file_name="recibos_individuales.zip",
            mime="application/zip"
        )

# Ejecutar si se llama directamente
if __name__ == "__main__":
    run()
