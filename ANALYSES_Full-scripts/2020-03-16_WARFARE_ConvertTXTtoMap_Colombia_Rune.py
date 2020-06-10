# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import math
import gdal, osr, ogr
from gdalconst import *
import numpy as np
import pandas as pd
import geopandas
from shapely.geometry import Point
import baumiTools as bt
import os
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvMemR = gdal.GetDriverByName('MEM')
drvMemV = ogr.GetDriverByName('Memory')
workFolder = "D:/Google Drive/Warfare_ForestLoss/"
outputFolder = "D:/OneDrive - Conservation Biogeography Lab/_RESEARCH/Publications/Publications-in-preparation/2020_Christiasen_Causality-conflict-forest-lss/Maps/"
inDS = outputFolder + "data_xy_colombia_temporally_aggregated_20200424.txt"
COL = bt.baumiVT.CopyToMem(outputFolder + "SHP-Files/COL_country.shp")
refSHP = workFolder + "_NewVariables_20190822/BIOMES_TropicsSavannas_10kmGrid_polygons.shp"
# ####################################### PROCESSING ########################################################## #
# (1) Load the UID-file into pandas df, merge with forest data
ds = pd.read_csv(inDS, sep=" ", header='infer', usecols=['PolygonID', 'lon', 'lat', 'FL_km_cumulative', 'RoadDist'])
ds['RoadDist_log10'] = np.log10(ds['RoadDist'] / 1000)

#ds = ds.fillna(99)
# (2) Get the proj4 coordinate string from the shapefile
shp = ogr.Open(refSHP)
lyr = shp.GetLayer()
SR = lyr.GetSpatialRef()
# (3) Build geometry from "Point_X" and "Point_Y", convert into GeoDataFrame, then copy to shapefile
ds['geometry'] = ds.apply(lambda x: Point((float(x.lon), float(x.lat))), axis=1)
ds_gpd = geopandas.GeoDataFrame(ds, geometry='geometry')
# (4) Add spatial references
ds_gpd.crs = SR.ExportToProj4()
# (5) Copy files to disc, then open them as shapefile
ds_gpd.to_file(outputFolder + 'ds_gpd.shp', driver = 'ESRI Shapefile')
ds_new = bt.baumiVT.CopyToMem(outputFolder + "ds_gpd.shp")
# (6) Build the properties for the raster files
ds_lyr = ds_new.GetLayer()
x_min, x_max, y_min, y_max = ds_lyr.GetExtent()
x_res = int(math.ceil((x_max - x_min) / float(10000.0)))
y_res = int(math.ceil((y_max - y_min) / float(10000.0)))
x_minGT = x_min - 5000 # Important: to put the first point a little bit towards the center in x-direction, so that we don't get the black line of 0-pixels in the middle
y_minGT = y_min - 5000
out_gt = ((x_minGT, 10000, 0, y_max, 0, -10000))
# (9) Build the empty rasters
# # Cummulative Forest loss
# FLcum = drvMemR.Create('', x_res, y_res, 1, gdal.GDT_Float32)
# FLcum.SetGeoTransform(out_gt)
# FLcum.SetProjection(SR.ExportToWkt())
# FLcum_rb = FLcum.GetRasterBand(1)
# FLcum_rb.SetNoDataValue(9999)
# Population density
popDens = drvMemR.Create('', x_res, y_res, 1, gdal.GDT_Float32)
popDens.SetGeoTransform(out_gt)
popDens.SetProjection(SR.ExportToWkt())
popDens_rb = popDens.GetRasterBand(1)
popDens_rb.SetNoDataValue(9999)
# (10) Rasterize
# gdal.RasterizeLayer(FLcum, [1], ds_lyr, options=["ATTRIBUTE=FL_km_cumu"])
gdal.RasterizeLayer(popDens, [1], ds_lyr, options=["ATTRIBUTE=RoadDist_l"])
# (11) Rasterize COL-Shape for cutting
COL_AsRaster = drvMemR.Create('', x_res, y_res, 1, gdal.GDT_Byte)
COL_AsRaster.SetGeoTransform(out_gt)
COL_AsRaster.SetProjection(SR.ExportToWkt())
COL_AsRaster_rb = COL_AsRaster.GetRasterBand(1)
gdal.RasterizeLayer(COL_AsRaster, [1], COL.GetLayer(), options=["ATTRIBUTE=ID_0"])
COL_arr = COL_AsRaster.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
# (12) Mask the four maps by the raster
# FLcum_arr = FLcum.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
# FLcum_arr = np.where((COL_arr != 53), 9999, FLcum_arr)
# FLcum.GetRasterBand(1).WriteArray(FLcum_arr, 0, 0)

popDens_arr = popDens.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
popDens_arr = np.where((COL_arr != 53), 9999, popDens_arr)
popDens.GetRasterBand(1).WriteArray(popDens_arr, 0, 0)

# (11) write to disc
# bt.baumiRT.CopyMEMtoDisk(FLcum, outputFolder + "COL_Cummulated_ForestLoss_2001-2018.tif")
bt.baumiRT.CopyMEMtoDisk(popDens, outputFolder + "COL_RoadDist_log_km.tif")

# (12) Delete temporary files
[os.remove(outputFolder + f) for f in os.listdir(outputFolder) if f.find("_gpd") >= 0]


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")