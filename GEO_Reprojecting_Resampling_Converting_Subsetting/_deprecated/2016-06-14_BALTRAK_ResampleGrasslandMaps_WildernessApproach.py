# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import math
import gdal
from gdalconst import *
import numpy as np
import baumiTools
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
outputFolder = "F:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/05_Wilderness_LivestockDisaggreg_InputData/03_CroplandData/"
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
def FindMax(percCropland, percPasture):
    drvMemR = gdal.GetDriverByName('MEM')
# Create the output file --> based on first raster in list, as all rasters have the same size
    refRas = percCropland
    cols = refRas.RasterXSize
    rows = refRas.RasterYSize
    pr = refRas.GetProjection()
    gt = refRas.GetGeoTransform()
    out = drvMemR.Create('', cols, rows, 1, GDT_Byte)
    out.SetProjection(pr)
    out.SetGeoTransform(gt)
# Fill the out-raster by looping through the files
    out_ras = out.GetRasterBand(1)
    for row in range(rows):
# Get the raster values into arrays
        cropland = percCropland.GetRasterBand(1).ReadAsArray(0, row, cols, 1)
        pasture = percPasture.GetRasterBand(1).ReadAsArray(0, row, cols, 1)
# Find the maximum value from the new array
        maxis = np.maximum.reduce([cropland, pasture])
# Now check from which array this one comes
        outData = maxis * 0
        np.putmask(outData, maxis == cropland, 2)
        np.putmask(outData, maxis == pasture, 3)
# Mask out the frame
        frame = cropland+pasture
        np.putmask(outData, frame < 0.5, 0)

# Write the output data
        out_ras.WriteArray(outData, 0, row)
    out_ras = None
    return out

# ####################################### PROCESSING ########################################################## #
# #### 1985 --> 1: Cropland, 2: Grassland, 0: Other
print("Processing year: 1990")
print("Reclassify")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0,0],[1,0],[2,0],[3,0],[4,0],
                                    [5,1],[6,1],[7,1],[8,2],[9,2],[10,2],
                                    [11,1],[12,0],[13,0],[14,2],[15,1]])
print("Calculate percentages of land cover")
print("Cropland")
perCropland = Aggregate(reclassRaster, 10, 1)
baumiTools.baumiRT.CopyMEMtoDisk(perCropland, (outputFolder + "1990_PercCropland_300m.tif"))
print("Grassland")
#perPasture = Aggregate(reclassRaster, 17, 2)
#CopyMEMtoDisk(perPasture, (outputFolder + "1990_PercGrassland_500m.tif"))
print("Create Classification Map")
#classMap = FindMax(perCropland,perPasture)
print("Build binary Grassland-Map")
#grasslandBIN = ReclassifyToMemory(classMap, [[0,0],[1,0],[2,1]])
#CopyMEMtoDisk(grasslandBIN, (outputFolder + "1990_Grassland_Binary_500m.tif"))
print("")
# #### 2000 --> 1: Cropland, 2: Grassland, 0: Other
print("Processing year: 2000")
print("Reclassify")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0],
                                    [5, 1], [6, 2], [7, 1], [8, 2], [9, 2], [10, 1],
                                    [11, 2], [12, 0], [13, 2], [14, 1], [15, 1]])
print("Calculate percentages of land cover")
print("Cropland")
perCropland = Aggregate(reclassRaster, 10, 1)
baumiTools.baumiRT.CopyMEMtoDisk(perCropland, (outputFolder + "2000_PercCropland_300m.tif"))
print("Pasture")
#perPasture = Aggregate(reclassRaster, 17, 2)
#CopyMEMtoDisk(perPasture, (outputFolder + "2000_PercGrassland_500m.tif"))
print("Create Classification Map")
#classMap = FindMax(perCropland,perPasture)
print("Build binary Grassland-Map")
#grasslandBIN = ReclassifyToMemory(classMap, [[0,0],[1,0],[2,1]])
#CopyMEMtoDisk(grasslandBIN, (outputFolder + "2000_Grassland_Binary_500m.tif"))
print("")
# #### 2015 --> 1: Cropland, 2: Grassland, 0: Other
print("Processing year: 2015")
print("Reclassify")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0],
                                    [5, 1], [6, 2], [7, 2], [8, 2], [9, 1], [10, 1],
                                    [11, 1], [12, 2], [13, 2], [14, 2], [15, 1]])
print("Calculate percentages of land cover")
print("Cropland")
perCropland = Aggregate(reclassRaster, 10, 1)
baumiTools.baumiRT.CopyMEMtoDisk(perCropland, (outputFolder + "2015_PercCropland_300m.tif"))
print("Pasture")
#perPasture = Aggregate(reclassRaster, 17, 2)
#CopyMEMtoDisk(perPasture, (outputFolder + "2015_Grassland_500m.tif"))
print("Create Classification Map")
#classMap = FindMax(perCropland,perPasture)
print("Build binary Grassland-Map")
#grasslandBIN = ReclassifyToMemory(classMap, [[0,0],[1,0],[2,1]])
#CopyMEMtoDisk(grasslandBIN, (outputFolder + "2015_Grassland_Binary_500m.tif"))

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")