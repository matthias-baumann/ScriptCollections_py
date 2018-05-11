# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, osr
from ZumbaTools._Vector_Tools import *
from ZumbaTools._Raster_Tools import *
from gdalconst import *
import gdal
import numpy as np
import csv
# ############################################################################################################# #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
outFile = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/Mapping_publication/Watersheds_MapSummaries_20160819.csv"
# ############################################################################################################# #
# ####################################### OPEN ALL FILES THAT WE WILL SUMMARIZE ############################### #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
drvMemV = ogr.GetDriverByName('Memory')
print("Load files to memory")
watershed = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/Mapping_publication/Watersheds.shp"),'')
watershedLYR = watershed.GetLayer()
parcel = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/Mapping_publication/00_Parcel_sample.shp"),'')
parcelLYR = parcel.GetLayer()
grows = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/Mapping_publication/Grows.shp"),'')
growsLYR = grows.GetLayer()

# ####################################### ADD FIELDS TO OUTPUT-LAYER ########################################## #
outList = []
header = ["Watershed_ID", "Av_ParcelSize_km2", "Nr_Grows", "Av_GrowSize"]
outList.append(header)
# ####################################### BUILD THE COORDINATE TRANSFORMATIONS ################################ #
print("Build coordinate transformation")
WS_grows_tr = CoordinateTransform_Vector(watershedLYR, growsLYR)
WS_parcel_tr = CoordinateTransform_Vector(watershedLYR, parcelLYR)
# ####################################### GET THE FIRST FEATURE OF THE ZONE-FILE, THEN LOOP ################### #
WS_feat = watershedLYR.GetNextFeature()
while WS_feat:
    vals = []
# Get unique identifier, then add it to the outvals
    ID = WS_feat.GetField("OBJECTID")
    print(ID)
    vals.append(ID)
# Get the Geometry of the feature
    geom = WS_feat.GetGeometryRef()
# Get Average size of Parcel
    # Create geometry-clone for the evaluation of the grows-layer, do coordinate transform
    geom_zone = geom.Clone()
    geom_zone.Transform(WS_parcel_tr)
    # Set spatial filter, get the summaries
    parcelLYR.SetSpatialFilter(geom_zone)
    nr_parcels = parcelLYR.GetFeatureCount()
    parcel_feat = parcelLYR.GetNextFeature()
    area_km = 0
    while parcel_feat:
        size = parcel_feat.GetField("Area_km2")
        area_km = area_km + size
        parcel_feat = parcelLYR.GetNextFeature()
    parcelLYR.ResetReading()
    averageSize = area_km / nr_parcels
    vals.append(averageSize)
# Get the # of grows and average grow size
    geom_zone = geom.Clone()
    geom_zone.Transform(WS_grows_tr)
    # Set spatial filter
    growsLYR.SetSpatialFilter(geom_zone)
    nr_grows = growsLYR.GetFeatureCount()
    grows_feat = growsLYR.GetNextFeature()
    nr_plants = 0
    while grows_feat:
        plants = grows_feat.GetField("n_plants")
        nr_plants = nr_plants + plants
        grows_feat = growsLYR.GetNextFeature()
    growsLYR.ResetReading()
    vals.append(nr_grows)
    if nr_plants > 0:
        average_grow = nr_plants / nr_grows
    else:
        average_grow = 0
    vals.append(average_grow)
# Add vals-list to outList, then go to next feature
    outList.append(vals)
    WS_feat = watershedLYR.GetNextFeature()
# (14) Write output
print("Write output")
with open(outFile, "w") as theFile:
    csv.register_dialect("custom", delimiter = ";", skipinitialspace = True, lineterminator = '\n')
    writer = csv.writer(theFile, dialect = "custom")
    for element in outList:
        writer.writerow(element)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")