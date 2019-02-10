# ####################################### SET TIME-COUNT ###################################################### ##
## EXTRACT LANDSAT TIME SERIES FOR POINTS (Version 1.1)                                                         ##
## (c) Matthias Baumann, March 2018                                                                             ##
## Humboldt-University Berlin                                                                                   ##
# ####################################### IMPORT MODULES, START EARTH-ENGINE ################################## ##
import time
import baumiTools as bt
import ogr
import csv
import ee
from tqdm import tqdm
ee.Initialize()
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
root_folder = 'D:/Teaching/WS_2018-2019/MSc-M1_Quantitative-methods/Data/'
shp = ogr.Open(root_folder + "Locations.shp")
output = root_folder + "MODIS/MODIS_EVI-data.csv"
# ####################################### SEARCH PARAMETERS ################################################### #
startDate = '2000-01-01'
endDate = '2018-10-31'
# ####################################### FUNCTIONS ########################################################### #
def Retrieve_EVI_Point(geometry, startDate, endDate):
    # startDate & endDate has to be in the format "2018-01-01"
    # --> https://mygeoblog.com/2017/09/08/modis-cloud-masking/
    def getQABit(image, start, end, newName):
        pattern = 0
        for i in range(start, end + 1):
            pattern += 2 ** i
        return image.select([0], [newName]).bitwiseAnd(pattern).rightShift(start)
    def maskQuality(image):
        # Select the QA band.
        QA = image.select('QA')
        # Get the internal_cloud_algorithm_flag bit.
        goodData = getQABit(QA, 0, 0, 'clear_sky')
        # Return an image masking out cloudy areas.
        return image.updateMask(goodData.eq(1))

    # Build an earth engine feature
    xCoord = geometry.GetX()
    yCoord = geometry.GetY()
    pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}
    # Now extract the individual data from the collections based on the definitions above
    # MODIS EVI Terra
    mod_EVI = ee.ImageCollection('MODIS/006/MOD13Q1'). \
        filterDate(startDate, endDate). \
        select('EVI')#.\
        #map(maskQuality)
    # MODIS EVI aqua
    myd_EVI = ee.ImageCollection('MODIS/006/MYD13Q1'). \
        filterDate(startDate, endDate). \
        select('EVI')#.\
        #map(maskQuality)
    # Merge
    values_all = ee.ImageCollection(mod_EVI.merge(myd_EVI)).getRegion(pts, 30).getInfo()
    return values_all
# ####################################### COLLECT THE VALUES PER POINT ######################################## #
print("Extract values for points in SHP-file")
valueList = []
lyr = shp.GetLayer()
coord = lyr.GetSpatialRef()
nFeat = lyr.GetFeatureCount()
feat = lyr.GetNextFeature()
while feat:
#for feat in tqdm(lyr):
# Extract ID-Info from SHP-file and other informations
    Pid = feat.GetField("Id")
    print("Processing Point ID " + str(Pid))
# Now get the geometry and do stuff
    geom = feat.GetGeometryRef()
# Now extract the individual data from the collections based on the definitions above
    vals = Retrieve_EVI_Point(geometry=geom, startDate=startDate, endDate=endDate)
# Add to the header-line the Variable-Name Point-ID, and add it to each element as well
    vals[0].append("Point-ID")
    for i in range(1,len(vals)):
        vals[i].append(Pid)
# Remove right away the masked values, and some remnants from the sceneID
    val_reduced = []
    for val in vals:
        if not None in val:
            sceneID = val[0]
            sceneID = sceneID[2:]
            val[0] = sceneID
            val_reduced.append(val)
# Append to output then get next feature
    valueList.append(val_reduced)
    feat = lyr.GetNextFeature()
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