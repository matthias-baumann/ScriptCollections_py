# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, gdal
import baumiTools as bt
from tqdm import tqdm
import struct
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
drvV = ogr.GetDriverByName('ESRI Shapefile')
outputFile = "D:/Projects-and-Publications/Publications/Publications-submitted-in-review/2018_butsic_Marihuana-California/Data/allgrows11_18_newVariables.csv"
grows = bt.baumiVT.CopyToMem("D:/Projects-and-Publications/Publications/Publications-submitted-in-review/2018_butsic_Marihuana-California/Data/allgrows11_18.shp")
#
agrLands = bt.baumiVT.CopyToMem("D:/Projects-and-Publications/Publications/Publications-submitted-in-review/2018_butsic_Marihuana-California/Data/_agriculturalLands.shp")
slope = bt.baumiRT.OpenRasterToMemory("D:/Projects-and-Publications/Publications/Publications-submitted-in-review/2018_butsic_Marihuana-California/Data/slope_perc.tif")
streams = bt.baumiVT.CopyToMem("D:/Projects-and-Publications/Publications/Publications-submitted-in-review/2018_butsic_Marihuana-California/Data/streams.shp")
# ####################################### FUNCTIONS ########################################################### #

# ####################################### LOOP THROUGH FEATURES ############################################### #
# (1) INITIALIZE OUTPUT-list
outList = [["OBJECTID_1", "Agric.Lands", "Slope_perc", "Dist.to.Streams_m"]]

# (2) GET LAYERS AND INITIALIZE LOOP
growLYR = grows.GetLayer()
agLYR = agrLands.GetLayer()
streamLYR = streams.GetLayer()

#feat = growLYR.GetNextFeature()
#while feat:
for feat in tqdm(growLYR):
    # Initiate output
    vals = [feat.GetField("OBJECTID_1")]
    # Get the Geometry
    geom = feat.GetGeometryRef()
    # Extract value of agricultural lands
    geom_cl = geom.Clone()
    CT = bt.baumiVT.CS_Transform(geom, agLYR)
    geom.Transform(CT)
    agLYR.SetSpatialFilter(geom)
    ag_yn = agLYR.GetFeatureCount()
    if ag_yn > 0:
        ag_feat = agLYR.GetNextFeature()
        value = ag_feat.GetField("Class")
    else:
        value = "Not in agric. land"
    vals.append(value)
    # Extract value of slope
    geom_cl = geom.Clone()
    CT = bt.baumiRT.ProjGeometryToRaster(geom, slope.GetProjection())
    geom_cl.Transform(CT)
    rasdType = bt.baumiRT.GetDataTypeHexaDec(slope.GetRasterBand(1).DataType)
    gt = slope.GetGeoTransform()
    mx, my = geom_cl.GetX(), geom_cl.GetY()
    # Extract raster value
    px = int((mx - gt[0]) / gt[1])
    py = int((my - gt[3]) / gt[5])
    structVar = slope.GetRasterBand(1).ReadRaster(px, py, 1, 1)
    value = struct.unpack(rasdType, structVar)[0]
    vals.append(value)
    # Distance to streams --> accuracy: 10m
    geom_cl = geom.Clone()
    CT = bt.baumiVT.CS_Transform(geom_cl, streamLYR)
    geom_cl.Transform(CT)
    control = 0
    buffer = 10 * 3.28084 # equals to 10m
    stepSize = 10 * 3.28084 # equals to ~10m
    while control == 0:
        geomBuff = geom.Buffer(buffer)
        streamLYR.SetSpatialFilter(geomBuff)
        streamCount = streamLYR.GetFeatureCount()
        if streamCount > 0:
            value = buffer
            control = 1
        else:
            control = control
            buffer = buffer + stepSize
    value = value / 3.28084 # conversion back to meters
    vals.append(value)
    # Add vals to output-list
    outList.append(vals)
    # Get Next feature
    #feat = growLYR.GetNextFeature()
# Write output-file
bt.baumiFM.WriteListToCSV(outputFile, outList, ",")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")