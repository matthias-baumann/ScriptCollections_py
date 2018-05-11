# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import math
import gdal
from gdalconst import *
import numpy as np
from ZumbaTools._Raster_Tools import *
from tqdm import tqdm
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
workFolder = "D:/kuemmerle_etal_CarbonCorridors/_00_Gasparri_Map/"
inBiomass = gdal.Open((workFolder + "biomasa_rf1.tif"))
# ####################################### PROCESSING ########################################################## #
# Create the new file
pr = inBiomass.GetProjection()
gt = inBiomass.GetGeoTransform()
cols = inBiomass.RasterXSize
rows = inBiomass.RasterYSize
output = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
output.SetProjection(pr)
output.SetGeoTransform(gt)
# Do the raster-calculation
rb = inBiomass.GetRasterBand(1)
out_rb = output.GetRasterBand(1)
ar = rb.ReadAsArray(0, 0, cols, rows)
out = np.zeros(ar.shape, dtype='float32')
min = np.min(ar)
max = np.max(ar)
out = (ar - min)/(max-min)
out_inv = (1 - out) * 1000
out_rb.WriteArray(out_inv, 0, 0)
# Write output
CopyMEMtoDisk(output, workFolder + "biomassa_rf1_normalized_inverted_1000.tif")

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")