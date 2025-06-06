# rrhh_maxmin_series.py
import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO
from datetime import datetime

def run():
    st.title("📦 Stock Mínimo y Máximo por Serie (RRHH)")

    uploaded_file = st.file_uploader("📤 Subí el archivo Excel base", type=["xlsx"])

    if uploaded_file and st.button("📊 Procesar archivo"):
        try:
            # Conexión
            conn_str = (
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=181.209.94.152,29433;'
                'DATABASE=MARAPROD24;'
                'UID=BIMA;'
                'PWD=Mar2024*'
            )
            conn = pyodbc.connect(conn_str)

            # Leer el Excel
            df_excel = pd.read_excel(uploaded_file, header=None, dtype={0: str})
            almacenes = df_excel.iloc[0, 1:].tolist()

            csv_data = []
            fecha_actualArchivo = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

            # Iterar por filas
            for i in range(1, len(df_excel)):
                codigo_articulo = df_excel.iloc[i, 0]
                for j in range(1, len(df_excel.columns)):
                    codigo_serie = df_excel.iloc[i, j]
                    if pd.isna(codigo_articulo) or pd.isna(codigo_serie):
                        continue

                    almacen = almacenes[j - 1]

                    query = f"""
                    SELECT 
                        GA_CODEBARRE,
                        GAM_QTEDISPOMINI,
                        GAM_QTEDISPOMAXI
                    FROM ARTICLESERIE
                    INNER JOIN DIMMASQUE ON GDM_MASQUE=GAM_DIMMASQUE AND GDM_TYPEMASQUE='LON'
                    INNER JOIN ARTICLE ON GAM_DIMMASQUE=GA_DIMMASQUE AND GAM_GRILLEDIM1=GA_GRILLEDIM1 AND GAM_GRILLEDIM2=GA_GRILLEDIM2 
                        AND GAM_CODEDIM1=GA_CODEDIM1 AND GAM_CODEDIM2=GA_CODEDIM2 AND GA_CODEARTICLE='{codigo_articulo}'
                    WHERE GAM_CODESERIE='{codigo_serie}'
                    """

                    df_query = pd.read_sql(query, conn)

                    for _, result_row in df_query.iterrows():
                        csv_data.append([
                            'SMIC1_',
                            result_row['GA_CODEBARRE'],
                            f"{int(result_row['GAM_QTEDISPOMINI'])};{int(result_row['GAM_QTEDISPOMAXI'])}",
                            almacen
                        ])

            conn.close()

            # Armar el DataFrame resultado
            csv_df = pd.DataFrame(csv_data, columns=['ENCABEZADO', 'CODIGO_BARRA', 'MIN;MAX', 'ALMACEN'])

            output = BytesIO()
            csv_df.to_csv(output, index=False, sep='|')
            st.success(f"✅ Procesado correctamente: {len(csv_df)} registros")

            st.download_button(
                label="📥 Descargar CSV generado",
                data=output.getvalue(),
                file_name=f"MAXMIN_{fecha_actualArchivo}.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
