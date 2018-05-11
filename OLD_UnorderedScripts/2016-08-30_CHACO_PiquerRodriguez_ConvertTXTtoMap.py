# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import math
import gdal, osr
from gdalconst import *
import numpy as np
from ZumbaTools._Raster_Tools import *
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvR = gdal.GetDriverByName('GTiff')
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemR = gdal.GetDriverByName('MEM')
drvMemV = ogr.GetDriverByName('Memory')
#inputFolder = "Y:/_SHARED_DATA/MPR_MB/neighb_matrices/_Run_20160916/"
#outputFolder = "Y:/_SHARED_DATA/MPR_MB/neighb_matrices/_Run_20160916/Maps/"
inputFolder = "R:/biogeo-lab/SAN_BioGeo/_SHARED_DATA/MPR_MB/neighb_matrices/_Run_20160928/"
outputFolder = "R:/biogeo-lab/SAN_BioGeo/_SHARED_DATA/MPR_MB/neighb_matrices/_Run_20160928/Maps/"
fileEnding = "_SummaryOutput.txt"
#maskShape = drvMemV.CopyDataSource(ogr.Open("Y:/_SHARED_DATA/MPR_MB/neighb_matrices/scenarios_study_area_shp/nrm_scenarios_study_area.shp"),'')
maskShape = drvMemV.CopyDataSource(ogr.Open("R:/biogeo-lab/SAN_BioGeo/_SHARED_DATA/MPR_MB/neighb_matrices/scenarios_study_area_shp/nrm_scenarios_study_area.shp"),'')
#maskRaster = OpenRasterToMemory("Y:/_SHARED_DATA/MPR_MB/neighb_matrices/_LU2010_20151216.tif")
# ####################################### PROCESSING ########################################################## #
processList = [inputFolder + file for file in os.listdir(inputFolder) if file.endswith(fileEnding)]
for file in processList:
    print(file)
# (1) Convert txt-file to shapefile
    print("--> Read values from txt-File.")
# (1-1) Get all the coordinate information from the txt-file
    txt_open = open(file, "r")
    coords = []
    next(txt_open) # To skip the first row, which is the header
    for line in txt_open:
        tupel = []
        p = line.find(",")
        val = float(line[:p]) # UID
        tupel.append(val)
        line = line[p+1:]
        p = line.find(",")
        val = float(line[:p]) # x-Coordinate
        tupel.append(val)
        line = line[p+1:]
        p = line.find(",")
        val = float(line[:p]) # y-Coordinate
        tupel.append(val)
        p = line.rfind(",")
        val = line[p+1:] # Raster Value
        if val == "NA\n":
            val = 0
        else:
            val = int(val)
        tupel.append(val)
        coords.append(tupel)
    txt_open.close()
# (1-2) Build shapefile in memory based on the new tupel
# (1-2-1) Build empty shapefile, with UID and VALUE as fields
    print("--> Build shapefile.")
    SR = osr.SpatialReference()
    SR.ImportFromEPSG(32720)
    shpMem = drvMemV.CreateDataSource('')
    #shpMem = drvV.CreateDataSource("Y:/_SHARED_DATA/MPR_MB/neighb_matrices/_Run_20160829_Output_100runs/Maps/1.shp")
    shpMem_lyr = shpMem.CreateLayer('shpMem', SR, geom_type=ogr.wkbPoint)
    UIDfield = ogr.FieldDefn('UID', ogr.OFTString)
    shpMem_lyr.CreateField(UIDfield)
    classField = ogr.FieldDefn('Value', ogr.OFTInteger)
    shpMem_lyr.CreateField(classField)
# (1-2-2) Loop through tupel list and build the shapefile point-by-point
    for c in coords:
        UID, x, y, val = c
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x, y)
        featDef = shpMem_lyr.GetLayerDefn()
        feat = ogr.Feature(featDef)
        feat.SetGeometry(point)
        feat.SetField('UID', UID)
        feat.SetField('Value', val)
        shpMem_lyr.CreateFeature(feat)
# (1-3) Convert shapefile to raster
    print("--> Build raster.")
    x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
    x_res = int(math.ceil((x_max - x_min) / float(1000.0)))
    y_res = int(math.ceil((y_max - y_min) / float(1000.0)))
    x_minGT = x_min - 500 # Important: to put the first point a little bit towards the center in x-direction, so that we don't get the black line of 0-pixels in the middle
    out_gt = ((x_minGT, 1000, 0, y_max, 0, -1000))
    pointAsRaster = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
    pointAsRaster.SetGeoTransform(out_gt)
    pointAsRaster.SetProjection(SR.ExportToWkt())
    pointAsRaster_rb = pointAsRaster.GetRasterBand(1)
    pointAsRaster_rb.SetNoDataValue(99)
    gdal.RasterizeLayer(pointAsRaster, [1], shpMem_lyr, options=["ATTRIBUTE=Value"])
# (1-4) Mask out areas outside the study region --> assign value of 99
    frameLYR = maskShape.GetLayer()
    frame_ras = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
    frame_ras.SetProjection(SR.ExportToWkt())
    frame_ras.SetGeoTransform(out_gt)
    frame_rb = frame_ras.GetRasterBand(1)
    gdal.RasterizeLayer(frame_ras, [1], frameLYR, options=["ATTRIBUTE=OBJECTID"])
    frame_array = np.array(frame_rb.ReadAsArray())
    LC_array = np.array(pointAsRaster_rb.ReadAsArray())
    out = np.where((frame_array == 1), LC_array, 99)
    pointAsRaster_rb.WriteArray(out, 0, 0)
# (1-4) Write output to disk
    print("--> Write to disk")
    p = file.rfind("/")
    outname = outputFolder + file[p+1:]
    outname = outname.replace("_SummaryOutput.txt", ".tif")
    CopyMEMtoDisk(pointAsRaster, outname)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")