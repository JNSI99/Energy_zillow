import pandas as pd
import Funciones as f
import Limites as lm
import numpy as np

#2030 Prediction


df = pd.read_csv("merged.csv", low_memory=False)
# Ahora vamos a hacer pruebas
# hacemos un sub df

df_test_fuels = df[["Calendar Year","BBL",
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
    ["Calendar Year","BBL", "Largest Property Use Type - Gross Floor Area (ft²)", "Primary Property Type - Self Selected"]].copy()

#Aqui se calcula la multa
year = 2030
df_emisions["Coefficient"] = df_emisions["Primary Property Type - Self Selected"].apply(
    lambda x: lm.get_emission_factor(x, year))

df_emisions["Largest Property Use Type - Gross Floor Area (ft²)"] = pd.to_numeric(
    df_emisions["Largest Property Use Type - Gross Floor Area (ft²)"].replace("Not Available", np.nan), errors='coerce')
df_emisions = df_emisions.fillna(0)

df_emisions["Limite"] = (df_emisions["Largest Property Use Type - Gross Floor Area (ft²)"] *
                         df_emisions["Coefficient"])



df_emisions["Exceso"] = df_test_fuels["Emisiones"] - df_emisions["Limite"]
df_emisions["multa 2030"] = df_emisions["Exceso"] * 268

df_predictions = df_emisions[["BBL","multa 2030"]].copy()

#Calculamos 2035

year = 2035
df_emisions["Coefficient"] = df_emisions["Primary Property Type - Self Selected"].apply(
    lambda x: lm.get_emission_factor(x, year))

df_emisions["Largest Property Use Type - Gross Floor Area (ft²)"] = pd.to_numeric(
    df_emisions["Largest Property Use Type - Gross Floor Area (ft²)"].replace("Not Available", np.nan), errors='coerce')
df_emisions = df_emisions.fillna(0)

df_emisions["Limite"] = (df_emisions["Largest Property Use Type - Gross Floor Area (ft²)"] *
                         df_emisions["Coefficient"])



df_emisions["Exceso"] = df_test_fuels["Emisiones"] - df_emisions["Limite"]
df_emisions["multa 2035"] = df_emisions["Exceso"] * 268

df_predictions["multa 2035"] = df_emisions["multa 2035"]

#Calculamos 2040


year = 2040
df_emisions["Coefficient"] = df_emisions["Primary Property Type - Self Selected"].apply(
    lambda x: lm.get_emission_factor(x, year))

df_emisions["Largest Property Use Type - Gross Floor Area (ft²)"] = pd.to_numeric(
    df_emisions["Largest Property Use Type - Gross Floor Area (ft²)"].replace("Not Available", np.nan), errors='coerce')
df_emisions = df_emisions.fillna(0)

df_emisions["Limite"] = (df_emisions["Largest Property Use Type - Gross Floor Area (ft²)"] *
                         df_emisions["Coefficient"])



df_emisions["Exceso"] = df_test_fuels["Emisiones"] - df_emisions["Limite"]
df_emisions["multa 2040"] = df_emisions["Exceso"] * 268

df_predictions["multa 2040"] = df_emisions["multa 2040"]

df_predictions.to_csv("predictions.csv", index=False,encoding="utf-8")








