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
outputFolder = workFolder + "deforestation_rates_first_differences/prob_geq0_MapConversion/"
UID_file = outputFolder + "UID_Coords.txt"
FL_data = workFolder + "Hansen_Summaries_ALL_20190129.csv"
refSHP = outputFolder + "BIOMES_TropicsSavannas_10kmGrid.shp"
vars = ["prob_geq0_noconflict.txt", "prob_geq0_conflictstart.txt", "prob_geq0_conflictcont.txt", "prob_geq0_conflictend.txt"]
FL_th = 5
conflict = workFolder + "deforestation_rates_first_differences/n_obs_Conflict.txt"
# ####################################### PROCESSING ########################################################## #
# (1) Load the UID-file into pandas df, merge with forest data
UIDs = pd.read_csv(UID_file, sep=";", header='infer', usecols=["UniqueID", "POINT_X", "POINT_Y"])
FL = pd.read_csv(FL_data, sep=";", decimal=",", header='infer', usecols=["UniqueID", "F2000_km_th25"])
UIDs_FL = pd.merge(UIDs, FL, left_on="UniqueID", right_on="UniqueID", how="inner")
# # Get the proj4 coordinate string from the shapefile
shp = ogr.Open(refSHP)
lyr = shp.GetLayer()
SR = lyr.GetSpatialRef()
# # Build a map of forest cover
# UIDs_FL_clean = UIDs_FL.fillna(0)
# # Build geometry from "Point_X" and "Point_Y", convert into GeoDataFrame, then copy to shapefile
# UIDs_FL_clean['geometry'] = UIDs_FL_clean.apply(lambda x: Point((float(x.POINT_X), float(x.POINT_Y))), axis=1)
# newData = geopandas.GeoDataFrame(UIDs_FL_clean, geometry='geometry')
# newData.crs = SR.ExportToProj4()
# newData.to_file(outputFolder + 'test.shp', driver = 'ESRI Shapefile')
# Convert the shapefile to raster
# shp = bt.baumiVT.CopyToMem(outputFolder + "test.shp")
# lyr = shp.GetLayer()
# x_min, x_max, y_min, y_max = lyr.GetExtent()
# x_res = int(math.ceil((x_max - x_min) / float(10000.0)))
# y_res = int(math.ceil((y_max - y_min) / float(10000.0)))
# x_minGT = x_min - 5000 # Important: to put the first point a little bit towards the center in x-direction, so that we don't get the black line of 0-pixels in the middle
# out_gt = ((x_minGT, 10000, 0, y_max, 0, -10000))
# pointAsRaster = drvMemR.Create('', x_res, y_res, 1, gdal.GDT_Float32)
# pointAsRaster.SetGeoTransform(out_gt)
# pointAsRaster.SetProjection(SR.ExportToWkt())
# pointAsRaster_rb = pointAsRaster.GetRasterBand(1)
# pointAsRaster_rb.SetNoDataValue(0)
# gdal.RasterizeLayer(pointAsRaster, [1], lyr, options=["ATTRIBUTE=F2000_km_t"])
# # Copy raster to disc
# bt.baumiRT.CopyMEMtoDisk(pointAsRaster, outputFolder + "Forest_2000" + ".tif")
# # delete temporary files
# [os.remove(outputFolder + f) for f in os.listdir(outputFolder) if f.find("test") >= 0]

#
# # (2) Loop through the variables, do the conversion
# for var in vars:
# 	print(var)
# # Load data, merge to UIDs
# 	var_pd = pd.read_csv(workFolder + "deforestation_rates_first_differences/" + var, sep=" ", header='infer', na_values="NA", usecols=["PolygonID", "prob"])
# 	merge = pd.merge(UIDs_FL, var_pd, left_on="UniqueID", right_on="PolygonID", how="inner")
# # Fill NA with 99 --> easier to label later in map
# 	merge2 = merge.fillna(0)
# # Set probabilites in areas with low forest cover to zero
# 	merge2['prob'] = merge2['prob'].where(merge2['F2000_km_th25'] > FL_th, 0)
# 	#searchIndex = (merge[merge['UniqueID'] == 60888].index.values.astype(int)[0])
# 	#print(merge[searchIndex:searchIndex + 10])
# 	#exit(0)
# # Build geometry from "Point_X" and "Point_Y", convert into GeoDataFrame, then copy to shapefile
# 	merge2['geometry'] = merge2.apply(lambda x: Point((float(x.POINT_X), float(x.POINT_Y))), axis=1)
# 	merge4 = geopandas.GeoDataFrame(merge2, geometry='geometry')
# 	merge4.crs = SR.ExportToProj4()
# 	merge4.to_file(outputFolder + 'test.shp', driver = 'ESRI Shapefile')
# 	#exit(0)
# # Convert the shapefile to raster
# 	shp = bt.baumiVT.CopyToMem(outputFolder + "test.shp")
# 	lyr = shp.GetLayer()
# 	x_min, x_max, y_min, y_max = lyr.GetExtent()
# 	x_res = int(math.ceil((x_max - x_min) / float(10000.0)))
# 	y_res = int(math.ceil((y_max - y_min) / float(10000.0)))
# 	x_minGT = x_min - 5000 # Important: to put the first point a little bit towards the center in x-direction, so that we don't get the black line of 0-pixels in the middle
# 	out_gt = ((x_minGT, 10000, 0, y_max, 0, -10000))
# 	pointAsRaster = drvMemR.Create('', x_res, y_res, 1, gdal.GDT_Float32)
# 	pointAsRaster.SetGeoTransform(out_gt)
# 	pointAsRaster.SetProjection(SR.ExportToWkt())
# 	pointAsRaster_rb = pointAsRaster.GetRasterBand(1)
# 	pointAsRaster_rb.SetNoDataValue(0)
# 	gdal.RasterizeLayer(pointAsRaster, [1], lyr, options=["ATTRIBUTE=prob"])
# # Copy raster to disc
# 	bt.baumiRT.CopyMEMtoDisk(pointAsRaster, outputFolder + var[:-4] + ".tif")
# # delete temporary files
# 	fl = os.listdir(outputFolder)
# 	[os.remove(outputFolder + f) for f in os.listdir(outputFolder) if f.find("test") >= 0]

# # # (3) Calculate the odds ratio
# def LoadToArray(filePath):
# 	f_open = bt.baumiRT.OpenRasterToMemory(filePath)
# 	cols = f_open.RasterXSize
# 	rows = f_open.RasterYSize
# 	rb = f_open.GetRasterBand(1)
# 	noData = rb.GetNoDataValue()
# 	arr = rb.ReadAsArray(0, 0, cols, rows)
# 	arr[np.isnan(arr)] = 0
# 	arr = np.where((arr == 1.0), 0.9999999, arr)
# 	return arr
# def WriteArrayToDisc(arr, filePath, refraster):
# 	ref_open = bt.baumiRT.OpenRasterToMemory(refraster)
# 	newRas = drvMemR.Create('', ref_open.RasterXSize, ref_open.RasterYSize, 1, GDT_Float32)
# 	newRas.SetProjection(ref_open.GetProjection())
# 	newRas.SetGeoTransform(ref_open.GetGeoTransform())
# 	rb = newRas.GetRasterBand(1)
# 	rb.SetNoDataValue(99)
# 	rb.WriteArray(arr, 0, 0)
# 	bt.baumiRT.CopyMEMtoDisk(newRas, filePath)
# # Load the maps to arrays --> via fix fileString
# noConflict = LoadToArray(outputFolder + vars[0][:-4] + ".tif")
# conflictStart = LoadToArray(outputFolder + vars[1][:-4] + ".tif")
# conflictEnd = LoadToArray(outputFolder + vars[3][:-4] + ".tif")
# # Calculate the lOR
# OR_start = np.where((noConflict > 0) & (conflictStart > 0),(conflictStart/(1-conflictStart)) / (noConflict/(1-noConflict)), 0)
# lOR_start = np.log10(OR_start)
# lOR_start = np.where((np.isinf(lOR_start)), 99, lOR_start)
# OR_end = np.where((noConflict > 0) & (conflictStart > 0), (conflictEnd/(1-conflictEnd)) / (noConflict/(1-noConflict)), 0)
# lOR_end = np.log10(OR_end)
# lOR_end = np.where((np.isinf(lOR_end)), 99, lOR_end)
# WriteArrayToDisc(lOR_start, outputFolder + "lOR_geq0_conflictStart.tif", outputFolder + vars[0][:-4] + ".tif")
# WriteArrayToDisc(lOR_end, outputFolder + "lOR_geq0_conflictEnd.tif", outputFolder + vars[0][:-4] + ".tif")
# exit(0)








# # (4) Produce a map for the conflict data
conlf_pd = pd.read_csv(workFolder + "deforestation_rates_first_differences/" + "n_obs_Conflict.txt", sep=" ", header='infer', na_values="NA", usecols=["PolygonID", "n_obs_noConflict"])
merge = pd.merge(UIDs_FL, conlf_pd, left_on="UniqueID", right_on="PolygonID", how="inner")
# merge['geometry'] = merge.apply(lambda x: Point((float(x.POINT_X), float(x.POINT_Y))), axis=1)
# merge = geopandas.GeoDataFrame(merge, geometry='geometry')
# merge.crs = SR.ExportToProj4()
# merge.to_file(outputFolder + 'test.shp', driver = 'ESRI Shapefile')
# # Convert the shapefile to raster
# shp = bt.baumiVT.CopyToMem(outputFolder + "test.shp")
# lyr = shp.GetLayer()
# x_min, x_max, y_min, y_max = lyr.GetExtent()
# x_res = int(math.ceil((x_max - x_min) / float(10000.0)))
# y_res = int(math.ceil((y_max - y_min) / float(10000.0)))
# x_minGT = x_min - 5000 # Important: to put the first point a little bit towards the center in x-direction, so that we don't get the black line of 0-pixels in the middle
# out_gt = ((x_minGT, 10000, 0, y_max, 0, -10000))
# pointAsRaster = drvMemR.Create('', x_res, y_res, 1, gdal.GDT_UInt16)
# pointAsRaster.SetGeoTransform(out_gt)
# pointAsRaster.SetProjection(SR.ExportToWkt())
# pointAsRaster_rb = pointAsRaster.GetRasterBand(1)
# pointAsRaster_rb.SetNoDataValue(0)
# gdal.RasterizeLayer(pointAsRaster, [1], lyr, options=["ATTRIBUTE=n_obs_noCo"])
# # Copy raster to disc
# bt.baumiRT.CopyMEMtoDisk(pointAsRaster, outputFolder + "n_obs_Conflict" + ".tif")
# # delete temporary files
# fl = os.listdir(outputFolder)
# [os.remove(outputFolder + f) for f in os.listdir(outputFolder) if f.find("test") >= 0]

# # (5) Conflict statistics
confStats_pd = pd.read_csv(workFolder + "deforestation_rates_first_differences/Conflict_summary_5x5.txt", sep=",", usecols=["PolygonID", "sum_events", "sum_fat", "mean_fat"])
polID_data = UIDs_FL[['UniqueID', 'POINT_X', 'POINT_Y']]
merge = pd.merge(polID_data, confStats_pd, left_on="UniqueID", right_on="PolygonID", how="inner")
merge['geometry'] = merge.apply(lambda x: Point((float(x.POINT_X), float(x.POINT_Y))), axis=1)
merge = geopandas.GeoDataFrame(merge, geometry='geometry')
merge.crs = SR.ExportToProj4()
merge.to_file(outputFolder + 'test.shp', driver = 'ESRI Shapefile')
#Convert the shapefile to raster, one for each attribute
attribs = [["sum_events", "UInt16"], ["sum_fat", "UInt16"], ["mean_fat", "Float"]]
shp = bt.baumiVT.CopyToMem(outputFolder + "test.shp")
lyr = shp.GetLayer()
x_min, x_max, y_min, y_max = lyr.GetExtent()
x_res = int(math.ceil((x_max - x_min) / float(10000.0)))
y_res = int(math.ceil((y_max - y_min) / float(10000.0)))
x_minGT = x_min - 5000 # Important: to put the first point a little bit towards the center in x-direction, so that we don't get the black line of 0-pixels in the middle
out_gt = ((x_minGT, 10000, 0, y_max, 0, -10000))
for att in attribs:
	if att[1] == "UInt16":
		pointAsRaster = drvMemR.Create('', x_res, y_res, 1, gdal.GDT_UInt16)
	if att[1] == "Float":
		pointAsRaster = drvMemR.Create('', x_res, y_res, 1, gdal.GDT_Float32)
	pointAsRaster.SetGeoTransform(out_gt)
	pointAsRaster.SetProjection(SR.ExportToWkt())
	pointAsRaster_rb = pointAsRaster.GetRasterBand(1)
	pointAsRaster_rb.SetNoDataValue(0)
	attState = "ATTRIBUTE=" + att[0]
	print(attState)
	gdal.RasterizeLayer(pointAsRaster, [1], lyr, options=[attState])
	bt.baumiRT.CopyMEMtoDisk(pointAsRaster, outputFolder + "Global_ConflictSummaries_" + att[0] + ".tif")
#delete temporary files
#fl = os.listdir(outputFolder)
#[os.remove(outputFolder + f) for f in os.listdir(outputFolder) if f.find("test") >= 0]
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")