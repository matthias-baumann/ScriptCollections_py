# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, osr
from ZumbaTools._Vector_Tools import *
from ZumbaTools._Raster_Tools import *
import csv
import gdal
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
outFile = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/SummaryDataset_V03_THP_20160428.csv"
skipIDs = ["05315125", "51313108", "road"]
# ####################################### OPEN FILES, BUILD COORDINATE TRANSFORMATION ######################### #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
parcel = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/00_Parcel.shp"),'')
THP = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/12_TimberHarvestPlan_PlanDissolve.shp"),'')
THPfield = "THP_YEAR"
#ocean = gdal.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/DistanceToOcean_5m.tif")
parcelLYR = parcel.GetLayer()
thpLYR = THP.GetLayer()
# Build the coordinate transformation
thpLYR_SR = thpLYR.GetSpatialRef()
parcelLYR_SR = parcelLYR.GetSpatialRef()
transform_THP = osr.CoordinateTransformation(parcelLYR_SR, thpLYR_SR)
# ####################################### CREATE THE OUTPUT-LISTS, ADD VARIABLE NAMES FIRST ################# #
outList = []
header = ["APN"]
thpFeat = thpLYR.GetNextFeature()
while thpFeat:
    name = "y_" + str(thpFeat.GetField(THPfield))
    header.append(name)
    thpFeat = thpLYR.GetNextFeature()
thpLYR.ResetReading()
outList.append(header)
# ####################################### LOOP THROUGH PARCELS ############################################## #
parcelFeat = parcelLYR.GetNextFeature()
while parcelFeat:
# Get APN identifier, check if in skip-feature
    ID = parcelFeat.GetField("APN")
    if not ID in skipIDs:
        print("Processing APN " + str(ID))
        vals = []
        vals.append(ID)
# Get the Geometry of the feature, transform to THP-coordinate systems
        geomParcel = parcelFeat.GetGeometryRef()
        geomParcel.Transform(transform_THP)
# Now loop through the features of the THP layer
        thpFeat = thpLYR.GetNextFeature()
        while thpFeat:
            geomTHP = thpFeat.GetGeometryRef()
            intersection = geomParcel.Intersection(geomTHP)
            if intersection.GetArea() == 0:
                vals.append(0)
            else:
                parcelArea = geomParcel.GetArea()
                intersectArea = intersection.GetArea()
                percentage = intersectArea / parcelArea
# Append percentage value, add value to vals
                vals.append(percentage)
            thpFeat = thpLYR.GetNextFeature()
# Append vals to outlist, reset reading of THP-Layer
        outList.append(vals)
        thpLYR.ResetReading()
        parcelFeat = parcelLYR.GetNextFeature()
    else:
        parcelFeat = parcelLYR.GetNextFeature()

# ####################################### WRITE OUTPUT ################################################## #
print("Write output")
with open(outFile, "w") as theFile:
    csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator = '\n')
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