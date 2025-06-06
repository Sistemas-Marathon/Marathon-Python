# reposicion_cruzada.py
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import zipfile

def run():
    st.title("🚛 Reposición Cruzada")

    uploaded_files = st.file_uploader("📤 Subí los archivos Excel", type=["xlsx"], accept_multiple_files=True)

    if uploaded_files:
        try:
            st.success("✅ Archivos recibidos. Procesando...")

            zip_buffer = BytesIO()
            numero = 1
            fecha_actual = datetime.now().strftime('%d/%m/%Y')
            fecha_actualArchivo = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zipf:
                for uploaded_file in uploaded_files:
                    sheets_dict = pd.read_excel(uploaded_file, sheet_name=None, dtype=str)
                    for sheet_name, df in sheets_dict.items():
                        columnas_emisores = df.iloc[0, 1:].tolist()
                        columnas_receptores = df.iloc[1, 1:].tolist()

                        if len(columnas_emisores) != len(columnas_receptores):
                            st.warning(f"La hoja '{sheet_name}' tiene diferente cantidad de emisores y receptores. Saltando.")
                            continue

                        comercial = df.iloc[0, 0]
                        referencia = df.iloc[1, 0]
                        referenciaext = ""

                        for idx, columnaEmisor in enumerate(columnas_emisores):
                            columna_receptor = columnas_receptores[idx]

                            data = {
                                'CABECERA': 'SDTC1_',
                                'COD BARRA': [],
                                'CANTIDAD': [],
                                'ESTABLECIMIENTO': [],
                                'ESTABLECIMIENTO RECEPTOR': [],
                                'ALMACEN RECEPTOR': [],
                                'FECHA DOCUMENTO': [],
                                'FECHA DE ENTREGA': [],
                                'FECHA DE REF EXTERNA': [],
                                'REFERENCIA INTERNA': [],
                                'COMERCIAL': [],
                                'REFERENCIA EXTERNA': []
                            }

                            for _, fila in df.iloc[2:].iterrows():
                                codigo_barra = str(fila[df.columns[0]])
                                valor_celda = fila[df.columns[idx + 1]]

                                if pd.notna(valor_celda) and str(valor_celda) != '0':
                                    data['COD BARRA'].append(codigo_barra)
                                    data['CANTIDAD'].append(str(valor_celda))
                                    data['ESTABLECIMIENTO'].append(columnaEmisor)
                                    data['ESTABLECIMIENTO RECEPTOR'].append(columna_receptor)
                                    data['ALMACEN RECEPTOR'].append(columna_receptor)
                                    data['FECHA DOCUMENTO'].append(fecha_actual)
                                    data['FECHA DE ENTREGA'].append(fecha_actual)
                                    data['FECHA DE REF EXTERNA'].append(fecha_actual)
                                    data['REFERENCIA INTERNA'].append(referenciaext)
                                    data['COMERCIAL'].append(comercial)
                                    data['REFERENCIA EXTERNA'].append(referencia)

                            if data['COD BARRA']:
                                df_filtrado = pd.DataFrame(data)
                                nombre_archivo = f'{str(numero).zfill(2)}-{sheet_name}-{columnaEmisor}-{columna_receptor}-{fecha_actualArchivo}.csv'
                                csv_buffer = df_filtrado.to_csv(index=False, sep='|').encode('utf-8')
                                zipf.writestr(nombre_archivo, csv_buffer)
                                numero += 1

            st.success("✅ Procesamiento completo. Descargá los archivos generados.")
            st.download_button(
                label="📥 Descargar CSVs en ZIP",
                data=zip_buffer.getvalue(),
                file_name=f"reposicion_{fecha_actualArchivo}.zip",
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"❌ Ocurrió un error al procesar los archivos: {e}")
