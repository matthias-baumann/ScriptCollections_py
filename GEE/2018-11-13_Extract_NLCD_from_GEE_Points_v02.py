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
root_folder = 'D:/_TEACHING/__Classes-Modules_HUB/MSc-M1_Quantitative-Methods/WS_2019-2020/Data/'
shp = ogr.Open(root_folder + "Locations_newALL.shp")
output = root_folder + "NLCD-data.csv"
# ####################################### FUNCTIONS ########################################################### #
def Retrieve_NLCD_fromGEE_Point(geometry):

    # Build an earth engine feature
    xCoord = geometry.GetX()
    yCoord = geometry.GetY()
    #pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}
    nlcd = ee.Image('USGS/NLCD/NLCD2016').select('landcover')

    pts = ee.Geometry.Point([xCoord, yCoord])
    # Now extract the values at the 30m-Level, add ID-value
    vals = nlcd.reduceRegion(geometry=pts, reducer=ee.Reducer.mean(), scale=30, maxPixels=1e13).getInfo()

    #vals = nlcd.reduceRegion(pts, 30).getInfo()

    return vals

# ####################################### COLLECT THE VALUES PER POINT ######################################## #
print("Extract values for points in SHP-file")
valueList = [["Point-ID", "NLCD16_value"]]
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
    try:
        vals = Retrieve_NLCD_fromGEE_Point(geometry=geom)
# Add to the header-line the Variable-Name Point-ID, and add it to each element as well
        val = [Pid, int(vals.get('landcover'))]
    except:
        val = [Pid, 9999]
# Append to output then get next feature
    valueList.append(val)
    feat = lyr.GetNextFeature()
# ##################################### WRITE OUTPUT ######################################################## #
print("Write output")
bt.baumiFM.WriteListToCSV(output, valueList, ",")
# ##################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")