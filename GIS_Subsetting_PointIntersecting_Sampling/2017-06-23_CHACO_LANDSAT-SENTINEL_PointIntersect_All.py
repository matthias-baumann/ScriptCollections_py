# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal
import ogr, osr
from gdalconst import *
import struct
import csv
import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### HARD-CODED FOLDERS AND FILES ######################################## #
shape = bt.baumiVT.CopyToMem("B:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_Pecent-TreeShrubCover_Chaco/__Analysis_and_Scripts/_shapeFiles_Samples/RandomPoints_Squares_Neighbors_AsPoint.shp")
out_file = "C:/Users/baumamat/Desktop/RandomPoints_Squares_Neighbors_AsPoint_S1-data-values_20170608.csv"
# shp files of surroundings of Sentinel-Tiles
vv_shp = "G:/CHACO/ReprojectedScenes/S1_Preprocessed/VV/_ScenesAsPolygons.shp"
vh_shp = "G:/CHACO/ReprojectedScenes/S1_Preprocessed/VH/_ScenesAsPolygons.shp"
# Tile folders
vv_folder = "G:/CHACO/ReprojectedScenes/S1_Preprocessed/VV/"
vh_folder = "G:/CHACO/ReprojectedScenes/S1_Preprocessed/VH/"
# data-type references
vv_ref = "G:/CHACO/ReprojectedScenes/S1_Preprocessed/VV/S1A_IW_GRDH_1SDV_20160515T090249_20160515T090314_011267_0110F5_A46C.tif"
vh_ref = "G:/CHACO/ReprojectedScenes/S1_Preprocessed/VH/S1A_IW_GRDH_1SDV_20141016T095853_20141016T095918_002853_003392_39BC.tif"
# ####################################### PROCESSING ########################################################## #
# Initialize output
valueList = []
header = ["Point_ID","TC","SC",
          "Scene_ID", "Polarization", "Value"]
valueList.append(header)
# Open the shapefile and build coordinate transformation
print("Open shp-file")
#ds_ogr = ogr.Open(shape, 1)
lyr = shape.GetLayer()
source_SR = lyr.GetSpatialRef()
target_SR = osr.SpatialReference()
target_SR.ImportFromWkt(gdal.Open(vv_ref).GetProjection())
coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
# Open the layers for the Sentinel-Shapefiles
vv_ogr = ogr.Open(vv_shp, 1)
vv_lyr = vv_ogr.GetLayer()
vh_ogr = ogr.Open(vh_shp, 1)
vh_lyr = vh_ogr.GetLayer()
# Loop through each feature and extract the values
feat = lyr.GetNextFeature()
while feat:
    # Check if observation should be used
    check = feat.GetField("use_YN")
    if check == 1:
        # Create list for the values of this feature, add Id-value
        id = feat.GetField("ID")
        print("Processing Point-ID ", id)
        tc = feat.GetField("TCperc")
        sc = feat.GetField("SCperc")
        # Get the values for the VV polarization
        # Set extent in the shp-file
        geom = feat.GetGeometryRef()
        geom_vv = geom.Clone()
        geom_vv.Transform(coordTrans)
        mx, my = geom_vv.GetX(), geom_vv.GetY()
        vv_lyr.SetSpatialFilter(geom_vv)
        # Now loop through each of the polygons, access associated raster file and extract value
        feat_vv = vv_lyr.GetNextFeature()
        while feat_vv:
        # Generate the list for the entry
            valList = []
            valList.append(id)
            valList.append(tc)
            valList.append(sc)
            sceneTiff = feat_vv.GetField("TileIndex")
            sceneID = sceneTiff[:-4]
            valList.append(sceneID)
            valList.append("VV")
        # Extract the value from the associated raster
            rasOpen = gdal.Open(vv_folder + sceneTiff, GA_ReadOnly)
            rasRB = rasOpen.GetRasterBand(1)
            rasdType = bt.baumiRT.GetDataTypeHexaDec(rasRB.DataType)
            gt = rasOpen.GetGeoTransform()
            px = int((mx - gt[0]) / gt[1])
            py = int((my - gt[3]) / gt[5])
            structVar = rasRB.ReadRaster(px, py, 1, 1)
            Val = struct.unpack(rasdType, structVar)[0]
            valList.append(Val)
        # Append values to valueList, take next feature
            valueList.append(valList)
            feat_vv = vv_lyr.GetNextFeature()
        # Reset layer, so that in the next point we can start over
        vv_lyr.ResetReading()
        # Get the values for the VH polarization
        geom_vh = geom.Clone()
        geom_vh.Transform(coordTrans)
        mx, my = geom_vh.GetX(), geom_vh.GetY()
        vh_lyr.SetSpatialFilter(geom_vh)
        # Now loop through each of the polygons, access associated raster file and extract value
        feat_vh = vh_lyr.GetNextFeature()
        while feat_vh:
        # Generate the list for the entry
            valList = []
            valList.append(id)
            valList.append(tc)
            valList.append(sc)
            sceneTiff = feat_vh.GetField("TileIndex")
            sceneID = sceneTiff[:-4]
            valList.append(sceneID)
            valList.append("VH")
        # Extract the value from the associated raster
            rasOpen = gdal.Open(vh_folder + sceneTiff, GA_ReadOnly)
            rasRB = rasOpen.GetRasterBand(1)
            rasdType = bt.baumiRT.GetDataTypeHexaDec(rasRB.DataType)
            gt = rasOpen.GetGeoTransform()
            px = int((mx - gt[0]) / gt[1])
            py = int((my - gt[3]) / gt[5])
            structVar = rasRB.ReadRaster(px, py, 1, 1)
            Val = struct.unpack(rasdType, structVar)[0]
            valList.append(Val)
        # Append values to valueList, take next feature
            valueList.append(valList)
            feat_vh = vh_lyr.GetNextFeature()
        # Reset layer, so that in the next point we can start over
        vh_lyr.ResetReading()
    # Take next point
        feat = lyr.GetNextFeature()
    else:
        feat = lyr.GetNextFeature()
lyr.ResetReading()
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