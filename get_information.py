import pandas as pd

"""
Creates a CSV that gives you basic information
about the building.
"""


df = pd.read_csv("merged.csv", low_memory=False)

df_test_fuels = df[[
    "Calendar Year",
    "BBL",
    "Address 1",
    "address",
    "Property Name"
    ]].copy()

df_test_fuels.to_csv("basic_information.csv",index = False,encoding='utf-8')