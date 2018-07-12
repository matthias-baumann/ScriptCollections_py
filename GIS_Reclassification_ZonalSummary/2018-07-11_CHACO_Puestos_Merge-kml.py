# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal, ogr, osr
import numpy as np
import baumiTools as bt
from tqdm import tqdm
import subprocess
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES #################################### #
rootFolder = "L:/_SHARED_DATA/_PUESTO_DATA/"
outfile = rootFolder + "_Puestos_ALL_cleaned.shp"
drvKML = ogr.GetDriverByName('KML')
drvMemV = ogr.GetDriverByName('Memory')
# ####################################### PROCESSING ########################################################## #
# (1) CREATE THE OUTPUT SHAPEFILE
outSHP = drvMemV.CreateDataSource('')
spatialRef = osr.SpatialReference()
spatialRef.ImportFromEPSG(4326)
outLYR = outSHP.CreateLayer('outSHP', spatialRef, geom_type=ogr.wkbPoint)
outLYR.CreateField(ogr.FieldDefn("UID", ogr.OFTInteger))
outLYR.CreateField(ogr.FieldDefn("PersonID", ogr.OFTString))
outLYR.CreateField(ogr.FieldDefn("Person", ogr.OFTString))
outLYR.CreateField(ogr.FieldDefn("Year01", ogr.OFTInteger))
outLYR.CreateField(ogr.FieldDefn("Year02", ogr.OFTInteger))
outLYR.CreateField(ogr.FieldDefn("Security", ogr.OFTString))
outLYR.CreateField(ogr.FieldDefn("FullInfo", ogr.OFTString))
outLYR.CreateField(ogr.FieldDefn("Keep_yn", ogr.OFTInteger))

# (2) LOOP OVER THE KML-FILES AND POPULATE THE SHAPEFILE -->
def ExtractXML(string):
    # Find the roung string
    #print(string)
    p1 = string.find("<td>PopupInfo</td> <td>")
    info = string[p1:p1+50]
    try:
        # Get the more detailed info
        p1 = info.rfind(" <td>")
        p2 = info.rfind("</td> </tr>")
        info = info[p1+5:p2]
        # now go stp by step through the string
        yr01 = int(info[:4])
        yr02 = int(info[5:9])
        sec = info[10:11]
    except:
        yr01 = 0
        yr02 = 0
        sec = "nan"
        info = "nan"
    return yr01, yr02, sec, info
counter = 1
# (2-1) Alfredo
print("Alfredo")
arm = drvKML.Open(rootFolder + "ARM/puestos_ARM_21122017_all_fix1_dissolvedByMB.kml")
arm_lyr = arm.GetLayer()
feat = arm_lyr.GetNextFeature()
while feat:
# Build the feature from the geometry
    geom = feat.GetGeometryRef()
    featDef = outLYR.GetLayerDefn()
    featOut = ogr.Feature(featDef)
    featOut.SetGeometry(geom)
# Now set the attributes in the feature from the first attribute in the kml
    featOut.SetField('UID', counter)
    name = feat.GetField('Name')
    featOut.SetField('PersonID', name)
    featOut.SetField('Person', "Alfredo")
# extract all the other info from the xml-string
    yr01, yr02, sec, full = ExtractXML(feat.GetField("Description"))
    featOut.SetField('Year01', yr01)
    featOut.SetField('Year02', yr02)
    featOut.SetField('Security', sec)
    featOut.SetField('FullInfo', full)
    featOut.SetField('Keep_yn', 1)
# Create the feature, get the next feature, increase count
    outLYR.CreateFeature(featOut)
    counter += 1
    feat = arm_lyr.GetNextFeature()

# (2-2) Asun
print("Asun")
asp = drvKML.Open(rootFolder + "ASP/ASP_20170830_1748_dissolveMB_clean.kml")
asp_lyr = asp.GetLayer()
feat = asp_lyr.GetNextFeature()
while feat:
# Build the feature from the geometry
    geom = feat.GetGeometryRef()
    featDef = outLYR.GetLayerDefn()
    featOut = ogr.Feature(featDef)
    featOut.SetGeometry(geom)
# Now set the attributes in the feature from the first attribute in the kml
    featOut.SetField('UID', counter)
    name = feat.GetField('Name')
    featOut.SetField('PersonID', name)
    featOut.SetField('Person', "Asun")
# extract all the other info from the xml-string
    yr01, yr02, sec, full = ExtractXML(feat.GetField("Description"))
    featOut.SetField('Year01', yr01)
    featOut.SetField('Year02', yr02)
    featOut.SetField('Security', sec)
    featOut.SetField('FullInfo', full)
    featOut.SetField('Keep_yn', 1)
# Create the feature, get the next feature, increase count
    outLYR.CreateFeature(featOut)
    counter += 1
    feat = asp_lyr.GetNextFeature()

# (2-3) Christian
print("Christian")
cl = drvKML.Open(rootFolder + "CL/puestos_CL_AllLocations_dissolveMB.kml")
cl_lyr = cl.GetLayer()
feat = cl_lyr.GetNextFeature()
while feat:
# Build the feature from the geometry
    geom = feat.GetGeometryRef()
    featDef = outLYR.GetLayerDefn()
    featOut = ogr.Feature(featDef)
    featOut.SetGeometry(geom)
# Now set the attributes in the feature from the first attribute in the kml
    featOut.SetField('UID', counter)
    name = feat.GetField('Name')
    featOut.SetField('PersonID', name)
    featOut.SetField('Person', "Christian")
# extract all the other info from the xml-string
    yr01, yr02, sec, full = ExtractXML(feat.GetField("Description"))
    featOut.SetField('Year01', yr01)
    featOut.SetField('Year02', yr02)
    featOut.SetField('Security', sec)
    featOut.SetField('FullInfo', full)
    featOut.SetField('Keep_yn', 1)
# Create the feature, get the next feature, increase count
    outLYR.CreateFeature(featOut)
    counter += 1
    feat = cl_lyr.GetNextFeature()

# (2-4) Matthias
print("Matthias")
mb = drvKML.Open(rootFolder + "MB/MB_20170814_1635.kml")
mb_lyr = mb.GetLayer()
feat = mb_lyr.GetNextFeature()
while feat:
# Build the feature from the geometry
    geom = feat.GetGeometryRef()
    featDef = outLYR.GetLayerDefn()
    featOut = ogr.Feature(featDef)
    featOut.SetGeometry(geom)
# Now set the attributes in the feature from the first attribute in the kml
    featOut.SetField('UID', counter)
    name = feat.GetField('Name')
    featOut.SetField('PersonID', name)
    featOut.SetField('Person', "Matthias")
# extract all the other info from the xml-string
    yr01, yr02, sec, full = ExtractXML(feat.GetField("Description"))
    featOut.SetField('Year01', yr01)
    featOut.SetField('Year02', yr02)
    featOut.SetField('Security', sec)
    featOut.SetField('FullInfo', full)
    featOut.SetField('Keep_yn', 1)
# Create the feature, get the next feature, increase count
    outLYR.CreateFeature(featOut)
    counter += 1
    feat = mb_lyr.GetNextFeature()

# (2-5) Teresa
print("Teresa")
tdm = drvKML.Open(rootFolder + "TDM/TDM_final_dissolveMB.kml")
tdm_lyr = tdm.GetLayer()
feat = tdm_lyr.GetNextFeature()
while feat:
# Build the feature from the geometry
    geom = feat.GetGeometryRef()
    featDef = outLYR.GetLayerDefn()
    featOut = ogr.Feature(featDef)
    featOut.SetGeometry(geom)
# Now set the attributes in the feature from the first attribute in the kml
    featOut.SetField('UID', counter)
    name = feat.GetField('Name')
    featOut.SetField('PersonID', name)
    featOut.SetField('Person', "Teresa")
# extract all the other info from the xml-string
    yr01, yr02, sec, full = ExtractXML(feat.GetField("Description"))
    featOut.SetField('Year01', yr01)
    featOut.SetField('Year02', yr02)
    featOut.SetField('Security', sec)
    featOut.SetField('FullInfo', full)
    featOut.SetField('Keep_yn', 1)
# Create the feature, get the next feature, increase count
    outLYR.CreateFeature(featOut)
    counter += 1
    feat = tdm_lyr.GetNextFeature()

# (2-6) Robert, Hendrik, Maria
print("Robert, Hendrik, maria")
rhm = drvKML.Open(rootFolder + "MPR_RW_HB/AllMerged_dissolvedMB.kml")
rhm_lyr = rhm.GetLayer()
feat = rhm_lyr.GetNextFeature()
while feat:
# Build the feature from the geometry
    geom = feat.GetGeometryRef()
    featDef = outLYR.GetLayerDefn()
    featOut = ogr.Feature(featDef)
    featOut.SetGeometry(geom)
# Now set the attributes in the feature from the first attribute in the kml
    featOut.SetField('UID', counter)
    name = feat.GetField('Name')
    featOut.SetField('PersonID', name)
    featOut.SetField('Person', "Robert, Hendrik, Maria")
# extract all the other info from the xml-string
    yr01, yr02, sec, full = ExtractXML(feat.GetField("Description"))
    featOut.SetField('Year01', yr01)
    featOut.SetField('Year02', yr02)
    featOut.SetField('Security', sec)
    featOut.SetField('FullInfo', full)
    featOut.SetField('Keep_yn', 1)
# Create the feature, get the next feature, increase count
    outLYR.CreateFeature(featOut)
    counter += 1
    feat = rhm_lyr.GetNextFeature()

# (3) WRITE FILE TO DISK
bt.baumiVT.CopySHPDisk(outSHP, outfile)
outkml = outfile
outkml = outkml.replace(".shp", "_kml.kml")
subprocess.call('ogr2ogr -f "KML" {} {} -dsco NameField=UID'.format(outkml, outfile))


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")