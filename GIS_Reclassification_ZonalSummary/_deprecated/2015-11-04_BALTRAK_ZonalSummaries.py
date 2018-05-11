# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import gdal, osr, ogr
from ZumbaTools.Vector_Tools import *
from gdalconst import *
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
shape = "H:/Baltrak/00_SHP/AdminBoundaries_StudyArea_large_20151107.shp"
classification = "S:/BALTRAK/01_ClassificationRuns/Run01_IMG.img"
classes = [[1, "01_Forest"],[2, "02_Wetland"],[3, "03_Water"],[4, "04_Other"],[5, "05_C-C-C"],[6, "06_C-G-G"],[7, "07_C-C-G"],[8, "08_G-G-G"],[9, "09_G-G-C"],[10, "10_C-G-C"],[11, "11_F-F-NF"], [12, "12_F-NF-NF"]]

# (1) ADD LABELS AS ATTRIBUTE TO SHAPEFILE
print("Add fields to shapefile")
for clas in classes:
    label = clas[1]
    AddFieldToSHP(shape, label, "float")
# (2) LOOP THROUGH EACH OF THE FEATURES IN THE SHAPEFILE AND GET THE AREAS OF EACH CLASS
# Load drivers etc.
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvR = gdal.GetDriverByName('ENVI')
drvMemV = ogr.GetDriverByName('Memory')
drvMemR = gdal.GetDriverByName('MEM')
# Open the Shapefile
sh_open = ogr.Open(shape, 1)
lyr = sh_open.GetLayer()
pol_srs = lyr.GetSpatialRef()
# Open the raster
ras_open = gdal.Open(classification, GA_ReadOnly)
gt = ras_open.GetGeoTransform()
pr = ras_open.GetProjection()
cols = ras_open.RasterXSize
rows = ras_open.RasterYSize
# Build the coordinate transformation
ras_srs = ras_open.GetProjection()
target_SR = osr.SpatialReference()
target_SR.ImportFromWkt(ras_srs)
transform = osr.CoordinateTransformation(pol_srs, target_SR)
# Loop through features
print("")
feat = lyr.GetNextFeature()
while feat:
# Get the Unique-ID for the print-statement
    id = feat.GetField("UniqueID")
    print("Processing polygon with Unique-ID:", id)
# Create a geometry and apply the coordinate transformation
    geom = feat.GetGeometryRef()
    geom.Transform(transform)
# Create new SHP-file in memory to which we copy the geometry
    shpMem = drvMemV.CreateDataSource('')
    shpMem_lyr = shpMem.CreateLayer('shpMem', target_SR, geom_type = ogr.wkbMultiPolygon)
    shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
    shpMem_feat = ogr.Feature(shpMem_lyr_defn)
    shpMem_feat.SetGeometry(geom.Clone())
    shpMem_lyr.CreateFeature(shpMem_feat)
# Load new SHP-file into array
    x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
    x_res = int((x_max - x_min) / 30) # 30 here is because of the Landsat resolution
    y_res = int((y_max - y_min) / 30)
    shpMem_asRaster = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
    shpMem_asRaster.SetProjection(ras_srs)
    shpMem_asRaster.SetGeoTransform((x_min, 30, 0, y_max, 0, -30))
    shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
    shpMem_asRaster_b.SetNoDataValue(255)
    gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
    shpMem_array = np.array(shpMem_asRaster_b.ReadAsArray())
# Subset the classification raster and load it into the array
    rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, gdal.GDT_Byte)
    rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
    rasMem.SetProjection(shpMem_asRaster.GetProjection())
    gdal.ReprojectImage(ras_open, rasMem, pr, shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
    rasMem_array = np.array(rasMem.GetRasterBand(1).ReadAsArray())
# Now mask out the areas outside the buffer (shpMem_array = 0)
    inBuff_array = rasMem_array
    np.putmask(inBuff_array, shpMem_array == 0, 999)
# Loop through each of the classes, extract the number of pixels, convert pixels into km2
    for cl in classes:
        val = cl[0]
        #nr_px = (inBuff_array == val).sum())
        nr_px = np.count_nonzero(inBuff_array == val)
        area = (nr_px*900)/1000000
        # Write area into input-shapefile
        feat.SetField(cl[1], area)
        lyr.SetFeature(feat)
# Destroy all memory elements
    shpMem.Destroy()
    shpMem_feat.Destroy()
    shpMem_asRaster = None
    shpMem_asRaster = None
    shpMem_array = None
    rasMem = None
    rasMem_array = None
    inBuff_array = None
# Get the next feature
    feat = lyr.GetNextFeature()
lyr.ResetReading()

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")