# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import math
import gdal, osr, ogr
from gdalconst import *
import numpy as np
import pandas as pd
import baumiTools as bt
import os
import minisom
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvMemR = gdal.GetDriverByName('MEM')
drvMemV = ogr.GetDriverByName('Memory')
workFolder = "C:/Users/baumamat/Google Drive/Warfare_ForestLoss/"
outputFolder = workFolder + "deforestation_rates_first_differences/prob_geq0_SOM/"
inputFolder = workFolder + "deforestation_rates_first_differences/prob_geq0_MapConversion/"
inLayers_v01 = ["lOR_geq0_conflictStart.tif", "lOR_geq0_conflictEnd.tif"]
inLayers_v02 = ["prob_geq0_conflictstart.tif", "prob_geq0_conflictend.tif", "prob_geq0_conflictcont.tif"]
# ####################################### FUNCTIONS ########################################################### #
def LoadToArray(filePath):
	f_open = bt.baumiRT.OpenRasterToMemory(filePath)
	cols = f_open.RasterXSize
	rows = f_open.RasterYSize
	rb = f_open.GetRasterBand(1)
	noData = rb.GetNoDataValue()
	arr = rb.ReadAsArray(0, 0, cols, rows)
	arr[np.isnan(arr)] = 0
	arr = np.where((arr == 1.0), 0.9999999, arr)
	return arr
def WriteArrayToDisc(arr, filePath, refraster):
	ref_open = bt.baumiRT.OpenRasterToMemory(refraster)
	newRas = drvMemR.Create('', ref_open.RasterXSize, ref_open.RasterYSize, 1, GDT_Float32)
	newRas.SetProjection(ref_open.GetProjection())
	newRas.SetGeoTransform(ref_open.GetGeoTransform())
	rb = newRas.GetRasterBand(1)
	rb.SetNoDataValue(99)
	rb.WriteArray(arr, 0, 0)
	bt.baumiRT.CopyMEMtoDisk(newRas, filePath)
# ####################################### PROCESSING ########################################################## #





# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")