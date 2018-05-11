# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal, ogr
import baumiTools as bt
from gdalconst import *
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
inFiles = bt.baumiFM.GetFilesInFolderWithEnding(
"F:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/05_Wilderness_LivestockDisaggreg_InputData/_WildernessRuns/20170227_Run10/",
"SOM_2x1_output.tif", True)
outFile = "F:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/05_Wilderness_LivestockDisaggreg_InputData/_WildernessRuns/20170227_Run10/_SOM_SumOfOutputs_20170626.tif"
drvR = gdal.GetDriverByName('GTiff')
# ####################################### PROCESSING ########################################################## #
# (0) OPEN THE FIRST RASTER-FILE IN THE LIST TO PULL THE PROPERTIES
ds1 = gdal.Open(inFiles[0], GA_ReadOnly)
cols = ds1.RasterXSize
rows = ds1.RasterYSize
pr = ds1.GetProjection()
gt = ds1.GetGeoTransform()
# (1) CREATE OUTPUT FILE IN MEMORY
outRas = drvR.Create(outFile, cols, rows, 1, GDT_Int16)
outRas.SetProjection(pr)
outRas.SetGeoTransform(gt)
outRas.GetRasterBand(1).SetNoDataValue(99)
outArray = np.zeros((rows, cols), dtype=np.int)
# (2) LOOP THROUGH ALL FILES IN THE LIST, DO THE PROCESSING.
for file in inFiles:
    # Open the file, get the array
    ds = gdal.Open(file, GA_ReadOnly)
    arr = ds.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    # Re-classify into binary map, sum to outArray
    arr = arr - 1
    outArray = outArray + arr
    ds = None
    arr = None
# (3) MASK AGAIN OUTSIDE THE STUDY REGION, THEN WRITE THE OUTPUT TO DISK
maskArray = ds1.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
outArray = np.where((maskArray >= 1), outArray, 99)
outRas.GetRasterBand(1).WriteArray(outArray, 0, 0)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")