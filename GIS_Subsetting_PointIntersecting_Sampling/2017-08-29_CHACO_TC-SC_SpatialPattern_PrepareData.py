# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time, os
import gdal, ogr, osr
from gdalconst import *
import baumiTools as bt
import csv
import struct
# ####################################### FUNCTIONS ########################################################### #
def ExtracRasterToPoint(lyrRef, feat, raster):
    ds = raster
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
# ####################################### START EXTERNAL PROCESS (IMPORTANT FOR PARALLEL PROCESSING) ########## #
if __name__ == '__main__':
# ####################################### SET TIME COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
# ####################################### FOLDER PATHS ######################################################## #
    inputFolder = "Y:/Baumann/_ANALYSES/PercentTreeCover/_02_Analysis_SpatialPattern/"
    shape = bt.baumiVT.CopyToMem(inputFolder + "RandomPoints_1000_100mDist.shp")
    outFile = inputFolder + "_RandomPoints_1000_100mDist_values.csv"

    crop = bt.baumiRT.OpenRasterToMemory(inputFolder + "Croplands_2015.tif")
    pasture = bt.baumiRT.OpenRasterToMemory(inputFolder + "Pasture_2015.tif")

    crop_dist = bt.baumiRT.OpenRasterToMemory(inputFolder + "Croplands_2015_EucDist.tif")
    CatExCap = bt.baumiRT.OpenRasterToMemory(inputFolder + "CECSOL_MEAN_30cm_250_NACD.tif")
    puesto_dist = bt.baumiRT.OpenRasterToMemory(inputFolder + "Puestos_2007_Gasparri_EucDist.tif")
    road_paved_dist = bt.baumiRT.OpenRasterToMemory(inputFolder + "Roads_ARG_2015_EucDist.tif")
    road_all_dist = bt.baumiRT.OpenRasterToMemory(inputFolder + "ALL_Roads_ARG_2015_EucDist.tif")
    rail_dist = bt.baumiRT.OpenRasterToMemory(inputFolder + "Railroad_2016_EucDist.tif")
    arid = bt.baumiRT.OpenRasterToMemory(inputFolder + "Normal_1981-2010_CMD.tif")
    TC = gdal.Open("Y:/Baumann/_ANALYSES/PercentTreeCover/__Run_20170823/L_CLEAN_S_CLEAN__TC.vrt", GA_ReadOnly)
    SC = gdal.Open("Y:/Baumann/_ANALYSES/PercentTreeCover/__Run_20170823/L_CLEAN_S_CLEAN__SC.vrt", GA_ReadOnly)


# ####################################### PROCESSING ########################################################## #
    # Initialize output
    valueList = []
    header = ["Point_ID","TC","SC","crop", "pasture", "crop_dist","CatExCap","puesto_dist","road_paved_dist","road_all_dist","rail_dist", "arid"]
    valueList.append(header)
    # Open the shapefile and build coordinate transformation
    lyr = shape.GetLayer()
    # Loop through each feature and extract the values
    feat = lyr.GetNextFeature()
    while feat:
        values = []
        id = feat.GetField("id")
        values.append(id)
        print("Processing Point-ID ", id)
        # Extract the values from the different rasters
        values.append(ExtracRasterToPoint(lyr, feat, TC))
        values.append(ExtracRasterToPoint(lyr, feat, SC))
        values.append(ExtracRasterToPoint(lyr, feat, crop))
        values.append(ExtracRasterToPoint(lyr, feat, pasture))
        values.append(ExtracRasterToPoint(lyr, feat, crop_dist))
        values.append(ExtracRasterToPoint(lyr, feat, CatExCap))
        values.append(ExtracRasterToPoint(lyr, feat, puesto_dist))
        values.append(ExtracRasterToPoint(lyr, feat, road_paved_dist))
        values.append(ExtracRasterToPoint(lyr, feat, road_all_dist))
        values.append(ExtracRasterToPoint(lyr, feat, rail_dist))
        values.append(ExtracRasterToPoint(lyr, feat, arid))
        # Append the values to the output-file
        valueList.append(values)
        # Go to next feature
        feat = lyr.GetNextFeature()
    # Write output
    print("Write output")
    with open(outFile, "w") as theFile:
        csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
        writer = csv.writer(theFile, dialect="custom")
        for element in valueList:
            writer.writerow(element)
# ####################################### END TIME-COUNT AND PRINT TIME STATS ################################# #
    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")