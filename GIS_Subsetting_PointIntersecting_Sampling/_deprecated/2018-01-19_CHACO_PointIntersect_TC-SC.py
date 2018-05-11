# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal
import ogr, osr
from gdalconst import *
import struct
import csv
import baumiTools as bt
from tqdm import tqdm
import os
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### HARD-CODED FOLDERS AND FILES ######################################## #
rootFolder = "L:/_SHARED_DATA/CL_MB/tc_sc/_Version02_300m/"
shape = bt.baumiVT.CopyToMem(rootFolder + "points_300m_clip.shp")
out_file = rootFolder + "points_300m_clip_values.csv"
# ####################################### FUNCTIONS ########################################################### #
def ExtracRasterToPoint(lyrRef, feat, ds):
    pr = ds.GetProjection()
    gt = ds.GetGeoTransform()
    rb = ds.GetRasterBand(1)
    rasdType = bt.baumiRT.GetDataTypeHexaDec(rb.DataType)
    # Create coordinate transformation for point
    source_SR = lyrRef.GetSpatialRef()
    target_SR = osr.SpatialReference()
    target_SR.ImportFromWkt(pr)
    coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
    # Get the coordinates of the point
    geom = feat.GetGeometryRef()
    geom_cl = geom.Clone()
    geom_cl.Transform(coordTrans)
    mx, my = geom_cl.GetX(), geom_cl.GetY()
    # Extract raster value
    px = int((mx - gt[0]) / gt[1])
    py = int((my - gt[3]) / gt[5])
    structVar = rb.ReadRaster(px, py, 1, 1)
    Val = struct.unpack(rasdType, structVar)[0]
    return Val
# ####################################### PROCESSING ########################################################## #
# Initialize output
valueList = []
header = ["Point_ID", "TC_LS", "SC_LS", "TC_L", "SC_L", "TC_S", "SC_S"]
valueList.append(header)
# Open the shapefile and build coordinate transformation
lyr = shape.GetLayer()
# Open the rasters, load into an array in memory
rasList = ["L_CLEAN_S_CLEAN__TC_300m.tif", "L_CLEAN_S_CLEAN__SC_300m.tif",
           "L_CLEAN_S_NONE__TC_300m.tif", "L_CLEAN_S_NONE__SC_300m.tif",
           "L_NONE_S_CLEAN__TC_300m.tif", "L_NONE_S_CLEAN__SC_300m.tif"]
rasMem = []
for ras in rasList:
    rasMem.append(bt.baumiRT.OpenRasterToMemory(rootFolder + ras))
# Loop through each feature and extract the values
feat = lyr.GetNextFeature()
while feat:
    id = feat.GetField("pointid")
    print("Processing Point-ID ", id)
    featVals = [id]
    # Now get the information at the rasters
    for ras in rasMem:
        featVals.append(ExtracRasterToPoint(lyr, feat, ras))
# Add to value list, take next point
    valueList.append(featVals)
    feat = lyr.GetNextFeature()
# Write the output-file
print("Write output")
with open(out_file, "w") as theFile:
    csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
    writer = csv.writer(theFile, dialect="custom")
    for element in valueList:
        writer.writerow(element)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")