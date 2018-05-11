# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import numpy as np
import time
import baumiTools as bt
import gdal
from gdalconst import *
from tqdm import tqdm
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
inRoot = "G:/Baumann/_ANALYSES/PercentTreeCover/___FinalMaps/"
outRoot = "G:/Baumann/_ANALYSES/PercentTreeCover/___MaskedProducts/"
#CHACOshp = bt.baumiVT.CopyToMem("G:/Baumann/_ANALYSES/PercentTreeCover/___MaskedProducts/CHACO_outline.shp")
files = [["SC_Landsat", "01_LandsatOnly/L_CLEAN_S_NONE_v02__SC.vrt"],
           ["TC_Landsat", "01_LandsatOnly/L_CLEAN_S_NONE_v02__TC.vrt"],
           ["SC_Sentinel", "02_SentinelOnly/L_NONE_S_CLEAN__SC.vrt"],
           ["TC_Sentinel", "02_SentinelOnly/L_NONE_S_CLEAN__TC.vrt"],
           ["SC_Landsat-Sentinel", "03_LandsatSentinel/L_CLEAN_S_CLEAN__SC.vrt"],
           ["TC_Landsat-Sentinel", "03_LandsatSentinel/L_CLEAN_S_CLEAN__TC.vrt"]]
LC_map = gdal.Open("G:/Baumann/_ANALYSES/LandUseChange_1985-2000-2015_UpdateWithRadar/Classification/Run_03/Run03_clumpEliminate_crop.tif", GA_ReadOnly)
valuesToMask = [4, 6, 7, 8, 9, 10, 12, 14, 20, 21, 22, 23]
LC_pr = LC_map.GetProjection()
LC_gt = LC_map.GetGeoTransform()
LC_cols = LC_map.RasterXSize
LC_rows = LC_map.RasterYSize
LC_xOrigin = LC_gt[0]
LC_yOrigin = LC_gt[3]
LC_rb = LC_map.GetRasterBand(1)
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
# Loop through the items in the file-list
for file in files:
# Define the paths
    print(file[1])
    input = gdal.Open(inRoot + file[1], GA_ReadOnly)
    output = outRoot + file[0] + ".tif"
# Define the output array --> the LC-map is smaller, so we take this as the
    input_gt = input.GetGeoTransform()
    input_pixelSize = input_gt[1]
    input_xOrigin = input_gt[0]
    input_yOrigin = input_gt[3]
    input_rb = input.GetRasterBand(1)
    #dType = input_rb.DataType
# Calculate the starting column for the reading --> the land-cover map is smaller that is why we hard-code things here
    startCol = int((LC_xOrigin - input_xOrigin) / 30)
    startRow = int((input_yOrigin - LC_yOrigin) / 30)
# Generate and output-file in memory
    drvMemR = gdal.GetDriverByName('MEM')
    outRas = drvMemR.Create('', LC_cols, LC_rows, 1, GDT_UInt16)
    outRas.SetProjection(LC_pr)
    outRas.SetGeoTransform(LC_gt)
    outRas_rb = outRas.GetRasterBand(1)
    outRas_rb.SetNoDataValue(9999)
# Now loop over the rows in the input LC-map, do the operations
    for y in tqdm(range(LC_rows)):
        LC_array = LC_map.GetRasterBand(1).ReadAsArray(0, y, LC_cols, 1)
        val_array = input_rb.ReadAsArray(startCol, y+startRow, LC_cols, 1)
        # First mask the stuff outside the study area
        out_array = np.where((LC_array == 0), 9999, val_array)
        # Then the values from the list
        for val in valuesToMask:
            out_array = np.where((LC_array == val), 0, out_array)
        # Now cap areas with values > 10000
        out_array = np.where((out_array > 10000), 10000, out_array)
        # Write to output
        outRas_rb.WriteArray(out_array, 0, y)
# Write the output to dis
    bt.baumiRT.CopyMEMtoDisk(outRas, output)
# Calculate pyramids
    bt.baumiRT.BuildPyramids(output, None)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")