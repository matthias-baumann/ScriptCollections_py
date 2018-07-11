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
root_folder = "E:/Baumann/BALTRAK/05_Wilderness_LivestockDisaggreg_InputData/"
outputFolder = root_folder + "_WildernessRuns/20180709_Run13/"
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
def FindMinMax(raster90, raster15, mask):
    # calculate the offsets for the two rasters
    mask_gt = mask.GetGeoTransform()
    raster90_gt = raster90.GetGeoTransform()
    raster15_gt = raster15.GetGeoTransform()
    cols = mask.RasterXSize
    rows = mask.RasterYSize
    x_min = mask_gt[0]
    y_max = mask_gt[3]
    # calculate the offsets for the raster90 / raster15
    raster90_gt_inv = gdal.InvGeoTransform(raster90_gt)
    raster90_gt_offUL = gdal.ApplyGeoTransform(raster90_gt_inv, x_min, y_max)
    raster90_off_ul_x, raster90_off_ul_y = map(int, raster90_gt_offUL)
    raster15_gt_inv = gdal.InvGeoTransform(raster15_gt)
    raster15_gt_offUL = gdal.ApplyGeoTransform(raster15_gt_inv, x_min, y_max)
    raster15_off_ul_x, raster15_off_ul_y = map(int, raster15_gt_offUL)
    # Load the arrays for
    arrmask = mask.GetRasterBand(1).ReadAsArray(0, 0, mask.RasterXSize, mask.RasterYSize)
    ras90arr = raster90.GetRasterBand(1).ReadAsArray(raster90_off_ul_x, raster90_off_ul_y, cols, rows)
    ras15arr = raster15.GetRasterBand(1).ReadAsArray(raster15_off_ul_x, raster15_off_ul_y, cols, rows)
    # Calculate the minimum and maximum values
    min90 = np.min(ras90arr[arrmask == 1])
    min15 = np.min(ras15arr[arrmask == 1])
    max90 = np.max(ras90arr[arrmask == 1])
    max15 = np.max(ras15arr[arrmask == 1])
    # calculate overall min/max
    maxO = max(max90, max15)
    minO = min(min90, min15)
    return minO, maxO
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
# REPROJECT THE GRASSLAND LAYERS
print("Reproject grassland layers")
crop90_proj = Reproject(crop90, shpRas)
crop15_proj = Reproject(crop15, shpRas)
# LOOP THROUGH 10% INCREMENTS OF DESTRUCTION THRESHOLD
threshs = [10, 50, 90]
for th in threshs:
    print("Processing threshold: >=", th, "%")
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
    cropMin, cropMax = FindMinMax(crop90_proj, crop15_proj, shpRas)
    settMin, settMax = FindMinMax(settDis90, settDis15, shpRas)
    ZimletMin, ZimletMax = FindMinMax(ZimLetDis90, ZimLetDis15, shpRas)
# Normalize the layers based on the minimum and maximum values
    crop90norm = Normalize(crop90_proj, cropMin, cropMax)
    crop15norm = Normalize(crop15_proj, cropMin, cropMax)
    settDis90norm = Normalize(settDis90, settMin, settMax, invert=True)
    settDis15norm = Normalize(settDis15, settMin, settMax, invert=True)
    ZimLetDist90norm = Normalize(ZimLetDis90, ZimletMin, ZimletMax, invert=True)
    ZimLetDist15norm = Normalize(ZimLetDis15, ZimletMin, ZimletMax, invert=True)
# Load the different datasets into arrays
    crop90 = crop90norm.GetRasterBand(1).ReadAsArray(0, 0, crop90norm.RasterXSize, crop90norm.RasterYSize)
    crop15 = crop15norm.GetRasterBand(1).ReadAsArray(0, 0, crop15norm.RasterXSize, crop15norm.RasterYSize)
    settDis90 = settDis90norm.GetRasterBand(1).ReadAsArray(0, 0, settDis90norm.RasterXSize, settDis90norm.RasterYSize)
    settDis15 = settDis15norm.GetRasterBand(1).ReadAsArray(0, 0, settDis15norm.RasterXSize, settDis15norm.RasterYSize)
    ZimLetDist90 = ZimLetDist90norm.GetRasterBand(1).ReadAsArray(0, 0, ZimLetDist90norm.RasterXSize, ZimLetDist90norm.RasterYSize)
    ZimLetDist15 = ZimLetDist15norm.GetRasterBand(1).ReadAsArray(0, 0, ZimLetDist15norm.RasterXSize, ZimLetDist15norm.RasterYSize)
# Write the layers to disc
    WriteAndMask(crop90, shpRas, outputFolder + "00_Layers-INPUT/thresh" + str(th) + "_Cropland_1990.tif")
    WriteAndMask(crop15, shpRas, outputFolder + "00_Layers-INPUT/thresh" + str(th) + "_Cropland_2015.tif")
    WriteAndMask(settDis90, shpRas, outputFolder + "00_Layers-INPUT/thresh" + str(th) + "_Distance-to-settlements_1990.tif")
    WriteAndMask(settDis15, shpRas, outputFolder + "00_Layers-INPUT/thresh" + str(th) + "_Distance-to-settlements_2015.tif")
    WriteAndMask(ZimLetDist90, shpRas, outputFolder + "00_Layers-INPUT/thresh" + str(th) + "_Distance-to-LivestockStations_1990.tif")
    WriteAndMask(ZimLetDist15, shpRas, outputFolder + "00_Layers-INPUT/thresh" + str(th) + "_Distance-to-LivestockStations_2015.tif")
# Calculate the wilderness indices, and mask
    # (1) Sum of the three
    # calculate the sums
    sum90 = crop90 + settDis90 + ZimLetDist90
    sum15 = crop15 + settDis15 + ZimLetDist15
    sum15_90 = sum15 - sum90
    sum90_15 = sum90 - sum15
    # Write to disc
    WriteAndMask(sum90, shpRas, outputFolder + "01_Layer-SUM/thresh" + str(th) + "_Wilderness_1990.tif")
    WriteAndMask(sum15, shpRas, outputFolder + "01_Layer-SUM/thresh" + str(th) + "_Wilderness_2015.tif")
    WriteAndMask(sum15_90, shpRas, outputFolder + "01_Layer-SUM/thresh" + str(th) + "_Wilderness_2015-1990_diff.tif")
    WriteAndMask(sum90_15, shpRas, outputFolder + "01_Layer-SUM/thresh" + str(th) + "_Wilderness_1990-2015_diff.tif")
    # (2) Product of the three
    # calculate the products
    prod90 = crop90 * settDis90 * ZimLetDist90
    prod15 = crop15 * settDis15 * ZimLetDist15
    prod15_90 = prod15 - prod90
    prod90_15 = prod90 - prod15
    # Write to disc
    WriteAndMask(prod90, shpRas, outputFolder + "02_Layer-PRODUCT/thresh" + str(th) + "_Wilderness_1990.tif")
    WriteAndMask(prod15, shpRas, outputFolder + "02_Layer-PRODUCT/thresh" + str(th) + "_Wilderness_2015.tif")
    WriteAndMask(prod15_90, shpRas, outputFolder + "02_Layer-PRODUCT/thresh" + str(th) + "_Wilderness_2015-1990_diff.tif")
    WriteAndMask(prod90_15, shpRas, outputFolder + "02_Layer-PRODUCT/thresh" + str(th) + "_Wilderness_1990-2015_diff.tif")
    # (3) Minimum of the three
    # calculate the differences
    min90 = np.minimum.reduce([crop90, settDis90, ZimLetDist90])
    min15 = np.minimum.reduce([crop15, settDis15, ZimLetDist15])
    min15_90 = min15 - min90
    min90_15 = min90 - min15
    # Write to disc
    WriteAndMask(min90, shpRas, outputFolder + "03_Layer-MIN/thresh" + str(th) + "_Wilderness_1990.tif")
    WriteAndMask(min15, shpRas, outputFolder + "03_Layer-MIN/thresh" + str(th) + "_Wilderness_2015.tif")
    WriteAndMask(min15_90, shpRas, outputFolder + "03_Layer-MIN/thresh" + str(th) + "_Wilderness_2015-1990_diff.tif")
    WriteAndMask(min90_15, shpRas, outputFolder + "03_Layer-MIN/thresh" + str(th) + "_Wilderness_1990-2015_diff.tif")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")