#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 15:54:07 2023

@author: dario
"""

import pandas as pd
import numpy as np
df = pd.read_csv('LB.csv')
dsr = pd.read_csv('LB_DSR_2.csv')
cams = pd.read_csv('CAMS-LB.csv', header=0, sep=";")
import matplotlib.pyplot as plt

df['Fecha'] = pd.to_datetime(df.Fecha)
dsr['Fecha'] = pd.to_datetime(dsr.Fecha)




Fechas = pd.date_range(
            start='2020/01/01 00:00', 
            end='2022/12/31 23:59', 
            freq="60 min")


cams['Fecha'] = Fechas









dsr = dsr.groupby(by=['Fecha']).mean().reset_index()


Fechas = pd.date_range(
            start='2020/01/01 00:00', 
            end='2022/12/31 23:59', 
            freq="1 min")


dsr = (dsr.set_index('Fecha')
      .reindex(Fechas)
      .rename_axis(['Fecha'])
      #.fillna(0)
      .reset_index())



df = (df.set_index('Fecha')
      .reindex(Fechas)
      .rename_axis(['Fecha'])
      #.fillna(0)
      .reset_index())





dsr['GHI'] = dsr.GHI.interpolate()


df['Sat'] = dsr.GHI.shift(-150)



show = df.dropna()



cams = (cams.set_index('Fecha')
      .reindex(show.Fecha)
      .rename_axis(['Fecha'])
      #.fillna(0)
      .reset_index())




show['CAMS'] = cams.GHI.shift(-2).values


show['Sat'] = np.where(show.GHI == 0, 0, show.Sat)


show.to_csv('LB_full.csv', index=False)




import matplotlib.pyplot as plt

plt.plot(show.Fecha, show.GHI, label="GHI")
plt.plot(show.Fecha, show.Sat, label="DSR")
plt.plot(show.Fecha, show.CAMS, label="CAMS")
plt.title("GHI LE")
plt.legend()



plt.plot(show.GHI, show.CAMS,  'o',label="CAMS", markersize=2)
plt.plot(show.GHI, show.Sat,'*', label="DSR", markersize=2)
plt.plot([x for x in range(1200)])
plt.legend()
plt.annotate("rRMSE-CAMS: 15.37% ", [800,0])
plt.annotate("rRMSE-DSR: 18.00% ", [800,100])
plt.title("GHI LB - CAMS vs DSR")
plt.xlabel("GHI LB")
plt.ylabel("GHI Satelital")
show.dropna(inplace = True)

import Metrics
import skill_metrics as sm
rrmse = Metrics.Metrics(show.GHI, show.Sat).relative_root_mean_squared_error()
rrmse_CAMS = Metrics.Metrics(show.GHI, show.CAMS).relative_root_mean_squared_error()

ssMurphy =   sm.skill_score_murphy(show.Sat, show.GHI)
ssMurphyCAMS =   sm.skill_score_murphy(show.CAMS, show.GHI)

import Geo
dfGeo = Geo.Geo(
         range_dates=Fechas,
         lat=-34.6720, 
         long=-56.3401, 
         gmt=-2, 
         beta=0,
         alt=38).df


dfGeo = (dfGeo.set_index('Fecha')
      .reindex(show.Fecha)
      .rename_axis(['Fecha'])
      #.fillna(0)
      .reset_index())



dfGeo['DSR'] = show.Sat.values
dfGeo['GHI'] = show.CAMS.values
dfGeo['CAMS'] = show.GHI.values

plt.plot(dfGeo.Fecha, dfGeo.GHI, label="GHI")
plt.plot(dfGeo.Fecha, dfGeo.CAMS, label="CAMS")
plt.plot(dfGeo.Fecha, dfGeo.DSR, label="DSR")
plt.legend()




dfGeo.to_csv('LB_full2.csv', index=False)

# show['alphaS'] = dfGeo.alphaS.values

# show_bajo = show[(show.alphaS >10) & (show.alphaS < 20) ]


# rrmse_bajo = Metrics.Metrics(show_bajo.GHI, show_bajo.Sat).relative_root_mean_squared_error()
# rrmse_CAMS_bajo = Metrics.Metrics(show_bajo.GHI, show_bajo.CAMS).relative_root_mean_squared_error()


# plt.plot(show_bajo.GHI, show_bajo.CAMS,  'o',label=f"CAMS rRMSE: 34.12%", markersize=2)
# plt.plot(show_bajo.GHI, show_bajo.Sat,'*', label=f"DSR rRMSE: 26.76%", markersize=2)
# plt.plot([x for x in range(1000)])
# plt.title("GHI LB - CAMS vs DSR considerando 10°<$\\alpha$<20°")
# plt.xlabel("GHI LB")
# plt.ylabel("GHI Satelital")
# plt.legend()