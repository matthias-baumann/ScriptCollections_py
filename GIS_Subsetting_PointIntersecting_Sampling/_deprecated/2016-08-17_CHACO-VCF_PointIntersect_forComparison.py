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

inputPoint = "D:/baumamat/PointDataset_withPercentCover_20160817.shp"
outputCSV = "D:/baumamat/PointDataset_withPercentCover_20160822.csv"
# ####################################### PROCESSING ##########################################################
#(1) Copy layers to memory
print("Load layers to memory")
pointMem = drvMemV.CopyDataSource(ogr.Open(inputPoint),'')
HANSEN_VCF_2000 = gdal.Open("D:/baumamat/Hansen_TreeCover2000_Mosaic")
HANSEN_VCF_2010 = gdal.Open("D:/baumamat/Hansen_2010_TreeCover/Hansen-TreeCover.vrt")
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
# Now transform the coordinates and get the pixel locations
    gt = gdalIMG.GetGeoTransform()
    geo = feature.GetGeometryRef()
    geom = geo.Clone()
    geom.Transform(coordTrans)
    mx, my = geom.GetX(), geom.GetY()
    px = int((mx - gt[0]) / gt[1])
    py = int((my - gt[3]) / gt[5])
    structVar = rb.ReadRaster(px,py,1,1)
    value= struct.unpack(dType, structVar)[0]
    return value

def ExtractFunc_vector(gdalSHP, lyr, feature, field):
# Build the coordinate transformation
    gdal_lyr = gdalSHP.GetLayer()
    target_SR = gdal_lyr.GetSpatialRef()
    source_SR = lyr.GetSpatialRef()
    coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
# Create a virtual point
    geo = feature.GetGeometryRef()
    geom = geo.Clone()
    geom.Transform(coordTrans)
    mx, my = geom.GetX(), geom.GetY()
    pt = ogr.Geometry(ogr.wkbPoint)
    pt.SetPoint_2D(0,mx,my)
# Set up a spatial filter for polygon layer based on that point location
    gdal_lyr.SetSpatialFilter(pt)
# Check length of lyr when filter is set, if count == 0, then return NaN, otherwise return value
    count = gdal_lyr.GetFeatureCount()
    if count == 0:
        value = "NaN"
    else:
        for feat_in in gdal_lyr:
            value = feat_in.GetFieldAsString(field)
    gdal_lyr.SetSpatialFilter(None)
    return value

# (4) GENERATE OUTPUT-LIST OF VARIABLE NAMES
outlist = []
header = ["ID", "IN_DATA", "HUB_VCF", "HANSEN_VCF_2000", "Hansen_VCF_2010"]
outlist.append(header)
# (5) LOOP THROUGH POINTS
pointLYR = pointMem.GetLayer()
feat = pointLYR.GetNextFeature()
while feat:
    vals = []
    ID = feat.GetField("ID")
    print("Processing Point:", ID)
    vals.append(ID)
    mapped = feat.GetField("TC_perc")
    vals.append(mapped)
# Raster  variables
    get_HUB = ExtractFunc_raster(HUB_VCF, pointLYR, feat)
    vals.append(get_HUB)
    get_Hansen00 = ExtractFunc_raster(HANSEN_VCF_2000, pointLYR, feat)
    vals.append(get_Hansen00)
    get_Hansen10 = ExtractFunc_raster(HANSEN_VCF_2010, pointLYR, feat)
    vals.append(get_Hansen10)
    # Attach values to outlist, get next feature
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