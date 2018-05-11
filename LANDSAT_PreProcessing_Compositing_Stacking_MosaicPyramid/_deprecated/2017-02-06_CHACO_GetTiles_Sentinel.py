# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, osr
import os, gdal
from gdalconst import *
import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
outfile = "G:/CHACO/ReprojectedScenes/S1_Preprocessed/VV/_ScenesAsPolygons_V02.shp"
tilesFolder = "G:/CHACO/ReprojectedScenes/S1_Preprocessed/VV/"
ref = gdal.Open("G:/CHACO/ReprojectedScenes/S1_Preprocessed/VH/S1A_IW_GRDH_1SDV_20150430T092609_20150430T092634_005711_00754A_AAE3.tif")
# ####################################### PROGRAMMING ######################################################### #
# Create output file in memory
outSHP = drvV.CreateDataSource(outfile)
target_SR = osr.SpatialReference()
target_SR.ImportFromWkt(ref.GetProjection())
outLYR = outSHP.CreateLayer('outSHP', target_SR, geom_type=ogr.wkbPolygon)
IDfield = ogr.FieldDefn('ID', ogr.OFTInteger)
outLYR.CreateField(IDfield)
tileIndex = ogr.FieldDefn('TileIndex', ogr.OFTString)
outLYR.CreateField(tileIndex)
# Now loop through the different tiles, extract corner coordinates, then populate the fields
tileList = [input for input in os.listdir(tilesFolder) if input.endswith('.tif')]
count = 1
for tile in tileList:
    print(tile)
    tilePath = tilesFolder + tile
# Get the corner coordinates from the raster
    minx, miny, maxx, maxy = bt.baumiRT.GetCorners(tilePath)

# Build the polygon
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(minx, miny)
    ring.AddPoint(minx, maxy)
    ring.AddPoint(maxx, maxy)
    ring.AddPoint(maxx, miny)
    ring.AddPoint(minx, miny)
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
# Set ID field, set location
    featDef = outLYR.GetLayerDefn()
    featOut = ogr.Feature(featDef)
    featOut.SetGeometry(poly)
    featOut.SetField('ID', count)
    featOut.SetField('TileIndex', tile)
# Build geometry
    outLYR.CreateFeature(featOut)
    count = count + 1

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")