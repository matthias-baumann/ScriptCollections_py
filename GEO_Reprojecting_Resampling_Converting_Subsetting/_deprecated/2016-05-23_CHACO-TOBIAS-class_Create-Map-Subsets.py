# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import gdal
import ogr, osr
from gdalconst import *
import numpy as np
from ZumbaTools._FileManagement_Tools import *
from ZumbaTools._Raster_Tools import *
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvR = gdal.GetDriverByName('HFA')
drvMemV = ogr.GetDriverByName('Memory')
drvMemR = gdal.GetDriverByName('MEM')
classification = gdal.Open(
    "D:/Matthias/Projects-and-Publications/Projects_Active/PASANOA/baumann-etal_LandCoverMaps_SingleYears/run12_classification_full_masked_clump-eliminate4px_reclass_V02.img", GA_ReadOnly)
subShape = drvMemV.CopyDataSource(ogr.Open("D:/New_Shapefile.shp"),'')
identifier= "Name"
outputFolder = "D:/"
# ####################################### PROCESSING ########################################################## #
# Get the properties of the files
gt = classification.GetGeoTransform()
pr = classification.GetProjection()
cols = classification.RasterXSize
rows = classification.RasterYSize
# Build the coordinate transformation
lyr = subShape.GetLayer()
point_srs = lyr.GetSpatialRef()
ras_srs = classification.GetProjection()
target_SR = osr.SpatialReference()
target_SR.ImportFromWkt(ras_srs)
transform = osr.CoordinateTransformation(point_srs, target_SR)
# Make the subsets
feat = lyr.GetNextFeature()
while feat:
    id = feat.GetField(identifier)
    print("Processing Point-ID:", str(id))
# Transform coordinates of points to raster coordinates
    geom = feat.GetGeometryRef()
    geom.Transform(transform)
# Create a temporary shape file in memory, into which we copy the buffer
    tmpSHPmem = drvMemV.CreateDataSource('')
    #buffSHPmem = drvV.CreateDataSource("D:/shpout.shp")
    tmpSHPmem_lyr = tmpSHPmem.CreateLayer('shpMem', target_SR, geom_type = ogr.wkbMultiPolygon)
    tmpSHPmem_lyr_defn = tmpSHPmem_lyr.GetLayerDefn()
    tmpSHPmem_feat = ogr.Feature(tmpSHPmem_lyr_defn)
    tmpSHPmem_feat.SetGeometry(geom)
    tmpSHPmem_lyr.CreateFeature(tmpSHPmem_feat)
# Rasterize the shapefile
    x_min, x_max, y_min, y_max = tmpSHPmem_lyr.GetExtent()
    cols_sub = int((x_max - x_min) / 30) # 30 here is because of Landsat resolution
    rows_sub = int((y_max - y_min) / 30)
    shpMem_asRaster = drvMemR.Create('', cols_sub, rows_sub, gdal.GDT_Byte)
    shpMem_asRaster.SetProjection(ras_srs)
    shpMem_asRaster.SetGeoTransform((x_min, 30, 0, y_max, 0, -30))
    shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
    shpMem_asRaster_b.SetNoDataValue(255)
    gdal.RasterizeLayer(shpMem_asRaster, [1], tmpSHPmem_lyr, burn_values=[1])
# Subset the classification raster and load it into the array
    rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, gdal.GDT_Byte)
    rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
    rasMem.SetProjection(shpMem_asRaster.GetProjection())
    gdal.ReprojectImage(classification, rasMem, pr, shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
# Now mask out the areas that are outside the buffer, set NoData value
    shpMem_array = np.array(shpMem_asRaster_b.ReadAsArray())
    rasMem_array = np.array(rasMem.GetRasterBand(1).ReadAsArray())
    np.putmask(rasMem_array, shpMem_array == 0, 0)
    rasMem.GetRasterBand(1).WriteArray(rasMem_array)
    rasMem.GetRasterBand(1).SetNoDataValue(0)
# Write clipped raterfile to output
    outFileName = outputFolder + str(id) + ".tif"
    CopyMEMtoDisk(rasMem, outFileName)
# Switch to next feature
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