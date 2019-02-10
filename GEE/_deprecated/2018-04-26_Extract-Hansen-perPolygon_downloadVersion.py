# ####################################### SET TIME-COUNT ###################################################### ##
## EXTRACT GLOBAL FOREST LOSS DATA (HANSEN ET AL) FROM GEE (Version 1.0)                                        ##
## (c) Matthias Baumann, May 2017                                                                             ##
## Credit to: https://mygeoblog.com/2017/10/06/from-gee-to-numpy-to-geotiff/#more-2904                           ##
## Humboldt-University Berlin                                                                                   ##
# ####################################### IMPORT MODULES, START EARTH-ENGINE ################################## ##
import time
import ogr, osr, gdal
import ee
import numpy as np
import csv
import baumiTools as bt
ee.Initialize()
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
shp = r'D:\baumamat\Warfare\_SHPs\BIOMES_TropicsSavannas_10kmGrid_polygons.shp'
outFolder = "D:/baumamat/Warfare/_Variables/Forest/"
# ####################################### FUNCTIONS ########################################################### #

# ####################################### START PREPARING THE FEATURE COLLECTION ############################## #
shape = bt.baumiVT.CopyToMem(shp)
lyr = shape.GetLayer()
source_SR = lyr.GetSpatialRef()
target_SR = osr.SpatialReference()
target_SR.ImportFromEPSG(4326)
transform = osr.CoordinateTransformation(source_SR, target_SR)
feat = lyr.GetNextFeature()
while feat:
    polID = feat.GetField("UniqueID")
    print(polID)
# Build an earth engine feature
    geom = feat.GetGeometryRef()
    geom_clone =geom.Clone()
    geom.Transform(transform)
    env = geom.GetEnvelope()  # Get Envelope returns a tuple (minX, maxX, minY, maxY)
    UL = [env[0], env[3]]  # UR = [env[1], env[3]]
    LR = [env[1], env[2]]  # LL = [env[0], env[2]]
    poly = ee.Geometry.Rectangle(coords=[UL, LR])
# Select the bands from the Forest dataset
    gfc2016 = ee.Image(r'UMD/hansen/global_forest_change_2016_v1_4')
    forest2000 = gfc2016.select(['treecover2000'])
    lossYear = gfc2016.select(['lossyear'])
    gain = gfc2016.select(['gain'])
# Extract the values into np-arrays
    latlon = ee.Image.pixelLonLat().addBands(forest2000).addBands(lossYear).addBands(gain)
    latlon = latlon.reduceRegion(reducer=ee.Reducer.toList(), geometry=poly, maxPixels=1e13, scale=30)
    forest = np.array((ee.Array(latlon.get("treecover2000")).getInfo()))
    l_yr = np.array((ee.Array(latlon.get("lossyear")).getInfo()))
    lats = np.array((ee.Array(latlon.get("latitude")).getInfo()))
    lons = np.array((ee.Array(latlon.get("longitude")).getInfo()))
# Determine the size of the output-files
    uniqueLats = np.unique(lats) # upper left corners
    uniqueLons = np.unique(lons)
    ncols = len(uniqueLons) # Array size
    nrows = len(uniqueLats)
    ys = uniqueLats[1] - uniqueLats[0] # determine pixelsizes
    xs = uniqueLons[1] - uniqueLons[0]
# create output-arrays with dimensions of image
    f_out = np.zeros([nrows, ncols], np.uint16)  # -9999
    l_out = np.zeros([nrows, ncols], np.uint8)
    # fill the array with values
    counter = 0
    for y in range(0, len(f_out), 1):
        for x in range(0, len(f_out[0]), 1):
            if lats[counter] == uniqueLats[y] and lons[counter] == uniqueLons[x] and counter < len(lats) - 1:
                counter += 1
                f_out[len(uniqueLats) - 1 - y, x] = forest[counter]
                l_out[len(uniqueLats) - 1 - y, x] = l_yr[counter]
# Create output_datasets
    drvMemR = gdal.GetDriverByName('MEM')
    gt_out = (np.min(uniqueLons), xs, 0, np.max(uniqueLats), 0, -ys)
    forMem = drvMemR.Create('', ncols, nrows, 1, gdal.GDT_UInt16)
    lossMem = drvMemR.Create('', ncols, nrows, 1, gdal.GDT_Byte)
    forMem.SetProjection(target_SR.ExportToWkt())
    forMem.SetGeoTransform(gt_out)
    lossMem.SetProjection(target_SR.ExportToWkt())
    lossMem.SetGeoTransform(gt_out)
# Write output
    forMem.GetRasterBand(1).WriteArray(f_out)
    lossMem.GetRasterBand(1).WriteArray(l_out)
    bt.baumiRT.CopyMEMtoDisk(forMem, outFolder + "Forest2000/" + str(polID) + ".tif")
    bt.baumiRT.CopyMEMtoDisk(lossMem, outFolder + "LossYear/" + str(polID) + ".tif")
# GetNextFeature
    feat = lyr.GetNextFeature()
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")