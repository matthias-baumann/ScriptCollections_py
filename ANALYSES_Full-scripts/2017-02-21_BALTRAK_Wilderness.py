# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal, ogr
from gdalconst import *
import numpy as np
import baumiTools
import math
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
drvMemV = ogr.GetDriverByName('Memory')
outputFolder = "F:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/05_Wilderness_LivestockDisaggreg_InputData/_WildernessRuns/20170227_Run10/"
baseFolder = "F:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/05_Wilderness_LivestockDisaggreg_InputData/"
settShape = drvMemV.CopyDataSource(ogr.Open("F:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/05_Wilderness_LivestockDisaggreg_InputData/01b_Settlements/BALTRAK_allsettlements_finished_2017_02_06.shp"),'')
# ####################################### FUNCTIONS ########################################################### #
def Reproject(inRaster, refRaster):
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
    res = gdal.ReprojectImage(inRaster, outfile, in_pr, out_pr, gdal.GRA_Cubic)
    return outfile
def Normalize(inRaster, min, max):
# Create Output-File
    pr = inRaster.GetProjection()
    gt = inRaster.GetGeoTransform()
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    output = drvMemR.Create('', cols, rows, 1, GDT_Float32)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
# Do the raster-calculation
    rb = inRaster.GetRasterBand(1)
    out_rb = output.GetRasterBand(1)
    ar = rb.ReadAsArray(0, 0, cols, rows)
    #out = np.zeros(ar.shape, dtype='uint16')
    out = (ar - min)/(max-min)
    #out = out * 10000
    out[out < 0] = 0
    out_rb.WriteArray(out, 0, 0)
    return output
def CalcWindernessSum(ListOfRasters):
    # Create Output-File
    pr = ListOfRasters[0].GetProjection()
    gt = ListOfRasters[0].GetGeoTransform()
    cols = ListOfRasters[0].RasterXSize
    rows = ListOfRasters[0].RasterYSize
    output = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
    out_rb = output.GetRasterBand(1)
    # Do the raster-calculation
    rb1 = ListOfRasters[0].GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    rb2 = ListOfRasters[1].GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    rb3 = ListOfRasters[2].GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    out = rb1 + rb2 + rb3
    out_rb.WriteArray(out, 0, 0)
    return(output)
def MaskRaster(inRaster, extent, activeVal):
    # Create Output-File
    pr = inRaster.GetProjection()
    gt = inRaster.GetGeoTransform()
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    dtype = inRaster.GetRasterBand(1).DataType
    output = drvMemR.Create('', cols, rows, 1, dtype)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
    # Do the raster-calculation
    rb_in = inRaster.GetRasterBand(1)
    rb_ext = extent.GetRasterBand(1)
    rb_out = output.GetRasterBand(1)
    rb_out.SetNoDataValue(99)
    ar_in = rb_in.ReadAsArray(0, 0, cols, rows)
    ar_ext = rb_ext.ReadAsArray(0, 0, cols, rows)
    out = np.where((ar_ext == activeVal), ar_in, 99)
    rb_out.WriteArray(out, 0, 0)
    return output
def CalcDistances(LYRsubset, pr, gt, pxSize, extSHP):
# Get geometry information from the refRaster
    x_min, x_max, y_min, y_max = extSHP.GetExtent()
# Now rasterize the layer
    shp = drvMemV.CreateDataSource("shp")
    shpLYR = shp.CopyLayer(LYRsubset, 'shp')
    x_res = int((x_max - x_min) / pxSize)
    y_res = int((y_max - y_min) / pxSize)
    shpRas = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
    shpRas.SetProjection(pr)
    shpRas.SetGeoTransform((x_min, pxSize, 0, y_max, 0, -pxSize))
    shpRas_rb = shpRas.GetRasterBand(1)
    gdal.RasterizeLayer(shpRas, [1], shpLYR, burn_values=[1])
# Calculate the distance
    shpDis = drvMemR.Create('', x_res, y_res, 1, GDT_Int16)
    shpDis.SetProjection(pr)
    shpDis.SetGeoTransform((x_min, pxSize, 0, y_max, 0, -pxSize))
    shpDis_band = shpDis.GetRasterBand(1)
    shpRas_rb = shpRas.GetRasterBand(1)
    creationoptions = ['VALUES=1', 'DISTUNITS=PIXEL']
    gdal.ComputeProximity(shpRas_rb, shpDis_band, creationoptions)
    return(shpDis)
def StackLayers(ListOfRasters):
    pr = ListOfRasters[0].GetProjection()
    gt = ListOfRasters[0].GetGeoTransform()
    cols = ListOfRasters[0].RasterXSize
    rows = ListOfRasters[0].RasterYSize
    output = drvMemR.Create('', cols, rows, 3, gdal.GDT_Float32)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
    b = 1
    for raster in ListOfRasters:
        rb = raster.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
        output.GetRasterBand(b).WriteArray(rb, 0, 0)
        b = b+1
    return output
def InvertValues(inRaster):
    # Create Output-File
    pr = inRaster.GetProjection()
    gt = inRaster.GetGeoTransform()
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    output = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
    # Do the raster-calculation
    arr = inRaster.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    arr_in = arr - 1
    arr_in = np.negative(arr_in)
    output.GetRasterBand(1).WriteArray(arr_in, 0, 0)
    return(output)
def FindMinMax(raster90, raster15):
    arr90 = raster90.GetRasterBand(1).ReadAsArray(0, 0, raster90.RasterXSize, raster90.RasterYSize)
    arr15 = raster15.GetRasterBand(1).ReadAsArray(0, 0, raster15.RasterXSize, raster15.RasterYSize)
    minAll = min(np.min(arr90), np.min(arr15))
    minAll = 0 if minAll < 0 else minAll
    flat90 = np.unique(arr90.flatten())
    flat90.sort()
    max90 = flat90[-2]
    flat15 = np.unique(arr15.flatten())
    flat15.sort()
    max15 = flat15[-2]
    maxAll = max(max90, max15)
    return minAll, maxAll
def CalcDiff(raster90, raster15):
# Create Output-File
    pr = raster90.GetProjection()
    gt = raster90.GetGeoTransform()
    cols = raster90.RasterXSize
    rows = raster90.RasterYSize
    output = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
# Calculate the difference
    arr90 = raster90.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    arr15 = raster15.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    out = arr90 - arr15
    output.GetRasterBand(1).WriteArray(out, 0, 0)
    return output
# ####################################### PROCESSING ########################################################## #
# #### GENERATE THE EXTENT POLYGON
print("Generate extent layer")
ref = gdal.Open(baseFolder + "03_CroplandData/1990_PercCropland_300m.tif", GA_ReadOnly)
pr = ref.GetProjection()
gt = ref.GetGeoTransform()
pxSize = int(gt[1])
shape = drvMemV.CopyDataSource(ogr.Open(baseFolder + "Extent_V02.shp"),'')
lyr = shape.GetLayer()
x_min, x_max, y_min, y_max = lyr.GetExtent()
x_res = int((x_max - x_min) / pxSize)
y_res = int((y_max - y_min) / pxSize)
shpRas = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
shpRas.SetProjection(pr)
shpRas.SetGeoTransform((x_min, pxSize, 0, y_max, 0, -pxSize))
shpRas_rb = shpRas.GetRasterBand(1)
shpRas_rb.SetNoDataValue(255)
gdal.RasterizeLayer(shpRas, [1], lyr, burn_values=[1])
# GET THE SHAPE-LAYER
settLYR = settShape.GetLayer()
# LOOP THROUGH 10% INCREMENTS OF DESTRUCTION THRESHOLD
threshs = [10 * x for x in range(0,10)]
for th in threshs:
    print("Processing threshold: >=", th, "%")
# Prepare the cropland layers
    crop90 = Reproject(gdal.Open(baseFolder + "03_CroplandData/1990_PercCropland_300m.tif", GA_ReadOnly), shpRas)
    crop15 = Reproject(gdal.Open(baseFolder + "03_CroplandData/2015_PercCropland_300m.tif", GA_ReadOnly), shpRas)
# Select the settlements, based on destruction, calculate distance
    selState = "Category = 'Settlement'"
    settLYR.SetAttributeFilter(selState)
    settDis90 = Reproject(CalcDistances(settLYR, pr, gt, pxSize, lyr), shpRas)
    selState = "Category = 'Settlement' and Status2015 >= " + str(th)
    settLYR.SetAttributeFilter(selState)
    settDis15 = Reproject(CalcDistances(settLYR, pr, gt, pxSize, lyr), shpRas)
# Select Zimovkas and Letovkas, based on destruction, calculate distance
    selState = "Category = 'Zimovka' or Category = 'Letovka'"
    settLYR.SetAttributeFilter(selState)
    ZimLetDis90 = Reproject(CalcDistances(settLYR, pr, gt, pxSize, lyr), shpRas)
    selState = "Category = 'Zimovka' or Category = 'Letovka' and Status2015 >= " + str(th)
    settLYR.SetAttributeFilter(selState)
    ZimLetDis15 = Reproject(CalcDistances(settLYR, pr, gt, pxSize, lyr), shpRas)
# Find max and min values for the normalization
    cropMinMax = FindMinMax(crop90, crop15)
    settMinMax = FindMinMax(settDis90, settDis15)
    ZimLetMinMax = FindMinMax(ZimLetDis90, ZimLetDis90)
# Normalize the layers based on the minimum and maximum values
    crop90norm = MaskRaster(Normalize(crop90, cropMinMax[0], cropMinMax[1]), shpRas, 1)
    crop15norm = MaskRaster(Normalize(crop15, cropMinMax[0], cropMinMax[1]), shpRas, 1)
    settDis90norm = Normalize(settDis90, settMinMax[0], settMinMax[1])
    settDis15norm = Normalize(settDis15, settMinMax[0], settMinMax[1])
    ZimLetDist90norm = Normalize(ZimLetDis90, ZimLetMinMax[0], ZimLetMinMax[1])
    ZimLetDist15norm = Normalize(ZimLetDis15, ZimLetMinMax[0], ZimLetMinMax[1])
# Invert rasters for settlemtns and livestock stations to represent them as measures of human influence
    settDis90norm = MaskRaster(InvertValues(settDis90norm), shpRas, 1)
    settDis15norm = MaskRaster(InvertValues(settDis15norm), shpRas, 1)
    ZimLetDist90norm = MaskRaster(InvertValues(ZimLetDist90norm), shpRas, 1)
    ZimLetDist15norm = MaskRaster(InvertValues(ZimLetDist15norm), shpRas, 1)
# Calculate Wilderness, make binary information
    wild90 = MaskRaster(CalcWindernessSum([crop90norm, settDis90norm, ZimLetDist90norm]), shpRas, 1)
    wild15 = MaskRaster(CalcWindernessSum([crop15norm, settDis15norm, ZimLetDist15norm]), shpRas, 1)
# Calculate differences
    cropDiff = MaskRaster(CalcDiff(crop90norm, crop15norm), shpRas, 1)
    settDiff = MaskRaster(CalcDiff(settDis90norm, settDis15norm), shpRas, 1)
    ZimLetDiff = MaskRaster(CalcDiff(ZimLetDist90norm, ZimLetDist15norm), shpRas, 1)
    wildDiff = MaskRaster(CalcDiff(wild90, wild15), shpRas, 1)
# Write Outputs
    baumiTools.baumiRT.CopyMEMtoDisk(crop90norm, outputFolder + "Thresh_" + str(th) + "_PercCrop_1990.tif")
    baumiTools.baumiRT.CopyMEMtoDisk(crop15norm, outputFolder + "Thresh_" + str(th) + "_PercCrop_2015.tif")
    baumiTools.baumiRT.CopyMEMtoDisk(settDis90norm, outputFolder + "Thresh_" + str(th) + "_DistToSett_1990.tif")
    baumiTools.baumiRT.CopyMEMtoDisk(settDis15norm, outputFolder + "Thresh_" + str(th) + "_DistToSett_2015.tif")
    baumiTools.baumiRT.CopyMEMtoDisk(ZimLetDist90norm, outputFolder + "Thresh_" + str(th) + "_DistToLivestock_1990.tif")
    baumiTools.baumiRT.CopyMEMtoDisk(ZimLetDist15norm, outputFolder + "Thresh_" + str(th) + "_DistToLivestock_2015.tif")
    baumiTools.baumiRT.CopyMEMtoDisk(wild90, outputFolder + "Thresh_" + str(th) + "_WildernessIndex_1990.tif")
    baumiTools.baumiRT.CopyMEMtoDisk(wild15, outputFolder + "Thresh_" + str(th) + "_WildernessIndex_2015.tif")
    baumiTools.baumiRT.CopyMEMtoDisk(cropDiff, outputFolder + "Thresh_" + str(th) + "_PercCrop_Change.tif")
    baumiTools.baumiRT.CopyMEMtoDisk(settDiff, outputFolder + "Thresh_" + str(th) + "_DistToSett_Change.tif")
    baumiTools.baumiRT.CopyMEMtoDisk(ZimLetDiff, outputFolder + "Thresh_" + str(th) + "_DistToLivestock_Change.tif")
    baumiTools.baumiRT.CopyMEMtoDisk(wildDiff, outputFolder + "Thresh_" + str(th) + "_WildernessIndex_Change.tif")

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")