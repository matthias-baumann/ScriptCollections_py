# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr
import os, gdal
from gdalconst import *
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
outfile = "G:/CHACO/_COMPOSITING/Tiles_as_Polygons_2.shp"
tilesFolder = "E:/Baumann/CHACO/_Composite_Landsat8_2015/Metrics_Nov15/"
ref = ogr.Open("B:/Projects-and-Publications/Publications/Publications-in-preparation/Macci-etal_Percent-tree-cover_Chaco/_Digitization_forVCF/_New Parameterization/_AllPoints_20170102.shp",1)
refLayer = ref.GetLayer()
# ####################################### PROGRAMMING ######################################################### #
# Create output file in memory
outSHP = drvV.CreateDataSource(outfile)
outLYR = outSHP.CreateLayer('outSHP', refLayer.GetSpatialRef(), geom_type=ogr.wkbPolygon)
IDfield = ogr.FieldDefn('ID', ogr.OFTInteger)
outLYR.CreateField(IDfield)
xStart = ogr.FieldDefn('XStart', ogr.OFTString)
outLYR.CreateField(xStart)
yStart = ogr.FieldDefn('YStart', ogr.OFTString)
outLYR.CreateField(yStart)
xSize = ogr.FieldDefn('XSize', ogr.OFTString)
outLYR.CreateField(xSize)
ySize = ogr.FieldDefn('YSize', ogr.OFTString)
outLYR.CreateField(ySize)
tileIndex = ogr.FieldDefn('TileIndex', ogr.OFTString)
outLYR.CreateField(tileIndex)
activeYN = ogr.FieldDefn('Active_YN', ogr.OFTString)
outLYR.CreateField(activeYN)
# Now loop through the different tiles, extract corner coordinates, then populate the fields
tileList = [input for input in os.listdir(tilesFolder) if input.endswith('.bsq')]
count = 1
for tile in tileList:
    print(tile)
    tilePath = tilesFolder + tile
# Get the Name tags
    p = tile.rfind("PBC")
    TI = tile[:p-1]
    p = tile.find("x")
    tile = tile[p:]
    p = tile.find("_")
    xStart = tile[:p]
    tile = tile[p+1:]
    p = tile.find("_")
    yStart = tile[:p]
    tile = tile[p+1:]
    p = tile.find("x")
    xSize = tile[:p]
    tile = tile[p+1:]
    p = tile.find("_")
    ySize = tile[:p]
# Get the corner coordinates from the raster
    f_open = gdal.Open(tilePath, GA_ReadOnly)
    width = f_open.RasterXSize
    height = f_open.RasterYSize
    gt = f_open.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width*gt[4] + height*gt[5]
    maxx = gt[0] + width*gt[1] + height*gt[2]
    maxy = gt[3]
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
    featOut.SetField('XStart', xStart)
    featOut.SetField('YStart', yStart)
    featOut.SetField('XSize', xSize)
    featOut.SetField('YSize', ySize)
    featOut.SetField('TileIndex', TI)
# Check if the raster is empty --> do this by checking if band-names are NoData
    tileHDR = tilePath
    tileHDR = tileHDR.replace(".bsq", ".hdr")
    active = 1
    hdrOpen = open(tileHDR, "r")
    for line in hdrOpen:
        if line.find("noData, noData") > 0:
            active = 0
    featOut.SetField('Active_YN', active)
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