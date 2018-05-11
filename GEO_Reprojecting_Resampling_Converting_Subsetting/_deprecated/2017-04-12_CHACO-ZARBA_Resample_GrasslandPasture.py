# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import math
import gdal
from gdalconst import *
import numpy as np
import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
outputFolder = "Z:/_PERSONAL_FOLDERS/baumann/Zarba_Natural-grasslands-Pastures/"
inClass = gdal.Open("Z:/_PERSONAL_FOLDERS/baumann/baumann_etal_2017_ChacoOnly_LCC_allClasses_85_00_13.img")
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
    for row in range(rows):
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
    out = drvMemR.Create('', outCols, outRows, 1, GDT_UInt16)
    out.SetProjection(inRaster.GetProjection())
    out.SetGeoTransform(out_gt)
# Create the output-array
    dataOut = np.zeros((outRows, outCols))
# Initialize block size
    out_i = 0
    for i in range(0, cols, windowSize):
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
            ratio = (sum_dOut / max) * 10000
# Write value to output-array
            dataOut[out_j, out_i] = ratio
# Make out_j, out_i continue to increase
            out_j = out_j + 1
        out_i = out_i + 1
# Write array to virtual output-file, return rasterfile
    out.GetRasterBand(1).WriteArray(dataOut, 0, 0)
    return out
# ####################################### PROCESSING ########################################################## #
# #### 1985 --> 1: Forest, 2: Cropland, 3: Pasture, 0: Other
print("Processing year: 1985")
print("Reclassify")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0,0],[1,0],[2,2],[3,0],[4,0],[5,1],[6,0],[7,0],[8,0],[9,0],
                                    [10,0],[11,0],[12,0],[13,0],[14,0],[15,2],[16,0],[17,0],[18,0],[19,0],[20,1],[21,1],[22,2],[23,2]])
print("Calculate percentages of land cover")
print("Pasture")
perPasture = Aggregate(reclassRaster, 8, 1)
bt.baumiRT.CopyMEMtoDisk(perPasture, (outputFolder + "1985_PercPasture_250m.tif"))
print("Natural grassland")
perNG = Aggregate(reclassRaster, 8, 2)
bt.baumiRT.CopyMEMtoDisk(perNG, (outputFolder + "1985_PercNG_250m.tif"))
print("")
# #### 2000 --> 1: Forest, 2: Cropland, 3: Pasture, 0: Other
print("Processing year: 2000")
print("Reclassify")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0,0],[1,0],[2,2],[3,0],[4,0],[5,1],[6,0],[7,0],[8,0],[9,0],
                                    [10,0],[11,1],[12,0],[13,0],[14,1],[15,2],[16,2],[17,0],[18,1],[19,0],[20,0],[21,1],[22,0],[23,2]])
print("Calculate percentages of land cover")
print("Pasture")
perPasture = Aggregate(reclassRaster, 8, 1)
bt.baumiRT.CopyMEMtoDisk(perPasture, (outputFolder + "2000_PercPasture_250m.tif"))
print("Natural grassland")
perNG = Aggregate(reclassRaster, 8, 2)
bt.baumiRT.CopyMEMtoDisk(perNG, (outputFolder + "2000_PercNG_250m.tif"))
print("")
# #### 2013 --> 1: Forest, 2: Cropland, 3: Pasture, 0: Other
print("Processing year: 2013")
print("Reclassify")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0,0],[1,0],[2,2],[3,0],[4,0],[5,1],[6,0],[7,0],[8,0],[9,0],
                                    [10,0],[11,1],[12,0],[13,1],[14,0],[15,2],[16,2],[17,0],[18,1],[19,1],[20,0],[21,0],[22,0],[23,0]])
print("Calculate percentages of land cover")
print("Pasture")
perPasture = Aggregate(reclassRaster, 8, 1)
bt.baumiRT.CopyMEMtoDisk(perPasture, (outputFolder + "2013_PercPasture_250m.tif"))
print("Natural grassland")
perNG = Aggregate(reclassRaster, 8, 2)
bt.baumiRT.CopyMEMtoDisk(perNG, (outputFolder + "2013_PercNG_250m.tif"))
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")