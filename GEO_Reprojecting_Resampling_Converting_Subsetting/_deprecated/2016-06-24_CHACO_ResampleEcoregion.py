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
inputFolder = "G:/CHACO/_ANALYSES/CarbonCorridors/"
outputFolder = "G:/CHACO/_ANALYSES/CarbonCorridors//"
inClass = gdal.Open((inputFolder + "DryWetVerydry_Chaco_Ecoregion_clip.tif"))
# ####################################### FUNCTIONS ########################################################### #
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

def Reproject(inRaster, refRaster):
    in_pr = inRaster.GetProjection()
    in_gt = inRaster.GetGeoTransform()
    out_pr = refRaster.GetProjection()
    out_gt = refRaster.GetGeoTransform()
    out_cols = refRaster.RasterXSize
    out_rows = refRaster.RasterYSize
    outfile = drvMemR.Create('', out_cols, out_rows, 1, GDT_Float32)
    outfile.SetProjection(out_pr)
    outfile.SetGeoTransform(out_gt)
    res = gdal.ReprojectImage(inRaster, outfile, in_pr, out_pr, gdal.GRA_NearestNeighbour)
    return outfile

# ####################################### PROCESSING ########################################################## #
print("Calculate percentages of subregions")
print("Wet Chaco")
print("Aggregate")
perWet = Aggregate(inClass, 1000, 1)
print("Resample back to 30m")
perWet30 = Reproject(perWet, inClass)
print("Dry Chaco")
print("Aggregate")
perDry = Aggregate(inClass, 1000, 2)
print("Resample back to 30m")
perDry30 = Reproject(perDry, inClass)
print("Very dry Chaco")
print("Aggregate")
perVeryDry = Aggregate(inClass, 1000, 3)
print("Resample back to 30m")
perVeryDry30 = Reproject(perVeryDry, inClass)


print("Copy files to disk")
CopyMEMtoDisk(perWet30, "G:/CHACO/_ANALYSES/CarbonCorridors/perWet30m.tif")
CopyMEMtoDisk(perWet, "G:/CHACO/_ANALYSES/CarbonCorridors/perWet30000m.tif")
CopyMEMtoDisk(perDry30, "G:/CHACO/_ANALYSES/CarbonCorridors/perDry30m.tif")
CopyMEMtoDisk(perDry, "G:/CHACO/_ANALYSES/CarbonCorridors/perDry30000m.tif")
CopyMEMtoDisk(perVeryDry30, "G:/CHACO/_ANALYSES/CarbonCorridors/perVeryDry30m.tif")
CopyMEMtoDisk(perVeryDry, "G:/CHACO/_ANALYSES/CarbonCorridors/perVeryDry30000m.tif")


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")