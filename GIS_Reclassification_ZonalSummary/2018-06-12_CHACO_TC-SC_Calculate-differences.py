# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
from tqdm import tqdm
import gdal, osr
import numpy as np
import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES #################################### #
rootFolder = "Y:/Baumann/_ANALYSES/PercentTreeCover/___MaskedProducts/"
# ####################################### FUNCTIONS ########################################################### #
def calcDIFF(img01, img02):
    # Create output dataset
    gt = img01.GetGeoTransform()
    pr = img01.GetProjection()
    cols = img01.RasterXSize
    rows = img01.RasterYSize
    drvMemR = gdal.GetDriverByName('MEM')
    outDS = drvMemR.Create('', cols, rows, 1, gdal.GDT_Int32)
    outDS.SetProjection(pr)
    outDS.SetGeoTransform(gt)
    # Calculate difference
    rb01 = img01.GetRasterBand(1)
    rb02 = img02.GetRasterBand(1)
    rbout = outDS.GetRasterBand(1)
    noData = rb01.GetNoDataValue()
    rbout.SetNoDataValue(9999)
    # Loop through the rows
    for row in tqdm(range(rows)):
        arr01 = rb01.ReadAsArray(0, row, cols, 1)
        arr02 = rb02.ReadAsArray(0, row, cols, 1)
        outArray = np.zeros((row, cols), dtype=np.int16)
        #outArray = arr01 - arr02
        outArray = np.where(arr01 == noData, 9999, arr01 - arr02)
        rbout.WriteArray(outArray, 0, row)
    return  outDS
# ####################################### BUILD THE DIFFERENCES ############################################### #
# Open the datasets
L_TC = gdal.Open(rootFolder + "TC_Landsat.tif")
L_SC = gdal.Open(rootFolder + "TC_Landsat.tif")
S_TC = gdal.Open(rootFolder + "TC_Sentinel.tif")
S_SC = gdal.Open(rootFolder + "SC_Sentinel.tif")
LS_TC = gdal.Open(rootFolder + "TC_Landsat-Sentinel.tif")
LS_SC = gdal.Open(rootFolder + "SC_Landsat-Sentinel.tif")
# Build the differences
#bt.baumiRT.CopyMEMtoDisk(calcDIFF(LS_TC, L_TC), rootFolder + "TC_Landsat-Sentinel_diff_Landsat.tif")
bt.baumiRT.BuildPyramids(rootFolder + "TC_Landsat-Sentinel_diff_Landsat.tif", None)
#exit(0)
#bt.baumiRT.CopyMEMtoDisk(calcDIFF(LS_TC, S_TC), rootFolder + "TC_Landsat-Sentinel_diff_Sentinel.tif")
bt.baumiRT.BuildPyramids(rootFolder + "TC_Landsat-Sentinel_diff_Sentinel.tif", None)

#bt.baumiRT.CopyMEMtoDisk(calcDIFF(L_TC, S_TC), rootFolder + "TC_Landsat_diff_Sentinel.tif")
bt.baumiRT.BuildPyramids(rootFolder + "TC_Landsat_diff_Sentinel.tif", None)

#bt.baumiRT.CopyMEMtoDisk(calcDIFF(LS_SC, L_SC), rootFolder + "SC_Landsat-Sentinel_diff_Landsat.tif")
bt.baumiRT.BuildPyramids(rootFolder + "SC_Landsat-Sentinel_diff_Landsat.tif", None)

#bt.baumiRT.CopyMEMtoDisk(calcDIFF(LS_SC, S_SC), rootFolder + "SC_Landsat-Sentinel_diff_Sentinel.tif")
bt.baumiRT.BuildPyramids(rootFolder + "SC_Landsat-Sentinel_diff_Sentinel.tif", None)

#bt.baumiRT.CopyMEMtoDisk(calcDIFF(L_SC, S_SC), rootFolder + "SC_Landsat_diff_Sentinel.tif")
bt.baumiRT.BuildPyramids(rootFolder + "SC_Landsat_diff_Sentinel.tif", None)


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")