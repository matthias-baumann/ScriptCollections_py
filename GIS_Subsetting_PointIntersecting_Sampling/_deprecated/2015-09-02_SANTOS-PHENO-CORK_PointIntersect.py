# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time, datetime
import gdal
import ogr, osr
from gdalconst import *
import struct
import csv
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### HARD-CODED FOLDERS AND FILES ######################################## #
shape = "D:/Matthias/Projects-and-Publications/Projects_Collaborating_Active/SANTOS_Badger-Phenology/02_AllSites_Badger/badger_all_2005_2006_UniqueID_new.shp"
LandsatFolder = "O:/Santos_BadgerPhenology_Landsat_evi-create/"
outCSV = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Santos-etal_Phenology-Productivity/Analysis_ChangesPhenology/EVI_Badger-DS_20150916.csv"
# ####################################### PROCESSING ########################################################## #
# Get Scene paths
print("Get ScenePaths")
sceneList = [LandsatFolder + file for file in os.listdir(LandsatFolder)]
# Prepare top row for output table, that contains the rows
print("Prepare Variables, read out ID-Values")
EVIList = []
IDlist = ["SceneID", "FP", "Year", "DOY"]
ds_ogr = ogr.Open(shape, 1)
lyr = ds_ogr.GetLayer()
feat = lyr.GetNextFeature()
while feat:
    id = feat.GetField("Unique_ID")
    IDlist.append(int(id))
    feat = lyr.GetNextFeature()
lyr.ResetReading()
lyr = None
ds_ogr = None
EVIList.append(IDlist)
# Now loop through the scenes and extract values
print("Loop through scenes to extract spectral values")
for scene in sceneList:
    print(scene)
    sceneVals = []
# Assign paths to the two files of interest
    evi = [scene + "/" + file for file in os.listdir(scene) if file.find("evi") >= 0][0]
    cfmask = [scene + "/" + file for file in os.listdir(scene) if file.find("cfmask") >= 0][0]
# Get the formal infos --> SceneID, Footprint, Acquisition Year, Acquisition-DOY
    p = evi.rfind("/")
    sceneID = evi[p+1:p+22]
    FP = evi[p+4:p+10]
    yr = int(evi[p+10:p+14])
    doy = int(evi[p+14:p+17])
    sceneVals.append(sceneID)
    sceneVals.append(FP)
    sceneVals.append(yr)
    sceneVals.append(doy)
# Now extract the evi values, mask out on-the-fly based on cfmask-info
# Open the imagery, assess data type and define rule for the read-out of the struct variable
    evi_b = gdal.Open(evi, GA_ReadOnly)
    evi_rb = evi_b.GetRasterBand(1)
    types = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
    dataType = evi_rb.DataType
    for type in types:
        if type[0] == dataType:
            evi_dType = type[1]
    cfmask_b = gdal.Open(cfmask, GA_ReadOnly)
    cfmask_rb = cfmask_b.GetRasterBand(1)
    dataType = cfmask_rb.DataType
    for type in types:
        if type[0] == dataType:
            cfmask_dType = type[1]
# Get GeoTransform and CSS
    gt = evi_b.GetGeoTransform()
    pr = evi_b.GetProjection()

# Open the shp-File
    point_ogr = ogr.Open(shape, 1)
    lyr = point_ogr.GetLayer()
#  Build Coordinate Transformation
    target_SR = osr.SpatialReference()
    target_SR.ImportFromWkt(pr)
    source_SR = lyr.GetSpatialRef()
    coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
# Loop through features in point-layer and get the spectral values
    feat = lyr.GetNextFeature()
    while feat:
# Get the ID-attributes from the shapefile
        id = feat.GetField("Unique_ID")
# Build the geometry-object, do the geometric transformation
        geom = feat.GetGeometryRef()
        geom.Transform(coordTrans)
        mx, my = geom.GetX(), geom.GetY()
        px = int((mx - gt[0]) / gt[1])
        py = int((my - gt[3]) / gt[5])
# Now get the values from the two layers
        #try:
        structVar_cl = cfmask_b.ReadRaster(px,py,1,1)
        cloudVal = struct.unpack(cfmask_dType, structVar_cl)[0]
        #except:
            #cloudVal = -9999
# Check if cloudVal == 0 --> means, it is a clear-sky observation --> only then check for the other raster, otherwise set EVI=-0
        if cloudVal == 0:
            #try:
            structVar_evi = evi_b.ReadRaster(px,py,1,1)
            eviVal = struct.unpack(evi_dType, structVar_evi)[0]
            eviVal = eviVal / 10000
            #except:
                #eviVal = -9999
        else:
            eviVal = 0
# Attach value to output-list, go to next feature


        sceneVals.append(eviVal)
        feat = lyr.GetNextFeature()
# ResetReading, so that for the next raster-file the counting starts at 1 again
    lyr.ResetReading()
    EVIList.append(sceneVals)


# Write EVIList to output-csv
with open(outCSV, "w") as theFile:
    csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator = '\n')
    writer = csv.writer(theFile, dialect = "custom")
    for element in EVIList:
        writer.writerow(element)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")