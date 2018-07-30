# ####################################### SET TIME-COUNT ###################################################### ##
## EXTRACT LANDSAT TIME SERIES FOR POINTS (Version 1.1)                                                         ##
## (c) Matthias Baumann, March 2018                                                                             ##
## Humboldt-University Berlin                                                                                   ##
# ####################################### IMPORT MODULES, START EARTH-ENGINE ################################## ##
import time
import baumiTools as bt
import ogr
exit(0)
import csv
import ee
from tqdm import tqdm
ee.Initialize()
exit(0)
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
shp = ogr.Open("D:/Projects-and-Publications/Publications/Publications-submitted-in-review/2018_butsic_Marihuana-California/allgrows11_18.shp")
output = "D:/Projects-and-Publications/Publications/Publications-submitted-in-review/2018_butsic_Marihuana-California/allgrows11_18_NLCD.csv"
field = "OBJECTID_1"
# ####################################### FUNCTIONS ########################################################### #
def Retrieve_SR01_fromGEE_Point(geometry, startDate, endDate):
    # startDate & endDate has to be in the format "2018-01-01"
    # Coordinate system has to be be WGS84 (EPSG:4326)
    # Material for masking
    # --> https://gis.stackexchange.com/questions/274048/apply-cloud-mask-to-landsat-imagery-in-google-earth-engine-python-api
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
        water = getQABit(QA, 2, 2,'water')
        #  var cloud_confidence = getQABits(QA,6,7,  'cloud_confidence')
        #cirrus = getQABit(QA, 9, 9, 'cirrus')
        # Return an image masking out cloudy areas.
        return image.updateMask(cloud.eq(0)).updateMask(shadow.eq(0).updateMask(water.eq(0)))

    # Build an earth engine feature
    xCoord = geometry.GetX()
    yCoord = geometry.GetY()
    pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}
    # Now extract the individual data from the collections based on the definitions above
    # Define the band names that we want to extract
    # l8bands = ee.List(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B1', 'B10', 'B11', 'pixel_qa'])
    # l8band_names = ee.List(['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'UB', 'T1', 'T2','pixel_qa'])
    l8bands = ee.List(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa'])
    l8band_names = ee.List(['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa'])
    l457bands = ee.List(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'])
    l457band_names = ee.List(['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa'])
    # Landsat 8
    coll_L8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR'). \
        filterDate(startDate, endDate). \
        select(l8bands, l8band_names). \
        map(maskQuality)
    # Landsat 7
    coll_L7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR'). \
        filterDate(startDate, endDate). \
        select(l457bands, l457band_names). \
        map(maskQuality)
    # Landsat 5
    coll_L5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR'). \
        filterDate(startDate, endDate). \
        select(l457bands, l457band_names). \
        map(maskQuality)
    # Landsat 4
    coll_L4 = ee.ImageCollection('LANDSAT/LT04/C01/T1_SR'). \
        filterDate(startDate, endDate). \
        select(l457bands, l457band_names). \
        map(maskQuality)
    # Merge
    values_all = ee.ImageCollection(coll_L4.merge(coll_L5).merge(coll_L7).merge(coll_L8)).getRegion(pts, 30).getInfo()
    return values_all
# ####################################### COLLECT THE VALUES PER POINT ######################################## #
# Open the shapefile, iitiate the output
print("Extract values for points in SHP-file")
valueList = [["OBJECTID_1", "NLCD_2001", "NLCD_2006", "NLCD_2011"]]
lyr = shp.GetLayer()
coord = lyr.GetSpatialRef()
nFeat = lyr.GetFeatureCount()
feat = lyr.GetNextFeature()
# Build the coordinate transformation
source_SR = lyr.GetSpatialRef()
target_SR = osr.SpatialReference()
target_SR.ImportFromEPSG(4326)
transform = osr.CoordinateTransformation(source_SR, target_SR)
# Build the image collection
nlcd01 = ee.Image('USGS/NLCD/NLCD2001').select('landcover')
nlcd06 = ee.Image('USGS/NLCD/NLCD2006').select('landcover')
nlcd11 = ee.Image('USGS/NLCD/NLCD2011').select('landcover')
nlcd_all = ee.ImageCollection(nlcd01.merge(nlcd06).merge(nlcd11))
# Now iterate through features
while feat:
#for feat in tqdm(lyr):
# Extract ID-Info from SHP-file and other informations
    Pid = feat.GetField("POINT_ID")
    #print("Processing Point ID " + str(Pid))
# Now get the geometry and do a coordinate-transformation, then build EE-Feature
    geom = feat.GetGeometryRef()
    geom.Transform(transform)
    xCoord = geom.GetX()
    yCoord = geom.GetY()
    pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}
# Now extract the values at the 30m-Level
    values = nlcd_all.getRegion(pts, 30).getInfo()
    print(values)
    exit(0)

# Now extract the individual data from the collections based on the definitions above
    vals = Retrieve_SR01_fromGEE_Point(geometry=geom, startDate=startDate, endDate=endDate)
# Add to the header-line the Variable-Name Point-ID, and add it to each element as well
    vals[0].append("Point-ID")
    for i in range(1,len(vals)):
        vals[i].append(Pid)
# Remove right away the masked values, and some remnants from the sceneID
    val_reduced = []
    for val in vals:
        if not None in val:
            sceneID = val[0]
            p1 = sceneID.find("L")
            sceneID = sceneID[p1:]
            val[0] = sceneID
            val_reduced.append(val)
# Append to output then get next feature
    valueList.append(val_reduced)
    #feat = lyr.GetNextFeature()
# ##################################### WRITE OUTPUT ######################################################## #
print("Write output")
with open(output, "w") as theFile:
    csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
    writer = csv.writer(theFile, dialect="custom")
    # Write the complete set of values (incl. the header) of the first entry
    for element in valueList[0]:
        writer.writerow(element)
    valueList.pop(0)
    # Now write the remaining entries, always pop the header
    for element in valueList:
        element.pop(0)
        for row in element:
            writer.writerow(row)
# ##################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")