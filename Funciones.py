from turtle import pd


def d_csv(url,nombre):
    #Download a csv
    import pandas as pd
    import certifi
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context

    df = pd.read_csv(url,low_memory=False)
    df.to_csv(nombre,index = False,encoding='utf-8')

    return print('Descargado con exito revisar carpeta')

def clean_ll84(df):
    import pandas as pd
    cols = ["Property ID",
    "Property Name",
    "Borough",
    "Address 1",
    "NYC Building Identification Number (BIN)",
    "NYC Borough, Block and Lot (BBL)",
    "Property GFA - Self-Reported (ft²)",
    "Primary Property Type - Self Selected",
    "Primary Property Type - Portfolio Manager-Calculated",
    "Largest Property Use Type - Gross Floor Area (ft²)",
    "Site EUI (kBtu/ft²)",
    "Site Energy Use (kBtu)",
    "Electricity Use - Grid Purchase (kWh)",
    "Natural Gas Use (kBtu)",
    "Fuel Oil #1 Use (kBtu)",
    "Fuel Oil #2 Use (kBtu)",
    "Fuel Oil #4 Use (kBtu)",
    "Fuel Oil #5 & 6 Use (kBtu)",
    "Diesel #2 Use (kBtu)",
    "District Steam Use (kBtu)",
    "Propane Use (kBtu)",
    "Kerosene Use (kBtu)",
    "Total (Location-Based) GHG Emissions (Metric Tons CO2e)",
    "Direct GHG Emissions (Metric Tons CO2e)",
    "Indirect (Location-Based) GHG Emissions (Metric Tons CO2e)",
    "Site EUI (kBtu/ft²)",
    "ENERGY STAR Score",
    "Calendar Year"]

    df2 = df[cols].copy()
    df2.to_csv('clean_ll84.csv',index = False,encoding='utf-8')
    return 'done clean ll84'

def clean_pluto(df):
    import pandas as pd
    cols = ["BBL",
    "borough",
    "address",
    "lotarea",
    "bldgarea",
    "bldgclass",
    "landuse",
    "numbldgs",
    "yearbuilt",
    "unitsres",
    "ownername",
    "latitude",
    "longitude"
    ]

    df2 = df[cols].copy()
    df2.to_csv('clean_pluto.csv',index = False,encoding='utf-8')
    return 'done clean pluto'

def columnas(df):

    cols = df.columns.tolist()
    for k in cols:
        print(k)

def unir (ll84,plut):
   import pandas as pd

   ll84['NYC Borough, Block and Lot (BBL)'] = pd.to_numeric(ll84['NYC Borough, Block and Lot (BBL)'], errors='coerce')
   plut['BBL'] = plut['BBL'].astype('float64')

   new_df = pd.merge(ll84,plut
            ,left_on='NYC Borough, Block and Lot (BBL)',right_on='BBL')

   new_df = new_df.drop(columns = ['NYC Borough, Block and Lot (BBL)'])
   new_df['BBL'] = new_df['BBL'].astype('int64')
   new_df['address'] = new_df['address'].astype('string')

   return new_df

def buscar_direcciones_similares(direccion, df, columna, n=5):
    from rapidfuzz import process,fuzz
    """
    direccion: string con la direccion a buscar
    df: dataframe
    columna: nombre de la columna con direcciones
    n: numero de coincidencias que quieres

    devuelve las n direcciones más similares
    """

    direcciones = df[columna].dropna().astype(str).tolist()

    resultados = process.extract(direccion, direcciones, scorer=fuzz.token_sort_ratio, limit=n)

    return resultados

def info_final(resultados,dataset):
    #Devuelve la direccion mas acertada y su bbl correspondiente
    #Suponiendo mejor busqueda como resultado valido
    #Dataset es un df con direccion y bbl

    resultado_valido = resultados[0][0]
    info_direccion = dataset[dataset['address'] == resultado_valido]
    lista = info_direccion.iloc[0].to_list()
    return lista[0],lista[1]

def display_information(year, bbl):
    
    df_ranking = pd.read_csv('ranking.csv')
    df_basic_information = pd.read_csv('basic_information.csv')
    df_fuels = pd.read_csv('fuels.csv')

    info1 = df_ranking[df_ranking['Calendar Year'] == year][df_ranking['BBL'] == bbl]
    info3 = df_basic_information[df_basic_information['Calendar Year'] == year][df_basic_information['BBL'] == bbl]
    info4 = df_fuels[df_fuels['Calendar Year'] == year][df_fuels['BBL'] == bbl]
    display1 = pd.merge(info1, info3, on=['Calendar Year', 'BBL'], how='inner')
    display2 = pd.merge(display1, info4, on=['Calendar Year', 'BBL'], how='inner')
    return display2

def display_predictions(year, bbl):
    df_prediction = pd.read_csv('predictions.csv')
    return df_prediction[(df_prediction['Calendar Year'] == year) & (df_prediction['BBL'] == bbl)]




