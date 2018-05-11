# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
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
inputFolder = "F:/Projects-and-Publications/Projects_Active/_PASANOA/baumann-etal_LandCoverMaps/"
outputFolder = "F:/Projects-and-Publications/Publications/Publications-in-preparation/Nazarro-etal_Habitat-LandCover-Chaco/"
inClass = gdal.Open((inputFolder + "baumann_etal_2017_ChacoOnly_LCC_allClasses_85_00_13.img"))
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
# 1985 --> 1: Forest, 2: Cropland, 3: Pasture, 4: natural grasslands
print("Processing year: 1985")
print("Reclassify")
#reclassRaster = ReclassifyToMemory(inClass,
#                                  [[0,0],[1,1],[2,4],[3,0],[4,2],[5,3],[6,0],[7,0],[8,0],[9,0],
#                                    [10,1],[11,1],[12,1],[13,1],[14,1],[15,4],[16,2],[17,1],[18,0],[19,0],[20,3],[21,3],[22,4],[23,4]])
print("Calculate percentages of land cover")
print("Forest")
#perForest = Aggregate(reclassRaster, 100, 1)
#CopyMEMtoDisk(perForest, (outputFolder + "1985_PercForest_3km.tif"))
print("Cropland")
#perCropland = Aggregate(reclassRaster, 100, 2)
#CopyMEMtoDisk(perCropland, (outputFolder + "1985_PercCropland_3km.tif"))
print("Pasture")
#perPasture = Aggregate(reclassRaster, 100, 3)
#CopyMEMtoDisk(perPasture, (outputFolder + "1985_PercPasture_3km.tif"))
print("Natural Grassland")
#perNG = Aggregate(reclassRaster, 100, 4)
#CopyMEMtoDisk(perNG, (outputFolder + "1985_NaturalGrasslands_3km.tif"))

print("")
# 2000 --> 1: Forest, 2: Cropland, 3: Pasture, 4: natural grasslands,
print("Processing year: 2000")
print("Reclassify stable classes")
#reclassRaster = ReclassifyToMemory(inClass,
#                                   [[0,0],[1,1],[2,4],[3,0],[4,2],[5,3],[6,0],[7,0],[8,0],[9,0],
#                                    [10,2],[11,3],[12,1],[13,1],[14,3],[15,4],[16,0],[17,1],[18,3],[19,0],[20,2],[21,3],[22,2],[23,4]])
print("Calculate percentages of land cover")
print("Forest")
#perForest = Aggregate(reclassRaster, 100, 1)
#CopyMEMtoDisk(perForest, (outputFolder + "2000_PercForest_3km.tif"))
print("Cropland")
#perCropland = Aggregate(reclassRaster, 100, 2)
#CopyMEMtoDisk(perCropland, (outputFolder + "2000_PercCropland_3km.tif"))
print("Pasture")
#perPasture = Aggregate(reclassRaster, 100, 3)
#CopyMEMtoDisk(perPasture, (outputFolder + "2000_PercPasture_3km.tif"))
print("Natural grasslands")
#perNG = Aggregate(reclassRaster, 100, 4)
#CopyMEMtoDisk(perNG, (outputFolder + "2000_NaturalGrasslands_3km.tif"))
# 5: forest-to-pasture, 6: forest-to-cropland, 7: pasture-to-cropland, 8: NG-to-cropland
print("Reclassify dynamic classes")
#reclassRaster = ReclassifyToMemory(inClass,
#                                   [[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],
#                                    [10,6],[11,5],[12,0],[13,0],[14,5],[15,0],[16,0],[17,0],[18,0],[19,0],[20,7],[21,0],[22,8],[23,0]])
print("Calculate percentages of forest-to-pasture")
#perFtP = Aggregate(reclassRaster, 100, 5)
#CopyMEMtoDisk(perFtP, (outputFolder + "1985-2000_Perc-Forest-to-Pasture-Conversion_3km.tif"))
print("Calculate percentages of forest-to-cropland")
#perFtC = Aggregate(reclassRaster, 100, 6)
#CopyMEMtoDisk(perFtC, (outputFolder + "1985-2000_Perc-Forest-to-Cropland-Conversion_3km.tif"))
print("Calculate percentages of pasture-to-cropland")
#perPtC = Aggregate(reclassRaster, 100, 7)
#CopyMEMtoDisk(perPtC, (outputFolder + "1985-2000_Perc-Pasture-to-Cropland-Conversion_3km.tif"))
print("Calculate percentages of pasture-to-cropland")
#perNGtC = Aggregate(reclassRaster, 100, 8)
#CopyMEMtoDisk(perNGtC, (outputFolder + "1985-2000_Perc-NaturalGrassland-to-Cropland-Conversion_3km.tif"))

print("")
# #### 2013 --> 1: Forest, 2: Cropland, 3: Pasture, 4: Natural grasslands
print("Processing year: 2013")
print("Reclassify stable classes")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0,0],[1,1],[2,4],[3,0],[4,2],[5,3],[6,0],[7,0],[8,0],[9,0],
                                    [10,2],[11,3],[12,2],[13,3],[14,2],[15,4],[16,4],[17,1],[18,3],[19,3],[20,2],[21,2],[22,2],[23,2]])
print("Calculate percentages of land cover")
print("Forest")
perForest = Aggregate(reclassRaster, 100, 1)
bt.baumiRT.CopyMEMtoDisk(perForest, (outputFolder + "2013_PercForest_3km_02.tif"))
print("Cropland")
perCropland = Aggregate(reclassRaster, 100, 2)
bt.baumiRT.CopyMEMtoDisk(perCropland, (outputFolder + "2013_PercCropland_3km_02.tif"))
print("Pasture")
perPasture = Aggregate(reclassRaster, 100, 3)
bt.baumiRT.CopyMEMtoDisk(perPasture, (outputFolder + "2013_PercPasture_3km_02.tif"))
print("Natural grasslands")
prNG = Aggregate(reclassRaster, 100, 4)
bt.baumiRT.CopyMEMtoDisk(prNG, (outputFolder + "2013_NaturalGrasslands_3km_02.tif"))
# 5: forest-to-pasture, 6: forest-to-cropland, 7: pasture-to-cropland, 8: NG-to=-cropaldn
print("Reclassify dynamic classes")
#reclassRaster = ReclassifyToMemory(inClass,
#                                   [[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],
#                                    [10,0],[11,0],[12,6],[13,5],[14,7],[15,0],[16,0],[17,0],[18,0],[19,0],[20,0],[21,7],[22,0],[23,8]])
print("Calculate percentages of forest-to-pasture")
#perFtP = Aggregate(reclassRaster, 100, 5)
#CopyMEMtoDisk(perFtP, (outputFolder + "2000-2013_Perc-Forest-to-Pasture-Conversion_3km.tif"))
print("Calculate percentages of forest-to-cropland")
#perFtC = Aggregate(reclassRaster, 100, 6)
#CopyMEMtoDisk(perFtC, (outputFolder + "2000-2013_Perc-Forest-to-Cropland-Conversion_3km.tif"))
print("Calculate percentages of pasture-to-cropland")
#perPtC = Aggregate(reclassRaster, 100, 7)
#CopyMEMtoDisk(perPtC, (outputFolder + "2000-2013_Perc-Pasture-to-Cropland-Conversion_3km.tif"))
print("Calculate percentages of natural-grassland-to-cropland")
#perNGtC = Aggregate(reclassRaster, 100, 8)
#CopyMEMtoDisk(perNGtC, (outputFolder + "2000-2013_Perc-NaturalGrassland-to-Cropland-Conversion_3km.tif"))

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")