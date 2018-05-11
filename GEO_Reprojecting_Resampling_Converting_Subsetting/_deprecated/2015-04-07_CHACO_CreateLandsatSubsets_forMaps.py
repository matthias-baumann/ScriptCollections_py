# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import gdal
import ogr, osr
from gdalconst import *
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### HARD-CODED FOLDERS AND FILES ######################################## #
#raster = "L:/Chaco/MB_MPR/Baumann-etal_LUC_carbon_Chaco/GIS/run12_classification_full_masked_clump-eliminate4px_reclass.img"
#raster = "E:/Baumann/LandsatData/03_ScratchData/GDAL-VRT_1985.vrt"
#raster = "E:/Baumann/LandsatData/03_ScratchData/GDAL-VRT_2000.vrt"
raster = "E:/Baumann/LandsatData/03_ScratchData/GDAL-VRT_2013.vrt"

shape = "L:/Chaco/MB_MPR/Baumann-etal_LUC_carbon_Chaco/GIS/boxes_combined.shp"
outFolder = "L:/Chaco/MB_MPR/Baumann-etal_LUC_carbon_Chaco/GIS/Image_Subsets/"
# ####################################### GLOBAL FUNCTIONS #################################################### #

# ####################################### PROCESSING ########################################################## #
# (1) OPEN THE VECTOR LAYER, GET THE COORDINATE INFORMATION, START LOOPING THROUGH FEATURES
ds_pol = ogr.Open(shape, GA_ReadOnly)
lyr = ds_pol.GetLayer()
pol_srs = lyr.GetSpatialRef()
feat = lyr.GetNextFeature()
while feat:
    id = feat.GetField('Id')
    name = feat.GetField('Box_Type')
    #(2) START LOOPING THROUGH THE RASTER-FILES, CREATE COORDINATE TRANSFORMATION
    ds_ras = gdal.Open(raster, GA_ReadOnly)
    ras_srs = ds_ras.GetProjection()
    numBand = ds_ras.RasterCount
    target_SR = osr.SpatialReference()
    target_SR.ImportFromWkt(ras_srs)
    transform = osr.CoordinateTransformation(pol_srs, target_SR)
    # Get vector geometry, transform the coordinate system, get bounding box -->  --> GetEnvelope() returns a tuple (minX, maxX, minY, maxY)
    geom = feat.GetGeometryRef()
    geom.Transform(transform)
    env = geom.GetEnvelope()
    # Create outputFileName --> outformats are TIFFs
    p = raster.rfind("/")
    outFile = raster[p+1:]
    p = outFile.rfind(".")
    outFile = name + "_" + outFile[:p] + ".tif"
    outPath = outFolder + outFile
    print(outPath)
    # Build the subset-command, execute
    if numBand == 1:
        command = "gdal_translate -of GTiff -projwin " + str(env[0]) + " " + str(env[3]) + " " + str(env[1]) + " " + str(env[2]) + " " + raster + " " + outPath
    else:
        command = "gdal_translate -b 1 -b 2 -b 3 -b 4 -b 5 -b 6 -of GTiff -projwin " + str(env[0]) + " " + str(env[3]) + " " + str(env[1]) + " " + str(env[2]) + " " + raster + " " + outPath
    os.system(command)
    # Switch to next feature
    feat = lyr.GetNextFeature()

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")