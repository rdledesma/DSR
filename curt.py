#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 12:10:37 2023

@author: dario
"""
from netCDF4 import Dataset
from osgeo import gdal                          # Python bindings for GDAL
from osgeo import osr                           # Python bindings for GDAL
import os        


#-----------------------------------------------------------------------------------------------------------

import glob

# absolute path to search all text files inside a specific folder
path = r'ABI-L2-DSRF/**/*.nc'
files = glob.glob(path, recursive=True)
print(files)
#-----------------------------------------------------------------------------------------------------------
var = 'DSR'



output = "Output"; os.makedirs(output, exist_ok=True)

extent = [-70.0, -40.0, -50.0, -20.0]



#For all files in folder:
for file_name in files:
    img = gdal.Open('NETCDF:'+file_name+':'+var)
    if not img is None:
        #Extrae los metadatos de la imagen para hacer la correción
      metadata = img.GetMetadata()
      
      ##Realiza la corrección por posición del satélite
      scale = float(metadata.get(var + '#scale_factor'))
      offset = float(metadata.get(var + '#add_offset'))
      undef = float(metadata.get(var + '#_FillValue'))
      dtime = metadata.get('NC_GLOBAL#time_coverage_start')

      # Load the data
      ds = img.ReadAsArray(0, 0, img.RasterXSize, img.RasterYSize).astype(float)

      # Apply the scale, offset and convert to celsius
      ds = (ds * scale + offset)

      # Read the original file projection and configure the output projection
      source_prj = osr.SpatialReference()
      source_prj.ImportFromProj4(img.GetProjectionRef())

      target_prj = osr.SpatialReference()
      target_prj.ImportFromProj4("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")

      # Reproject the data
      GeoT = img.GetGeoTransform()
      driver = gdal.GetDriverByName('MEM')
      raw = driver.Create('raw', ds.shape[0], ds.shape[1], 1, gdal.GDT_Float32)
      raw.SetGeoTransform(GeoT)
      raw.GetRasterBand(1).WriteArray(ds)

      # Define the parameters of the output file  
      options = gdal.WarpOptions(format = 'netCDF', 
                srcSRS = source_prj, 
                dstSRS = target_prj,
                outputBounds = (extent[0], extent[3], extent[2], extent[1]), 
                outputBoundsSRS = target_prj, 
                outputType = gdal.GDT_Float32, 
                srcNodata = undef, 
                dstNodata = 'nan', 
                xRes = 0.02, 
                yRes = 0.02, 
                resampleAlg = gdal.GRA_NearestNeighbour)

      #print(options)

      # Write the reprojected file on disk
      new_name = file_name[12:16] + file_name[23:-3] + "_ret.nc"

      gdal.Warp(f'{new_name}', raw, options=options)
        
    else:
        print("no es")
# Open the file
#img = gdal.Open(f'NETCDF:{input}/{file_name}.nc:' + var)
file_name = files[12]
img = gdal.Open('NETCDF:'+file_name+':'+var)




# Read the header metadata
metadata = img.GetMetadata()



type(img)



scale = float(metadata.get(var + '#scale_factor'))
offset = float(metadata.get(var + '#add_offset'))
undef = float(metadata.get(var + '#_FillValue'))
dtime = metadata.get('NC_GLOBAL#time_coverage_start')

# Load the data
ds = img.ReadAsArray(0, 0, img.RasterXSize, img.RasterYSize).astype(float)

# Apply the scale, offset and convert to celsius
ds = (ds * scale + offset)

# Read the original file projection and configure the output projection
source_prj = osr.SpatialReference()
source_prj.ImportFromProj4(img.GetProjectionRef())

target_prj = osr.SpatialReference()
target_prj.ImportFromProj4("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")

# Reproject the data
GeoT = img.GetGeoTransform()
driver = gdal.GetDriverByName('MEM')
raw = driver.Create('raw', ds.shape[0], ds.shape[1], 1, gdal.GDT_Float32)
raw.SetGeoTransform(GeoT)
raw.GetRasterBand(1).WriteArray(ds)

# Define the parameters of the output file  
options = gdal.WarpOptions(format = 'netCDF', 
          srcSRS = source_prj, 
          dstSRS = target_prj,
          outputBounds = (extent[0], extent[3], extent[2], extent[1]), 
          outputBoundsSRS = target_prj, 
          outputType = gdal.GDT_Float32, 
          srcNodata = undef, 
          dstNodata = 'nan', 
          xRes = 0.02, 
          yRes = 0.02, 
          resampleAlg = gdal.GRA_NearestNeighbour)

print(options)

# Write the reprojected file on disk
new_name = file_name[12:16] + file_name[23:-3] + "_ret.nc"

gdal.Warp(f'{new_name}', raw, options=options)
#-----------------------------------------------------------------------------------------------------------
# Open the reprojected GOES-R image
file = Dataset(new_name)

# Get the pixel values
data = file.variables['Band1'][:]
#-----------------------------------------------------------------------------------------------------------
# Choose the plot size (width x height, in inches)
import matplotlib.pyplot as plt    
import cartopy, cartopy.crs as ccrs  
import numpy as np 
from datetime import datetime   
plt.figure(figsize=(10,10))

# Use the Geostationary projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# Define the image extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# Define the color scale based on the channel
#colormap = "gray_r" # White to black for IR channels
colormap = "inferno" # White to black for IR channels
     
# Plot the image
img = ax.imshow(data, origin='upper', extent=img_extent, cmap=colormap)

# Add coastlines, borders and gridlines
ax.coastlines(resolution='10m', color='white', linewidth=0.8)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='white', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='gray', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 180,2), ylocs=np.arange(-90, 90, 2), draw_labels=True)
gl.top_labels = False
gl.right_labels = False

# Add a colorbar
plt.colorbar(img, label='Factor de Reflectancia', extend='both', orientation='horizontal', pad=0.05, fraction=0.05)

# Extract date
date = (datetime.strptime(dtime, '%Y-%m-%dT%H:%M:%S.%fZ'))

# Add a title
plt.title('GOES-16 Band 02 ' + date.strftime('%Y-%m-%d %H:%M') + ' UTC', fontweight='bold', fontsize=10, loc='left')
plt.title('Reg.: ' + str(extent) , fontsize=10, loc='right')
#-----------------------------------------------------------------------------------------------------------
# Save the image
plt.savefig(f'{output}/Image_14.png', bbox_inches='tight', pad_inches=0, dpi=300)

# Show the image
plt.show()