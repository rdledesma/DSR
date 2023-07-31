#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 15:54:07 2023

@author: dario
"""

import pandas as pd

df = pd.read_csv('abra_adaptados_ledesma_5_GHI.csv')
sat = pd.read_csv('AP_DSR.csv')






import matplotlib.pyplot as plt
df['Fecha'] = pd.to_datetime(df.Fecha)
sat['Fecha'] = pd.to_datetime(sat.Fecha)



df = df[df.Fecha.dt.year >= 2020]


df = df.resample(
                    '60 min', 
                    on='Fecha', 
                    offset='0 min')['GHIAdapCDF','GHISat'].mean().reset_index()








Fechas = pd.date_range(
            start='2020/01/01 00:00', 
            end='2022/12/31 23:59', 
            freq="60 min")



df = (df.set_index('Fecha')
      .reindex(Fechas)
      .rename_axis(['Fecha'])
      #.fillna(0)
      .reset_index())



sat = sat.groupby(by=['Fecha']).mean().reset_index()
sat = (sat.set_index('Fecha')
      .reindex(Fechas)
      .rename_axis(['Fecha'])
      #.fillna(0)
      .reset_index())




sat['GHI'] = sat.GHI.shift(-3)








df['Sat'] = sat.GHI.values


df = df[['Fecha','GHIAdapCDF','Sat','GHISat']]

df = df[df['GHIAdapCDF']<600]

df = df.dropna()

#plt.plot(df.Fecha, df.GHIAdapCDF, label="Med")
#plt.plot(df.Fecha, df.Sat, label="Sat")
#plt.legend()

import skill_metrics as sm
import Metrics

rrmseGOES = Metrics.Metrics(df.GHIAdapCDF, df.Sat).relative_root_mean_squared_error()
rrmseCAMS = Metrics.Metrics(df.GHIAdapCDF, df.GHISat).relative_root_mean_squared_error()




plt.plot(df.Fecha, df.GHIAdapCDF,label=f"GHI vs GOES rRMSE : {rrmseGOES}", markersize=1.5)
plt.plot(df.Fecha, df.GHISat,label=f"GHI vs CAMS rRMSE : {rrmseCAMS}", markersize=1.5)
plt.plot(df.Fecha, df.Sat,label=f"DSR", markersize=1.5)

#plt.plot([x for x in range(1200)]) 

plt.legend()
plt.show()

