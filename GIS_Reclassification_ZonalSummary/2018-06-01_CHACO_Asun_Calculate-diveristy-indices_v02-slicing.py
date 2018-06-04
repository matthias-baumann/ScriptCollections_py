# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import baumiTools as bt
import gdal
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES #################################### #
rootFolder = "L:/_SHARED_DATA/ASP_MB/LC2015/"
#rootFolder = "Y:/Baumann/_ANALYSES/LandUseChange_1985-2000-2015_UpdateWithRadar/Classification/Run_03/Tiles/"
windowSize_px = 3000 # [3000, 5000]
drvMemR = gdal.GetDriverByName('MEM')
offsetOut = int(windowSize_px / 2)
# ####################################### FUNCTIONS ########################################################### #
def calcSHDI(array):
    arraySize = array.size
    SHDI = 0
    vals = [1, 2, 3, 5]
    array = np.where(array == 17, 1, array) # reclassify open woodlands into forest
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
def makeSlices(array, windowSize):
    # adopted from cgarrard, make later a function in btTools out of it
    # array : 2d array"
    # windowSize : size of the moving window --> in cgarrad cols/rows are different, here they are squared

    # Calculate the nr ofcolumns and rows
    rows = array.shape[0] - windowSize + 1
    cols = array.shape[1] - windowSize + 1
    # Create an empty list for the slices
    slices = []
    # Populate the list
    for i in range(windowSize):
        for j in range(windowSize):
            slices.append(array[i:rows+i, j:cols+j])
            #print(slices)
        #exit(0)
    slices = np.array(slices)
    return slices
# ####################################### START PROCESSING #################################################### #
# (1) Load image to memory, get infos from it
print("Copy raster to memory")
ds = bt.baumiRT.OpenRasterToMemory(rootFolder + "Run03_clumpEliminate_crop_2015_8px.tif")
ds = gdal.Open(rootFolder + "Run03_clumpEliminate_crop_2015_8px.tif")
#ds = bt.baumiRT.OpenRasterToMemory(rootFolder + "Tile_x17999_y20999_1000x1000.tif")
gt = ds.GetGeoTransform()
pr = ds.GetProjection()
cols = ds.RasterXSize
rows = ds.RasterYSize
ds_array = ds.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
#print(ds_array.shape)
# (2) Build the slices
print("Slicing...")
slice_arrays = makeSlices(ds_array, windowSize_px)
# (3) Apply the function
print("Calculating index...")
SHDI = np.apply_along_axis(calcSHDI, 0, slice_arrays)
# (4) Write values to disc
print("Write output")
SHDI_out = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
SHDI_out.SetProjection(pr)
SHDI_out.SetGeoTransform(gt)
out_array = np.zeros((rows, cols), np.float32) * -99 # Initialize output array to Nodata
out_array[offsetOut:-(offsetOut-1), offsetOut:-(offsetOut-1)] = SHDI
SHDI_out.GetRasterBand(1).WriteArray(out_array, 0, 0)
#bt.baumiRT.CopyMEMtoDisk(SHDI_out, rootFolder + "Tile_x17999_y20999_1000x1000_sub_SHDI2.tif")
bt.baumiRT.CopyMEMtoDisk(SHDI_out, rootFolder + "Run03_clumpEliminate_crop_2015_8px_SHDI_r1500.tif")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")