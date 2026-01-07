
# rrhh_desglose_recibos_dab.py
import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
import zipfile
import re

def buscar_dato_abajo(pagina, palabra_clave, delta_y=5):
    """
    Busca la palabra_clave en el PDF y retorna el texto que esté justo debajo (en línea vertical).
    """
    bloques = pagina.get_text("dict")["blocks"]
    candidatos = []
    for bloque in bloques:
        for linea in bloque.get("lines", []):
            for span in linea["spans"]:
                if palabra_clave.lower() in span["text"].lower():
                    x0, y0 = span["bbox"][0], span["bbox"][1]
                    # Buscar texto más cercano hacia abajo
                    for otro_bloque in bloques:
                        for otra_linea in otro_bloque.get("lines", []):
                            for otro_span in otra_linea["spans"]:
                                x1, y1 = otro_span["bbox"][0], otro_span["bbox"][1]
                                if abs(x0 - x1) < 30 and 0 < y1 - y0 < delta_y:
                                    candidatos.append((y1, otro_span["text"].strip()))
    if candidatos:
        # Ordenar por y (de menor a mayor) y tomar el primero
        candidatos.sort()
        return candidatos[0][1]
    return None

def dividir_pdf_streamlit(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
        for i, pagina in enumerate(doc):
            # --- LEGAJO ---
            legajo_raw = buscar_dato_abajo(pagina, "Legajo", delta_y=20) or f"desconocido_{i+1}"

            # Extraer solo números del legajo
            m = re.search(r"\d+", str(legajo_raw))
            legajo = m.group(0) if m else f"desconocido_{i+1}"

            # Prefijo según cantidad de dígitos
            prefijo = "100" if legajo.isdigit() and len(legajo) == 2 else "10"

            # --- DESCRIPCIÓN ---
            descripcion = buscar_dato_abajo(pagina, "Descripción del pago", delta_y=20) or "sin_descripcion"

            # --- NOMBRE DE ARCHIVO ---
            nombre_archivo = f"{prefijo}{legajo} - {descripcion}.pdf"
            nombre_archivo = nombre_archivo.replace("/", "-").replace("\\", "-").strip()

            # --- CREAR PDF INDIVIDUAL ---
            nuevo_pdf = fitz.open()
            nuevo_pdf.insert_pdf(doc, from_page=i, to_page=i)
            pdf_bytes_individual = nuevo_pdf.write()
            zipf.writestr(nombre_archivo, pdf_bytes_individual)
            nuevo_pdf.close()

    doc.close()
    zip_buffer.seek(0)
    return zip_buffer

def run():
    st.set_page_config(page_title="Desglose de Recibos DAB", page_icon="📄")
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

if __name__ == "__main__":
    run()
