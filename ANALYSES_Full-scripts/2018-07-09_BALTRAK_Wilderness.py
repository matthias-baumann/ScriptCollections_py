# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal, ogr
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
root_folder = "Y:/Baumann/BALTRAK/05_Wilderness_LivestockDisaggreg_InputData/"
#outputFolder = root_folder + "_WildernessRuns/20180709_Run13/"
outputFolder = "Y:/Baumann/BALTRAK/Connectivity/"
settShape = bt.baumiVT.CopyToMem(root_folder + "01_Settlements-LivestockStations/BALTRAK_allsettlements_finished_2017_02_06.shp")
extentShape = bt.baumiVT.CopyToMem(root_folder + "Extent_V02.shp")
crop90 = bt.baumiRT.OpenRasterToMemory(root_folder + "02_CroplandData/1990_PercCropland_300m.tif")
crop15 = bt.baumiRT.OpenRasterToMemory(root_folder + "02_CroplandData/2015_PercCropland_300m.tif")
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
def FindMinMax(rasList, mask):
    # Load the mask array
    arrmask = mask.GetRasterBand(1).ReadAsArray(0, 0, mask.RasterXSize, mask.RasterYSize)
    # initialize Min and max
    maxALL = 0
    minALL = 9999999
    # Loop through rasters, and check whether minALL/maxALL need to be updated
    for ras in rasList:
        rasarr = ras.GetRasterBand(1).ReadAsArray(0, 0, ras.RasterXSize, ras.RasterYSize)
        min = np.min(rasarr[arrmask == 1])
        max = np.max(rasarr[arrmask == 1])
        if min < minALL:
            minALL = min
        else:
            min = min
        if max > maxALL:
            maxALL = max
        else:
            max = max
    return minALL, maxALL
def Normalize(inRaster, min, max, invert=False):
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
    # https://math.stackexchange.com/questions/2635331/inverse-normalization-function
    if invert == True:
        out = 1 - (ar - min)/(max-min)
    else:
        out = (ar - min)/(max-min)
    out[out < 0] = 0
    out[out > 1] = 1
    out_rb.WriteArray(out, 0, 0)
    return output
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
def WriteAndMask(valueArray, maskRaster, outname):
    # Create new file as output
    drvR = gdal.GetDriverByName('GTiff')
    outDS = drvR.Create(outname, maskRaster.RasterXSize, maskRaster.RasterYSize, 1, gdal.GDT_Float32)
    outDS.SetProjection(maskRaster.GetProjection())
    outDS.SetGeoTransform(maskRaster.GetGeoTransform())
    outRB = outDS.GetRasterBand(1)
    outRB.SetNoDataValue(99)
    # Load mask array
    maskarr = maskRaster.GetRasterBand(1).ReadAsArray(0, 0, maskRaster.RasterXSize, maskRaster.RasterYSize)
    # do masking
    out = np.where(maskarr == 1, valueArray, 99)
    # Write output
    outRB.WriteArray(out, 0, 0)
# ####################################### PROCESSING ########################################################## #
# #### GENERATE THE EXTENT POLYGON
print("Generate extent layer")
pr = crop90.GetProjection()
gt = crop90.GetGeoTransform()
pxSize = int(gt[1])
lyr = extentShape.GetLayer()
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
# PROCESS THE LAYERS AND WRITE TEMPORARY FILES
print("Generate input layers")
print("Cropland")
crop90_proj = Reproject(crop90, shpRas)
crop15_proj = Reproject(crop15, shpRas)
cropMin, cropMax = FindMinMax([crop90_proj, crop15_proj], shpRas)
crop90norm = Normalize(crop90_proj, cropMin, cropMax)
crop15norm = Normalize(crop15_proj, cropMin, cropMax)
#WriteAndMask(crop90norm.GetRasterBand(1).ReadAsArray(0, 0, crop90norm.RasterXSize, crop90norm.RasterYSize), shpRas, outputFolder + "00_Layers-INPUT/Cropland_1990_normalized.tif")
#WriteAndMask(crop15norm.GetRasterBand(1).ReadAsArray(0, 0, crop15norm.RasterXSize, crop15norm.RasterYSize), shpRas, outputFolder + "00_Layers-INPUT/Cropland_2015_normalized.tif")

print("Distance to settlements")
selState = "Category = 'Settlement'"
settLYR.SetAttributeFilter(selState)
settDis90 = Reproject(CalcDistances(settLYR, pr, gt, pxSize, lyr), shpRas)
def CalcSettDist(th):
    selState = "Category = 'Settlement' and Status2015 >= " + str(th)
    settLYR.SetAttributeFilter(selState)
    settDis15 = Reproject(CalcDistances(settLYR, pr, gt, pxSize, lyr), shpRas)
    return settDis15
settDis15_10 = CalcSettDist(10)
settDis15_50 = CalcSettDist(50)
settDis15_90 = CalcSettDist(90)
settMin, settMax = FindMinMax([settDis90, settDis15_10, settDis15_50, settDis15_90], shpRas)
settDis90norm = Normalize(settDis90, settMin, settMax, invert=True)
settDis15_10norm = Normalize(settDis15_10, settMin, settMax, invert=True)
settDis15_50norm = Normalize(settDis15_50, settMin, settMax, invert=True)
settDis15_90norm = Normalize(settDis15_50, settMin, settMax, invert=True)
#WriteAndMask(settDis90norm.GetRasterBand(1).ReadAsArray(0, 0, settDis90norm.RasterXSize, settDis90norm.RasterYSize), shpRas, outputFolder + "00_Layers-INPUT/Distance-to-settlements_1990_normalized.tif")
#WriteAndMask(settDis15_10norm.GetRasterBand(1).ReadAsArray(0, 0, settDis15_10norm.RasterXSize, settDis15_10norm.RasterYSize), shpRas, outputFolder + "00_Layers-INPUT/Distance-to-settlements_2015_th10_normalized.tif")
#WriteAndMask(settDis15_50norm.GetRasterBand(1).ReadAsArray(0, 0, settDis15_50norm.RasterXSize, settDis15_50norm.RasterYSize), shpRas, outputFolder + "00_Layers-INPUT/Distance-to-settlements_2015_th50_normalized.tif")
#WriteAndMask(settDis15_90norm.GetRasterBand(1).ReadAsArray(0, 0, settDis15_90norm.RasterXSize, settDis15_90norm.RasterYSize), shpRas, outputFolder + "00_Layers-INPUT/Distance-to-settlements_2015_th90_normalized.tif")

print("Distance to livestock stations")
selState = "Category = 'Zimovka' or Category = 'Letovka'"
settLYR.SetAttributeFilter(selState)
ZimLetDist90 = Reproject(CalcDistances(settLYR, pr, gt, pxSize, lyr), shpRas)
def CalcLiveDist(th):
    selState = "Category = 'Zimovka' or Category = 'Letovka' and Status2015 >= " + str(th)
    settLYR.SetAttributeFilter(selState)
    ZimLetDis15 = Reproject(CalcDistances(settLYR, pr, gt, pxSize, lyr), shpRas)
    return ZimLetDis15
ZimLetDist15_10 = CalcLiveDist(10)
ZimLetDist15_50 = CalcLiveDist(50)
ZimLetDist15_90 = CalcLiveDist(90)
ZimletMin, ZimletMax = FindMinMax([ZimLetDist90, ZimLetDist15_10, ZimLetDist15_50, ZimLetDist15_90], shpRas)
ZimLetDist90norm = Normalize(ZimLetDist90, settMin, settMax, invert=True)
ZimLetDist15_10norm = Normalize(ZimLetDist15_10, ZimletMin, ZimletMax, invert=True)
ZimLetDist15_50norm = Normalize(ZimLetDist15_50, ZimletMin, ZimletMax, invert=True)
ZimLetDist15_90norm = Normalize(ZimLetDist15_50, ZimletMin, ZimletMax, invert=True)
#WriteAndMask(ZimLetDist90norm.GetRasterBand(1).ReadAsArray(0, 0, ZimLetDist90norm.RasterXSize, ZimLetDist90norm.RasterYSize), shpRas, outputFolder + "00_Layers-INPUT/Distance-to-LivestockStations_1990_normalized.tif")
#WriteAndMask(ZimLetDist15_10norm.GetRasterBand(1).ReadAsArray(0, 0, ZimLetDist15_10norm.RasterXSize, ZimLetDist15_10norm.RasterYSize), shpRas, outputFolder + "00_Layers-INPUT/Distance-to-LivestockStations_2015_th10_normalized.tif")
#WriteAndMask(ZimLetDist15_50norm.GetRasterBand(1).ReadAsArray(0, 0, ZimLetDist15_50norm.RasterXSize, ZimLetDist15_50norm.RasterYSize), shpRas, outputFolder + "00_Layers-INPUT/Distance-to-LivestockStations_2015_th50_normalized.tif")
#WriteAndMask(ZimLetDist15_90norm.GetRasterBand(1).ReadAsArray(0, 0, ZimLetDist15_90norm.RasterXSize, ZimLetDist15_90norm.RasterYSize), shpRas, outputFolder + "00_Layers-INPUT/Distance-to-LivestockStations_2015_th90_normalized.tif")
print("")
print("Calculate Winderness indices, and changes therein")
crop90 = crop90norm.GetRasterBand(1).ReadAsArray(0, 0, crop90norm.RasterXSize, crop90norm.RasterYSize)
crop15 = crop15norm.GetRasterBand(1).ReadAsArray(0, 0, crop15norm.RasterXSize, crop15norm.RasterYSize)
settDis90 = settDis90norm.GetRasterBand(1).ReadAsArray(0, 0, settDis90norm.RasterXSize, settDis90norm.RasterYSize)
settDis15_10 = settDis15_10norm.GetRasterBand(1).ReadAsArray(0, 0, settDis15_10norm.RasterXSize, settDis15_10norm.RasterYSize)
settDis15_50 = settDis15_50norm.GetRasterBand(1).ReadAsArray(0, 0, settDis15_50norm.RasterXSize, settDis15_50norm.RasterYSize)
settDis15_90 = settDis15_90norm.GetRasterBand(1).ReadAsArray(0, 0, settDis15_90norm.RasterXSize, settDis15_90norm.RasterYSize)
ZimLetDis90 = ZimLetDist90norm.GetRasterBand(1).ReadAsArray(0, 0, ZimLetDist90norm.RasterXSize, ZimLetDist90norm.RasterYSize)
ZimLetDis15_10 = ZimLetDist15_10norm.GetRasterBand(1).ReadAsArray(0, 0, ZimLetDist15_10norm.RasterXSize, ZimLetDist15_10norm.RasterYSize)
ZimLetDis15_50 = ZimLetDist15_50norm.GetRasterBand(1).ReadAsArray(0, 0, ZimLetDist15_50norm.RasterXSize, ZimLetDist15_50norm.RasterYSize)
ZimLetDis15_90 = ZimLetDist15_90norm.GetRasterBand(1).ReadAsArray(0, 0, ZimLetDist15_90norm.RasterXSize, ZimLetDist15_90norm.RasterYSize)
# print("Sum of layers")
# sum90 = crop90 + settDis90 + ZimLetDis90
# sum15_10 = crop15 + settDis15_10 + ZimLetDis15_10
# sum15_50 = crop15 + settDis15_50 + ZimLetDis15_50
# sum15_90 = crop15 + settDis15_90 + ZimLetDis15_90
# diff1590_10 = sum15_10 - sum90
# diff1590_50 = sum15_50 - sum90
# diff1590_90 = sum15_90 - sum90
# WriteAndMask(sum90, shpRas, outputFolder + "01_Layer-SUM/SUM_Wilderness_1990.tif")
# WriteAndMask(sum15_10, shpRas, outputFolder + "01_Layer-SUM/SUM_Wilderness_2015_th10.tif")
# WriteAndMask(sum15_50, shpRas, outputFolder + "01_Layer-SUM/SUM_Wilderness_2015_th50.tif")
# WriteAndMask(sum15_90, shpRas, outputFolder + "01_Layer-SUM/SUM_Wilderness_2015_th90.tif")
# WriteAndMask(diff1590_10, shpRas, outputFolder + "01_Layer-SUM/SUM_Wilderness_2015-1990_th10.tif")
# WriteAndMask(diff1590_50, shpRas, outputFolder + "01_Layer-SUM/SUM_Wilderness_2015-1990_th50.tif")
# WriteAndMask(diff1590_90, shpRas, outputFolder + "01_Layer-SUM/SUM_Wilderness_2015-1990_th90.tif")
#
print("Product of layers")
prod90 = crop90 * settDis90 * ZimLetDis90
prod15_10 = crop15 * settDis15_10 * ZimLetDis15_10
prod15_50 = crop15 * settDis15_50 * ZimLetDis15_50
prod15_90 = crop15 * settDis15_90 * ZimLetDis15_90
# diff1590_10 = prod15_10 - prod90
# diff1590_50 = prod15_50 - prod90
# diff1590_90 = prod15_90 - prod90
diff1590_10 = prod90 - prod15_10
diff1590_50 = prod90 - prod15_50
diff1590_90 = prod90 - prod15_90
WriteAndMask(prod90, shpRas, outputFolder + "02_Layer-PRODUCT/PRODUCT_Wilderness_1990.tif")
WriteAndMask(prod15_10, shpRas, outputFolder + "02_Layer-PRODUCT/PRODUCT_Wilderness_2015_th10.tif")
WriteAndMask(prod15_50, shpRas, outputFolder + "02_Layer-PRODUCT/PRODUCT_Wilderness_2015_th50.tif")
WriteAndMask(prod15_90, shpRas, outputFolder + "02_Layer-PRODUCT/PRODUCT_Wilderness_2015_th90.tif")
WriteAndMask(diff1590_10, shpRas, outputFolder + "02_Layer-PRODUCT/PRODUCT_Wilderness_2015-1990_th10.tif")
WriteAndMask(diff1590_50, shpRas, outputFolder + "02_Layer-PRODUCT/PRODUCT_Wilderness_2015-1990_th50.tif")
WriteAndMask(diff1590_90, shpRas, outputFolder + "02_Layer-PRODUCT/PRODUCT_Wilderness_2015-1990_th90.tif")
#
# print("Minimum of layers")
# min90 = np.minimum.reduce([crop90, settDis90, ZimLetDis90])
# min15_10 = np.minimum.reduce([crop15, settDis15_10, ZimLetDis15_10])
# min15_50 = np.minimum.reduce([crop15, settDis15_50, ZimLetDis15_50])
# min15_90 = np.minimum.reduce([crop15, settDis15_90, ZimLetDis15_90])
# diff1590_10 = min15_10 - min90
# diff1590_50 = min15_50 - min90
# diff1590_90 = min15_90 - min90
# WriteAndMask(min90, shpRas, outputFolder + "03_Layer-MIN/MIN_Wilderness_1990.tif")
# WriteAndMask(min15_10, shpRas, outputFolder + "03_Layer-MIN/MIN_Wilderness_2015_th10.tif")
# WriteAndMask(min15_50, shpRas, outputFolder + "03_Layer-MIN/MIN_Wilderness_2015_th50.tif")
# WriteAndMask(min15_90, shpRas, outputFolder + "03_Layer-MIN/MIN_Wilderness_2015_th90.tif")
# WriteAndMask(diff1590_10, shpRas, outputFolder + "03_Layer-MIN/MIN_Wilderness_2015-1990_th10.tif")
# WriteAndMask(diff1590_50, shpRas, outputFolder + "03_Layer-MIN/MIN_Wilderness_2015-1990_th50.tif")
# WriteAndMask(diff1590_90, shpRas, outputFolder + "03_Layer-MIN/MIN_Wilderness_2015-1990_th90.tif")

print("Maximum of layers")
max90 = np.maximum.reduce([crop90, settDis90, ZimLetDis90])
max15_10 = np.maximum.reduce([crop15, settDis15_10, ZimLetDis15_10])
max15_50 = np.maximum.reduce([crop15, settDis15_50, ZimLetDis15_50])
max15_90 = np.maximum.reduce([crop15, settDis15_90, ZimLetDis15_90])
# diff1590_10 = max15_10 - max90
# diff1590_50 = max15_50 - max90
# diff1590_90 = max15_90 - max90
diff1590_10 = max90 - max15_10
diff1590_50 = max90 - max15_50
diff1590_90 = max90 - max15_90
WriteAndMask(max90, shpRas, outputFolder + "04_Layer-MAX/MAX_Wilderness_1990.tif")
WriteAndMask(max15_10, shpRas, outputFolder + "04_Layer-MAX/MAX_Wilderness_2015_th10.tif")
WriteAndMask(max15_50, shpRas, outputFolder + "04_Layer-MAX/MAX_Wilderness_2015_th50.tif")
WriteAndMask(max15_90, shpRas, outputFolder + "04_Layer-MAX/MAX_Wilderness_2015_th90.tif")
WriteAndMask(diff1590_10, shpRas, outputFolder + "04_Layer-MAX/MAX_Wilderness_2015-1990_th10.tif")
WriteAndMask(diff1590_50, shpRas, outputFolder + "04_Layer-MAX/MAX_Wilderness_2015-1990_th50.tif")
WriteAndMask(diff1590_90, shpRas, outputFolder + "04_Layer-MAX/MAX_Wilderness_2015-1990_th90.tif")

print("Mean of layers")
mean90 = (crop90 + settDis90 + ZimLetDis90) / 3
mean15_10 = (crop15 + settDis15_10 + ZimLetDis15_10) / 3
mean15_50 = (crop15 + settDis15_50 + ZimLetDis15_10) / 3
mean15_90 = (crop15 + settDis15_90 + ZimLetDis15_10) / 3
# diff1590_10 = mean15_10 - mean90
# diff1590_50 = mean15_50 - mean90
# diff1590_90 = mean15_90 - mean90
diff1590_10 = mean90 - mean15_10
diff1590_50 = mean90 - mean15_50
diff1590_90 = mean90 - mean15_90
WriteAndMask(mean90, shpRas, outputFolder + "05_Layer-MEAN/MEAN_Wilderness_1990.tif")
WriteAndMask(mean15_10, shpRas, outputFolder + "05_Layer-MEAN/MEAN_Wilderness_2015_th10.tif")
WriteAndMask(mean15_50, shpRas, outputFolder + "05_Layer-MEAN/MEAN_Wilderness_2015_th50.tif")
WriteAndMask(mean15_90, shpRas, outputFolder + "05_Layer-MEAN/MEAN_Wilderness_2015_th90.tif")
WriteAndMask(diff1590_10, shpRas, outputFolder + "05_Layer-MEAN/MEAN_Wilderness_2015-1990_th10.tif")
WriteAndMask(diff1590_50, shpRas, outputFolder + "05_Layer-MEAN/MEAN_Wilderness_2015-1990_th50.tif")
WriteAndMask(diff1590_90, shpRas, outputFolder + "05_Layer-MEAN/MEAN_Wilderness_2015-1990_th90.tif")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")