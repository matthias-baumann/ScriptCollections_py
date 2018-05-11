# ####################################### SET TIME-COUNT ###################################################### ##
## EXTRACT LANDSAT TIME SERIES FOR POINTS                                                                       ##
## (c) Jared Stapp, UC Berkeley, July 2016                                                                      ##
## modified by Matthias Baumann, April 2017 to work in python                                                   ##
# ####################################### SET TIME-COUNT ###################################################### ##
import time
import ogr
import ee
ee.Initialize()
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
shp = ogr.Open("C:/Users/baumamat/Desktop/Bleyhl/shepherd_camp_locations/highres_camps_bg_pol_nounsure_GCS_WGS84_firstTwo.shp")
output = "C:/Users/baumamat/Desktop/Bleyhl/shepherd_camp_locations/highres_camps_bg_pol_nounsure_GCS_WGS84_firstTwo_values.csv"
# ####################################### SEARCH PARAMETERS ################################################### #
startDate = '2016-04-01'
endDate = '2017-04-25'
maxCloudPerc = 80
# ####################################### START PREPARING THE FEATURE COLLECTION ############################## #
print("Collecting features")
# Open SHP-File, get layer and iterate through features to convert into ee-FeatureCollection, make packages of 50
pointList = []
pointID_list = []
pointID_list.append(["u'id'", "u'longitude", "u'latitude'"])
lyr = shp.GetLayer()
coord = lyr.GetSpatialRef()
feat = lyr.GetNextFeature()
while feat:
# Translate OGR Feature into ee Feature
    geom = feat.GetGeometryRef()
    xCoord = geom.GetX()
    yCoord = geom.GetY()
    point = ee.Feature(ee.Geometry.Point([xCoord, yCoord]))
# Populate the pointID_list, so that we can merge the data later nicely
    id = feat.GetField("Id")
    Id_index = [id, xCoord, yCoord]
# Append to lists
    pointList.append(point)
    pointID_list.append(Id_index)
    feat = lyr.GetNextFeature()
# Convert list of features into feature collection
pts = ee.FeatureCollection(ee.List(pointList))
print("")
# ####################################### EXTRACT VALUES FROM COLLECTIONS ##################################### #
print("Extracting values")
# https://code.earthengine.google.com/datasets
BandsDict = {'L8': ee.List([1, 2, 3, 4, 5, 6, 8]),
             'L7_Tier1': ee.List([0, 1, 2, 3, 4, 7]),
             'L7': ee.List([0, 1, 2, 3, 4, 7, 9]),
             'L5': ee.List([0, 1, 2, 3, 4, 5, 7]),
             'L4': ee.List([0, 1, 2, 3, 4, 5, 7])}
print("Landsat 8")
#L8 = ee.ImageCollection('LANDSAT/LC8_SR'). \
L8 = ee.ImageCollection('LANDSAT/LC8_L1T_TOA_FMASK').\
    filterDate(startDate, endDate).\
    filter(ee.Filter.lt('CLOUD_COVER', maxCloudPerc)).\
    select(BandsDict.get('L8'))
print("Landsat 7")
#L7 = ee.ImageCollection('LANDSAT/LE7_L1T_TOA_FMASK').\
L7_Tier1 = ee.ImageCollection('LANDSAT/LE07/C01/T1_TOA').\
            filterDate(startDate, endDate).\
            filter(ee.Filter.lt('CLOUD_COVER', maxCloudPerc)).\
            select(BandsDict.get('L7_Tier1'))
vals_L7_Tier1 = L7_Tier1.getRegion(pts, 30, "epsg:4326").getInfo()
print("Landsat 5")
L5 = ee.ImageCollection('LANDSAT/LT5_L1T_TOA_FMASK').\
    filterDate(startDate, endDate).\
    filter(ee.Filter.lt('CLOUD_COVER', maxCloudPerc)).\
    select(BandsDict.get('L5'))
print("Landsat 4")
L4 = ee.ImageCollection('LANDSAT/LT4_L1T_TOA_FMASK').\
    filterDate(startDate, endDate).\
    filter(ee.Filter.lt('CLOUD_COVER', maxCloudPerc)).\
    select(BandsDict.get('L4'))
print("")
print("Merge to point IDs")
def MergeLists(IDlist, LandsatList, collection):
    if collection == "L7_Tier1":
        outList = []
        header = [IDlist[0], LandsatList[0]]
        outList.append(header)
        for ID in IDlist:
            id = ID[0]
            x = ID[1]
            y = ID[2]
            merge = 0
            i=1
            while merge == 0:
                item = LandsatList[i]
                xx = item[1]
                yy = item[2]
                if x == xx and y == yy:
                    out = [id, x, y, item[4], item[5], item[6], item[7], item[8], item[9]]
                    print(out)
                    outList.append(out)
                    merge = 1
                else:
                    i = i+1
    return outList


output = MergeLists(pointID_list, vals_L7_Tier1, "L7_Tier1")

for ot in output:
    print(ot)



# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")