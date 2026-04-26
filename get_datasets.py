#This script is used for get the datasets LL84 an PLUTO as CSV

#comprobado si funciona


import pandas as pd
import Funciones as f

from rapidfuzz import process, utils


url_ll84 = "https://data.cityofnewyork.us/api/views/5zyy-y8am/rows.csv?accessType=DOWNLOAD"
url_pluto = "https://data.cityofnewyork.us/api/views/64uk-42ks/rows.csv?accessType=DOWNLOAD"

f.d_csv(url_ll84,'LL84.csv')
f.d_csv(url_pluto,'Pluto.csv')


