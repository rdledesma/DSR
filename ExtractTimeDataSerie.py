#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 15:04:22 2023

@author: dario
"""
from netCDF4 import Dataset
import numpy as np
import glob

#Almacenand lat y lon dentro de las variables

#tomando punto de estudio el AP-

lat_les=-22.80205 
lon_les=-65.47105 


path = r'ABI-L2-DSRF/**/*.nc'
files = glob.glob(path, recursive=True)

time = []
ghi = []

for item in files:
    try:
        data = Dataset(item, 'r')
        
        
        
        lat = data.variables['lat'][:]
        lon = data.variables['lon'][:]
    
    
    
    
    
        #cuadrado de las diferencias de lat y lon
        sq_diff_lat = (lat - lat_les)**2
        sq_diff_lon = (lon - lon_les)**2
        
        
        
        #Identificar el indice del minimo valor para lat y lon
        
        min_index_lat = sq_diff_lat.argmin()
        min_index_lon = sq_diff_lon.argmin()
    
    
    
        dsr = data.variables['DSR']
        
        from datetime import datetime, timedelta
        dt = datetime(2000, 1, 1, 12, 00, 00)
         # 👉️ 2023-09-24 09:30:35


        starting_date = data.variables['t'][:].data
        result = dt + timedelta(seconds= float(starting_date))
        print(result)
        
        

        ghi.append(dsr[min_index_lat, min_index_lon])
        time.append(result)
    except Exception:
        print("corrupted ")
    
    
#Creando dataframe y desenmascarando datos    
import pandas as pd
df = pd.DataFrame()


df['Fecha'] = time
df['GHI'] = ghi
df['GHI'] = np.ma.filled(df.GHI.astype(float), np.nan)

df['Fecha'] = df.Fecha.dt.strftime('%Y-%m-%d %H:00:00')

df['Fecha'] = pd.to_datetime(df.Fecha)

##Completando la serie de datos

# Fechas = pd.date_range(
#             start='2020/01/01 00:00', 
#             end='2020/01/31 23:59', 
#             freq="60 min")


# df = (df.set_index('Fecha')
#       .reindex(Fechas)
#       .rename_axis(['Fecha'])
#       #.fillna(0)
#       .reset_index())


df.to_csv('AP_DSR.csv', index=False)


import pandas as pd


df = pd.read_csv('LE_DSR.csv')
med = pd.read_csv('datos_LEyLB_2020_a_2022_PX60/Anual/LB/LB_PX60_2020.csv')

df['Fecha'] = pd.to_datetime(df.Fecha)
med['Fecha'] = pd.to_datetime(med.Fecha)


# df = df[ (df.Fecha.dt.month == 5) & (df.Fecha.dt.day == 2)]
# med = med[(med.Fecha.dt.month == 5) & (med.Fecha.dt.day == 2)]



df = df[(df.Fecha.dt.year == 2020) & (df.Fecha.dt.month == 5)]
med = med[(med.Fecha.dt.year == 2020) & (med.Fecha.dt.month == 5)]


Fechas = pd.date_range(
            start='2020/05/01 00:00', 
            end='2020/05/31 23:59', 
            freq="60 min")


df = (df.set_index('Fecha')
      .reindex(Fechas)
      .rename_axis(['Fecha'])
      #.fillna(0)
      .reset_index())



    
df['GHI'] = df.GHI.shift(-2)



#df['Fecha'] = df['Fecha'] + timedelta(minutes=-30)

import matplotlib.pyplot as plt

plt.plot(med.Fecha, med.GHI, label="Med")
plt.plot(df.Fecha, df.GHI, label="Sat")
plt.title('GHI LE y DSR ')
plt.legend()
plt.show()


dfMerge = pd.DataFrame()
dfMerge['GHI'] = med.GHI.values
dfMerge['Sat'] = df.GHI.values
dfMerge['Fecha'] = Fechas


plt.plot(dfMerge.Fecha, dfMerge.GHI, label="Med")
plt.plot(dfMerge.Fecha, dfMerge.Sat, label="Sat")
plt.title('GHI LE y DSR ')
plt.legend()
plt.show()



Fechas = pd.date_range(
            start='2020/05/01 00:00', 
            end='2020/05/31 23:59', 
            freq="1 min")



dfMerge = (dfMerge.set_index('Fecha')
      .reindex(Fechas)
      .rename_axis(['Fecha'])
      #.fillna(0)
      .reset_index())


dfMerge['Sat'] = dfMerge.Sat.interpolate()
dfMerge['Sat'] = dfMerge.Sat.shift(-25)




import Geo
from datetime import datetime, timedelta
dfGeo = Geo.Geo(
         range_dates=dfMerge['Fecha'],
         lat=-31.2827, 
         long=-57.9181, 
         gmt=-3, 
         beta=0,
         alt=56).df


dfMerge['CTZ'] = dfGeo.CTZ

dfMerge = dfMerge.dropna()
import numpy as np
dfMerge['GHI'] = np.where(dfMerge.CTZ<=0, 0, dfMerge.GHI)

dfMerge['Sat'] = np.where(dfMerge.CTZ<=0, 0, dfMerge.Sat)


import matplotlib.pyplot as plt

plt.plot(dfMerge.Fecha, dfMerge.Sat, label="Sat")
plt.plot(dfMerge.Fecha, dfMerge.GHI, label="Med")
#plt.plot(dfGeo.Fecha+timedelta(minutes=30), dfGeo.GHIargp, label="argp")
plt.legend()
plt.show()


df  = dfMerge.dropna()


plt.plot(df.Fecha, df.Sat, label="Sat")
plt.plot(df.Fecha, df.GHI, label="Med")
#plt.plot(dfGeo.Fecha+timedelta(minutes=30), dfGeo.GHIargp, label="argp")
plt.legend()
plt.show()



import Metrics
import skill_metrics as sm




df = df[df.CTZ>0.1217]

rrmse = Metrics.Metrics(df.GHI, df.Sat).relative_root_mean_squared_error()
ssMurphy =   sm.skill_score_murphy(df.Sat, df.GHI)



