# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time, datetime
import gdal
import ogr, osr
from gdalconst import *
#import struct
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### HARD-CODED FOLDERS AND FILES ######################################## #
classification = "E:/Baumann/LandsatData/999_ClassificationRuns/Run02/LandSystems_1985-2000-2013/Run12_Classification_FULL"
shape = "E:/Baumann/LandsatData/00_shapeFiles/Chaco_boundary_LAEA.shp"
field = "BIOME"
type = "HFA"
# ####################################### GLOBAL FUNCTIONS #################################################### #
def MaskRasterByPolygon(polygon_Input, polygon_field, raster_Input, raster_Output, type_Output): # "GTiff"=tif, "HFA"=img, "ENVI"=bsq
    print("Executing: MaskRasterByPolygon")
    # Make check if all entries of polygon_field[polygon_file] are greater than zero
    checkList = []
    polygon = ogr.Open(polygon_Input)
    lyr = polygon.GetLayer()
    feature = lyr.GetNextFeature()
    while feature:
        value = feature.GetField(polygon_field)
        checkList.append(int(value))
        feature = lyr.GetNextFeature()
    lyr.ResetReading()
    polygon = None
    if 0 in checkList:
        print("Some entries in the Polygon-File contain the value '0'")
        print("Choose field with all Values > 0 and run script again")
        exit(0)
    else:
        # Get pixel size from raster
        in_ds = gdal.Open(raster_Input)
        gt = in_ds.GetGeoTransform()
        pixelsize = gt[1]
        # Convert polygon to raster
        input = polygon_Input
        out_TMP = input
        out_TMP = out_TMP.replace(".shp", "TMPFile.tif")
        # create Layer-Name
        (shpPath, shpName) = os.path.split(input)
        (shapeShort, shapeExt) = os.path.splitext(shpName)
        #command = "gdal_rasterize -l " + shapeShort + " -a " + polygon_field + " -tr " + str(pixelsize) + " " + str(pixelsize) + " -q -of GTiff " + input + " " + out_TMP
        print("Convert Shape-file to raster file")
        command = "E:/Baumann/Scripts/GDAL/gdal_rasterize -ot Byte -l " + shapeShort + " -a " + polygon_field + " -tr " + str(pixelsize) + " " + str(pixelsize) + " -q -of GTiff " + input + " " + out_TMP
        os.system(command)
        # Clip Raster based on extent of temporary raster
        out_TMP02 = out_TMP
        out_TMP02 = out_TMP02.replace(".tif","02.img")
        ds = gdal.Open(out_TMP)
        gt = ds.GetGeoTransform()
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        ext = []
        xarr = [0,cols]
        yarr = [0,rows]
        for px in xarr:
            for py in yarr:
                x = gt[0] + (px*gt[1])+(py*gt[2])
                y = gt[3] + (px*gt[4])+(py*gt[5])
                ext.append([x,y])
            yarr.reverse()
        #command = "gdal_translate -q -ot Byte -of " + type_Output + " -projwin " + str((ext[0][0])) + " " + str((ext[0][1])) + " " + str((ext[2][0])) + " " + str((ext[2][1])) + " " + raster_Input + " " + out_TMP02
        print("Clip raster")
        command = "E:/Baumann/Scripts/GDAL/gdal_translate -q -of " + type_Output + " -projwin " + str((ext[0][0])) + " " + str((ext[0][1])) + " " + str((ext[2][0])) + " " + str((ext[2][1])) + " " + raster_Input + " " + out_TMP02
        os.system(command)
        ds = None
        # Do the masking
        print("Mask raster")
        # (a) Get all information from the input-files
        out_TMP_gdal = gdal.Open(out_TMP)
        out_TMP02_gdal = gdal.Open(out_TMP02)
        cols = out_TMP_gdal.RasterXSize
        rows = out_TMP_gdal.RasterYSize
        rb_TMP = out_TMP_gdal.GetRasterBand(1)
        rb_TMP02 = out_TMP02_gdal.GetRasterBand(1)
        out_dataType = rb_TMP02.DataType
        # (b) build the output-file with the properties
        outDrv = gdal.GetDriverByName(type_Output)
        out = outDrv.Create(raster_Output, cols, rows, 1, out_dataType)
        out.SetProjection(out_TMP02_gdal.GetProjection())
        out.SetGeoTransform(out_TMP02_gdal.GetGeoTransform())
        rb_out = out.GetRasterBand(1)
        rb_out.SetCategoryNames(rb_TMP02.GetCategoryNames())
        rb_out.SetColorTable(rb_TMP02.GetColorTable())
        rb_out.SetNoDataValue(0)
        # (c) Process the raster
        for y in range(rows):
            tmp01 = rb_TMP.ReadAsArray(0,y,cols,1)
            tmp02 = rb_TMP02.ReadAsArray(0,y,cols,1)
            dataOut = tmp02
            np.putmask(dataOut, tmp01 == 0, 0)
            # dataOut.shape = (1,-1)
            rb_out.WriteArray(dataOut, 0,y)
        out_TMP_gdal = None
        out_TMP02_gdal = None
        #rb_out.SetDefaultRAT()
        rb_out = None
        # Remove temp-File
        print("Delete temporary files")
        p = out_TMP.rfind("/")
        folder = out_TMP[:p+1]
        list = os.listdir(folder)
        #s.remove(out_TMP)
        os.remove(out_TMP02)
        extraTMP02 = out_TMP02 + ".aux.xml"
        os.remove(extraTMP02)

# ####################################### START PROCESSING #################################################### #
outfile = "E:/Baumann/LandsatData/999_ClassificationRuns/Run02/LandSystems_1985-2000-2013/Run12_Classification_FULL_masked.img"
MaskRasterByPolygon(shape, field, classification, outfile, type)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #		
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")