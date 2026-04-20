import pandas as pd
import Funciones as f
import Limites as lm
import certifi
from rapidfuzz import process, utils
import numpy as np

#Ranking

# 1. Carga y limpieza inicial
df = pd.read_csv("merged.csv", low_memory=False)
df_fuels = pd.read_csv("fuels.csv", low_memory=False)

# 2. Preparar df_ranking (Asegúrate de quedarte con un solo registro por BBL, ej: el año más reciente)
df_ranking = df[["BBL", "ENERGY STAR Score", "Calendar Year"]].copy()
df_ranking["ENERGY STAR Score"] = pd.to_numeric(df_ranking["ENERGY STAR Score"].replace("Not Available", np.nan), errors='coerce')


# 3. Preparar df_fuels (Sumar las emisiones si un BBL tiene varias fuentes de combustible)
df_fuels1 = df_fuels[["Calendar Year","BBL", "Emisiones DOB"]].copy()

# 4. Ahora el merge será 1 a 1. El resultado será máximo de 72k filas.
df_ranking_final = pd.merge(df_ranking, df_fuels1, on=["BBL","Calendar Year"], how="inner")


# 5. Ranking computing
df_ranking_final["ranking1"] = df_ranking_final["ENERGY STAR Score"].rank(ascending=False, method='min')
df_ranking_final["ranking2"] = df_ranking_final["Emisiones DOB"].rank(ascending=True, method='min')


df_ranking_final["puntuaje"] = df_ranking_final["ranking1"] + df_ranking_final["ranking2"]
df_ranking_final["ranking"] = df_ranking_final["puntuaje"].rank(ascending=True, method='dense').astype('Int64')

#Cleaning dataframe before export
df_ranking_final.drop(columns=["ranking1", "ranking2", "puntuaje"], inplace=True)

df_ranking_final.drop_duplicates(subset=["BBL", "Calendar Year"], inplace=True)

#Dataset export
df_ranking_final.to_csv("ranking.csv", index=False, encoding='utf-8')

