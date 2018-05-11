# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal
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
drvMemR = gdal.GetDriverByName('MEM')
outputFolder = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/05_Wilderness_LivestockDisaggreg_InputData/_WildernessRuns/20160926_Run05/"
baseFolder = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/05_Wilderness_LivestockDisaggreg_InputData/"
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
def ReScaleNTL(NTL, c0, c1, c2):
# Create Output-File
    pr = NTL.GetProjection()
    gt = NTL.GetGeoTransform()
    cols = NTL.RasterXSize
    rows = NTL.RasterYSize
    output = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
# Do the raster-calculation
    rb = NTL.GetRasterBand(1)
    out_rb = output.GetRasterBand(1)
# Equation
    ar = rb.ReadAsArray(0, 0, cols, rows)
    out = np.zeros(ar.shape, dtype='float32')
    out = c0 + c1 * ar + c2 * ar * ar
# Set everything smaller zero to zero
    out = np.where((out < 0), 0, out)
    out_rb.WriteArray(out, 0, 0)
# return the results
    return output
def Normalize(inRaster):
# Create Output-File
    pr = inRaster.GetProjection()
    gt = inRaster.GetGeoTransform()
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    output = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
# Do the raster-calculation
    rb = inRaster.GetRasterBand(1)
    out_rb = output.GetRasterBand(1)
    ar = rb.ReadAsArray(0, 0, cols, rows)
    out = np.zeros(ar.shape, dtype='float32')
    min = np.min(ar)
    max = np.max(ar)
    out = (ar - min)/(max-min)
    out_rb.WriteArray(out, 0, 0)
    return output
def SubDivide(inRaster):
    # Create Output-File
    pr = inRaster.GetProjection()
    gt = inRaster.GetGeoTransform()
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    output = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
    # Do the raster-calculation
    rb = inRaster.GetRasterBand(1)
    out_rb = output.GetRasterBand(1)
    ar = rb.ReadAsArray(0, 0, cols, rows)
    out = np.zeros(ar.shape, dtype = 'float32')
    # Do it by percentile
    out = np.where((ar <= 0.1), 0.1, out)
    out = np.where((ar > 0.1) * (ar <= 0.2), 0.2, out)
    out = np.where((ar > 0.2) * (ar <= 0.3), 0.3, out)
    out = np.where((ar > 0.3) * (ar <= 0.4), 0.4, out)
    out = np.where((ar > 0.4) * (ar <= 0.5), 0.5, out)
    out = np.where((ar > 0.5) * (ar <= 0.6), 0.6, out)
    out = np.where((ar > 0.6) * (ar <= 0.7), 0.7, out)
    out = np.where((ar > 0.7) * (ar <= 0.8), 0.8, out)
    out = np.where((ar > 0.8) * (ar <= 0.9), 0.9, out)
    out = np.where((ar > 0.9), 1, out)
    out_rb.WriteArray(out, 0, 0)
    return(output)
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
    rb4 = ListOfRasters[3].GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    out = rb1 + rb2 + rb3 + rb4
    out_rb.WriteArray(out, 0, 0)
    return(output)
def CalcWindernessMinTwo(ListOfRasters):
    # Wilderness Definition: wild is an area in which 2 layers are in the 20% percentile of the value range
    # Create Output-File
    pr = ListOfRasters[0].GetProjection()
    gt = ListOfRasters[0].GetGeoTransform()
    cols = ListOfRasters[0].RasterXSize
    rows = ListOfRasters[0].RasterYSize
    output = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
    out_rb = output.GetRasterBand(1)
    # Load the rasters to arrays
    rb1 = ListOfRasters[0].GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    rb2 = ListOfRasters[1].GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    rb3 = ListOfRasters[2].GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    rb4 = ListOfRasters[3].GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    # Do the evaluation
    l12 = np.where((rb1 <= 0.1) * (rb2 <= 0.1), 1, 0)
    l13 = np.where((rb1 <= 0.1) * (rb3 <= 0.1), 1, 0)
    l14 = np.where((rb1 <= 0.1) * (rb4 <= 0.1), 1, 0)
    l23 = np.where((rb2 <= 0.1) * (rb3 <= 0.1), 1, 0)
    l24 = np.where((rb2 <= 0.1) * (rb4 <= 0.1), 1, 0)
    l34 = np.where((rb3 <= 0.1) * (rb4 <= 0.1), 1, 0)
    out = l12 + l13 + l14 + l23 + l24 + l34
    out = np.where((out > 1), 1, out)
    out_rb.WriteArray(out, 0, 0)
    return(output)
def CapLifestock(inRaster, capVal):
    # Create Output-File
    pr = inRaster.GetProjection()
    gt = inRaster.GetGeoTransform()
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    output = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
    # Do the raster-calculation
    rb = inRaster.GetRasterBand(1)
    out_rb = output.GetRasterBand(1)
    ar = rb.ReadAsArray(0, 0, cols, rows)
    out = np.where((ar > capVal), capVal, ar)
    out = np.where((out < 0), 0, out)
    out_rb.WriteArray(out, 0, 0)
    return (output)
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
    rb_out.SetNoDataValue(999)
    ar_in = rb_in.ReadAsArray(0, 0, cols, rows)
    ar_ext = rb_ext.ReadAsArray(0, 0, cols, rows)
    out = np.where((ar_ext == activeVal), ar_in, 999)
    rb_out.WriteArray(out, 0, 0)
    return output
def CalcDiffSum(ras01, ras02):
    # Create Output-File
    pr = ras01.GetProjection()
    gt = ras01.GetGeoTransform()
    cols = ras01.RasterXSize
    rows = ras01.RasterYSize
    dtype = ras01.GetRasterBand(1).DataType
    output = drvMemR.Create('', cols, rows, 1, dtype)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
    # Do the raster calculation
    ras01_rb = ras01.GetRasterBand(1)
    ras02_rb = ras02.GetRasterBand(1)
    out_rb = output.GetRasterBand(1)
    ras01_ar = ras01_rb.ReadAsArray(0, 0, cols, rows)
    ras02_ar = ras02_rb.ReadAsArray(0, 0, cols, rows)
    out = ras02_ar - ras01_ar
    out_rb.WriteArray(out, 0, 0)
    return output
def CalDiffMinTwo(ras01, ras02):
    # Create Output-File
    pr = ras01.GetProjection()
    gt = ras01.GetGeoTransform()
    cols = ras01.RasterXSize
    rows = ras01.RasterYSize
    dtype = ras01.GetRasterBand(1).DataType
    output = drvMemR.Create('', cols, rows, 1, dtype)
    output.SetProjection(pr)
    output.SetGeoTransform(gt)
    # Do the raster calculation
    ras01_rb = ras01.GetRasterBand(1)
    ras02_rb = ras02.GetRasterBand(1)
    out_rb = output.GetRasterBand(1)
    ras01_ar = ras01_rb.ReadAsArray(0, 0, cols, rows)
    ras02_ar = ras02_rb.ReadAsArray(0, 0, cols, rows)
    out = np.where((ras02_ar > ras01_ar), 1, 0)
    out = np.where((ras02_ar < ras01_ar), 2, out)
    out_rb.WriteArray(out, 0, 0)
    return output
# ####################################### PROCESSING ########################################################## #
print("rasterize ExtentPolygon")
ref = gdal.Open(baseFolder + "03_CroplandData/1990_PercCropland_500m.tif", GA_ReadOnly)
pr = ref.GetProjection()
gt = ref.GetGeoTransform()
shape = drvMemV.CopyDataSource(ogr.Open(baseFolder + "Extent.shp"),'')
lyr = shape.GetLayer()
x_min, x_max, y_min, y_max = lyr.GetExtent()
x_res = int((x_max - x_min) / 500)
y_res = int((y_max - y_min) / 500)
shpRas = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
shpRas.SetProjection(pr)
shpRas.SetGeoTransform((x_min, 500, 0, y_max, 0, -500))
shpRas_rb = shpRas.GetRasterBand(1)
shpRas_rb.SetNoDataValue(255)
gdal.RasterizeLayer(shpRas, [1], lyr, burn_values=[1])
print("Calculate Road-Distance")
# # First rasterize the layer
# road_shape = drvMemV.CopyDataSource(ogr.Open(baseFolder + "02_DistanceToRoads/Roads_Clipped.shp"),'')
# lyr_road = road_shape.GetLayer()
# x_res = int((x_max - x_min) / 30)
# y_res = int((y_max - y_min) / 30)
# roadRas = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
# roadRas.SetProjection(pr)
# roadRas.SetGeoTransform((x_min, 30, 0, y_max, 0, -30))
# roadRas_rb = roadRas.GetRasterBand(1)
# gdal.RasterizeLayer(roadRas, [1], lyr_road, burn_values=[1])
# # Now calculate euclidean distance
# roadDis30 = drvMemR.Create('', x_res, y_res, 1, GDT_Int16)
# roadDis30.SetProjection(pr)
# roadDis30.SetGeoTransform((x_min, 30, 0, y_max, 0, -30))
# roadDis_band = roadDis30.GetRasterBand(1)
# roadRas_rb = roadRas.GetRasterBand(1)
# creationoptions = ['VALUES=1', 'DISTUNITS=PIXEL']
# gdal.ComputeProximity(roadRas_rb, roadDis_band, creationoptions)
# # Do the scaling and everything
# roadDis_repro = MaskRaster(Reproject(roadDis30, shpRas),shpRas,1)
# # Invert the normalized distance raster
# roadDis_inv = drvMemR.Create('', roadDis_repro.RasterXSize, roadDis_repro.RasterYSize, 1, gdal.GDT_Float32)
# roadDis_inv.SetProjection(roadDis_repro.GetProjection())
# roadDis_inv.SetGeoTransform(roadDis_repro.GetGeoTransform())
# roadDis_inv_rb = roadDis_repro.GetRasterBand(1)
# roadDis_ar = roadDis_repro.ReadAsArray(0, 0, roadDis_repro.RasterXSize, roadDis_repro.RasterYSize)
# out = np.negative(roadDis_ar)
# # Manually: max = -2, min = -600
# max = -2
# min = -550
# out = (out - min)/(max-min)
# out = np.where((out < 0), 0, out)
# roadDis_inv.GetRasterBand(1).WriteArray(out, 0, 0)
# roadDisNormSubDiv = MaskRaster(SubDivide(roadDis_inv), shpRas, 1)
# CopyMEMtoDisk(roadDisNormSubDiv, outputFolder + "RoadDis_norm.tif")
roadDisNormSubDiv = OpenRasterToMemory(outputFolder + "RoadDis_norm.tif")
# #### 1. (1990)
print("----> Process 1990")
files90 = [
    baseFolder + "01_NightTimeLights/Composites/F101992.v4/F101992.v4b_web.stable_lights.avg_vis.tif",
    baseFolder + "03_CroplandData/1990_PercCropland_500m.tif",
    baseFolder + "04_Livestock_Hankerson/1.9.2-1990_grazedNPP.tif"]
print("Homogenize coordinate systems")
NTL90 = Reproject(gdal.Open(files90[0]), shpRas)
crop90 = Reproject(gdal.Open(files90[1]), shpRas)
graze90 = Reproject(gdal.Open(files90[2]), shpRas)
#roadDis = Reproject(roadDis30, shpRas)
print("Re-Scale NTL, cap lifestock")
NTL90scale = ReScaleNTL(NTL90, -2.0570, 1.5903, -0.0090)
graze90cap = CapLifestock(graze90, 200)
print("Scale everything between 0 and 1, convert into deciles")
NTL90_scaled = SubDivide(Normalize(NTL90scale))
crop90_scaled = SubDivide(Normalize(crop90))
graze90_scaled = SubDivide(Normalize(graze90cap))
print("Calculate Wilderness")
wild90 = CalcWindernessSum([NTL90_scaled, roadDisNormSubDiv, crop90_scaled, graze90_scaled])#
wild90min = CalcWindernessMinTwo([NTL90_scaled, roadDisNormSubDiv, crop90_scaled, graze90_scaled])
print("Mask rastervalues")
NTL90out = MaskRaster(NTL90_scaled, shpRas, 1)
crop90out = MaskRaster(crop90_scaled, shpRas, 1)
graze90out = MaskRaster(graze90_scaled, shpRas, 1)
wild90out = MaskRaster(wild90, shpRas, 1)
wild90minOut = MaskRaster(wild90min, shpRas, 1)
print("Copy files to disk")
CopyMEMtoDisk(NTL90out, outputFolder + "NTL90.tif")
CopyMEMtoDisk(crop90out, outputFolder + "crop90.tif")
CopyMEMtoDisk(graze90out, outputFolder + "graze90.tif")
CopyMEMtoDisk(wild90out, outputFolder + "wild90_sum.tif")
CopyMEMtoDisk(wild90minOut, outputFolder + "wild90_minTwo.tif")
print("")
# #### 2. (2000)
print("----> Process 2000")
files00 = [
    baseFolder + "01_NightTimeLights/Composites/F152000.v4/F152000.v4b_web.stable_lights.avg_vis.tif",
    baseFolder + "03_CroplandData/2000_PercCropland_500m.tif",
    baseFolder + "04_Livestock_Hankerson/1.9.0-2000_grazedNPP.tif"]
print("Homogenize coordinate systems")
NTL00 = Reproject(gdal.Open(files00[0]), shpRas)
crop00 = Reproject(gdal.Open(files00[1]), shpRas)
graze00 = Reproject(gdal.Open(files00[2]), shpRas)
#roadDis = Reproject(roadDis30, shpRas)
print("Re-Scale NTL, cap lifestock")
NTL00scale = ReScaleNTL(NTL00, 0.1254, 1.0452, -0.0010)
graze00cap = CapLifestock(graze00, 200)
print("Scale everything between 0 and 1, convert into deciles")
NTL00_scaled = SubDivide(Normalize(NTL00scale))
crop00_scaled = SubDivide(Normalize(crop00))
graze00_scaled = SubDivide(Normalize(graze00cap))
print("Calculate Wilderness")
wild00 = CalcWindernessSum([NTL00_scaled, roadDisNormSubDiv, crop00_scaled, graze00_scaled])#
wild00min = CalcWindernessMinTwo([NTL00_scaled, roadDisNormSubDiv, crop00_scaled, graze00_scaled])
print("Mask rastervalues")
NTL00out = MaskRaster(NTL00_scaled, shpRas, 1)
crop00out = MaskRaster(crop00_scaled, shpRas, 1)
graze00out = MaskRaster(graze00_scaled, shpRas, 1)
wild00out = MaskRaster(wild00, shpRas, 1)
wild00minOut = MaskRaster(wild00min, shpRas, 1)
print("Copy files to disk")
CopyMEMtoDisk(NTL00out, outputFolder + "NTL00.tif")
CopyMEMtoDisk(crop00out, outputFolder + "crop00.tif")
CopyMEMtoDisk(graze00out, outputFolder + "graze00.tif")
CopyMEMtoDisk(wild00out, outputFolder + "wild00_sum.tif")
CopyMEMtoDisk(wild00minOut, outputFolder + "wild00_minTwo.tif")
print("")

# #### 3. (2015)
print("----> Process 2015")
files15 = [
    baseFolder + "01_NightTimeLights/Composites/F182012.v4/F182012.v4c_web.stable_lights.avg_vis.tif",
    baseFolder + "03_CroplandData/2015_PercCropland_500m.tif",
    baseFolder + "04_Livestock_Hankerson/1.9.0-2015_grazedNPP.tif"]
print("Homogenize coordinate systems")
NTL15 = Reproject(gdal.Open(files15[0]), shpRas)
crop15 = Reproject(gdal.Open(files15[1]), shpRas)
graze15 = Reproject(gdal.Open(files15[2]), shpRas)
#roadDis = Reproject(roadDis30, shpRas)
print("Re-Scale NTL, cap lifestock")
NTL15scale = ReScaleNTL(NTL15, 1.8750, 0.6203, 0.0052)
graze15cap = CapLifestock(graze15, 200)
print("Scale everything between 0 and 1, convert into deciles")
NTL15_scaled = SubDivide(Normalize(NTL15scale))
crop15_scaled = SubDivide(Normalize(crop15))
graze15_scaled = SubDivide(Normalize(graze15cap))
print("Calculate Wilderness")
wild15 = CalcWindernessSum([NTL15_scaled, roadDisNormSubDiv, crop15_scaled, graze15_scaled])#
wild15min = CalcWindernessMinTwo([NTL15_scaled, roadDisNormSubDiv, crop15_scaled, graze15_scaled])
print("Mask rastervalues")
NTL15out = MaskRaster(NTL15_scaled, shpRas, 1)
crop15out = MaskRaster(crop15_scaled, shpRas, 1)
graze15out = MaskRaster(graze15_scaled, shpRas, 1)
wild15out = MaskRaster(wild15, shpRas, 1)
wild15minOut = MaskRaster(wild15min, shpRas, 1)
print("Copy files to disk")
CopyMEMtoDisk(NTL15out, outputFolder + "NTL15.tif")
CopyMEMtoDisk(crop15out, outputFolder + "crop15.tif")
CopyMEMtoDisk(graze15out, outputFolder + "graze15.tif")
CopyMEMtoDisk(wild15out, outputFolder + "wild15_sum.tif")
CopyMEMtoDisk(wild15minOut, outputFolder + "wild15_minTwo.tif")
print("")
# #### 4. (DIFFERENCES)
print("Calculate differences")
CopyMEMtoDisk(MaskRaster(CalcDiffSum(wild15, wild90), shpRas, 1), outputFolder + "wild_sum_Diff_9015.tif")
CopyMEMtoDisk(MaskRaster(CalcDiffSum(wild15, wild00), shpRas, 1), outputFolder + "wild_sum_Diff_0015.tif")
CopyMEMtoDisk(MaskRaster(CalcDiffSum(wild00, wild90), shpRas, 1), outputFolder + "wild_sum_Diff_9000.tif")

CopyMEMtoDisk(MaskRaster(CalDiffMinTwo(wild15min, wild90min), shpRas, 1), outputFolder + "wild_minTwo_Diff_9015.tif")
CopyMEMtoDisk(MaskRaster(CalDiffMinTwo(wild15min, wild00min), shpRas, 1), outputFolder + "wild_minTwo_Diff_0015.tif")
CopyMEMtoDisk(MaskRaster(CalDiffMinTwo(wild00min, wild90min), shpRas, 1), outputFolder + "wild_minTwo_Diff_9000.tif")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")