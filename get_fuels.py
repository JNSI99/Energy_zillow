import pandas as pd
import Funciones as f
import Limites as lm
import certifi
from rapidfuzz import process, utils
import numpy as np

"""
We use merged.csv to do the calculations
We want to get a df with the fuels consumptions
the BBL, the fine etc...
"""


# Abrimos el df


df = pd.read_csv("merged.csv", low_memory=False)
# Ahora vamos a hacer pruebas
# hacemos un sub df

df_test_fuels = df[["BBL",
                    "Fuel Oil #2 Use (kBtu)",
                    "Fuel Oil #4 Use (kBtu)",
                    "Fuel Oil #5 & 6 Use (kBtu)",
                    "Diesel #2 Use (kBtu)",
                    "Natural Gas Use (kBtu)",
                    "Electricity Use - Grid Purchase (kWh)",
                    "District Steam Use (kBtu)",
                    "Kerosene Use (kBtu)",
                    "Propane Use (kBtu)"]].copy()

list = ["BBL",
        "Fuel Oil #2 Use (kBtu)",
        "Fuel Oil #4 Use (kBtu)",
        "Fuel Oil #5 & 6 Use (kBtu)",
        "Diesel #2 Use (kBtu)",
        "Natural Gas Use (kBtu)",
        "Electricity Use - Grid Purchase (kWh)",
        "District Steam Use (kBtu)",
        "Kerosene Use (kBtu)",
        "Propane Use (kBtu)"]

for k in list:
    df_test_fuels[k] = pd.to_numeric(df_test_fuels[k].replace("Not Available", np.nan), errors='coerce')

df_test_fuels = df_test_fuels.fillna(0)

df_test_fuels["Emisiones"] = (df_test_fuels["Fuel Oil #2 Use (kBtu)"] * 0.00007421 +
                              df_test_fuels["Fuel Oil #4 Use (kBtu)"] * 0.00007529 +
                              df_test_fuels["Fuel Oil #5 & 6 Use (kBtu)"] * 0.00007529 +
                              df_test_fuels["Diesel #2 Use (kBtu)"] * 0.00007421 +
                              df_test_fuels["Natural Gas Use (kBtu)"] * 0.00005311 +
                              (df_test_fuels["Electricity Use - Grid Purchase (kWh)"]) * 0.000288962 +
                              df_test_fuels["District Steam Use (kBtu)"] * 0.00004493 +
                              df_test_fuels["Kerosene Use (kBtu)"] * 0.00007769 +
                              df_test_fuels["Propane Use (kBtu)"] * 0.00006425)

# Calculo manual de emisiones de CO2 funciones de claude
# Feature x coeeficiente
# Calculo del maximo de emisiones

df_emisions = df[
    ["BBL", "Largest Property Use Type - Gross Floor Area (ft²)", "Primary Property Type - Self Selected"]].copy()
year = 2024
df_emisions["Coefficient"] = df_emisions["Primary Property Type - Self Selected"].apply(
    lambda x: lm.get_emission_factor(x, year))

df_emisions["Largest Property Use Type - Gross Floor Area (ft²)"] = pd.to_numeric(
    df_emisions["Largest Property Use Type - Gross Floor Area (ft²)"].replace("Not Available", np.nan), errors='coerce')
df_emisions = df_emisions.fillna(0)

df_emisions["Limite"] = (df_emisions["Largest Property Use Type - Gross Floor Area (ft²)"] *
                         df_emisions["Coefficient"])



df_emisions["Exceso"] = df_test_fuels["Emisiones"] - df_emisions["Limite"]
df_emisions["multa"] = df_emisions["Exceso"] * 268


# 1. Crea el DataFrame usando DOBLE corchete [[]] para mantenerlo como DataFrame
df_total_emisiones = df[["BBL", "Total (Location-Based) GHG Emissions (Metric Tons CO2e)"]].copy()

# 2. Renombra la columna original para mayor claridad
df_total_emisiones.rename(columns={"Total (Location-Based) GHG Emissions (Metric Tons CO2e)": "Emisiones DOB"},
                          inplace=True)

# 3. Asigna los cálculos (Asegúrate de que los índices coincidan)
df_total_emisiones["Emisiones Calculadas"] = df_test_fuels["Emisiones"]

# Convertir a numérico y forzar errores a NaN (esto convierte cualquier texto residual en 'Not a Number')
df_total_emisiones["Emisiones DOB"] = pd.to_numeric(df_total_emisiones["Emisiones DOB"], errors='coerce')
df_total_emisiones["Emisiones Calculadas"] = pd.to_numeric(df_total_emisiones["Emisiones Calculadas"], errors='coerce')

# Ahora sí, calcula la diferencia (los NaN se ignorarán o resultarán en NaN, evitando el error)
df_total_emisiones["Diferencia"] = df_total_emisiones["Emisiones Calculadas"] - df_total_emisiones["Emisiones DOB"]
df_total_emisiones["Relativo"] = df_total_emisiones["Diferencia"] / df_total_emisiones["Emisiones DOB"]
df_total_emisiones['Relativo'] = df_total_emisiones['Relativo'].replace([np.inf, -np.inf], 0)


df_final = pd.merge(df_emisions, df_total_emisiones, how='inner', on='BBL')
df_final.drop('Largest Property Use Type - Gross Floor Area (ft²)', axis=1, inplace=True)
df_final.drop('Primary Property Type - Self Selected', axis=1, inplace=True)
df_final.drop('Coefficient', axis=1, inplace=True)

#df_final.to_csv("Fuels.csv",index=False,encoding='utf-8')

"""

df_final columns
'BBL'
'Limite',
'Exceso', 'multa', 'Emisiones DOB', 'Emisiones Calculadas',
'Diferencia', 'Relativo'],

df_final_combs data for dashboard

"""
df_final["status"] = df["Exceso"]<0 #True significa que si cumple la normativa


df_final.to_csv("Fuels.csv",index=False,encoding='utf-8')

