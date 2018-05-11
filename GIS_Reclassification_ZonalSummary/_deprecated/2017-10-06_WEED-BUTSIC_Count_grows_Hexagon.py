# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, osr
import csv
import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
root_folder = "C:/Users/Matthias/Desktop/butsic_Marihuana-California/"
outFile = root_folder + "_summary_perHexagon_500m_v02.csv"
# ####################################### OPEN FILES, BUILD COORDINATE TRANSFORMATION ######################### #
#drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
grows = bt.baumiVT.CopyToMem(root_folder + "Data/allgrows11_18.shp")
hexa = bt.baumiVT.CopyToMem(root_folder + "Analysis/counties_sub_hexagons_500m.shp")
growsLYR = grows.GetLayer()
hexaLYR = hexa.GetLayer()
# ####################################### BUILD COORDINATE TRANSFORMATION ##################################### #
outPR = growsLYR.GetSpatialRef()
inPR = hexaLYR.GetSpatialRef()
transform = osr.CoordinateTransformation(inPR, outPR)
# ####################################### BUILD HEADER FILE ################################################### #
outList = []
header = ["hexa_ID", "growCount_12", "oplants_12", "gplants_12", "osize_12", "gzise_12", "oplants_16", "gplants_16", "osize_16", "gzise_16"]
outList.append(header)
# ####################################### LOOP THROUGH FEATURES ############################################### #
hexa_feat = hexaLYR.GetNextFeature()
while hexa_feat:
#### Check if object in skipList
    ID = hexa_feat.GetField("Id")
    print("Processing hexagon " + str(ID))
# Get the Geometry, make clone
    geom = hexa_feat.GetGeometryRef()
    geom.Transform(transform)
# Get the number of grows that are inside the parcel
    growsLYR.SetSpatialFilter(geom)
# Loop through each feature, make a shortcut, if the number of points is 0
    ngrow = growsLYR.GetFeatureCount()
    if ngrow == 0:
        vals = [ID, ngrow, 0, 0, 0, 0, 0, 0, 0, 0]
        outList.append(vals)
    else:
# Create the variables that we want
        oplants12 = 0
        gplants12 = 0
        osize12 = 0
        gsize12 = 0
        oplants16 = 0
        gplants16 = 0
        osize16 = 0
        gsize16 = 0
# Loop through each grow-feature and extract the numbers
        grow_feat = growsLYR.GetNextFeature()
        while grow_feat:
        # Check if the point is from the year 2012 or 2016
            year = grow_feat.GetField("year")
            if year == 12:
                oplants12 = oplants12 + grow_feat.GetField("oplants")
                gplants12 = gplants12 + grow_feat.GetField("gplants")
                osize12 = osize12 + grow_feat.GetField("osize")
                gsize12 = gsize12 + grow_feat.GetField("gsize")
            if year == 16:
                oplants16 = oplants16 + grow_feat.GetField("oplants")
                gplants16 = gplants16 + grow_feat.GetField("gplants")
                osize16 = osize16 + grow_feat.GetField("osize")
                gsize16 = gsize16 + grow_feat.GetField("gsize")
        # Take next grow
            grow_feat = growsLYR.GetNextFeature()
    # Once we are through, rest the iteration
        growsLYR.ResetReading()
    # Attach the value sums to the output list
        vals = [ID, ngrow, oplants12, gplants12, osize12, gsize12, oplants16, gplants16, osize16, gsize16]
        outList.append(vals)
# Take the next hexagon
    hexa_feat = hexaLYR.GetNextFeature()
# Write output-file
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