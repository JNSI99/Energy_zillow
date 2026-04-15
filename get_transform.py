import pandas as pd
import Funciones as f
import certifi
import ssl
from rapidfuzz import process, utils

"""
This script takes the csv donwloaded previusly and it  cleans the data and 
storage the clean data on a new csv called merged with the next columns
Property ID
Property Name
Borough
Address 1
NYC Building Identification Number (BIN)
Property GFA - Self-Reported (ft²)
Primary Property Type - Self Selected
Largest Property Use Type - Gross Floor Area (ft²)
Site EUI (kBtu/ft²)
Site Energy Use (kBtu)
Electricity Use - Grid Purchase (kWh)
Natural Gas Use (kBtu)
Fuel Oil #1 Use (kBtu)
Fuel Oil #2 Use (kBtu)
Fuel Oil #4 Use (kBtu)
Fuel Oil #5 & 6 Use (kBtu)
District Steam Use (kBtu)
Total (Location-Based) GHG Emissions (Metric Tons CO2e)
Direct GHG Emissions (Metric Tons CO2e)
Indirect (Location-Based) GHG Emissions (Metric Tons CO2e)
Site EUI (kBtu/ft²).1
ENERGY STAR Score
Year Ending
BBL
borough
address
lotarea
bldgarea
bldgclass
landuse
numbldgs
yearbuilt
unitsres
ownername
latitude
longitude
"""


#Open CSV

df_ll84 = pd.read_csv('LL84.csv',low_memory=False)
df_pluto = pd.read_csv('Pluto.csv',low_memory=False)

#Clean CSV

f.clean_ll84(df_ll84)
f.clean_pluto(df_pluto)

#Merge


df_ll84 = pd.read_csv('clean_ll84.csv',low_memory=False)
df_pluto = pd.read_csv('clean_pluto.csv',low_memory=False)


merged = f.unir(df_ll84,df_pluto)

merged.to_csv('merged.csv',index = False,encoding='utf-8')