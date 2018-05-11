# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import gdal, ogr
from gdalconst import *
from ZumbaTools._Raster_Tools import *
from ZumbaTools._Vector_Tools import *
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
#inVRT = "H:/Baltrak/03_Classification/02_NewExtent/ClassRuns/Run08_VRT.vrt"
LandsatOutlineSHP = "H:/Baltrak/00_SHP/LandsatFootprints_StudyArea_large_20151107_dissolve.shp"
outSieve = "H:/Baltrak/03_Classification/02_NewExtent/ClassRuns/Run08_ClumpSieve_10px.tif"
#outMasked = "H:/Baltrak/03_Classification/02_NewExtent/ClassRuns/Run08_ClumpSieve_10px_masked.tif"
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvR = gdal.GetDriverByName('GTiff')
drvMemV = ogr.GetDriverByName('Memory')
drvMemR = gdal.GetDriverByName('MEM')
# #### (1) Clunmp-Sieve the image
print("Do clump/sieve")
clumpSieve = ClumpEliminate(inVRT, 8, 10)
# #### (2) Mask out by shapeoutline
print("Mask by shapeoutline")
# Build the coordinate transformation
ras_srs = clumpSieve.GetProjection()
gt = clumpSieve.GetGeoTransform()
cols = clumpSieve.RasterXSize
rows = clumpSieve.RasterYSize
shp = ogr.Open(LandsatOutlineSHP)
lyr = shp.GetLayer()
pol_srs = lyr.GetSpatialRef()
target_SR = osr.SpatialReference()
target_SR.ImportFromWkt(ras_srs)
transform = osr.CoordinateTransformation(pol_srs, target_SR)
feat = lyr.GetNextFeature()
geom = feat.GetGeometryRef()
geom.Transform(transform)
# Create new SHP-file in memory to which we copy the geometry
shpMem = drvMemV.CreateDataSource('')
shpMem_lyr = shpMem.CreateLayer('shpMem', target_SR, geom_type=ogr.wkbMultiPolygon)
shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
shpMem_feat = ogr.Feature(shpMem_lyr_defn)
shpMem_feat.SetGeometry(geom.Clone())
shpMem_lyr.CreateFeature(shpMem_feat)
# Make a raster out of the shapefile
shpMem_asRaster = drvMemR.Create('', cols, rows, gdal.GDT_Byte)
shpMem_asRaster.SetProjection(ras_srs)
shpMem_asRaster.SetGeoTransform(gt)
shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
shpMem_asRaster_b.SetNoDataValue(255)
gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
# Now mask the vrt file --> process oldschool row by row
out = drvMemR.Create('', cols, rows, 1, gdal.GDT_Byte)
out.SetProjection(ras_srs)
out.SetGeoTransform(gt)
for row in range(rows):
    clas = clumpSieve.GetRasterBand(1).ReadAsArray(0, row, cols, 1)
    mask = shpMem_asRaster.GetRasterBand(1).ReadAsArray(0, row, cols, 1)
    outArray = clas
    np.putmask(outArray, mask == 0, 0)
    out.GetRasterBand(1).WriteArray(outArray, 0, row)
# #### (3) WRITE OUTPUTS
print("Write Outputs")
CopyMEMtoDisk(clumpSieve, outSieve)
CopyMEMtoDisk(out, outMasked)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")