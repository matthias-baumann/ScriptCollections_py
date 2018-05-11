# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import csv
import ogr, osr

import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FOLDER-PATHS ######################################################## #
grows = bt.baumiVT.CopyToMem("C:/Users/baumamat/Desktop/cannabis/matthias2.shp")
growID = "UniqueID"
addFields = ["hucid", "year", "county", "greenhouse", "growsize", "plants"]
parcel = bt.baumiVT.CopyToMem("C:/Users/baumamat/Desktop/cannabis/parcel (2017_11_13 16_42_19 UTC).shp")
parcelID = "APN"
outFile = "C:/Users/baumamat/Desktop/cannabis/allData.csv"
# ####################################### PROCESSING ########################################################## #
# Build outlist and header
outlist = []
header = ["UniqueID", "APN", "hucid", "county", "greenhouse", "growsize", "plants"]
outlist.append(header)
# Build coordinate transformation
growLYR = grows.GetLayer()
parcelLYR = parcel.GetLayer()
grow_SR = growLYR.GetSpatialRef()
parcel_SR = parcelLYR.GetSpatialRef()
coordTrans = osr.CoordinateTransformation(grow_SR, parcel_SR)
# Start looping over the features
feat = growLYR.GetNextFeature()
while feat:
    vals = []
# Get the id information
    id = feat.GetField(growID)
    print("Processing ID:", str(id))
    vals.append(id)
# Get the APN it is located in
    geom = feat.GetGeometryRef()
    geom.Transform(coordTrans)
    parcelLYR.SetSpatialFilter(geom)
    try:
        feat2 = parcelLYR.GetNextFeature()
        apn = feat2.GetField(parcelID)
    except:
        apn = "outside_parcels"
    parcelLYR.ResetReading()
    vals.append(apn)
# Get the other attributes
    for at in addFields:
        fieldVal = str(feat.GetField(at))
        vals.append(fieldVal)
# Attach values to outlist, get next feature
    outlist.append(vals)
    feat = growLYR.GetNextFeature()
# (5) WRITE OUTPUT
print("Write output")
with open(outFile, "w") as theFile:
    csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator = '\n')
    writer = csv.writer(theFile, dialect = "custom")
    for element in outlist:
        writer.writerow(element)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")