# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import math
import gdal
from gdalconst import *
import numpy as np
import baumiTools as bt
from tqdm import tqdm
# ############################
# ########### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
outputFolder = "C:/Users/baumamat/Desktop/"
inClass = bt.baumiRT.OpenRasterToMemory("D:/Research/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/Run09_ClumpSieve_10px_masked_clip.tif")
outFile_Recult = outputFolder + "Percent-Recultivation_150m.tif"
outFile_aband = outputFolder + "Percent-Abandonment_9000_150m.tif"
outFile_stableCrop = outputFolder + "Percent-Crop_90_150m.tif"
windowSize = 5
# ####################################### FUNCTIONS ########################################################### #
def ReclassifyToMemory(inRaster, tupel):
    drvMemR = gdal.GetDriverByName('MEM')
# Create output-file
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    ds = inRaster.GetRasterBand(1)
    outDtype = ds.DataType
    out = drvMemR.Create('', cols, rows, outDtype)
    out.SetProjection(inRaster.GetProjection())
    out.SetGeoTransform(inRaster.GetGeoTransform())
    out_ras = out.GetRasterBand(1)
# Reclassify based on the tupel
    for row in tqdm(range(rows)):
        vals = ds.ReadAsArray(0, row, cols, 1)
        dataOut = vals
        for tup in tupel:
            in_val = tup[0]
            out_val = tup[1]
            np.putmask(dataOut, vals == in_val, out_val)
        out_ras.WriteArray(dataOut, 0, row)
    out_ras = None
    return out
def Aggregate(inRaster, windowSize, value):
    drvMemR = gdal.GetDriverByName('MEM')
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    gt = inRaster.GetGeoTransform()
# Build the output-File --> update cols/rows and GeoTransform!
# Calculate cols and rows, Cut off the edges, so that the image-boundaries line up with the window size
    cols = windowSize*(math.floor(cols/windowSize))
    rows = windowSize*(math.floor(rows/windowSize))
    outCols = int(cols/windowSize)
    outRows = int(rows/windowSize)
    cols = cols - 1
    rows = rows - 1
# Build new GeoTransform
    out_gt = [gt[0], float(gt[1])*windowSize, gt[2], gt[3], gt[4], float(gt[5])*windowSize]
# Now create the output-file
    out = drvMemR.Create('', outCols, outRows, 1, GDT_Float32)
    out.SetProjection(inRaster.GetProjection())
    out.SetGeoTransform(out_gt)
# Create the output-array
    dataOut = np.zeros((outRows, outCols))
# Initialize block size
    out_i = 0
    for i in tqdm(range(0, cols, windowSize)):
        if i + windowSize < cols:
            numCols = windowSize
        else:
            numCols = cols - i
        out_j = 0
        for j in range(0, rows, windowSize):
            if j + windowSize < rows:
                numRows = windowSize
            else:
                numRows = rows - j
# Load the input-file
            inArray = inRaster.GetRasterBand(1).ReadAsArray(i, j, numCols, numRows)
            max = windowSize * windowSize
# Create a binary mask, based on the rasterValue
            dOut = np.zeros((inArray.shape[0], inArray.shape[1]))
            np.putmask(dOut, inArray == value, 1)
            sum_dOut = np.sum(dOut)
            ratio = sum_dOut / max
# Write value to output-array
            dataOut[out_j, out_i] = ratio
# Make out_j, out_i continue to increase
            out_j = out_j + 1
        out_i = out_i + 1
# Write array to virtual output-file, return rasterfile
    out.GetRasterBand(1).WriteArray(dataOut, 0, 0)
    return out

# ####################################### PROCESSING ########################################################## #
# Do the aggregations
drvMemR = gdal.GetDriverByName('MEM')
cols = inClass.RasterXSize
rows = inClass.RasterYSize
gt = inClass.GetGeoTransform()
# Build the output-File --> update cols/rows and GeoTransform!
# Calculate cols and rows, Cut off the edges, so that the image-boundaries line up with the window size
cols = windowSize*(math.floor(cols/windowSize))
rows = windowSize*(math.floor(rows/windowSize))
outCols = int(cols/windowSize)
outRows = int(rows/windowSize)
cols = cols - 1
rows = rows - 1
# Build new GeoTransform
out_gt = [gt[0], float(gt[1])*windowSize, gt[2], gt[3], gt[4], float(gt[5])*windowSize]
# Now create the output-files
out_recult = drvMemR.Create('', outCols, outRows, 1, GDT_UInt16)
out_recult.SetProjection(inClass.GetProjection())
out_recult.SetGeoTransform(out_gt)
out_aband = drvMemR.Create('', outCols, outRows, 1, GDT_UInt16)
out_aband.SetProjection(inClass.GetProjection())
out_aband.SetGeoTransform(out_gt)
out_crop = drvMemR.Create('', outCols, outRows, 1, GDT_UInt16)
out_crop.SetProjection(inClass.GetProjection())
out_crop.SetGeoTransform(out_gt)
# Create the output-arrays
dataRecult = np.zeros((outRows, outCols))
dataAban = np.zeros((outRows, outCols))
dataCrop = np.zeros((outRows, outCols))
# Initialize block size
out_i = 0
for i in tqdm(range(0, cols, windowSize)):
	if i + windowSize < cols:
		numCols = windowSize
	else:
		numCols = cols - i
	out_j = 0
	for j in range(0, rows, windowSize):
		if j + windowSize < rows:
			numRows = windowSize
		else:
			numRows = rows - j
# Load the input-file
		inArray = inClass.GetRasterBand(1).ReadAsArray(i, j, numCols, numRows)
		max = windowSize * windowSize
# Create binary masks, based on the rasterValue
		crop90 = np.sum(np.where((inArray == 5) | (inArray == 6) | (inArray == 7) | (inArray == 11), 1, 0))
		aban9000 = np.sum(np.where((inArray == 6) | (inArray == 11), 1, 0))
		recult0015 = np.sum(np.where((inArray == 11), 1, 0))
# Do the summaries
		p_crop90 = (crop90 / max) * 10000 # *10000 to get UInt16
		if p_crop90 == 0:
			p_aban9000 = 65535
			p_recult0015 = 65535
		else:
			if crop90 > 0:
				p_aban9000 = (aban9000 / crop90) * 10000
			else:
				p_aban9000 = 0
			if aban9000 > 0:
				p_recult0015 = (recult0015 / aban9000) * 10000
			else:
				p_recult0015 = 0
		#print(p_crop90,p_aban9000,p_recult0015 )

# Write values to the output-arrays
		dataCrop[out_j, out_i] = int(p_crop90)
		dataAban[out_j, out_i] = int(p_aban9000)
		dataRecult[out_j, out_i] = int(p_recult0015)
# Make out_j, out_i continue to increase
		out_j = out_j + 1
	out_i = out_i + 1
# Write array to virtual output-file
	out_crop.GetRasterBand(1).WriteArray(dataCrop, 0, 0)
	out_aband.GetRasterBand(1).WriteArray(dataAban, 0, 0)
	out_recult.GetRasterBand(1).WriteArray(dataRecult, 0, 0)
# Set NodataValues
out_crop.GetRasterBand(1).SetNoDataValue(65535)
out_aband.GetRasterBand(1).SetNoDataValue(65535)
out_recult.GetRasterBand(1).SetNoDataValue(65535)
# Copy files to disc
bt.baumiRT.CopyMEMtoDisk(out_recult, outFile_Recult)
bt.baumiRT.CopyMEMtoDisk(out_aband, outFile_aband)
bt.baumiRT.CopyMEMtoDisk(out_crop, outFile_stableCrop)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")