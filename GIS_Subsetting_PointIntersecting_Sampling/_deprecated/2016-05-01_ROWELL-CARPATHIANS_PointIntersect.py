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
#pointOldGrow = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Rowell-etal_Romania-Restitution-OldGrowth/Analysis/01_OldGrow_Sample.shp"
pointPublicPrivate = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Rowell-etal_Romania-Restitution-OldGrowth/Analysis/02_PublicPrivate.shp"
#OldGrowOut = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Rowell-etal_Romania-Restitution-OldGrowth/Analysis/01_OldGrow_Sample_values_20160501.csv"
PublicPrivateOut = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Rowell-etal_Romania-Restitution-OldGrowth/Analysis/02_PublicPrivate_values_20160501.csv"
# ####################################### PROCESSING ##########################################################
lyrRoot = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Rowell-etal_Romania-Restitution-OldGrowth/Analysis/Inputdata/"
#(1) Copy layers to memory
print("Load layers to memory")
pointMem = drvMemV.CopyDataSource(ogr.Open(pointPublicPrivate),'')
road_dis = gdal.Open((lyrRoot + "DistToRoad.tif"))
rail_dis = gdal.Open((lyrRoot + "DistToRailway.tif"))
sett_dis = gdal.Open((lyrRoot + "DistanceToSettlements.tif"))
slope = gdal.Open((lyrRoot + "Slope_degrees.tif"))
lc = gdal.Open((lyrRoot + "LandCoverMap.img"))
elevation = gdal.Open((lyrRoot + "Elevation.tif"))
private = drvMemV.CopyDataSource(ogr.Open((lyrRoot + "PrivateLands.shp")),'')
oldgrow = drvMemV.CopyDataSource(ogr.Open((lyrRoot + "OldGrowth.shp")),'')
dfe85 = gdal.Open((lyrRoot + "DistanceToForestEdge_1985.tif"))
dfe90 = gdal.Open((lyrRoot + "DistanceToForestEdge_1990.tif"))
dfe95 = gdal.Open((lyrRoot + "DistanceToForestEdge_1995.tif"))
dfe00 = gdal.Open((lyrRoot + "DistanceToForestEdge_2000.tif"))
dfe05 = gdal.Open((lyrRoot + "DistanceToForestEdge_2005.tif"))
dfe10 = gdal.Open((lyrRoot + "DistanceToForestEdge_2010.tif"))

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
header = ["ID", "LandCover", "RoadDis", "RailDis", "SettDist", "Slope", "Elevation",
		  "DFE85", "DFE90", "DFE95", "DFE00", "DFE05", "DFE10", "Privatized", "OldGrow"]
outlist.append(header)
# (5) LOOP THROUGH POINTS
pointLYR = pointMem.GetLayer()
feat = pointLYR.GetNextFeature()
while feat:
    vals = []
    ID = feat.GetField("ID")
    print("Processing Point:", ID)
    vals.append(ID)
# Raster  variables
    get_lc = ExtractFunc_raster(lc, pointLYR, feat)
    vals.append(get_lc)
    get_roaddis = ExtractFunc_raster(road_dis, pointLYR, feat)
    vals.append(get_roaddis)
    get_raildis = ExtractFunc_raster(rail_dis, pointLYR, feat)
    vals.append(get_raildis)
    get_settdis = ExtractFunc_raster(sett_dis, pointLYR, feat)
    vals.append(get_settdis)
    get_slope = ExtractFunc_raster(slope, pointLYR, feat)
    vals.append(get_slope)
    get_elevation = ExtractFunc_raster(elevation, pointLYR, feat)
    vals.append(get_elevation)
    get_dfe85 = ExtractFunc_raster(dfe85, pointLYR, feat)
    vals.append(get_dfe85)
    get_dfe90 = ExtractFunc_raster(dfe90, pointLYR, feat)
    vals.append(get_dfe90)
    get_dfe95 = ExtractFunc_raster(dfe95, pointLYR, feat)
    vals.append(get_dfe95)
    get_dfe00 = ExtractFunc_raster(dfe00, pointLYR, feat)
    vals.append(get_dfe00)
    get_dfe05 = ExtractFunc_raster(dfe05, pointLYR, feat)
    vals.append(get_dfe05)
    get_dfe10 = ExtractFunc_raster(dfe10, pointLYR, feat)
    vals.append(get_dfe10)
# Vector layers
    get_priv = ExtractFunc_vector(private, pointLYR, feat, "Date_of_da")
    vals.append(get_priv)
    get_oldGrow = ExtractFunc_vector(oldgrow, pointLYR, feat, "OldGrow")
    vals.append(get_oldGrow)
    # Attach values to outlist, get next feature
    outlist.append(vals)
    feat = pointLYR.GetNextFeature()
# (5) WRITE OUTPUT
print("Write output")
with open(PublicPrivateOut, "w") as theFile:
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