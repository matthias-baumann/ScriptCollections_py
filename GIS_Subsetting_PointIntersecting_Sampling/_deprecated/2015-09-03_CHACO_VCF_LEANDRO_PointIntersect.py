# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import gdal
import ogr, osr
from gdalconst import *
import struct
import csv
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### HARD-CODED FOLDERS AND FILES ######################################## #
shape = "S:/Matthias/Projects-and-Publications/Projects_Collaborating_Active/MACCI_Chaco-VCF/RandomSample_Run01_Points_CenterCorner.shp"
VRTroot = "E:/Baumann/CHACO/01_Compositing/03_ScratchData/"
out_root = "S:/Matthias/Projects-and-Publications/Projects_Collaborating_Active/MACCI_Chaco-VCF/"
# data-type references
imagery = "E:/Baumann/CHACO/01_Compositing/03_ScratchData/2013/Tile_x0_y0_999x999_2012-2013_CHACO_PBC_multiYear_Imagery.bsq"
metrics = "E:/Baumann/CHACO/01_Compositing/03_ScratchData/2013/Tile_x0_y0_999x999_2012-2013_CHACO_PBC_multiYear_Metrics.bsq"
flags = "E:/Baumann/CHACO/01_Compositing/03_ScratchData/2013/Tile_x0_y0_999x999_2012-2013_CHACO_PBC_multiYear_MetaFlags.bsq"

# ####################################### PROCESSING ########################################################## #
# Get list of all VRTs
vrtList = [VRTroot + file for file in os.listdir(VRTroot) if file.endswith(".vrt")]
# Loop through list of VRTs
for vrt in vrtList:
    print(vrt)
# Check what type of VRT it is --> Imagery, Metrics, or Flags
    types = [["Imagery",["Point_ID", "b1", "b2", "b3", "b4", "b5", "b6"], imagery],
            ["Flags", ["Point_ID", "PR", "Year", "DOY", "Month", "Day", "nClearObs", "nCloudedObs", "Zenit", "Azimuth"], flags],
            ["Metrics", ["Point_ID",
                         "b1mean", "b2mean", "b3mean", "b4mean", "b5mean", "b6mean",
                         "b1median", "b2median", "b3median", "b4median", "b5median", "b6median",
                         "b1STDV", "b2STDV", "b3STDV", "b4STDV", "b5STDV", "b6STDV",
                         "b1Q25", "b2Q25", "b3Q25", "b4Q25", "b5Q25", "b6Q25",
                         "b1Q50", "b2Q50", "b3Q50", "b4Q50", "b5Q50", "b6Q50",
                         "b1Q75", "b2Q75", "b3Q75", "b4Q75", "b5Q75", "b6Q75",
                         "b1Median25Q50", "b2Median25Q50", "b3Median25Q50", "b4Median25Q50", "b5Median25Q50", "b6Median25Q50",
                         "b1Median50Q75", "b2Median50Q75", "b3Median50Q75", "b4Median50Q75", "b5Median50Q75", "b6Median50Q75",
                         "b1Slope", "b2Slope", "b3Slope", "b4Slope", "b5Slope", "b6Slope",
                         "b1RangeQ75Q25", "b2RangeQ75Q25", "b3RangeQ75Q25", "b4RangeQ75Q25", "b5RangeQ75Q25", "b6RangeQ75Q25"], metrics]]
    for type in types:
        if vrt.find(type[0]) >= 0:
            whichType = type[0]
            topRow = type[1]
            ref = type[2]
# Build path to output-csv
    p = vrt.rfind("/")
    file = vrt[p+1:len(vrt)-7] + "PointValues.csv"
    outcsv = out_root + file
# Open the VRT-Raster to extract the values
    print("Open VRT")
    vrt_open = gdal.Open(vrt, GA_ReadOnly)
    gt = vrt_open.GetGeoTransform()
    pr = vrt_open.GetProjection()
    numBand = vrt_open.RasterCount
# Open the shapefile, create info from unique-ID field, put into outlist
    print("Get Point-IDs")
    idList = []
    point_ogr = ogr.Open(shape, 1)
    lyr = point_ogr.GetLayer()
    feat = lyr.GetNextFeature()
    while feat:
        id = feat.GetField("ID")
        idList.append([int(id)])
        feat = lyr.GetNextFeature()
    lyr.ResetReading()
# Open the reference-raster, to extract the data-types later
    ref_open = gdal.Open(ref, GA_ReadOnly)
# Loop through bands of input-vrt and extract the value
    print("Get band values")
    for band in range(numBand):
        print(band + 1)
        vrt_rb = vrt_open.GetRasterBand(band+1)
# Get the info about the datatype from the ref-raster
        ref_rb = ref_open.GetRasterBand(band+1)
        dTypes = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
        ref_dType = ref_rb.DataType
        for dT in dTypes:
            if dT[0] == ref_dType:
                band_dType = dT[1]
#  Build Coordinate Transformation
        target_SR = osr.SpatialReference()
        target_SR.ImportFromWkt(pr)
        source_SR = lyr.GetSpatialRef()
        coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
# Get the band values at the point location, set counter, so that we can add things to the idList (makes it easier later to write the output)
        counter = 0
        feat = lyr.GetNextFeature()
        while feat:
# Build the geometry-object, do the geometric transformation
            geom = feat.GetGeometryRef()
            geom.Transform(coordTrans)
            mx, my = geom.GetX(), geom.GetY()
            px = int((mx - gt[0]) / gt[1])
            py = int((my - gt[3]) / gt[5])
# Get the raster-value
            structVar = vrt_rb.ReadRaster(px,py,1,1)
            Val = struct.unpack(band_dType, structVar)[0]
            idList[counter].append(Val)
            counter = counter + 1
            feat = lyr.GetNextFeature()
        lyr.ResetReading()
# Write the output-file
    print("Write output")
    with open(outcsv, "w") as theFile:
        csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator = '\n')
        writer = csv.writer(theFile, dialect = "custom")
        writer.writerow(topRow)
        for element in idList:
            writer.writerow(element)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")