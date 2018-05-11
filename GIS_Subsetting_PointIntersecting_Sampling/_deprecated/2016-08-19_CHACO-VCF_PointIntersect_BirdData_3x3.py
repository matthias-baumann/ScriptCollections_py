# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import csv
import gdal, ogr, osr
import struct
from ZumbaTools._Raster_Tools import *
from ZumbaTools._Vector_Tools import *
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
drvTiff = gdal.GetDriverByName('GTiff')
drvIMG = gdal.GetDriverByName('HFA')
drvMemR = gdal.GetDriverByName('MEM')

inputPoint = "B:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Macci-etal_Percent-tree-cover_Chaco/sitios91x9_hendrik_20160915_AsPoints.shp"
outputCSV = "B:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Macci-etal_Percent-tree-cover_Chaco/sitios91x9_hendrik_20160915_AsPoints.csv"

#### PIXEL STRUCTURE --> ID refers to the point
# A   B   C
# D   ID  E
# F   G   H
# ####################################### PROCESSING ##########################################################
#(1) Copy layers to memory
print("Load layers to memory")
pointMem = drvMemV.CopyDataSource(ogr.Open(inputPoint),'')
HUB_VCF = gdal.Open("D:/baumamat/__Run_20160802/_01_tree_cover_preds/FINAL_metrics_azizenDOY/_02_capped_VRT.vrt")

# (3) EXTRACTION-FUNCTION
def ExtractFunc_raster(gdalIMG, lyr, feature):
# Build the coordinate transformation
    target_SR = osr.SpatialReference()
    target_SR.ImportFromWkt(gdalIMG.GetProjection())
    source_SR = lyr.GetSpatialRef()
    coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
# Define output data type
    rb = gdalIMG.GetRasterBand(1)
    types = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
    dataType = rb.DataType
    for type in types:
        if type[0] == dataType:
            dType = type[1]
# Now transform the coordinates and get the pixel location of the center pixel
    gt = gdalIMG.GetGeoTransform()
    geo = feature.GetGeometryRef()
    geom = geo.Clone()
    geom.Transform(coordTrans)
    mx, my = geom.GetX(), geom.GetY()
    px = int((mx - gt[0]) / gt[1])
    py = int((my - gt[3]) / gt[5])
# Check which pixel we actually want to get --> tupel = [[type, x_off, y_off],...], loop through it
    whichPX = [["A", -1, -1], ["B", 0, -1], ["C", 1, -1], ["D", -1, 0], ["CenterPX", 0, 0], ["E", 1, 0], ["F", -1, 1], ["G", 0, 1], ["H", 1, 1]]
    outList = []
    for combo in whichPX:
        liste = []
        liste.append(combo[0])
        new_px = px + combo[1]
        new_py = py + combo[2]
        structVar = rb.ReadRaster(new_px, new_py, 1, 1)
        value = struct.unpack(dType, structVar)[0]
        liste.append(value)
        outList.append(liste)
    return outList

# (4) GENERATE OUTPUT-LIST OF VARIABLE NAMES
outlist = []
header = ["Unique_ID", "plot", "point", "pixel", "TreeCover"]
outlist.append(header)
# (5) LOOP THROUGH POINTS
pointLYR = pointMem.GetLayer()
feat = pointLYR.GetNextFeature()
while feat:
    ID = feat.GetField("Unique_ID")
    plot = feat.GetField("plot")
    point = feat.GetField("point")
    print("Processing Point:", ID)
# Raster  variables
    values = ExtractFunc_raster(HUB_VCF, pointLYR, feat)
    for v in values:
        vals = []
        vals.append(ID)
        vals.append(plot)
        vals.append(point)
        vals.append(v[0])
        vals.append(v[1])
        outlist.append(vals)
    feat = pointLYR.GetNextFeature()
# (5) WRITE OUTPUT
print("Write output")
with open(outputCSV, "w") as theFile:
    csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator = '\n')
    writer = csv.writer(theFile, dialect = "custom")
    for element in outlist:
        writer.writerow(element)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")