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
workFolder = "C:/Users/baumamat/Google Drive/Warfare_ForestLoss/"
outputFolder = "D:/Classes_Workshops/2019_KOSMOS_Colombia/"
UID_file = workFolder + "uniqueID_country_Biome_LS_Anthrome_20190130.csv"
FL_data = workFolder + "Hansen_Summaries_ALL_20190129.csv"
refSHP = workFolder + "deforestation_rates_first_differences/prob_geq0_MapConversion/BIOMES_TropicsSavannas_10kmGrid.shp"
conflictData = workFolder + "PRIO-summaries_aggregated_20190329.csv"
COL = bt.baumiVT.CopyToMem(outputFolder + "Colombia_SHP.shp")
# ####################################### PROCESSING ########################################################## #
# (1) Load the UID-file into pandas df, merge with forest data
UIDs = pd.read_csv(UID_file, sep=",", header='infer', usecols=['UniqueID', 'GID_0', 'POINT_X', 'POINT_Y'])
FL = pd.read_csv(FL_data, sep=";", header='infer', usecols=['UniqueID', 'F2000_km_th25', 'FLall_km', 'F2017_km'])
conf = pd.read_csv(conflictData, sep=",", header='infer', usecols=["PolygonID", "nr_events", "nr_fatalities"])
# (2) Subset the ID-Data, so that we only have Colombia
UIDs_sub = UIDs.loc[UIDs['GID_0'] == "COL"]
# (3) Merge the files together
UIDs_FL = pd.merge(UIDs_sub, FL, left_on="UniqueID", right_on="UniqueID", how="inner")
UIDs_conf = pd.merge(UIDs_sub, conf, left_on="UniqueID", right_on="PolygonID", how="inner")
UIDs_FL = UIDs_FL.fillna(0) # Fill NA with 99 --> easier to label later in map
UIDs_conf = UIDs_conf.fillna(0)
# (4) Get the proj4 coordinate string from the shapefile
shp = ogr.Open(refSHP)
lyr = shp.GetLayer()
SR = lyr.GetSpatialRef()
# (5) Build geometry from "Point_X" and "Point_Y", convert into GeoDataFrame, then copy to shapefile
UIDs_FL['geometry'] = UIDs_FL.apply(lambda x: Point((float(x.POINT_X), float(x.POINT_Y))), axis=1)
UIDs_conf['geometry'] = UIDs_conf.apply(lambda x: Point((float(x.POINT_X), float(x.POINT_Y))), axis=1)
UIDs_FL_gpd = geopandas.GeoDataFrame(UIDs_FL, geometry='geometry')
UIDs_conf_gpd = geopandas.GeoDataFrame(UIDs_conf, geometry='geometry')
# (6) Add spatial references
UIDs_FL_gpd.crs = SR.ExportToProj4()
UIDs_conf_gpd.crs = SR.ExportToProj4()
# (7) Copy files to disc, then open them as shapefile
UIDs_FL_gpd.to_file(outputFolder + 'UIDs_FL_gpd.shp', driver = 'ESRI Shapefile')
UIDs_conf_gpd.to_file(outputFolder + 'UIDs_conf_gpd.shp', driver = 'ESRI Shapefile')
UIDs_FL = bt.baumiVT.CopyToMem(outputFolder + "UIDs_FL_gpd.shp")
UIDs_conf = bt.baumiVT.CopyToMem(outputFolder + "UIDs_conf_gpd.shp")
# (8) Build the properties for the raster files
UIDs_FL_lyr = UIDs_FL.GetLayer()
UIDs_conf_lyr = UIDs_conf.GetLayer()
x_min, x_max, y_min, y_max = UIDs_FL_lyr.GetExtent()
x_res = int(math.ceil((x_max - x_min) / float(10000.0)))
y_res = int(math.ceil((y_max - y_min) / float(10000.0)))
x_minGT = x_min - 5000 # Important: to put the first point a little bit towards the center in x-direction, so that we don't get the black line of 0-pixels in the middle
out_gt = ((x_minGT, 10000, 0, y_max, 0, -10000))
# (9) Build the empty raster
UIDs_FL_AsRaster = drvMemR.Create('', x_res, y_res, 1, gdal.GDT_Float32)
UIDs_FL_AsRaster.SetGeoTransform(out_gt)
UIDs_FL_AsRaster.SetProjection(SR.ExportToWkt())
UIDs_FL_AsRaster_rb = UIDs_FL_AsRaster.GetRasterBand(1)
UIDs_FL_AsRaster_rb.SetNoDataValue(9999)
UIDs_F17_AsRaster = drvMemR.Create('', x_res, y_res, 1, gdal.GDT_Float32)
UIDs_F17_AsRaster.SetGeoTransform(out_gt)
UIDs_F17_AsRaster.SetProjection(SR.ExportToWkt())
UIDs_F17_AsRaster_rb = UIDs_F17_AsRaster.GetRasterBand(1)
UIDs_F17_AsRaster_rb.SetNoDataValue(9999)
UIDs_events_AsRaster = drvMemR.Create('', x_res, y_res, 1, gdal.GDT_UInt16)
UIDs_events_AsRaster.SetGeoTransform(out_gt)
UIDs_events_AsRaster.SetProjection(SR.ExportToWkt())
UIDs_events_AsRaster_rb = UIDs_events_AsRaster.GetRasterBand(1)
UIDs_events_AsRaster_rb.SetNoDataValue(9999)
UIDs_fats_AsRaster = drvMemR.Create('', x_res, y_res, 1, gdal.GDT_UInt16)
UIDs_fats_AsRaster.SetGeoTransform(out_gt)
UIDs_fats_AsRaster.SetProjection(SR.ExportToWkt())
UIDs_fats_AsRaster_rb = UIDs_fats_AsRaster.GetRasterBand(1)
UIDs_fats_AsRaster_rb.SetNoDataValue(9999)
# (10) Rasterize
gdal.RasterizeLayer(UIDs_FL_AsRaster, [1], UIDs_FL_lyr, options=["ATTRIBUTE=FLall_km"])
gdal.RasterizeLayer(UIDs_F17_AsRaster, [1], UIDs_FL_lyr, options=["ATTRIBUTE=F2017_km"])
gdal.RasterizeLayer(UIDs_events_AsRaster, [1], UIDs_conf_lyr, options=["ATTRIBUTE=nr_events"])
gdal.RasterizeLayer(UIDs_fats_AsRaster, [1], UIDs_conf_lyr, options=["ATTRIBUTE=nr_fatalit"])
# (11) Rasterize COL-Shape for cutting
COL_AsRaster = drvMemR.Create('', x_res, y_res, 1, gdal.GDT_Byte)
COL_AsRaster.SetGeoTransform(out_gt)
COL_AsRaster.SetProjection(SR.ExportToWkt())
COL_AsRaster_rb = COL_AsRaster.GetRasterBand(1)
gdal.RasterizeLayer(COL_AsRaster, [1], COL.GetLayer(), options=["ATTRIBUTE=ID_0"])
COL_arr = COL_AsRaster.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
# (12) Mask the four maps by the raster
FL_arr = UIDs_FL_AsRaster.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
FL_arr = np.where((COL_arr != 53), 9999, FL_arr)
UIDs_FL_AsRaster.GetRasterBand(1).WriteArray(FL_arr, 0, 0)

F17_arr = UIDs_F17_AsRaster.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
F17_arr = np.where((COL_arr != 53), 9999, F17_arr)
UIDs_F17_AsRaster.GetRasterBand(1).WriteArray(F17_arr, 0, 0)

events_arr = UIDs_events_AsRaster.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
events_arr = np.where((COL_arr != 53), 9999, events_arr)
UIDs_events_AsRaster.GetRasterBand(1).WriteArray(events_arr, 0, 0)
#
fats_arr = UIDs_fats_AsRaster.GetRasterBand(1).ReadAsArray(0, 0, x_res, y_res)
fats_arr = np.where((COL_arr != 53), 9999, fats_arr)
UIDs_fats_AsRaster.GetRasterBand(1).WriteArray(fats_arr, 0, 0)

# (11) write to disc
bt.baumiRT.CopyMEMtoDisk(UIDs_FL_AsRaster, outputFolder + "COL_ForestLoss_2000-2017.tif")
bt.baumiRT.CopyMEMtoDisk(UIDs_F17_AsRaster, outputFolder + "COL_Forest2017.tif")
bt.baumiRT.CopyMEMtoDisk(UIDs_events_AsRaster, outputFolder + "COL_Events_2000-2017.tif")
bt.baumiRT.CopyMEMtoDisk(UIDs_fats_AsRaster, outputFolder + "COL_Fatalities_2000-2017.tif")
# (12) Delete temporary files
#[os.remove(outputFolder + f) for f in os.listdir(outputFolder) if f.find("_gpd") >= 0]


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")