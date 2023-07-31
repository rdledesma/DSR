#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 09:40:03 2023

@author: dario
"""

import pandas as pd

les = pd.read_csv('LE_full2.csv')
lb = pd.read_csv('LB_full2.csv')


les['Fecha'] = pd.to_datetime(les.Fecha)
lb['Fecha'] = pd.to_datetime(lb.Fecha)


#ploteo inicial

import matplotlib.pyplot as plt

plt.plot(les.Fecha, les.GHI, label="GHI")
plt.plot(les.Fecha, les.TOA, label="TOA")
plt.plot(les.Fecha, les.DSR, label="DSR")
plt.plot(les.Fecha, les.CAMS, label="CAMS")
plt.legend()

import numpy as np

def rmsd(coordenadas_1, coordenadas_2):
    rmsd =  np.sqrt((((coordenadas_1 - coordenadas_2)**2).sum())/len(coordenadas_1))
    rrmsd = rmsd / coordenadas_1.mean() 
    return rrmsd * 100

x = np.array([2,1.1])
y = np.array([2,1])

rmsd(x,y)



les.alphaS.describe()

rmse_gci_cams = []
angles = np.arange(0, 91, 10)

for angle in angles:
    subset = les[(les['alphaS'] >= angle) & (les['alphaS'] < angle + 10)]
    error = rmsd(np.array(subset['GHI']), np.array(subset['CAMS']))
    rmse_gci_cams.append(error)

rmse_gci_dsr = []

for angle in angles:
    subset = les[(les['alphaS'] >= angle) & (les['alphaS'] < angle + 10)]
    error = rmsd(np.array(subset['GHI']), np.array(subset['DSR']))
    rmse_gci_dsr.append(error)


plt.figure(figsize=(10, 6))

plt.bar(angles, rmse_gci_cams, width=5, align='edge', label='RMSE GCI vs. GCams', alpha=0.7)

plt.bar(angles, rmse_gci_dsr, width=5, align='center', label='RMSE GCI vs. GDsr', alpha=0.7)

plt.xlabel('Altura Solar (grados)')
plt.ylabel('RMSE')
plt.title('RMSE entre GHI y diferentes fuentes')
plt.legend()
plt.grid(True)
plt.xticks(angles[:-1])
plt.ylim(0, max(max(rmse_gci_cams), max(rmse_gci_dsr)) + 5)

plt.show()




cut = les[(les.alphaS>10) & (les.alphaS<20)]

rmsd(cut.GHI, cut.CAMS)



les = les[les.CTZ>0]

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
import numpy as np

# Supongamos que tienes un DataFrame llamado "data" con las columnas 'altura_solar', 'ghi_medida', 'ghi_cams' y 'ghi_dsr'.

# Ajustamos los bines para que haya 11 bines en total (0° a 9°, 10° a 19°, ..., 80° a 90°).
angles = np.arange(0, 91, 10)

# Calculamos el RMSE para cada bin de altura solar para "ghi medida" vs. "ghi cams":
rmse_gci_cams = []
for i in range(len(angles) - 1):
    subset = les[(les['alphaS'] >= angles[i]) & (les['alphaS'] < angles[i + 1])]
    rmse = rmsd(subset['GHI'], subset['CAMS'])
    rmse_gci_cams.append(rmse)

# Calculamos el RMSE para cada bin de altura solar para "ghi medida" vs. "ghi dsr":
rmse_gci_dsr = []
for i in range(len(angles) - 1):
    subset = les[(les['alphaS'] >= angles[i]) & (les['alphaS'] < angles[i + 1])]
    rmse = rmsd(subset['GHI'], subset['DSR'])
    rmse_gci_dsr.append(rmse)

# Creamos el gráfico de barras:
plt.figure(figsize=(10, 6))

plt.bar(angles[:-1], rmse_gci_cams, width=5, align='edge', label='RMSE GHI vs. CAMS', alpha=0.7)
plt.bar(angles[:-1], rmse_gci_dsr, width=5, align='center', label='RMSE GHI vs. DSR', alpha=0.7)

# Etiquetas para el eje x con los grados de inicio y fin de cada bin.
x_labels = [f"{angle+5}°" for angle in angles[:-1]]
plt.xticks(angles[:-1], x_labels)

plt.xlabel('Altura Solar (grados)')
plt.ylabel('RMSD')
#plt.title('RMSD entre GHI medida y modelos satelitales')
plt.legend()
plt.grid(True)
plt.ylim(0, max(max(rmse_gci_cams), max(rmse_gci_dsr)) + 5)

plt.show()
