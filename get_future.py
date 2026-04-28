import pandas as pd
import Funciones as f

bbl = 4096930051

df_w = pd.read_csv("weights_fuels.csv")
df = pd.read_csv("fuels_analisis.csv")



#Creamos pesos
df = df[df["Calendar Year"]==2024]


df["Total"] = df["Fuel Oil"] + df["Electricity"] + df["Natural Gas"] 

df["Fuel Oil"] = df["Fuel Oil"] / df["Total"]
df["Electricity"] = df["Electricity"] / df["Total"]
df["Natural Gas"] = df["Natural Gas"] / df["Total"]
df = df.drop(columns=["Total"])


df_building = df[["BBL","Fuel Oil", "Electricity", "Natural Gas"]].copy()
df_building = df_building.drop_duplicates(subset=["BBL"], keep="first")
df_building = df_building.dropna(subset=["Fuel Oil"])

r,c = df_building.shape

#Operacion para oil
columnas = ["BBL",
             "low_2030", "med_2030", "high_2030",
             "low_2035", "med_2035", "high_2035",
               "low_2040", "med_2040", "high_2040"]

df_final = pd.DataFrame(columns=columnas)



"""

for k in range(r):

    fila1 = df_building.iloc[k,1:4].to_numpy()

    fila21 = df_w.iloc[0,[1,4,7]].to_numpy()
    fila22 = df_w.iloc[0,[2,5,8]].to_numpy()
    fila23 = df_w.iloc[0,[3,6,9]].to_numpy()

    var_low_2030 = (fila1 * fila21).sum()
    var_med_2030 = (fila1 * fila22).sum()
    var_high_2030 = (fila1 * fila23).sum()

    fila31 = df_w.iloc[1,[1,4,7]].to_numpy()
    fila32 = df_w.iloc[1,[2,5,8]].to_numpy()
    fila33 = df_w.iloc[1,[3,6,9]].to_numpy()

    var_low_2035 = (fila1 * fila31).sum()
    var_med_2035 = (fila1 * fila32).sum()   
    var_high_2035 = (fila1 * fila33).sum()

    fila41 = df_w.iloc[2,[1,4,7]].to_numpy()
    fila42 = df_w.iloc[2,[2,5,8]].to_numpy()    
    fila43 = df_w.iloc[2,[3,6,9]].to_numpy()

    var_low_2040 = (fila1 * fila41).sum()
    var_med_2040 = (fila1 * fila42).sum()
    var_high_2040 = (fila1 * fila43).sum()

    df_final.loc[len(df_final)] = [df_building.iloc[k,0], 
                               var_low_2030, var_med_2030, var_high_2030,
                               var_low_2035, var_med_2035, var_high_2035,
                               var_low_2040, var_med_2040, var_high_2040]



df_final.to_csv("pred_to_display.csv",index=False,encoding='utf-8')
"""




k = f.display_future(bbl)
print(k)
