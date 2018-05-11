# ####################################### SET TIME-COUNT ###################################################### ##
## EXTRACT LANDSAT TIME SERIES FOR POINTS (Version 1.0)                                                         ##
## (c) Matthias Baumann, April 2017                                                                             ##
## Humboldt-University Berlin                                                                                   ##
# ####################################### IMPORT MODULES, START EARTH-ENGINE ################################## ##
import time
import ogr
import ee
import csv
ee.Initialize()
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
#shp = ogr.Open("C:/Users/Matthias/Work/Desktop/Bleyhl/shepherd_camp_locations/highres_camps_bg_pol_nounsure_GCS_WGS84.shp")
shp = ogr.Open("F:/Projects-and-Publications/Publications/Publications-in-preparation/bleyhl-etal_Sheppard-camps-Caucaus/highres_camps_bg_pol_nounsure_GCS_WGS84_firstFive.shp")
#output = "C:/Users/Matthias/Work/Desktop/Bleyhl/shepherd_camp_locations/_highres_camps_bg_pol_nounsure_GCS_WGS84_2014-2017.csv"
output = "F:/Projects-and-Publications/Publications/Publications-in-preparation/bleyhl-etal_Sheppard-camps-Caucaus/_highres_camps_bg_pol_nounsure_GCS_WGS84_2014-2017.csv"
# ####################################### SEARCH PARAMETERS ################################################### #
startDate = '2017-04-01'
endDate = '2017-12-31'
maxCloudPerc = 80
packageSize = 2 # Create subsets of points because EE does not return large datasets. Variable refers to # points in subset
# https://code.earthengine.google.com/datasets
collection = 'LANDSAT/LE07/C01/T1_TOA' # 'LANDSAT/LC8_L1T_TOA_FMASK', 'LANDSAT/LT5_L1T_TOA_FMASK', 'LANDSAT/LT4_L1T_TOA_FMASK'
collection_abbr = 'L7_Tier1' # 'L8_TOA_FMASK', 'L7_TOA_FMASK', 'L5_TOA_FMASK', 'L4_TOA_FMASK'
# ####################################### START PREPARING THE FEATURE COLLECTION ############################## #
print("Collecting features, subdivide in packages")
packageList = []
pointList = []
lyr = shp.GetLayer()
coord = lyr.GetSpatialRef()
feat = lyr.GetNextFeature()
pointCount = 0
while feat:
    pointCount = pointCount + 1
    if pointCount <= packageSize:
# Translate OGR Feature into ee Feature
        Pid = feat.GetField("Id")
        geom = feat.GetGeometryRef()
        xCoord = geom.GetX()
        yCoord = geom.GetY()
        point = ee.Feature(ee.Geometry.Point([xCoord, yCoord]), {'Point-ID': str(Pid)})
# Append to lists
        pointList.append(point)
        feat = lyr.GetNextFeature()
    else:
        # Convert list of features into feature collection
        pts = ee.FeatureCollection(ee.List(pointList))
        packageList.append(pts)
        pointList = []
        pointCount = 1
# Translate OGR Feature into ee Feature
        Pid = feat.GetField("Id")
        geom = feat.GetGeometryRef()
        xCoord = geom.GetX()
        yCoord = geom.GetY()
        point = ee.Feature(ee.Geometry.Point([xCoord, yCoord]), {"Point_ID": str(Pid)})
# Append to lists
        pointList.append(point)
        feat = lyr.GetNextFeature()
# Put the last package to the packageList
pts = ee.FeatureCollection(ee.List(pointList))
packageList.append(pts)
lyr.ResetReading()
print("")
# ####################################### EXTRACT VALUES FROM COLLECTIONS ##################################### #
print("Extracting values")
# Function for better application
def GetData(points, collection, startDate, endDate, maxCloudPerc, BandsDict_short):
    BandsDict = {'L8_TOA_FMASK': ee.List([1, 2, 3, 4, 5, 6, 8]),
                 'L7_Tier1': ee.List([0, 1, 2, 3, 4, 7]),
                 'L7_TOA_FMASK': ee.List([0, 1, 2, 3, 4, 7, 9]),
                 'L5_TOA_FMASK': ee.List([0, 1, 2, 3, 4, 5, 7]),
                 'L4_TOA_FMASK': ee.List([0, 1, 2, 3, 4, 5, 7])}
    command = ee.ImageCollection(collection).\
        filterDate(startDate, endDate).\
        filter(ee.Filter.lt('CLOUD_COVER', maxCloudPerc)).\
        select(BandsDict.get(BandsDict_short))


    retrieve = command.getRegion(points, 30, "epsg:4326").getInfo()

    return retrieve
valueList = []
for package in packageList:
    print(packageList.index(package)+1, "out of", len(packageList))
    values = GetData(package, collection, startDate, endDate, maxCloudPerc, collection_abbr)
    valueList.append(values)

# ####################################### CORRECT LOCATIONS AND WRITE OUTPUT ################################## #
def MergeLists(LandsatList, inputPoint):
    buff = 0.000001
# Load input shapefile to memorey
    drvMemV = ogr.GetDriverByName('Memory')
    lyr = inputPoint.GetLayer()
    outList = []
    header = LandsatList[0]
    header.append("PointID")
    #outList.append(header)
    LandsatList.pop(0)
# Get the unique locations from the LandsatList
    LandsatList_unique = []
    for L in LandsatList:
        coord = [L[1], L[2]]
        if coord not in LandsatList_unique:
            LandsatList_unique.append(coord)
# Now loop over each coordinate in the LandsatList_unique, and create a virtual shapefile
    coord_pair = []
    for L in LandsatList_unique:
        values = L
# Create a virtual shapefile and make a geometry of the point coordinates
        x = L[0]
        y = L[1]
        shpMem = drvMemV.CreateDataSource('')
        shpMem_lyr = shpMem.CreateLayer('shpMem', lyr.GetSpatialRef(), geom_type=ogr.wkbPoint)
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x, y)
        featDef = shpMem_lyr.GetLayerDefn()
        feat = ogr.Feature(featDef)
        feat.SetGeometry(point)
        geom = feat.GetGeometryRef()
# Now buffer until we intersect with the shp-file
        geomBuff = geom.Buffer(buff)
        lyr.SetSpatialFilter(geomBuff)
        control = lyr.GetFeatureCount()
        while control == 0:
            geomBuff = geomBuff.Buffer(buff)
            lyr.SetSpatialFilter(geomBuff)
            nFeat = lyr.GetFeatureCount()
            if nFeat > 0:
                lyrFeat = lyr.GetNextFeature()
                pointID = lyrFeat.GetField("Id")
                lyr.ResetReading()
                control = 1
            else:
                control = control
        pair = [x, y, pointID]
        coord_pair.append(pair)
# Now merge the pointIDs to all entries in the database
    for L in LandsatList:
        values = L
        x = L[1]
        y = L[2]
        for c in coord_pair:
            xx = c[0]
            yy = c[1]
            id = c[2]
            if x == xx and y == yy:
                values.append(id)
        outList.append(values)
    return outList, header
def WriteOutput(packageList, outFileName):
    with open(outFileName, "w") as theFile:
        csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
        writer = csv.writer(theFile, dialect="custom")
        writer.writerow(packageList[0])
        packageList.pop(0)
        for package in packageList:
            for element in package:
                writer.writerow(element)
print("Correct locations to inputSHP")
correctedList = []
for values in valueList:
    print(valueList.index(values) + 1, "out of", len(valueList))
    correct = MergeLists(values, shp)
    correctedList.append(correct[0])
correctedList.insert(0, correct[1])#add the header-item, correct format first
print("Write Output")
WriteOutput(correctedList, output)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")