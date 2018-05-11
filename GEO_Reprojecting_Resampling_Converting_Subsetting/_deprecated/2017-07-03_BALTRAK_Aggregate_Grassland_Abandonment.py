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
outputFolder = "F:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/05_Wilderness_LivestockDisaggreg_InputData/_WildernessRuns/20170703_Run12/"
inClass = gdal.Open("F:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/Run09_ClumpSieve_10px_masked_clip.tif")
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
    out = drvMemR.Create('', outCols, outRows, 1, GDT_Float32)
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
print("Processing year: 1990") # --> class 1: grassland
print("Reclassify")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0,0],[1,0],[2,0],[3,0],[4,0],
                                    [5,0],[6,0],[7,0],[8,1],[9,1],[10,1],
                                    [11,0],[12,0],[13,0],[14,1],[15,0]])
print("Calculate percentages of land cover")
print("Grassland")
outFile = outputFolder + "1990_PercGrassland_300m.tif"
if not os.path.exists(outFile):
    perGrassland = Aggregate(reclassRaster, 10, 1)
    bt.baumiRT.CopyMEMtoDisk(perGrassland, outFile)
# #### 2015 --> Grassland=1; abandonmetn 90-00=2; 00-15 abandonment=3
print("Processing year: 2015")
print("Reclassify #1")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0,0],[1,0],[2,0],[3,0],[4,0],
                                    [5,0],[6,1],[7,1],[8,1],[9,0],[10,0],
                                    [11,0],[12,1],[13,1],[14,1],[15,0]])
print("Calculate percentages of land cover")
print("Grassland")
outFile = outputFolder + "2015_PercGrassland_300m.tif"
if not os.path.exists(outFile):
    perGrassland = Aggregate(reclassRaster, 10, 1)
    bt.baumiRT.CopyMEMtoDisk(perGrassland, outFile)
print("Reclassify #2")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0,0],[1,0],[2,0],[3,0],[4,0],
                                    [5,0],[6,2],[7,3],[8,1],[9,0],[10,0],
                                    [11,0],[12,1],[13,1],[14,3],[15,0]])
print("Abandonment 90-00")
outFile = outputFolder + "2015_Abandonment_90-00_300m.tif"
if not os.path.exists(outFile):
    aband9000 = Aggregate(reclassRaster, 10, 2)
    bt.baumiRT.CopyMEMtoDisk(aband9000, outFile)
print("Abandonment 00-15")
outFile = outputFolder + "2015_Abandonment_00-15_300m.tif"
if not os.path.exists(outFile):
    aband0015 = Aggregate(reclassRaster, 10, 3)
    bt.baumiRT.CopyMEMtoDisk(aband0015, outFile)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")