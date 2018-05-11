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
folder = "G:/Baumann/_ANALYSES/Extract_Tiles_GEE/"
shp = ogr.Open(folder + "TestTiles_WGS84.shp")
# ####################################### SEARCH PARAMETERS ################################################### #
startYear = '2016-12-10'
endYear = '2016-12-31'
# ####################################### FUNCTIONS ########################################################### #
# --> https://github.com/gee-community/gee_tools
def getQABit(image, start, end, newName):
    pattern = 0
    for i in range(start, end + 1):
        pattern += 2 ** i
    return image.select([0], [newName]).bitwiseAnd(pattern).rightShift(start)
def maskQuality(image):
    # Select the QA band.
    QA = image.select('pixel_qa')
    # Get the internal_cloud_algorithm_flag bit.
    shadow = getQABit(QA, 3, 3, 'cloud_shadow')
    cloud = getQABit(QA, 5, 5, 'cloud')
    water = getQABit(QA, 2, 2, 'water')
    #  var cloud_confidence = getQABits(QA,6,7,  'cloud_confidence')
    # cirrus = getQABit(QA, 9, 9, 'cirrus')
    # Return an image masking out cloudy areas.
    return image.updateMask(cloud.eq(0)).updateMask(shadow.eq(0).updateMask(water.eq(0)))
# ####################################### START PREPARING THE FEATURE COLLECTION ############################## #
print("Extract values for points in SHP-file")
tupel = []
lyr = shp.GetLayer()
coord = lyr.GetSpatialRef()
nFeat = lyr.GetFeatureCount()
count = 1
# Get Point-ID from shapefile
feat = lyr.GetNextFeature()
while feat:
# Check if the value is usable
    check = feat.GetField("Active_YN")
    if check == 0:
        feat = lyr.GetNextFeature()
    else:
# Extract ID-Info from SHP-file and other informations
        tileID = feat.GetField("TileIndex")
        print("Processing Tile " + tileID)
    # Now get the geometry and do stuff
        geom = feat.GetGeometryRef()
        env = geom.GetEnvelope() # Get Envelope returns a tuple (minX, maxX, minY, maxY)
        UL = [env[0], env[3]]
        UR = [env[1], env[3]]
        LR = [env[1], env[2]]
        LL = [env[0], env[2]]
    # Build an earth engine feature
        poly = ee.Geometry.Rectangle(coords = [UL, LR])#, LR, LL])

    # Define the Landsat band names
        l8bands = ee.List(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa'])
        l8band_names = ee.List(['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa'])
        l457bands = ee.List(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'])
        l457band_names = ee.List(['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa'])
    # Get the image information
        def setProperty(image):
            #dict = image.reduceRegion(ee.Reducer.mean(), poly)
            dict = image.reduceRegion(ee.Reducer.median(), poly)
            return image.set(dict)

    # Test --> only with Landsat 8
        coll_L8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR'). \
        filterDate(startYear, endYear). \
        select(l8bands, l8band_names). \
        filterBounds(poly). \
        map(maskQuality)

        withMean = coll_L8.map(setProperty)


        meanb2 = withMean.aggregate_array('B5').getInfo()


        print(meanb2)
        exit(0)






print("")
# ####################################### EXTRACT VALUES FROM COLLECTIONS ##################################### #
print("Extracting values")
# Function for better application
def GetData(points, collection, startDate, endDate, maxCloudPerc, BandsDict_short):

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