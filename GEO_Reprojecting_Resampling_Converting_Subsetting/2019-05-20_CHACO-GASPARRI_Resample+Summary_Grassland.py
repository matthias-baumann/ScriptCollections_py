# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import math
import gdal, ogr, osr
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
drvMemV = ogr.GetDriverByName('memory')
outputFolder = "D:/_RESEARCH/Publications/Publications-in-preparation/Gasparri-Baumann_Grasslands-Chaco/Maps/"
inClass = gdal.Open("Y:/Baumann/_ANALYSES/LandUseChange_1985-2000-2015_UpdateWithRadar/Classification/Run_03/Run03_clumpEliminate_crop.tif")
CHACO_ALL = bt.baumiVT.CopyToMem("Z:/CHACO/_SHP_Files/CHACO_VeryDry_Dry_Humid_LAEA.shp")
CHACO_dvd = bt.baumiVT.CopyToMem("D:/_RESEARCH/Publications/Publications-in-preparation/Gasparri-Baumann_Grasslands-Chaco/CHACO_dry_veryDry_dissolve.shp")
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
    out = drvMemR.Create('', outCols, outRows, 1, GDT_UInt16)
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
            ratio = (sum_dOut / max) * 10000
# Write value to output-array
            dataOut[out_j, out_i] = ratio
# Make out_j, out_i continue to increase
            out_j = out_j + 1
        out_i = out_i + 1
# Write array to virtual output-file, return rasterfile
    out.GetRasterBand(1).WriteArray(dataOut, 0, 0)
    return out
# ####################################### PROCESSING ########################################################## #
# #### Reclassify to have the grassland classes
print("Reclassify --> StableGrassland=1, GrasslandLoss8515=2, rest=0")
reclassRaster = ReclassifyToMemory(inClass,
                                   [[0,0],[1,0],[2,1],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],
                                    [10,0],[11,0],[12,0],[13,0],[14,0],[15,0],[16,0],[17,0],[18,0],[19,0],[20,0],[21,0],[22,2],[23,2]])
# #### Aggregate
print("Aggregate Natural grasslands")
perNG = Aggregate(reclassRaster, 667, 1)
bt.baumiRT.CopyMEMtoDisk(perNG, (outputFolder + "2015_PercNG_20000m_Entire-Chaco.tif"))
# #### Reproject into dry and very dry chaco only
dvd_lyr = CHACO_dvd.GetLayer()
dvd_feat = dvd_lyr.GetNextFeature()
dvd_geom = dvd_feat.GetGeometryRef()
# Check if the geometry we are processing is larger than 1x1 pixel
x_min, x_max, y_min, y_max = dvd_lyr.GetExtent()
x_res = int((x_max - x_min) / 20000)
y_res = int((y_max - y_min) / 20000)
#
dvd_ras = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
dvd_ras.SetProjection(inClass.GetProjection())
dvd_ras.SetGeoTransform((x_min, 20000, 0, y_max, 0, -20000))
dvd_ras_rb = dvd_ras.GetRasterBand(1)
dvd_ras_rb.SetNoDataValue(255)
gdal.RasterizeLayer(dvd_ras, [1], dvd_lyr, burn_values=[1])
# Reproject the 300m classification
perNG_sub = drvMemR.Create('', dvd_ras.RasterXSize, dvd_ras.RasterYSize, 1, gdal.GDT_UInt16)
perNG_sub.SetGeoTransform(dvd_ras.GetGeoTransform())
perNG_sub.SetProjection(dvd_ras.GetProjection())
perNG_sub_rb = perNG_sub.GetRasterBand(1)
perNG_sub_rb.SetNoDataValue(65535)
gdal.ReprojectImage(perNG, perNG_sub, perNG.GetProjection(), perNG_sub.GetProjection(), gdal.GRA_NearestNeighbour)
dvd_ras_np = dvd_ras_rb.ReadAsArray(0, 0, x_res, y_res)
perNG_sub_np = perNG_sub_rb.ReadAsArray(0, 0, x_res, y_res)
perNG_sub_np = np.where((dvd_ras_np==1), perNG_sub_np, 65536)
perNG_sub_rb.WriteArray(perNG_sub_np, 0, 0)

bt.baumiRT.CopyMEMtoDisk(perNG_sub, (outputFolder + "2015_PercNG_20000m_Dry-veryDry-Chaco.tif"))
# #### make summary statistics for all three regions
outTab = [["Region", "NG_2015_km2", "NG_loss_1985-2015_km2"]]
all_lyr = CHACO_ALL.GetLayer()
all_feat = all_lyr.GetNextFeature()
while all_feat:
	region = all_feat.GetField("Region")
	geom = all_feat.GetGeometryRef()
	geom_np, LC_np = bt.baumiRT.Geom_Raster_to_np(geom, reclassRaster)
	area_15 = np.count_nonzero(LC_np == 1) * 900 / 1000000
	area_loss = np.count_nonzero(LC_np == 2) * 900 / 1000000
	outTab.append([region, area_15, area_loss])
	all_feat = all_lyr.GetNextFeature()
# write to output
bt.baumiFM.WriteListToCSV(outputFolder + "Grassland_stats.csv", outTab, delim=",")





# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")