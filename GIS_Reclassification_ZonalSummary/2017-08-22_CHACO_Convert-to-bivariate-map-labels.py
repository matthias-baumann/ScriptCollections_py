# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import baumiTools as bt
import gdal
from gdalconst import *
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
workDir = "G:/Baumann/_ANALYSES/PercentTreeCover/___MaskedProducts/"
drvMemR = gdal.GetDriverByName('MEM')
def Normalize(inRaster):
    drvMemR = gdal.GetDriverByName('MEM')
# Create Output-File
    pr = inRaster.GetProjection()
    gt = inRaster.GetGeoTransform()
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    output = drvMemR.Create('', cols, rows, 1, GDT_Float32)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
# Load the raster into an array
    rb = inRaster.GetRasterBand(1)
    ar = rb.ReadAsArray(0, 0, cols, rows)
# Convert values outside the area into NAN, so that they don't interfer with the mean/std
    ar = np.where((ar == 9999), np.nan, ar)
    min = np.nanmin(ar)
    max = np.nanmax(ar)
    out = (ar - min) / (max - min)
    out_mask = np.where((ar == 9999), np.nan, out)
    #out_mask[out_mask < 0] = 0
    #out_mask[out_mask > 1] = 1
# Write the output
    out_rb = output.GetRasterBand(1)
    out_rb.WriteArray(out_mask, 0, 0)
    return output
def zTransform(inRaster, extRas):
    drvMemR = gdal.GetDriverByName('MEM')
# Create Output-File
    pr = inRaster.GetProjection()
    gt = inRaster.GetGeoTransform()
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    output = drvMemR.Create('', cols, rows, 1, GDT_Float32)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
# Load the raster into an array
    rb = inRaster.GetRasterBand(1)
    ar = rb.ReadAsArray(0, 0, cols, rows)
# Convert values outside the area into NAN, so that they don't interfer with the mean/std
    ar_ext = extRas.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    ar_mask = np.where((ar_ext == 1), ar, np.nan)
    mean = np.nanmean(ar_mask)
    std = np.nanstd(ar_mask)
    zTrans = (ar_mask - mean) / std
    zTrans_mask = np.where((ar_ext == 1), zTrans, 999)
# Write the output
    out_rb = output.GetRasterBand(1)
    out_rb.WriteArray(zTrans_mask, 0, 0)
    return output
def CalcQuant(inRaster, seps, extRas):
# Calculate the quantile-borders
    stepSize=qS = 100/seps
    qSeps = []
    while (qS < 100):
        step = int(qS)
        qSeps.append(step)
        qS = qS + stepSize
    qSeps.append(100)
# Open the raster, get properties, generate new raster
    drvMemR = gdal.GetDriverByName('MEM')
# Create Output-File
    pr = inRaster.GetProjection()
    gt = inRaster.GetGeoTransform()
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    output = drvMemR.Create('', cols, rows, 1, GDT_UInt16)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
# Load the raster into an array
    rb = inRaster.GetRasterBand(1)
    ar = rb.ReadAsArray(0, 0, cols, rows)
# Load the extent-raster into an array, mask the values outside the Chaco as NaN
    ar_ext = extRas.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    ar_mask = np.where((ar_ext == 1), ar, np.nan)
# Generate empty array with only zeros
    out = np.zeros(ar.shape, dtype='uint16')
# Now loop through each of the qSeps, and reclassify the raster accordingly
    lowerLimit = 0
    for qS in qSeps:
        value = np.nanpercentile(ar_mask, qS)
        out = np.where((ar >= lowerLimit) * (ar < value), qS, out)
        lowerLimit = value
# Mask the final output again using the extent raster2
    out_masked = np.where((ar_ext == 1), out, 999)
# Write the output
    out_rb = output.GetRasterBand(1)
    out_rb.SetNoDataValue(999)
    out_rb.WriteArray(out_masked, 0, 0)
    return output
# ####################################### PROCESSING ########################################################## #
print("Open Rasterfiles")
tc = bt.baumiRT.OpenRasterToMemory(workDir + "TC_Landsat-Sentinel.tif")
sc = bt.baumiRT.OpenRasterToMemory(workDir + "SC_Landsat-Sentinel.tif")

print("Calculate normalization")
tc_norm = Normalize(tc)
sc_norm = Normalize(sc)
# Create an outputFile
pr = tc_norm.GetProjection()
gt = tc_norm.GetGeoTransform()
cols = tc_norm.RasterXSize
rows = tc_norm.RasterYSize
outTC = drvMemR.Create('', cols, rows, 1, GDT_Float32)
outTC.SetProjection(pr)
outTC.SetGeoTransform(gt)
outSC = drvMemR.Create('', cols, rows, 2, GDT_Float32)
outSC.SetProjection(pr)
outSC.SetGeoTransform(gt)
# Load the two maps into an array
tc_arr = tc_norm.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
sc_arr = sc_norm.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
outTC.GetRasterBand(1).WriteArray(tc_arr, 0, 0)
outSC.GetRasterBand(1).WriteArray(sc_arr, 0, 0)
outTC.GetRasterBand(1).SetNoDataValue(9999)
outSC.GetRasterBand(1).SetNoDataValue(9999)
bt.baumiRT.CopyMEMtoDisk(outTC, workDir + "TC_Landsat-Sentinel_normalized.tif")
bt.baumiRT.CopyMEMtoDisk(outSC, workDir + "SC_Landsat-Sentinel_normalized.tif")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")