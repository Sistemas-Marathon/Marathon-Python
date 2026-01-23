# rrhh_maxmin_streamlit.py
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

def run():
    st.title("📦 Stock Mínimo y Máximo por Código de Barras")

    uploaded_file = st.file_uploader(
        "📤 Subí el archivo Excel base (múltiples hojas)",
        type=["xlsx"]
    )

    if uploaded_file and st.button("📊 Procesar archivo"):
        try:
            # Leer todas las hojas del Excel
            excel_data = pd.read_excel(
                uploaded_file,
                sheet_name=None,
                engine="openpyxl"
            )

            fecha_actualArchivo = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
            csv_data = []

            for sheet_name, df in excel_data.items():
                st.write(f"📄 Procesando hoja: **{sheet_name}**")

                # Renombrar primera columna como codigo_barras
                df = df.rename(columns={df.columns[0]: 'codigo_barras'})

                # Filtrar filas con códigos válidos
                df = df[
                    df['codigo_barras'].notna() &
                    (df['codigo_barras'].astype(str).str.strip() != '')
                ]

                for row in df.itertuples(index=False):
                    codigo_barras = str(row.codigo_barras).strip()

                    for col_name, valor_celda in zip(df.columns[1:], row[1:]):
                        if (
                            pd.notna(valor_celda)
                            and isinstance(valor_celda, str)
                            and ';' in valor_celda
                        ):
                            partes = valor_celda.split(';')

                            if len(partes) == 2:
                                try:
                                    stock_min = int(partes[0].strip())
                                    stock_max = int(partes[1].strip())

                                    csv_data.append([
                                        'SMIC1_',
                                        codigo_barras,
                                        stock_min,
                                        stock_max,
                                        col_name
                                    ])
                                except ValueError:
                                    st.warning(
                                        f"⚠️ Valores no numéricos | Hoja: {sheet_name} | "
                                        f"Código: {codigo_barras} | Columna: {col_name}"
                                    )
                            else:
                                st.warning(
                                    f"⚠️ Formato incorrecto | Hoja: {sheet_name} | "
                                    f"Código: {codigo_barras} | Columna: {col_name}"
                                )

                        elif pd.notna(valor_celda):
                            st.warning(
                                f"⚠️ Formato inválido (sin ;) | Hoja: {sheet_name} | "
                                f"Código: {codigo_barras} | Columna: {col_name}"
                            )

            # Crear DataFrame final
            csv_df = pd.DataFrame(
                csv_data,
                columns=[
                    'ENCABEZADO',
                    'CODIGO DE BARRAS',
                    'STOCK MIN',
                    'STOCK MAX',
                    'ALMACEN'
                ]
            )

            output = BytesIO()
            csv_df.to_csv(
                output,
                index=False,
                sep='|',
                encoding='utf-8-sig'
            )

            st.success(f"✅ Procesado correctamente: {len(csv_df)} registros")

            st.download_button(
                label="📥 Descargar CSV generado",
                data=output.getvalue(),
                file_name=f"MAXMIN_{fecha_actualArchivo}.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"❌ Error durante el procesamiento: {e}")
