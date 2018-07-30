# ####################################### SET TIME-COUNT ###################################################### ##
## EXTRACT LANDSAT TIME SERIES FOR POINTS (Version 1.1)                                                         ##
## (c) Matthias Baumann, March 2018                                                                             ##
## Humboldt-University Berlin                                                                                   ##
# ####################################### IMPORT MODULES, START EARTH-ENGINE ################################## ##
import time
import baumiTools as bt
import ogr, osr
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
shp = ogr.Open("D:/Projects-and-Publications/Publications/Publications-submitted-in-review/2018_butsic_Marihuana-California/Data/allgrows11_18.shp")
output = "D:/Projects-and-Publications/Publications/Publications-submitted-in-review/2018_butsic_Marihuana-California/allgrows11_18_NLCD.csv"
field = "OBJECTID_1"
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
#nlcd_all = ee.ImageCollection(nlcd01.merge(nlcd06).merge(nlcd11))
nlcd_all = nlcd01.addBands(nlcd06).addBands(nlcd11)
# Now iterate through features
#while feat:
for feat in tqdm(lyr):
# Extract ID-Info from SHP-file and other informations
    Pid = feat.GetField(field)
#    print("Processing Point ID " + str(Pid))
# Now get the geometry and do a coordinate-transformation, then build EE-Feature
    geom = feat.GetGeometryRef()
    geom.Transform(transform)
    xCoord = geom.GetX()
    yCoord = geom.GetY()
    #pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}
    pts = ee.Geometry.Point([xCoord, yCoord])
# Now extract the values at the 30m-Level, add ID-value
    vals = nlcd_all.reduceRegion(geometry=pts, reducer=ee.Reducer.mean(), scale=30, maxPixels=1e13).getInfo()
    vals = [int(x) for x in list(vals.values())]
    vals.insert(0, Pid)
    valueList.append(vals)
# Get Next Feature
    #feat = lyr.GetNextFeature()
# Write output
bt.baumiFM.WriteListToCSV(output, valueList, ",")
# ##################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")