# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal, ogr, osr
from gdalconst import *
import numpy as np
import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
L_Tiles = bt.baumiVT.CopyToMem("G:/CHACO/_COMPOSITING/Tiles_as_Polygons.shp")
outFolder = "E:/Baumann/CHACO/_Composites_ALOS-Palsar_HH/"
ALOS_vrt = gdal.Open("G:/CHACO/ReprojectedScenes/ALOS_PALSAR_extracted/_ALOS_PALSAR_HH.vrt")
ALOS_ref = gdal.Open("G:/CHACO/ReprojectedScenes/ALOS_PALSAR_extracted/S15W051_15_sl_HH_F02DAR")
dType = ALOS_ref.GetRasterBand(1).DataType
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
drvMemR = gdal.GetDriverByName('MEM')
refFile = gdal.Open("E:/Baumann/CHACO/_Composite_Landsat8_2015/Metrics_Nov15/Tile_x0_y0_999x999_2014-2015_CHACO_PBC_multiYear_Metrics.bsq")
outPR = refFile.GetProjection()
# ####################################### GET LAYERS, BUILD TRANSFORM, START ITERATION ######################## #
L_lyr = L_Tiles.GetLayer()
L_PR = L_lyr.GetSpatialRef()
feat_L = L_lyr.GetNextFeature()
while feat_L:
# Check if it is an active tile, if not then skip     Tile_x10999_y55999_1000x1000_2014-2015_CHACO
    active = feat_L.GetField("Active_YN")
    if int(active) == 0:
        feat_L = L_lyr.GetNextFeature()
    else:
        tileName = feat_L.GetField("TileIndex")
    #if tileName == "Tile_x10999_y55999_1000x1000_2014-2015_CHACO":
        print("--> " + tileName)
        geom = feat_L.GetGeometryRef()
        geom_clone = geom.Clone()
    # Create new SHP-file in memory to which we copy the geometry
        shpMem = drvMemV.CreateDataSource('')
        shpMem_lyr = shpMem.CreateLayer('shpMem', L_PR, geom_type=ogr.wkbMultiPolygon)
        shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
        shpMem_feat = ogr.Feature(shpMem_lyr_defn)
        shpMem_feat.SetGeometry(geom)
        shpMem_lyr.CreateFeature(shpMem_feat)
    # Rasterize polygon
        x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
        xSize = int((x_max - x_min) / 30)
        ySize = int((y_max - y_min) / 30)
        shpMem_asRaster = drvMemR.Create('', xSize, ySize, gdal.GDT_Byte)
        shpMem_asRaster.SetProjection(outPR)
        shpMem_asRaster.SetGeoTransform((x_min, 30, 0, y_max, 0, -30))
        shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
        shpMem_asRaster_b.SetNoDataValue(0)
        gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
    # Re-project original sentinel image into new raster
        rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, dType)
        rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
        rasMem.SetProjection(shpMem_asRaster.GetProjection())
        gdal.ReprojectImage(ALOS_vrt, rasMem, ALOS_vrt.GetProjection(), shpMem_asRaster.GetProjection(), gdal.GRA_Cubic)
        bt.baumiRT.CopyMEMtoDisk(rasMem, outFolder + tileName + "_ALOS-PALSAR_HV.tif")
        feat_L = L_lyr.GetNextFeature()
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")