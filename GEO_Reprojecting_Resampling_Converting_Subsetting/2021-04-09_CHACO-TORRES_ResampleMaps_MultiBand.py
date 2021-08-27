# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
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

root_folder = "G:/Baumann/_ANALYSES/AnnualLandCoverChange_CHACO-CHIQUI_EarthEngine/"
CHACO_shape = bt.baumiVT.CopyToMem(root_folder + "OtherShapefiles/CHACO_outline_EPSG4326.shp")
outFolder = root_folder + "01_F_C_P_OV_O/99_MapExtracts/Torres_MapAggregations_1km/"
LC_folder = root_folder + "01_F_C_P_OV_O/05_MapProducts/Run12/output_LandCover_2/"
windowSize = 33
# ####################################### FUNCTIONS ########################################################### #

# (1) Create a VRT of the Land Cover
print("Build vrt...")
def BuildVRT(folder, outfile):
    fileList = bt.baumiFM.GetFilesInFolderWithEnding(folder, ".tif", fullPath=True)
    vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest', addAlpha=False)
    vrt = gdal.BuildVRT(outfile, fileList, options=vrt_options)
    vrt = None
    return outfile
vrt = BuildVRT(LC_folder, root_folder + "01_F_C_P_OV_O/05_MapProducts/Run12/LandCover_2_torres.vrt")
vrtOpen = gdal.Open(vrt)

# (2) Get the raster information from the raster
print("Create output-files")
cols = vrtOpen.RasterXSize
rows = vrtOpen.RasterYSize
bands = vrtOpen.RasterCount
gt = vrtOpen.GetGeoTransform()
pr = vrtOpen.GetProjection()

# (3) build the output-file
cols = windowSize * (math.floor(cols / windowSize))
rows = windowSize * (math.floor(rows / windowSize))
outCols = int(cols / windowSize)
outRows = int(rows / windowSize)
cols = cols - 1
rows = rows - 1
out_gt = [gt[0], float(gt[1])*windowSize, gt[2], gt[3], gt[4], float(gt[5])*windowSize] # Build new GeoTransform
out = drvMemR.Create('', outCols, outRows, 1, GDT_Float32)
out.SetProjection(pr)
out.SetGeoTransform(out_gt)

# (4) Instantiate output array
wl = np.zeros((outRows, outCols, bands))
onv = np.zeros((outRows, outCols, bands))
c = np.zeros((outRows, outCols, bands))
p = np.zeros((outRows, outCols, bands))
o = np.zeros((outRows, outCols, bands))

# (5) Start the loop
print("Do the aggregation")
time.sleep(3)
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
# (6) Do the operation inside the loop
        for bandCount, arrCount in enumerate(range(bands), start=1):
            arr_in = vrtOpen.GetRasterBand(bandCount).ReadAsArray(i, j, numCols, numRows)
            # Calculate the proportions
            p_wl = (((arr_in == 1).sum()) / (windowSize * windowSize)) * 10000
            p_onv = (((arr_in == 20).sum() + (arr_in == 21).sum() + (arr_in == 22).sum() + (arr_in == 23).sum()) / (windowSize * windowSize)) * 10000
            p_c = (((arr_in == 3).sum()) / (windowSize * windowSize)) * 10000
            p_p = (((arr_in == 4).sum()) / (windowSize * windowSize)) * 10000
            p_o = (((arr_in == 5).sum()) / (windowSize * windowSize)) * 10000
            # Write into output arrays
            wl[out_j, out_i, arrCount] = p_wl
            onv[out_j, out_i, arrCount] = p_onv
            c[out_j, out_i, arrCount] = p_c
            p[out_j, out_i, arrCount] = p_p
            o[out_j, out_i, arrCount] = p_o
        # Increase counter
        out_j += 1
    out_i += 1
# (7) Create virtual rasters in memory for each land cover
print("Create virtual raster files")
def CreateMEMRas(arr, cols, rows, gt, pr, type):
    # Get numbber of bands from array (i.e. third dimension
    dims = arr.ndim
    if dims == 2:
        outRas = drvMemR.Create('', cols, rows, 1, type)
        outRas.SetProjection(pr)
        outRas.SetGeoTransform(gt)
        outRas.GetRasterBand(1).WriteArray(arr, 0, 0)
    if dims > 2:
        outRas = drvMemR.Create('', cols, rows, arr.shape[2], type)
        outRas.SetProjection(pr)
        outRas.SetGeoTransform(gt)
        for bandCount, arrCount in enumerate(range(arr.shape[2]), start=1):
            outRas.GetRasterBand(bandCount).WriteArray(arr[:, :, arrCount], 0, 0)
    return outRas
wl_ras = CreateMEMRas(wl, outCols, outRows, out_gt, pr, GDT_UInt16)
onv_ras = CreateMEMRas(onv, outCols, outRows, out_gt, pr, GDT_UInt16)
c_ras = CreateMEMRas(c, outCols, outRows, out_gt, pr, GDT_UInt16)
p_ras = CreateMEMRas(p, outCols, outRows, out_gt, pr, GDT_UInt16)
o_ras = CreateMEMRas(o, outCols, outRows, out_gt, pr, GDT_UInt16)

# (8) Crop and mask them
print("Crop the rasters to the Chaco extent")
wl_clip = bt.baumiRT.ClipRasterBySHP(CHACO_shape, wl_ras, mask=True)
onv_clip = bt.baumiRT.ClipRasterBySHP(CHACO_shape, onv_ras, mask=True)
c_clip = bt.baumiRT.ClipRasterBySHP(CHACO_shape, c_ras, mask=True)
p_clip = bt.baumiRT.ClipRasterBySHP(CHACO_shape, p_ras, mask=True)
o_clip = bt.baumiRT.ClipRasterBySHP(CHACO_shape, o_ras, mask=True)

# (9) Write to disc
print("Write to disc")
bt.baumiRT.CopyMEMtoDisk(wl_clip, outFolder + "Run12_Perc-Woodland_1km_1985-2020.tif")
bt.baumiRT.CopyMEMtoDisk(onv_clip, outFolder + "Run12_Perc-OtherVegetation_1km_1985-2020.tif")
bt.baumiRT.CopyMEMtoDisk(c_clip, outFolder + "Run12_Perc-Cropland_1km_1985-2020.tif")
bt.baumiRT.CopyMEMtoDisk(p_clip, outFolder + "Run12_Perc-Pasture_1km_1985-2020.tif")
bt.baumiRT.CopyMEMtoDisk(o_clip, outFolder + "Run12_Perc-Other_1km_1985-2020.tif")


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")