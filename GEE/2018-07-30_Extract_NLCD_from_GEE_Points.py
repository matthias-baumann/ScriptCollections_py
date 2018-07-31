# ####################################### SET TIME-COUNT ###################################################### ##
## EXTRACT NLCD-data at point locations   (Version 1.1)                                                         ##
## (c) Matthias Baumann, March 2018                                                                             ##
## Humboldt-University Berlin                                                                                   ##
# ####################################### IMPORT MODULES, START EARTH-ENGINE ################################## ##
import time
import baumiTools as bt
import ogr, osr
import os
import pandas as pd
import ee
#ee.Initialize()
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
shp = bt.baumiVT.CopyToMem("G:/Baumann/allgrows11_18.shp")
tempFolder = "G:/Baumann/temp/"
output = "G:/Baumann/allgrows11_18_NLCD.csv"
field = "OBJECTID_1"
chunkSize = 100
# ####################################### COLLECT THE VALUES PER POINT ######################################## #
# Generate packs of 100 points
lyr = shp.GetLayer()
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
idLists = list(chunks(range(1, lyr.GetFeatureCount()), chunkSize))
# Create coordinate transformation
source_SR = lyr.GetSpatialRef()
target_SR = osr.SpatialReference()
target_SR.ImportFromEPSG(4326)
transform = osr.CoordinateTransformation(source_SR, target_SR)
# loop over each pack of the chunks and extract the points from GEE
for l in idLists:
    min = l[0]
    try:
        max = l[chunkSize-1]
    except:
        max = lyr.GetFeatureCount()
    min_str = "{:05d}".format(min)
    max_str = "{:05d}".format(max)
# Check, if the shapefile with these point values already exists.
    tempFileName = tempFolder + min_str + "_" + max_str + ".csv"
    check = os.path.exists(tempFileName)
    while check == False:
        print("Extract values for points", min_str, "to", max_str)
        # Create a attribute filter to the shapefile
        filterString = "OBJECTID_1 >= " + min_str + " AND OBJECTID_1 <= " + max_str
        lyr.SetAttributeFilter(filterString)
        try:
            # Initiate the output
            valueList = [["OBJECTID_1", "NLCD_2001", "NLCD_2006", "NLCD_2011"]]
            # Build the image collection
            ee.Initialize()
            nlcd01 = ee.Image('USGS/NLCD/NLCD2001').select('landcover')
            nlcd06 = ee.Image('USGS/NLCD/NLCD2006').select('landcover')
            nlcd11 = ee.Image('USGS/NLCD/NLCD2011').select('landcover')
            nlcd_all = nlcd01.addBands(nlcd06).addBands(nlcd11)
            # Loop through the features
            feat = lyr.GetNextFeature()
            while feat:
            # Extract ID-Info from SHP-file and other informations
                Pid = feat.GetField(field)
                #print("Processing Point ID " + str(Pid))
            # Now get the geometry and do a coordinate-transformation, then build EE-Feature
                geom = feat.GetGeometryRef()
                geom.Transform(transform)
                xCoord = geom.GetX()
                yCoord = geom.GetY()
                pts = ee.Geometry.Point([xCoord, yCoord])
            # Now extract the values at the 30m-Level, add ID-value
                vals = nlcd_all.reduceRegion(geometry=pts, reducer=ee.Reducer.mean(), scale=30, maxPixels=1e13).getInfo()
                vals = [int(x) for x in list(vals.values())]
                vals.insert(0, Pid)
                valueList.append(vals)
            # Get Next Feature
                feat = lyr.GetNextFeature()
        # Write output
            bt.baumiFM.WriteListToCSV(tempFileName, valueList, ",")
            check = True
        except:
            print("--> GEE timed out, waiting 3min before restarting...")
            print("   --> ", time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()))
            time.sleep(180)
            check = check
# Merge the individual files
appended_data = []
for infile in bt.baumiFM.GetFilesInFolderWithEnding(tempFolder, ".csv", fullPath = True):
    data = pd.read_csv(infile)
    # store DataFrame in list
    appended_data.append(data)
# see pd.concat documentation for more info
appended_data = pd.concat(appended_data, axis=0)
# write DataFrame to an excel sheet
appended_data.to_csv(output, index=False)

# ##################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")