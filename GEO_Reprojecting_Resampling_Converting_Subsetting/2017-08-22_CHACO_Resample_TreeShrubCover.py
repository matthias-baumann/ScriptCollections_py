# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import math
import gdal
from gdalconst import *
import numpy as np
import baumiTools as bt
from tqdm import tqdm
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
workFolder = "G:/Baumann/_ANALYSES/PercentTreeCover/___MaskedProducts//"
#inClass = gdal.Open((inputFolder + "baumann_etal_2017_ChacoOnly_LCC_allClasses_85_00_13.img"))
# ####################################### FUNCTIONS ########################################################### #
def Aggregate(inRaster, windowSize):
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
# Calculate the mean value in the window
            mean = np.mean(inArray)


# Write value to output-array
            dataOut[out_j, out_i] = mean
# Make out_j, out_i continue to increase
            out_j = out_j + 1
        out_i = out_i + 1
# Write array to virtual output-file, return rasterfile
    out.GetRasterBand(1).WriteArray(dataOut, 0, 0)
    return out
# ####################################### PROCESSING ########################################################## #
# (1) TREE COVER
print("tree cover")
tc = bt.baumiRT.OpenRasterToMemory(workFolder + "TC_Landsat-Sentinel.tif")
mean = Aggregate(tc, 10)
bt.baumiRT.CopyMEMtoDisk(mean, workFolder + "TC_Landsat-Sentinel_300m.tif")
# (2) SHRUB COVER
print("shrub cover")
sc = bt.baumiRT.OpenRasterToMemory(workFolder + "SC_Landsat-Sentinel.tif")
mean = Aggregate(sc, 10)
bt.baumiRT.CopyMEMtoDisk(mean, workFolder + "SC_Landsat-Sentinel_300m.tif")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")