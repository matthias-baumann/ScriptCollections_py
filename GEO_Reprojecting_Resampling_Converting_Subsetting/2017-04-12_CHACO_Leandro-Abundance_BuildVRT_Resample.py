# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time,os
import math
import gdal
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
rootFolder = "G:/Baumann/_ANALYSES/SpeciesPredictions/Run04_20171024/"
ChacoSHP = "G:/Baumann/_ANALYSES/SpeciesPredictions/NADC_Outline.shp"
aggLevel = 1000
# ####################################### PROCESSING ########################################################## #
speciesList = ["Amazonaaes","Ammodramus", "Anthuslute", "Athenecuni", "Cacicuschr", "Camptostom", "Colaptesme",
               "Cranioleuc","Cyanocorax", "Elaeniaalb", "Elaeniaspe", "Elanusleuc", "Embernagra",
               "Furnariusc", "Furnariusr", "Geranoae_1", "Glaucidium", "Hemitriccu", "Icterusict", "Melanerpes",
               "Milvagochi", "Mimustriur", "Myiarchust", "Myiodynast", "Ortaliscan", "Polioptila", "Rheaameric",
               "Setophagap", "Stigmatura", "Thamnophil"]
# Build VRTs
outnames = []
print("Build VRTs...")
for sp in speciesList:
    print(sp)
# Build a VRT from the tiles in folder
    fileList = os.listdir(rootFolder + sp + "/")
    txtTemp = rootFolder + sp + ".txt"
    txt_open = open(txtTemp, "w")
    for item in fileList:
        path = rootFolder + sp + "/" + item
        txt_open.write(path + "\n")
    txt_open.close()
    vrtTemp = rootFolder + sp + ".vrt"
    outnames.append(vrtTemp)
    command = "gdalbuildvrt.exe -overwrite -q -b 1 -input_file_list " + txtTemp + " " + vrtTemp
    os.system(command)
    os.remove(txtTemp)
# Create temp raster for Chaco-SHP
print("")
print("Build Chaco-mask....")
shpMem = bt.baumiVT.CopyToMem(ChacoSHP)
shpLyr = shpMem.GetLayer()
shpFeat = shpLyr.GetNextFeature()
shpGeom = shpFeat.GetGeometryRef()
shpSpatRef = shpGeom.GetSpatialReference()
x_min, x_max, y_min, y_max = shpLyr.GetExtent()
x_res = int((x_max - x_min) / aggLevel)
y_res = int((y_max - y_min) / aggLevel)
shpRas = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
shpRas.SetProjection(str(shpSpatRef))
shpRas.SetGeoTransform((x_min, aggLevel, 0, y_max, 0, -aggLevel))
shpRasBand = shpRas.GetRasterBand(1)
shpRasBand.SetNoDataValue(0)
gdal.RasterizeLayer(shpRas, [1], shpLyr, burn_values=[1])
shpArray = shpRasBand.ReadAsArray()
# Now resample all VRTs to 1000m by applying the average
print("")
print("Resampling now...")
for vrt in outnames:
    print(vrt)
    # Resample
    ds = gdal.Open(vrt, GA_ReadOnly)
    outMem = drvMemR.Create('', shpRas.RasterXSize, shpRas.RasterYSize, 1, GDT_Float32)
    outMem.SetGeoTransform(shpRas.GetGeoTransform())
    outMem.SetProjection(shpRas.GetProjection())
    gdal.ReprojectImage(ds, outMem, ds.GetProjection(), shpRas.GetProjection(), gdal.GRA_Average)
    # Mask out areas outside the Chaco
    outRB = outMem.GetRasterBand(1)
    outRB.SetNoDataValue(0)
    outArray = outRB.ReadAsArray()
    outArray = np.where((shpArray == 0), 0, outArray)
    outRB.WriteArray(outArray,0,0)
    outname = vrt
    outname = outname.replace(".vrt", "_1000m.tif")
    bt.baumiRT.CopyMEMtoDisk(outMem, outname)
    os.remove(vrt)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")