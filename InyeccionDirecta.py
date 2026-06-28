#import numpy as np
import pandas as pd
from molmass import Formula

archivo = 'moleculas'
input = archivo + '.csv'
output = archivo + '_output.csv'
samples = pd.read_csv(input, sep=';')

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


proton = 1.007276

new_rows = []

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
        print(f"Error procesando {name} ({formula}): {e}")



#guardar new_rows en un csv
new_df = pd.DataFrame(new_rows)
new_df.to_csv(output, index=False)


