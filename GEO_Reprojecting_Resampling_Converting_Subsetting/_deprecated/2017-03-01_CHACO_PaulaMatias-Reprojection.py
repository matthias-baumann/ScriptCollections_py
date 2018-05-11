# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time, os
import gdal, osr, ogr
from gdalconst import *
import numpy as np
import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
drvMemV = ogr.GetDriverByName('Memory')
drvV = ogr.GetDriverByName('ESRI Shapefile')
outputFolder = "Z:/_SHARED_DATA/4Paula/_Reprojected/"
pr = gdal.Open("F:/Projects-and-Publications/Publications/Publications-accepted/2016_Baumann-etal_Chaco-LCLUC_Carbon/run12_classification_full_masked_clump-eliminate4px_reclass_V02.img", GA_ReadOnly).GetProjection()
referenceRaster = gdal.Open("F:/Projects-and-Publications/Publications/Publications-accepted/2016_Baumann-etal_Chaco-LCLUC_Carbon/run12_classification_full_masked_clump-eliminate4px_reclass_V02.img", GA_ReadOnly)
chaco = bt.baumiVT.CopyToMem("Z:/_SHARED_DATA/4Paula/_Reprojected/Chaco_Boundary_Ref.shp")
# ####################################### FUNCTIONS ########################################################### #
def ReprojectRaster(inRaster, refRaster, nearest_cubic):
    in_pr = inRaster.GetProjection()
    in_gt = inRaster.GetGeoTransform()
    out_pr = refRaster.GetProjection()
    out_gt = refRaster.GetGeoTransform()
    out_cols = refRaster.RasterXSize
    out_rows = refRaster.RasterYSize
    dtype = inRaster.GetRasterBand(1).DataType
    outfile = drvMemR.Create('', out_cols, out_rows, 1, dtype)
    outfile.SetProjection(out_pr)
    outfile.SetGeoTransform(out_gt)
    if nearest_cubic == "cubic":
        res = gdal.ReprojectImage(inRaster, outfile, in_pr, out_pr, gdal.GRA_Cubic)
    if nearest_cubic == "nearest":
        res = gdal.ReprojectImage(inRaster, outfile, in_pr, out_pr, gdal.GRA_NearestNeighbour)
    return outfile
def ReprojectShape(inShape, outProj):
# Open the layer of the input shapefile
    lyr = inShape.GetLayer()
# Build the coordinate Transformation
    inPR = lyr.GetSpatialRef()
    outPR = osr.SpatialReference()
    outPR.ImportFromWkt(outProj)
    transform = osr.CoordinateTransformation(inPR, outPR)
# Create the output-SHP and LYR, get geometry type first
    feat = lyr.GetNextFeature()
    geom = feat.GetGeometryRef()
    geomType = geom.GetGeometryType()
    lyr.ResetReading()
    outSHP = drvMemV.CreateDataSource('')
    outLYR = outSHP.CreateLayer('outSHP', outPR, geom_type=geomType)
# Create all fields in the new shp-file that we created before
    inLayerDefn = lyr.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLYR.CreateField(fieldDefn)
# get the output layer's feature definition
    outLYRDefn = outLYR.GetLayerDefn()
# Now loop through the features from the inSHP, transform geometries, add to new SHP and also take the values in the attributes
    feat = lyr.GetNextFeature()
    while feat:
        geom = feat.GetGeometryRef()
        geom.Transform(transform)
        outFeat = ogr.Feature(outLYRDefn)
        outFeat.SetGeometry(geom)
        for i in range(0, outLYRDefn.GetFieldCount()):
            outFeat.SetField(outLYRDefn.GetFieldDefn(i).GetNameRef(), feat.GetField(i))
        outLYR.CreateFeature(outFeat)
# Destroy/Close the features and get next input-feature
        outFeat.Destroy()
        feat.Destroy()
        feat = lyr.GetNextFeature()
    return outSHP
# ####################################### FILE LISTS ########################################################## #
shpList = [
    ["Z:/_SHARED_DATA/4Paula/Freshwater/01_EspejosDeAgua_ManualSubset_UTM20S_extended.shp","01_EspejosDeAgua_clip_LAEA.shp"],
    ["Z:/_SHARED_DATA/4Paula/Freshwater/cursos_agua_poly_UTM20S.shp","cursos_agua_poly_clip_LAEA.shp"],
    ["Z:/_SHARED_DATA/4Paula/Suelos-de-la-Republica-Argentina-1-500.000_2/suelos_500000_v9.shp", "Suelos-de-la-Republica-Argentina-1-500.000_clip_LAEA.shp"],
    #["Z:/_SHARED_DATA/4Paula/Inventario_Forestal_Nacional/TOTAL_PAIS/COBERTURAS_LCCS/BAP/BAP_LCCS.shp","InventarioForestal_COBERTURAS_LCCS_BAP_LCCS_clip_LAEA.shp"],
    ["Z:/_SHARED_DATA/4Paula/Inventario_Forestal_Nacional/TOTAL_PAIS/COBERTURAS_LCCS/ESP/ESP_LCCS.shp","InventarioForestal_COBERTURAS_LCCS_ESP_LCCS_clip_LAEA.shp" ],
    #["Z:/_SHARED_DATA/4Paula/Inventario_Forestal_Nacional/TOTAL_PAIS/COBERTURAS_LCCS/MON/MON_LCCS.shp","InventarioForestal_COBERTURAS_LCCS_MON_LCCS_clip_LAEA.shp"],
    ["Z:/_SHARED_DATA/4Paula/Inventario_Forestal_Nacional/TOTAL_PAIS/COBERTURAS_LCCS/PCH/PCH_LCCS.shp","InventarioForestal_COBERTURAS_LCCS_PCH_LCCS_clip_LAEA.shp"],
    #["Z:/_SHARED_DATA/4Paula/Inventario_Forestal_Nacional/TOTAL_PAIS/COBERTURAS_LCCS/SM/SM_LCCS.shp","InventarioForestal_COBERTURAS_LCCS_SM_LCCS_clip_LAEA.shp"],
    ["Z:/_SHARED_DATA/4Paula/Inventario_Forestal_Nacional/TOTAL_PAIS/COBERTURAS_LCCS/STB/STB_LCCS.shp","InventarioForestal_COBERTURAS_LCCS_STB_LCCS_clip_LAEA.shp"],
    #["Z:/_SHARED_DATA/4Paula/Inventario_Forestal_Nacional/TOTAL_PAIS/COBERTURAS_UMSEF/BAP/BAP_LCCS.shp","InventarioForestal_COBERTURAS_UMSEF_BAP_LCCS_clip_LAEA.shp"],
    #["Z:/_SHARED_DATA/4Paula/Inventario_Forestal_Nacional/TOTAL_PAIS/COBERTURAS_UMSEF/ESP/ESP_LCCS.shp","InventarioForestal_COBERTURAS_UMSEF_ESP_LCCS_clip_LAEA.shp"],
    #["Z:/_SHARED_DATA/4Paula/Inventario_Forestal_Nacional/TOTAL_PAIS/COBERTURAS_UMSEF/MON/MON_LCCS.shp","InventarioForestal_COBERTURAS_UMSEF_MON_LCCS_clip_LAEA.shp"],
    #["Z:/_SHARED_DATA/4Paula/Inventario_Forestal_Nacional/TOTAL_PAIS/COBERTURAS_UMSEF/PCH/PCH_LCCS.shp","InventarioForestal_COBERTURAS_UMSEF_PCH_LCCS_clip_LAEA.shp"],
    #["Z:/_SHARED_DATA/4Paula/Inventario_Forestal_Nacional/TOTAL_PAIS/COBERTURAS_UMSEF/SM/SM_LCCS.shp","InventarioForestal_COBERTURAS_UMSEF_SM_LCCS_clip_LAEA.shp"],
    #["Z:/_SHARED_DATA/4Paula/Inventario_Forestal_Nacional/TOTAL_PAIS/COBERTURAS_UMSEF/STB/STB_LCCS.shp","InventarioForestal_COBERTURAS_UMSEF_STB_LCCS_clip_LAEA.shp"],
]
rasList = [
    ["Z:/_SHARED_DATA/4Paula/DEM250_south_america.tif","DEM250_south_america_clip_LAEA.tif"]
]

# LOOP THROUGH THE SHAPES
for shp in shpList:
    print(shp)
    inSHP = bt.baumiVT.CopyToMem(shp[0])
    outname = outputFolder + shp[1]
    if not os.path.exists(outname):
# Clip to Chaco-extent, reproject
        #clip = bt.baumiVT.ClipSHPbySHP(inSHP, chaco)
        clip_pr = ReprojectShape(inSHP, pr)
# Write  output
        bt.baumiVT.CopySHPDisk(clip_pr, outname)
# LOOP THROUGH THE RASTERS
for ras in rasList:
    print(ras)
    inRas = gdal.Open(ras[0], GA_ReadOnly)
    outname = outputFolder + ras[1]
    if not os.path.exists(outname):
        outRas = ReprojectRaster(inRas,referenceRaster, "cubic")
        bt.baumiRT.CopyMEMtoDisk(outRas, outname)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")