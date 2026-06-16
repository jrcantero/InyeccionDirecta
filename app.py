import streamlit as st
import pandas as pd
from molmass import Formula
import io

# Configuración de la página web
st.set_page_config(page_title="Procesador de Inyección Directa", page_icon="🧪", layout="centered")

st.title("🧪 Procesador de Masa Monoisotópica")
st.write("Sube tu archivo CSV (separado por punto y coma), procesa las fórmulas químicas y descarga los resultados.")

# 1. Componente para subir el archivo
uploaded_file = st.file_uploader("Elige tu archivo CSV", type=['csv'])

if uploaded_file is not None:
    try:
        # Leer el archivo subido en memoria
        # Se usa sep=';' manteniendo tu lógica original
        samples = pd.read_csv(uploaded_file, sep=';')
        
        # Validar que las columnas necesarias existan
        if 'Muestra' not in samples.columns or 'Formula' not in samples.columns:
            st.error("El archivo CSV debe contener las columnas 'Muestra' y 'Formula'.")
        else:
            st.success("Archivo subido correctamente. Vista previa:")
            st.dataframe(samples.head()) # Muestra las primeras filas en la web

            # Botón para iniciar el procesamiento
            if st.button("Procesar Datos"):
                with st.spinner("Calculando masas espectrales..."):
                    
                    monoisotopica_H = 1.007825
                    new_rows = []

                    # Tu lógica original de procesamiento
                    for index, row in samples.iterrows():
                        name = row['Muestra']
                        formula = row['Formula']
                        
                        try:
                            mol = Formula(formula)
                            molecular_weight = mol.mass
                            spectrum = mol.spectrum()
                            
                            # Obtener la masa del pico más intenso
                            masa_registrada = max(spectrum.values(), key=lambda p: p.intensity).mass

                            masa_positiva = masa_registrada + monoisotopica_H
                            masa_negativa = masa_registrada - monoisotopica_H
                            
                            new_rows.append({
                                'Muestra': name,
                                'Formula': formula,
                                'Molecular Weight': molecular_weight,
                                'M+H': masa_positiva,
                                'M-H': masa_negativa
                            })
                        except Exception as e:
                            # Por si hay alguna fórmula mal escrita en el CSV
                            st.warning(\u0066"Error al procesar la fórmula '{formula}' en la fila {index}: {e}")

                    # Crear el nuevo DataFrame
                    new_df = pd.DataFrame(new_rows)
                    
                    st.write("### Resultados Procesados")
                    st.dataframe(new_df.head())

                    # 2. Convertir el DataFrame a CSV en memoria para la descarga
                    output_stream = io.StringIO()
                    new_df.to_csv(output_stream, index=False)
                    csv_data = output_stream.getvalue()

                    # 3. Componente para descargar el archivo terminado
                    st.download_button(
                        label="📥 Descargar archivo procesado",
                        data=csv_data,
                        file_name="resultados_masas.csv",
                        mime="text/csv"
                    )

    except Exception as e:
        st.error(\u0066"Ocurrió un error al leer el archivo: {e}")