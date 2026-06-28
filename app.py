import streamlit as st
import pandas as pd
from molmass import Formula
import io

# Configuración de la página web
st.set_page_config(page_title="Obtener masas para Inyección Directa", page_icon="🧪", layout="centered")

st.title("🧪 Procesador de Masa Monoisotópica")
st.write("Sube tu archivo CSV (separado por punto y coma), procesa las fórmulas químicas y descarga los resultados.")
st.write("El archivo debe tener las columnas Muestra y Formula")

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

            # Botón para comenzar
            if st.button("Procesar Datos"):
                with st.spinner("Calculando masas espectrales..."):
                    
                    proton = 1.007276
                    new_rows = []

                    def calcular_iones(molecula, ion):
                        composicion = molecula.composition().dataframe()

                        if ion=='pos':
                            composicion.loc[composicion.index == 'H', 'Count'] += 1
                        elif ion=='neg':
                            composicion.loc[composicion.index == 'H', 'Count'] -= 1
                        
                        formula_ion = "".join(f"{element}{int(row['Count'])}" for element, row in composicion.iterrows())
                        mol_ion = Formula(formula_ion)
                        patron_isotopico = mol_ion.spectrum()
                        masa_ion = max(patron_isotopico.values(), key=lambda p: p.intensity).mass

                        return masa_ion

                    # procesando las masas
                    for index, row in samples.iterrows():
                        name = row['Muestra']
                        formula = row['Formula']
                        
                        try:
                            mol = Formula(formula)
                            molecular_weight = mol.monoisotopic_mass
                                
                            new_rows.append({
                                'Muestra': name,
                                'Formula': formula,
                                'Molecular Weight': molecular_weight,
                                'M+H': calcular_iones(mol, 'pos'),
                                'M-H': calcular_iones(mol, 'neg')
                            })

                        except Exception as e:
                            # Por si existe algun error
                            st.warning("Error al procesar la fórmula '{formula}' en la fila {index}: {e}")

                    # crear ultimo dataframe
                    new_df = pd.DataFrame(new_rows)
                    
                    st.write("### Resultados Procesados")
                    st.dataframe(new_df.head())

                    # convertir a csv
                    output_stream = io.StringIO()
                    new_df.to_csv(output_stream, index=False, sep=';')
                    csv_data = output_stream.getvalue()

                    # descarga de archivo
                    st.download_button(
                        label="📥 Descargar archivo procesado",
                        data=csv_data,
                        file_name="resultados_masas.csv",
                        mime="text/csv"
                    )

    except Exception as e:
        st.error("Ocurrió un error al leer el archivo: {e}")
