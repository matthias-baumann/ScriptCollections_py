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
outFile = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/baumann-kuemmerle_Warfare-LandUseChange/ConflictsPerCountry_All_20160527.csv"
# ####################################### OPEN FILES, BUILD COORDINATE TRANSFORMATION ######################### #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
country = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/baumann-kuemmerle_Warfare-LandUseChange/LiteratureSearch/ESRI_Countries.shp"),'')
conflict = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/baumann-kuemmerle_Warfare-LandUseChange/Anthromes_vs_Conflict/UCDP-PRIO_ArmedConflictDataset/UCDP-PRIO_GeoreferencedEventDatasets_1946-2014_ged40.shp"),'')
countryfield = "CNTRY_NAME"
countryLYR = country.GetLayer()
conflictLYR = conflict.GetLayer()
# Build the coordinate transformation
countryLYR_SR = countryLYR.GetSpatialRef()
conflictLYR_SR = conflictLYR.GetSpatialRef()
transform = osr.CoordinateTransformation(countryLYR_SR, conflictLYR_SR)
# ####################################### CREATE THE OUTPUT-LISTS, ADD VARIABLE NAMES FIRST ################# #
outList = []
header = ["Country", "Nr_Events"]
outList.append(header)
# ####################################### LOOP THROUGH PARCELS ############################################## #
countryFeat = countryLYR.GetNextFeature()
while countryFeat:
# Get APN identifier, check if in skip-feature
    ctr = countryFeat.GetField(countryfield)
    print("Processing APN " + str(ctr))
    # Append value
    vals = []
    vals.append(ctr)
    # Get the Geometry, make clone
    geom = countryFeat.GetGeometryRef()
    geom_zone = geom.Clone()
    # Count first the number of plants in the geometry itself which we later subtract from the other sums
    geom_zone.Transform(transform)
    conflictLYR.SetSpatialFilter(geom_zone)
    nr_events = conflictLYR.GetFeatureCount()
    vals.append(nr_events)
    # Add to output-list, then switch to next feature
    outList.append(vals)
    countryFeat = countryLYR.GetNextFeature()
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