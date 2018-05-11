# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import csv
import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
outFile = "C:/Users/baumamat/Desktop/SHP/Grow-to-APN_20170123.csv"
# ####################################### OPEN FILES, BUILD COORDINATE TRANSFORMATION ######################### #
grows = bt.baumiVT.CopyToMem("C:/Users/baumamat/Desktop/SHP/newgrowset.shp")
parcel = bt.baumiVT.CopyToMem("C:/Users/baumamat/Desktop/SHP/00_Parcel.shp")
growsLYR = grows.GetLayer()
parcelLYR = parcel.GetLayer()
tr = bt.baumiVT.CS_Transform(growsLYR,parcelLYR)
# ####################################### GET THE FIRST FEATURE OF THE ZONE-FILE, THEN LOOP ################### #
outList = []
header = ["GrowID", "jplants", "g_plants", "highslope", "chindist", "steeldist", "cohohabita", "tplants", "totalplant", "APN"]
outList.append(header)
grow_feat = growsLYR.GetNextFeature()
while grow_feat:
    ID = grow_feat.GetField("OBJECTID")
    print(ID)
# Append value
    vals = []
    vals.append(ID)
# Get first the attributes, append to 'vals'
    vals.append(grow_feat.GetField("jplants"))
    vals.append(grow_feat.GetField("g_plants"))
    vals.append(grow_feat.GetField("highslope"))
    vals.append(grow_feat.GetField("chindist"))
    vals.append(grow_feat.GetField("steeldist"))
    vals.append(grow_feat.GetField("cohohabita"))
    vals.append(grow_feat.GetField("tplants"))
    vals.append(grow_feat.GetField("totalplant"))
# Now get the APN, by creating a spatial filter
    geom = grow_feat.GetGeometryRef()
    geom_clone = geom.Clone()
    geom_clone.Transform(tr)
    parcelLYR.SetSpatialFilter(geom_clone)
    id = "NA"
# Check first if grow is in the APN extent
    if growsLYR.GetFeatureCount() > 0:
        apn = parcelLYR.GetNextFeature()
        while apn:
            id = apn.GetField("APN")
            apn = parcelLYR.GetNextFeature()
        parcelLYR.ResetReading()
    else:
        id = "NA"
    vals.append(id)
# Put vals to output list and get next feature
    outList.append(vals)
    grow_feat = growsLYR.GetNextFeature()
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