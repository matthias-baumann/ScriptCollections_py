# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal, ogr, osr
from gdalconst import *
import numpy as np
import baumiTools as bt
from scipy import stats
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
L_Tiles = bt.baumiVT.CopyToMem("G:/CHACO/_COMPOSITING/Tiles_as_Polygons.shp")
S_Tiles = bt.baumiVT.CopyToMem("G:/CHACO/ReprojectedScenes/S1_extracted_new/_ScenesAsPolygons.shp")
outFolder = "E:/Baumann/CHACO/_Composite_Sentinel1_2015_new/HH_mean/"
S_folder = "G:/CHACO/ReprojectedScenes/S1_extracted_new/"
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
drvMemR = gdal.GetDriverByName('MEM')
band = 1
selectMonths = [5,6,7,8,9,10] # dry season --> wet season is November-April
selectYears = [2015, 2016]
def GetYearMonthDayfromSentinelIndex(string):
    p = string.find("_2")
    string = string[p+1:]
    #print(string)
    year = int(string[0:4])
    month = int(string[4:6])
    day = int(string[6:8])
    return year, month, day
def GetS1arrayForTile(feature, rasterPath):
# get needed proporties of files
    pxSize = 30
    geom = feature.GetGeometryRef()
    rasOpen = gdal.Open(rasterPath, GA_ReadOnly)
    spatialRef = geom.GetSpatialReference()
    dtype = rasOpen.GetRasterBand(1).DataType
# Build SHP-file in memory from the geometry
    shpMem = drvMemV.CreateDataSource('')
    shpMem_lyr = shpMem.CreateLayer('shpMem', spatialRef, geom_type=ogr.wkbMultiPolygon)
    shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
    shpMem_feat = ogr.Feature(shpMem_lyr_defn)
    shpMem_feat.SetGeometry(geom)
    shpMem_lyr.CreateFeature(shpMem_feat)
# Build 30m Landsat raster from the new SHP-file
    x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
    x_res = int((x_max - x_min) / pxSize)
    y_res = int((y_max - y_min) / pxSize)
    shpMem_asRaster = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
    shpMem_asRaster.SetProjection(str(spatialRef))
    shpMem_asRaster.SetGeoTransform((x_min, pxSize, 0, y_max, 0, -pxSize))
    shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
    shpMem_asRaster_b.SetNoDataValue(0)
    gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
    shpMem_array = np.array(shpMem_asRaster_b.ReadAsArray())
# Subset the inputRaster raster and load it into the array
    rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, dtype)
    rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
    rasMem.SetProjection(shpMem_asRaster.GetProjection())
    gdal.ReprojectImage(rasOpen, rasMem, rasOpen.GetProjection(), shpMem_asRaster.GetProjection(), gdal.GRA_Average)
    #bt.baumiRT.CopyMEMtoDisk(rasMem, "E:/Baumann/CHACO/_Composite_Sentinel1_2015_new/HH/3.tif")
    rasMem_array = np.array(rasMem.GetRasterBand(1).ReadAsArray())
    outList = [rasMem, rasMem_array]
    return outList
def CalculateMetric(listOfArrays, function, maxIgnore):
# Mask out 0 and 1 and flag them as DatIgnoreValues
    stack = np.dstack(listOfArrays)
    if function == "mean":
        mask = np.ma.masked_less_equal(stack, maxIgnore)
        #print(mask[0])
        value = np.mean(mask, axis=2)
        #print(mean)
    if function == "median":
        mask = np.ma.masked_less_equal(stack, maxIgnore)
        value = np.median(mask, axis=2)
    if function == "max":
        mask = np.ma.masked_less_equal(stack, maxIgnore)
        value = np.max(mask, axis=2)

    return value
def ConvertMetricToRaster(array,raster):
    #rasOpen = gdal.Open(raster)
    raster.GetRasterBand(1).WriteArray(array, 0, 0)
    return raster

# ####################################### GET LAYERS, BUILD TRANSFORM, START ITERATION ######################## #
# FOr testing: onl;y a few tiles (manually selected)
testTiles = ["Tile_x20999_y37999_1000x1000_2014-2015_CHACO_Sentinel1.tif", "Tile_x20999_y38999_1000x1000_2014-2015_CHACO_Sentinel1.tif", "Tile_x21999_y37999_1000x1000_2014-2015_CHACO_Sentinel1.tif",
             "Tile_x21999_y38999_1000x1000_2014-2015_CHACO_Sentinel1.tif", "Tile_x22999_y37999_1000x1000_2014-2015_CHACO_Sentinel1.tif", "Tile_x22999_y38999_1000x1000_2014-2015_CHACO_Sentinel1.tif"]
# ############
L_lyr = L_Tiles.GetLayer()
S_lyr = S_Tiles.GetLayer()
L_PR = L_lyr.GetSpatialRef()
S_PR = S_lyr.GetSpatialRef()
transform = osr.CoordinateTransformation(L_PR, S_PR)
feat_L = L_lyr.GetNextFeature()
while feat_L:
# Check if it is an active tile, if not then skip
    active = feat_L.GetField("Active_YN")
    if int(active) != 1:
        feat_L = L_lyr.GetNextFeature()
    #select = feat_L.GetField("TileIndex")
    #select = select + "_Sentinel1.tif"
    #if select not in testTiles:
    #    feat_L = L_lyr.GetNextFeature()
    else:
        tileName = feat_L.GetField("TileIndex")
        print("--> " + tileName)
        geom = feat_L.GetGeometryRef()
        geom_clone = geom.Clone()
# Check which scenes we have intersecting in that tile
        geom_clone.Transform(transform)
        S_lyr.SetSpatialFilter(geom_clone)
        S_count = S_lyr.GetFeatureCount()
        #print(S_count)
# Make a list of the Sentinel-Tiffs that intersect with the Landsat tile
        S1_names = []
        feat_S = S_lyr.GetNextFeature()
        while feat_S:
            name = feat_S.GetField("TileIndex")
            S1tilePath = S_folder + name
            S1_names.append(S1tilePath)
            feat_S = S_lyr.GetNextFeature()
        S_lyr.ResetReading()
        S1_select = []
        for n in S1_names:
            year, month, day = GetYearMonthDayfromSentinelIndex(n)
            if year in selectYears and month in selectMonths:
                S1_select.append(n)
# Now load the files as arrays into list, crop them prior to that
        arrayList = []
        #count = 1
        for S1 in S1_select:
            array = GetS1arrayForTile(feat_L, S1)
            arrayList.append(array[1])
            #bt.baumiRT.CopyMEMtoDisk(array[0], outFolder + str(count) + ".tif")
            #count = count+1
        mean = CalculateMetric(arrayList, "mean", 20)
# Write output array --> use output from GetS1arryForTile()[0]
        outras = ConvertMetricToRaster(mean, array[0])
        bt.baumiRT.CopyMEMtoDisk(outras, outFolder + tileName + ".tif")

        S_lyr.ResetReading()
        feat_L = L_lyr.GetNextFeature()
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")