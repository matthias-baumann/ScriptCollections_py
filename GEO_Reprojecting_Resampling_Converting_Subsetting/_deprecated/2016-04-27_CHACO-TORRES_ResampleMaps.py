# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import math
import gdal
from gdalconst import *
import numpy as np
from ZumbaTools._Raster_Tools import *
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
inputFolder = "D:/Matthias/Projects-and-Publications/Projects_Active/PASANOA/baumann-etal_LandCoverMaps_SingleYears/"
outputFolder = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Torres-etal_Peccari-Habitat-LandCover/"
inClass = gdal.Open((inputFolder + "run12_classification_full_masked_clump-eliminate4px_reclass_V02.img"))
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
def FindMax(percForest, percCropland, percPasture):
    drvMemR = gdal.GetDriverByName('MEM')
# Create the output file --> based on first raster in list, as all rasters have the same size
    refRas = percForest
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
        forest = percForest.GetRasterBand(1).ReadAsArray(0, row, cols, 1)
        cropland = percCropland.GetRasterBand(1).ReadAsArray(0, row, cols, 1)
        pasture = percPasture.GetRasterBand(1).ReadAsArray(0, row, cols, 1)
# Find the maximum value from the new array
        maxis = np.maximum.reduce([forest, cropland, pasture])
# Now check from which array this one comes
        outData = maxis * 0
        np.putmask(outData, maxis == forest, 1)
        np.putmask(outData, maxis == cropland, 2)
        np.putmask(outData, maxis == pasture, 3)
# Mask out the frame
        frame = forest+cropland+pasture
        np.putmask(outData, frame < 0.5, 0)

# Write the output data
        out_ras.WriteArray(outData, 0, row)
    out_ras = None
    return out

# ####################################### PROCESSING ########################################################## #
# #### 1985 --> 1: Forest, 2: Cropland, 3: Pasture, 0: Other
print("Processing year: 1985")
print("Reclassify")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0,0],[1,1],[2,0],[3,0],[4,2],[5,3],[6,0],[7,0],[8,0],[9,0],
                                    [10,1],[11,1],[12,1],[13,1],[14,1],[15,0],[16,2],[17,1],[18,0],[19,0],[20,3],[21,3],[22,0],[23,0]])
print("Calculate percentages of land cover")
print("Forest")
perForest = Aggregate(reclassRaster, 33, 1)
CopyMEMtoDisk(perForest, (outputFolder + "1985_PercForest_1km.tif"))
print("Cropland")
perCropland = Aggregate(reclassRaster, 33, 2)
CopyMEMtoDisk(perCropland, (outputFolder + "1985_PercCropland_1km.tif"))
print("Pasture")
perPasture = Aggregate(reclassRaster, 33, 3)
CopyMEMtoDisk(perPasture, (outputFolder + "1985_PercPasture_1km.tif"))
print("Create Classification Map")
classMap = FindMax(perForest,perCropland,perPasture)
CopyMEMtoDisk(classMap, (outputFolder + "1985_LandCover_1km.tif"))
print("")
# #### 2000 --> 1: Forest, 2: Cropland, 3: Pasture, 0: Other
print("Processing year: 2000")
print("Reclassify")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0,0],[1,1],[2,0],[3,0],[4,2],[5,3],[6,0],[7,0],[8,0],[9,0],
                                    [10,2],[11,3],[12,1],[13,1],[14,3],[15,0],[16,0],[17,1],[18,3],[19,0],[20,2],[21,3],[22,2],[23,0]])
print("Calculate percentages of land cover")
print("Forest")
perForest = Aggregate(reclassRaster, 33, 1)
CopyMEMtoDisk(perForest, (outputFolder + "2000_PercForest_1km.tif"))
print("Cropland")
perCropland = Aggregate(reclassRaster, 33, 2)
CopyMEMtoDisk(perCropland, (outputFolder + "2000_PercCropland_1km.tif"))
print("Pasture")
perPasture = Aggregate(reclassRaster, 33, 3)
CopyMEMtoDisk(perPasture, (outputFolder + "2000_PercPasture_1km.tif"))
print("Create Classification Map")
classMap = FindMax(perForest,perCropland,perPasture)
CopyMEMtoDisk(classMap, (outputFolder + "2000_LandCover_1km.tif"))
print("")
# #### 2013 --> 1: Forest, 2: Cropland, 3: Pasture, 0: Other
print("Processing year: 2013")
print("Reclassify")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0,0],[1,1],[2,0],[3,0],[4,2],[5,3],[6,0],[7,0],[8,0],[9,0],
                                    [10,2],[11,3],[12,2],[13,3],[14,2],[15,0],[16,0],[17,1],[18,3],[19,3],[20,2],[21,2],[22,2],[23,2]])
print("Calculate percentages of land cover")
print("Forest")
perForest = Aggregate(reclassRaster, 33, 1)
CopyMEMtoDisk(perForest, (outputFolder + "2013_PercForest_1km.tif"))
print("Cropland")
perCropland = Aggregate(reclassRaster, 33, 2)
CopyMEMtoDisk(perCropland, (outputFolder + "2013_PercCropland_1km.tif"))
print("Pasture")
perPasture = Aggregate(reclassRaster, 33, 3)
CopyMEMtoDisk(perPasture, (outputFolder + "2013_PercPasture_1km.tif"))
print("Create Classification Map")
classMap = FindMax(perForest,perCropland,perPasture)
CopyMEMtoDisk(classMap, (outputFolder + "2013_LandCover_1km.tif"))

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")