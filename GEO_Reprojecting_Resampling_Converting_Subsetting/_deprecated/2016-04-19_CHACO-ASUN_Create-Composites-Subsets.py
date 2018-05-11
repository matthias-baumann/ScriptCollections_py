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
composite1985 = gdal.Open("E:/Baumann/CHACO/_Composites_5yearIntervals/1985_Imagery_VRT.vrt", GA_ReadOnly)
composite2005 = gdal.Open("E:/Baumann/CHACO/_Composites_5yearIntervals/2005_Imagery_VRT.vrt", GA_ReadOnly)
composite2010 = gdal.Open("E:/Baumann/CHACO/_Composites_5yearIntervals/2010_Imagery_VRT.vrt", GA_ReadOnly)
subsetShape = drvMemV.CopyDataSource(ogr.Open("L:/biogeo-lab/SAN_BioGeo/_SHARED_DATA/ASP_MB/ARG_adm1_studyarea_dissolve.shp"),'')
outputFolder = "L:/biogeo-lab/SAN_BioGeo/_SHARED_DATA/ASP_MB/"
# ####################################### PROCESSING ########################################################## #
# Get the properties of the files
gt = composite1985.GetGeoTransform()
pr = composite1985.GetProjection()
cols = composite1985.RasterXSize
rows = composite1985.RasterYSize
# Build the coordinate transformation
lyr = subsetShape.GetLayer()
point_srs = lyr.GetSpatialRef()
ras_srs = composite1985.GetProjection()
target_SR = osr.SpatialReference()
target_SR.ImportFromWkt(ras_srs)
transform = osr.CoordinateTransformation(point_srs, target_SR)
# Get the polygon-feature
feat = lyr.GetNextFeature()
print("Building raster from polygon in memory")
# Create a temporary shapefile in memory to make the coordinate transformation, then rasterize the layer
geom = feat.GetGeometryRef()
geom.Transform(transform)
# Create a temporary shape file in memory, into which we copy the buffer
SHPmem = drvMemV.CreateDataSource('')
SHPmem_lyr = SHPmem.CreateLayer('shpMem', target_SR, geom_type = ogr.wkbMultiPolygon)
SHPmem_lyr_defn = SHPmem_lyr.GetLayerDefn()
SHPmem_feat = ogr.Feature(SHPmem_lyr_defn)
SHPmem_feat.SetGeometry(geom)
SHPmem_lyr.CreateFeature(SHPmem_feat)
x_min, x_max, y_min, y_max = SHPmem_lyr.GetExtent()
cols_sub = int((x_max - x_min) / 30) # 30 here is because of Landsat resolution
rows_sub = int((y_max - y_min) / 30)
shpMem_asRaster = drvMemR.Create('', cols_sub, rows_sub, gdal.GDT_Byte)
shpMem_asRaster.SetProjection(ras_srs)
shpMem_asRaster.SetGeoTransform((x_min, 30, 0, y_max, 0, -30))
shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
shpMem_asRaster_b.SetNoDataValue(255)
gdal.RasterizeLayer(shpMem_asRaster, [1], SHPmem_lyr, burn_values=[1])
# Subset the three composites
print("Subsetting the composites")
print("1985")
rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 6, composite1985.GetRasterBand(1).DataType)
rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
rasMem.SetProjection(shpMem_asRaster.GetProjection())
gdal.ReprojectImage(composite1985, rasMem, pr, shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
outFileName = outputFolder + "1985_composite.bsq"
CopyMEMtoDisk(rasMem, outFileName)
print("2005")
rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 6, composite2005.GetRasterBand(1).DataType)
rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
rasMem.SetProjection(shpMem_asRaster.GetProjection())
gdal.ReprojectImage(composite2005, rasMem, pr, shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
outFileName = outputFolder + "2005_composite.bsq"
CopyMEMtoDisk(rasMem, outFileName)
print("2010")
rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 6, composite2010.GetRasterBand(1).DataType)
rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
rasMem.SetProjection(shpMem_asRaster.GetProjection())
gdal.ReprojectImage(composite2010, rasMem, pr, shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
outFileName = outputFolder + "2010_composite.bsq"
CopyMEMtoDisk(rasMem, outFileName)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #		
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")