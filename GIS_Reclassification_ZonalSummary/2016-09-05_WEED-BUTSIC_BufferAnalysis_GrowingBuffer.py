# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, osr
from ZumbaTools._Vector_Tools import *
import csv

# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
outFile = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/SummaryDataset_V06_Parcel_DistanceToNextGrow_m_20160905.csv"
# ####################################### OPEN FILES, BUILD COORDINATE TRANSFORMATION ######################### #
#drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
grows = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/01_Grows.shp"),'')
parcel = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/00_Parcel.shp"),'')
growsLYR = grows.GetLayer()
parcelLYR = parcel.GetLayer()
skipList = ["05315125"]
# ####################################### BUILD COORDINATE TRANSFORMATION ##################################### #
outPR = growsLYR.GetSpatialRef()
inPR = parcelLYR.GetSpatialRef()
transform = osr.CoordinateTransformation(inPR, outPR)
# ####################################### BUILD HEADER FILE ################################################### #
outList = []
header = ["APN", "m_to_NextGrow"]
outList.append(header)
# ####################################### LOOP THROUGH FEATURES ############################################### #
zone_feat = parcelLYR.GetNextFeature()
while zone_feat:
#### Check if object in skipList
    ID = zone_feat.GetField("APN")
    if not ID in skipList:
        print("Processing APN " + str(ID))
    # Append value
        vals = []
        vals.append(ID)
    # Get the Geometry, make clone
        geom = zone_feat.GetGeometryRef()
        geom.Transform(transform)
    # Get the number of grows that are inside the parcel
        growsLYR.SetSpatialFilter(geom)
        nrGrow = growsLYR.GetFeatureCount()
    # Set control variable which will be changed to one if nr_points_new is larger than nrGrow
        control = 0
        buff = 30 # --> make buffer rings of 10m (30feet) and increase until grows are more than the intial
        while control == 0:
            geomBuff = geom.Buffer(buff)
            growsLYR.SetSpatialFilter(geomBuff)
            nrGrowN = growsLYR.GetFeatureCount()
            if nrGrowN > nrGrow:
                control = 1
            else:
                control = control
                buff = buff + 30
        vals.append(buff)
    # Add the values to the output-list, go to next feature
        outList.append(vals)
        zone_feat = parcelLYR.GetNextFeature()
    else:
        zone_feat = parcelLYR.GetNextFeature()
# Write output-file
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