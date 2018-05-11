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
shp = ogr.Open("C:/Users/baumamat/Desktop/Muflon/mouflon_presence_170515.shp")
# ####################################### SEARCH PARAMETERS AND FUNCTIONS ##################################### #
startDate = '1999-01-01'
endDate = '2017-12-31'
maxCloudPerc = 80
# https://code.earthengine.google.com/datasets
def Convert_to_GCSWGS84(geom, lyrSR):
    inPR = lyrSR
    targetSR = osr.SpatialReference()
    targetSR.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(inPR, targetSR)
    geom.Transform(transform)
    return geom
def GetData(points, collection, startDate, endDate, maxCloudPerc, BandsDict_short):
    BandsDict = {'L8_Tier1': ee.List([1, 2, 3, 4, 5, 6]),
                 'L7_Tier1': ee.List([0, 1, 2, 3, 4, 7]),
                 'L7_TOA_FMASK': ee.List([0, 1, 2, 3, 4, 7, 9]),
                 'L5_TOA_FMASK': ee.List([0, 1, 2, 3, 4, 5, 7]),
                 'L4_TOA_FMASK': ee.List([0, 1, 2, 3, 4, 5, 7])}
    command = ee.ImageCollection(collection). \
        filterDate(startDate, endDate). \
        filter(ee.Filter.lt('CLOUD_COVER', maxCloudPerc)). \
        select(BandsDict.get(BandsDict_short))
    retrieve = command.getRegion(points, 30, "epsg:4326").getInfo()
    return retrieve
def WriteOutput(outList, outFileName):
    with open(outFileName, "w") as theFile:
        csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
        writer = csv.writer(theFile, dialect="custom")
        for element in outList:
            writer.writerow(element)
# ####################################### START PREPARING THE FEATURE COLLECTION ############################## #
L8_output = []
L7_output = []
lyr = shp.GetLayer()
coord = lyr.GetSpatialRef()
feat = lyr.GetNextFeature()
nFeat = lyr.GetFeatureCount()
count = 1
while feat:
    Pid = feat.GetField("Id")
    print("Processing Point " + str(count) + " of " + str(nFeat))
    geom = Convert_to_GCSWGS84(feat.GetGeometryRef(),coord)
    #geom = feat.GetGeometryRef()
    xCoord = geom.GetX()
    yCoord = geom.GetY()
    point = ee.Feature(ee.Geometry.Point([xCoord, yCoord]), {'Point-ID': str(Pid)})
    pts = ee.FeatureCollection(point)
    valL8t1 = GetData(pts, 'LANDSAT/LC08/C01/T1_TOA', startDate, endDate, maxCloudPerc, 'L8_Tier1')
    time.sleep(1)
    if count == 1:
        header = valL8t1[0]
        header.append("Point_ID")
        L8_output.append(header)
        for i in range(1,len(valL8t1)):
            values = valL8t1[i]
            values.append(Pid)
            L8_output.append(values)
    else:
        for i in range(1,len(valL8t1)):
            values = valL8t1[i]
            values.append(Pid)
            L8_output.append(values)
    valL7t1 = GetData(pts, 'LANDSAT/LE07/C01/T1_TOA', startDate, endDate, maxCloudPerc, 'L7_Tier1')
    time.sleep(1)
    if count == 1:
        header = valL7t1[0]
        header.append("Point_ID")
        L7_output.append(header)
        for i in range(1,len(valL7t1)):
            values = valL7t1[i]
            values.append(Pid)
            L7_output.append(values)
    else:
        for i in range(1,len(valL7t1)):
            values = valL7t1[i]
            values.append(Pid)
            L7_output.append(values)
    count = count+1
    feat = lyr.GetNextFeature()
print("")
print("Write Output")
WriteOutput(L8_output, "C:/Users/baumamat/Desktop/Muflon/mouflon_presence_170515_values_L8_1999-2017.csv")
WriteOutput(L7_output, "C:/Users/baumamat/Desktop/Muflon/mouflon_presence_170515_values_L7_1999-2017.csv")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")