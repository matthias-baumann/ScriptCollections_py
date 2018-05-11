# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal
import ogr, osr
from gdalconst import *
import struct
import csv
import baumiTools as bt
from tqdm import tqdm
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### HARD-CODED FOLDERS AND FILES ######################################## #
shape = bt.baumiVT.CopyToMem("B:/Projects-and-Publications/Publications/Publications-in-preparation/Wilting-etal_CameraTraps_LandsatTimeSeries/Sabah coarse grid/Sabah_TFR_STC_stations.shp")
out_file = "B:/Projects-and-Publications/Publications/Publications-in-preparation/Wilting-etal_CameraTraps_LandsatTimeSeries/Sabah coarse grid/Sabah_TFR_STC_stations_values_02.csv"
# Landsat_Folder
L_folder = "E:/Baumann/KALIMANTAN_Wilting/Landsat_TS/"
# ####################################### FUNCTIONS ########################################################### #
def ExtracRasterToPoint(lyrRef, feat, rasPath):
    # Open raster-file, get datatype
    ds = gdal.Open(rasPath, GA_ReadOnly)
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
header = ["Point_ID","Scene_ID","IndexName","Value"]
valueList.append(header)
# Open the shapefile and build coordinate transformation
print("Open shp-file")
lyr = shape.GetLayer()
# Loop through each feature and extract the values
feat = lyr.GetNextFeature()
while feat:
    id = feat.GetField("UniqueID")
    print("Processing Point-ID ", id)
    # Loop through folders in L_folder
    sceneList = bt.baumiFM.GetFilesInFolderWithEnding(L_folder,"",fullPath=True)
    for sc in tqdm(sceneList):
    # Get the product-ID from the xml-File
        prodID = bt.baumiFM.GetFilesInFolderWithEnding(sc,".xml",fullPath=False)
        prodID = prodID[:-4]
    # Now get the information at the rasters
        # (1) Pixel_Qa
        img = bt.baumiFM.GetFilesInFolderWithEnding(sc, "pixel_qa.tif", fullPath = True)
        rasval = ExtracRasterToPoint(lyr, feat, img)
        valList = [id, prodID, "pixelQA", rasval]
        valueList.append(valList)
        # (2) Sensor_azimuth_band4
        img = bt.baumiFM.GetFilesInFolderWithEnding(sc, "_sensor_azimuth_band4.tif", fullPath=True)
        rasval = ExtracRasterToPoint(lyr, feat, img)
        valList = [id, prodID, "sensor_azimuth_b4", rasval]
        valueList.append(valList)
        # (3) Sensor_zenith_band4
        img = bt.baumiFM.GetFilesInFolderWithEnding(sc, "_sensor_zenith_band4.tif", fullPath=True)
        rasval = ExtracRasterToPoint(lyr, feat, img)
        valList = [id, prodID, "sensor_zenith_b4", rasval]
        valueList.append(valList)
        # (4) Solar_azimuth_band4
        img = bt.baumiFM.GetFilesInFolderWithEnding(sc, "_solar_azimuth_band4.tif", fullPath=True)
        rasval = ExtracRasterToPoint(lyr, feat, img)
        valList = [id, prodID, "solar_azimuth_b4", rasval]
        valueList.append(valList)
        # (5) Solar_zenith_band4
        img = bt.baumiFM.GetFilesInFolderWithEnding(sc, "_solar_zenith_band4.tif", fullPath=True)
        rasval = ExtracRasterToPoint(lyr, feat, img)
        valList = [id, prodID, "solar_zenith_b4", rasval]
        valueList.append(valList)
        # (6) EVI
        img = bt.baumiFM.GetFilesInFolderWithEnding(sc, "_sr_evi.tif", fullPath=True)
        rasval = ExtracRasterToPoint(lyr, feat, img)
        valList = [id, prodID, "sr_evi", rasval]
        valueList.append(valList)
        # (7) Solar_zenith_band4
        img = bt.baumiFM.GetFilesInFolderWithEnding(sc, "_sr_msavi.tif", fullPath=True)
        rasval = ExtracRasterToPoint(lyr, feat, img)
        valList = [id, prodID, "sr_msavi", rasval]
        valueList.append(valList)
        # (8) Solar_zenith_band4
        img = bt.baumiFM.GetFilesInFolderWithEnding(sc, "_sr_nbr2.tif", fullPath=True)
        rasval = ExtracRasterToPoint(lyr, feat, img)
        valList = [id, prodID, "sr_nbr2", rasval]
        valueList.append(valList)
        # (9) Solar_zenith_band4
        img = bt.baumiFM.GetFilesInFolderWithEnding(sc, "_sr_ndmi.tif", fullPath=True)
        rasval = ExtracRasterToPoint(lyr, feat, img)
        valList = [id, prodID, "sr_ndmi", rasval]
        valueList.append(valList)
        # (10) Solar_zenith_band4
        img = bt.baumiFM.GetFilesInFolderWithEnding(sc, "_sr_savi.tif", fullPath=True)
        rasval = ExtracRasterToPoint(lyr, feat, img)
        valList = [id, prodID, "sr_savi", rasval]
        valueList.append(valList)
# Take next point
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