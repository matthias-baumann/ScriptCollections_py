# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import baumiTools as bt
import gdal
import itertools
from tqdm import tqdm
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES #################################### #
rootFolder = "Z:/_SHARED_DATA/ASP_MB/Diversity/"
windowSize = 3000 # [3000, 3200, 3400] radius of [1500, 1600, 1700]
windowSize_px = int(windowSize / 30)
drvMemR = gdal.GetDriverByName('MEM')
# ####################################### FUNCTIONS ########################################################### #
def calcSHDI(array):
    arraySize = array.size
    SHDI = 0
    vals = [1,2,3,4]
    for val in vals:
        count = (array == val).sum()
        # Check if value in in there, if not (i.e., count=0) then skip, because otherwise the ln will not be calculated
        if count > 0:
            prop = count / arraySize
            SHDI = SHDI + (prop * np.log(prop))
        else:
            SHDI = SHDI
    SHDI = - SHDI
    return SHDI
def calcSHEI(array):
    arraySize = array.size
    SHEI = 0
    vals = [1,2,3,4]
    nrPathType = 0
    for val in vals:
        count = (array == val).sum()
        # Check if value in in there, if not (i.e., count=0) then skip, because otherwise the ln will not be calculated
        if count > 0:
            prop = count / arraySize
            SHEI = SHEI + (prop * np.log(prop))
            nrPathType = nrPathType + 1
        else:
            SHEI = SHEI
    SHEI = - SHEI
    SHEI = SHEI / np.log(nrPathType)
    return SHEI
def calcSIDI(array):
    arraySize = array.size
    SIDI = 1
    vals = [1,2,3,4]
    for val in vals:
        count = (array == val).sum()
        # Check if value in in there, if not (i.e., count=0) then skip, because otherwise the ln will not be calculated
        if count > 0:
            prop = count / arraySize
            prop = prop * prop
            SIDI = SIDI - prop
        else:
            SIDI = SIDI
    return SIDI
# ####################################### START PROCESSING #################################################### #
# (1) Load image to memory, get infos from it
print("Copy raster to memory")
ds = bt.baumiRT.OpenRasterToMemory(rootFolder + "LC_2013/LandCover_2013_clump8px.tif")
gt = ds.GetGeoTransform()
pr = ds.GetProjection()
cols = ds.RasterXSize
rows = ds.RasterYSize
# (2) Create new virtual image of the same size
SHDI_out = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
SHDI_out.SetProjection(pr)
SHDI_out.SetGeoTransform(gt)
SHEI_out = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
SHEI_out.SetProjection(pr)
SHEI_out.SetGeoTransform(gt)
SIDI_out = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
SIDI_out.SetProjection(pr)
SIDI_out.SetGeoTransform(gt)
# (3) Now create all coordinate combinations, that we then give to the loop
print("Build Coordinate pairs")
xCoords = list(range(windowSize_px, cols - windowSize_px))
yCoords = list(range(windowSize_px, rows - windowSize_px))
permuts = list(itertools.product(xCoords, yCoords))
# (4) Now loop over the coordinates and do the stuff
print("Do processing")
rb = ds.GetRasterBand(1)
SHDI_array = np.zeros((rows, cols))
SHEI_array = np.zeros((rows, cols))
SIDI_array = np.zeros((rows, cols))
for i in tqdm(range(len(permuts))):
    x_coord = permuts[i][0]
    y_coord = permuts[i][1]
# Get the array according to the coordinates and the windowSize
    x_min = x_coord - windowSize_px
    y_min = y_coord - windowSize_px
    array = rb.ReadAsArray(x_min, y_min, windowSize_px, windowSize_px)
# Reclassify 'Open woodlands' into forests --> convert 17 into 1
# Reclassify 'Pastures' from value 5 to value 4
    array = np.where((array == 17), 1, array)
    array = np.where((array == 5), 4, array)
# Calculate indices
    SHDI = calcSHDI(array)
    SHEI = calcSHEI(array)
    SIDI = calcSIDI(array)
# Write to output arrays
    SHDI_array[y_coord, x_coord] = SHDI
    SHEI_array[y_coord, x_coord] = SHEI
    SIDI_array[y_coord, x_coord] = SIDI
    #time.sleep(0.1)
# Write output files
SHDI_out.GetRasterBand(1).WriteArray(SHDI_array, 0, 0)
bt.baumiRT.CopyMEMtoDisk(SHDI_out, rootFolder + "LC_2013/SHDI_3000buff_2013.tif")
SHEI_out.GetRasterBand(1).WriteArray(SHEI_array, 0, 0)
bt.baumiRT.CopyMEMtoDisk(SHEI_out, rootFolder + "LC_2013/SHEI_3000buff_2013.tif")
SIDI_out.GetRasterBand(1).WriteArray(SIDI_array, 0, 0)
bt.baumiRT.CopyMEMtoDisk(SIDI_out, rootFolder + "LC_2013/SIDI_3000buff_2013.tif")

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")