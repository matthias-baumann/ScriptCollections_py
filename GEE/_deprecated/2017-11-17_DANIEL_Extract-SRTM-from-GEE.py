# ####################################### SET TIME-COUNT ###################################################### ##
## EXTRACT LANDSAT TIME SERIES FOR POINTS (Version 1.1)                                                         ##
## (c) Matthias Baumann, MAY 2017                                                                             ##
## Humboldt-University Berlin                                                                                   ##
# ####################################### IMPORT MODULES, START EARTH-ENGINE ################################## ##
import time
import ogr
import ee
import csv
import osr
ee.Initialize()
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
shp = ogr.Open("C:/Users/Matthias/Desktop/latlong/latlong.shp")
# ####################################### SEARCH PARAMETERS AND FUNCTIONS ##################################### #
#startDate = '1985-01-01'
#endDate = '2016-01-21'
#maxCloudPerc = 90
# https://code.earthengine.google.com/datasets
def Convert_to_GCSWGS84(geom, lyrSR):
    inPR = lyrSR
    targetSR = osr.SpatialReference()
    targetSR.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(inPR, targetSR)
    geom.Transform(transform)
    return geom
def WriteOutput(outList, outFileName):
    with open(outFileName, "w") as theFile:
        csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
        writer = csv.writer(theFile, dialect="custom")
        for element in outList:
            writer.writerow(element)
# ####################################### START PREPARING THE FEATURE COLLECTION ############################## #
outList = []
lyr = shp.GetLayer()
coord = lyr.GetSpatialRef()
feat = lyr.GetNextFeature()
nFeat = lyr.GetFeatureCount()
count = 1
while feat:
    tupel = []
    # Get Point-ID from shapefile
    Pid = feat.GetField("ID")
    x = feat.GetField("lon")
    y = feat.GetField("lat")
    tupel.append(Pid)
    tupel.append(x)
    tupel.append(y)
    print("Processing Point " + str(Pid) + " of " + str(nFeat))
    #geom = Convert_to_GCSWGS84(feat.GetGeometryRef(),coord)
    geom = feat.GetGeometryRef()
    # Build an earth engine feature
    xCoord = geom.GetX()
    yCoord = geom.GetY()
    eeGeom = ee.Geometry.Point([xCoord, yCoord])
    point = ee.Feature(eeGeom, {'Point-ID': str(Pid)})
    pts = ee.FeatureCollection(point)
    # Get the value at the point
    image = ee.Image('CGIAR/SRTM90_V4')
    val =  image.reduceRegion(ee.Reducer.mean(), eeGeom, 30).get('elevation')
    #time.sleep(0.5)
    val = val.getInfo()
    tupel.append(val)
    # Append to valueList
    outList.append(tupel)
    feat = lyr.GetNextFeature()
print("")
print("Write Output")
WriteOutput(outList, "C:/Users/Matthias/Desktop/latlong/latlong_srtm.csv")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")