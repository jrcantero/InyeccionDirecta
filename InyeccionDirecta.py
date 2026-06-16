import numpy as np
import pandas as pd
from molmass import Formula

archivo = 'Vilches'
input = archivo + '.csv'
output = archivo + '_output.csv'
samples = pd.read_csv(input, sep=';')


monoisotopica_H = 1.007825

new_rows = []

for index, row in samples.iterrows():
    name = row['Muestra']
    formula = row['Formula']
    
    mol = Formula(formula)
    molecular_weight = mol.mass

    spectrum = mol.spectrum()

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



#guardar new_rows en un csv
new_df = pd.DataFrame(new_rows)
new_df.to_csv(output, index=False)


