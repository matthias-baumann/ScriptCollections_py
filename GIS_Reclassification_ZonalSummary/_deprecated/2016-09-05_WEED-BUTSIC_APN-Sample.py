# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
from ZumbaTools._Raster_Tools import *

# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
drvV = ogr.GetDriverByName('ESRI Shapefile')
parcel = drvV.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/Mapping_publication/00_Parcel_sample.shp",1)
parcelLYR = parcel.GetLayer()
txt = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/Mapping_publication/apn_selection.txt"
# ####################################### GET THE INFO FROM THE TEXT FILE WHICH APN ARE SAMPLED ############### #
apn_list = []
txt_open = open(txt, "r")
for line in txt_open:
    line = line.replace("\n","")
    line = line.replace("'","")
    apn_list.append(int(line))
txt_open.close()
####################################### LOOP THROUGH PARCELS, CHECK IF APN IS IN LIST, ADD ATTRIBUTE ########## #
fieldDefn = ogr.FieldDefn('Sample2_YN', ogr.OFTInteger)
parcelLYR.CreateField(fieldDefn)
feat = parcelLYR.GetNextFeature()
while feat:
    ID = feat.GetField("APN")
    if ID.find("ohra") < 0 and ID.find("h") < 0 and ID.find("r") < 0 and ID.find("a") < 0 and ID.find("R") < 0 and ID.find("H") < 0 and ID.find("p") < 0:
        ID = int(ID)
        if ID in apn_list:
            print(ID)
            feat.SetField('Sample2_YN', 1)
            parcelLYR.SetFeature(feat)
            feat = parcelLYR.GetNextFeature()
        else:
            feat = parcelLYR.GetNextFeature()
    else:
        feat = parcelLYR.GetNextFeature()
parcelLYR.ResetReading()
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")