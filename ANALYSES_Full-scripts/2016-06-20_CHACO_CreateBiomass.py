# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import gdal
import ogr, osr
from gdalconst import *
import numpy as np
from ZumbaTools._FileManagement_Tools import *
from ZumbaTools._Raster_Tools import *
from tqdm import tqdm
import math
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
# #### OUTPUT-FILES
outfile30 = "G:/CHACO/_ANALYSES/CarbonCorridors/Chaco_Biomass_30m_run02_20160624.tif"
outfile300 = "G:/CHACO/_ANALYSES/CarbonCorridors/Chaco_Biomass_300m_run02_20160624.tif"
outfile1000 = "G:/CHACO/_ANALYSES/CarbonCorridors/Chaco_Biomass_1000m_run02_20160624.tif"
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
# #### INPUT-INFO
LC = gdal.Open("G:/CHACO/_ANALYSES/CarbonCorridors/baumann_etal_LCdata_Reclassified2013.tif", GA_ReadOnly)
eco = gdal.Open("G:/CHACO/_ANALYSES/CarbonCorridors/DryWetVerydry_Chaco_Ecoregion_clip.tif", GA_ReadOnly)
wet = gdal.Open("G:/CHACO/_ANALYSES/CarbonCorridors/perWet30m.tif", GA_ReadOnly)
dry = gdal.Open("G:/CHACO/_ANALYSES/CarbonCorridors/perDry30m.tif", GA_ReadOnly)
vDry = gdal.Open("G:/CHACO/_ANALYSES/CarbonCorridors/perVeryDry30m.tif", GA_ReadOnly)
tc = gdal.Open("G:/CHACO/_ANALYSES/CarbonCorridors/01_normalised_Tiff_clip.tif", GA_ReadOnly)
AGBcoeff = [
    # [ Class-label, Class-Name, ChacoPart (1->Wet,2->Dry,3->veryDry), AGB-Mg/px ]
    [1, "Forest", 1, 0.01512],[1, "Forest", 2, 0.00935],[1, "Forest", 3, 0.00503],
    [2, "Grassland", 1, 0.00065],[2, "Grassland", 2, 0.00061],[2, "Grassland", 3, 0.00135],
    [3, "Savanna", 1, 0],[3, "Savanna", 2, 0],[3, "Savanna", 3, 0],
    [4, "Croplands", 1, 0.0005],[4, "Croplands", 2, 0.0005],[4, "Croplands", 3, 0.0005],
    [5, "Pastures", 1, 0],[5, "Pastures", 2, 0],[5, "Pastures", 3, 0],
    [6, "Soil/Salt", 1, 0],[6, "Soil/Salt", 2, 0],[6, "Soil/Salt", 3, 0],
    [7, "Water", 1, 0],[7, "Water", 2, 0],[7, "Water", 3, 0],
    [8, "Wetlands", 1, 0.01512],[8, "Wetlands", 2, 0.00935],[8, "Wetlands", 3, 0.00503],
    [9, "Urban", 1, 0],[9, "Urban", 2, 0],[9, "Urban", 3, 0]]
silvoTS = 0.30
# ####################################### PROCESSING ########################################################## #
print("Build the biomass-map at 30m resolution")
# Build the 30m output-file in memory
pr = LC.GetProjection()
gt = LC.GetGeoTransform()
cols = LC.RasterXSize
rows = LC.RasterYSize
mem30m = drvMemR.Create('', cols, rows, 1, gdal.GDT_Float32)
mem30m.SetProjection(pr)
mem30m.SetGeoTransform(gt)
# Load all the rasterbands
mem30_rb = mem30m.GetRasterBand(1)
LC_rb = LC.GetRasterBand(1)
eco_rb = eco.GetRasterBand(1)
tc_rb = tc.GetRasterBand(1)
wet_rb = wet.GetRasterBand(1)
dry_rb = dry.GetRasterBand(1)
vDry_rb = vDry.GetRasterBand(1)
# Loop though rows and write stuff into output-file
#bar = pyprind.ProgBar(rows, monitor=True, title= "Calculate Biomass")
for row in tqdm(range(rows)):
    # Load rasters in array
    LC_ar = LC_rb.ReadAsArray(0, row, cols, 1)
    eco_ar = eco_rb.ReadAsArray(0, row, cols, 1)
    tc_ar = tc_rb.ReadAsArray(0, row, cols, 1)
    wet_ar = wet_rb.ReadAsArray(0, row, cols, 1)
    dry_ar = dry_rb.ReadAsArray(0, row, cols, 1)
    vDry_ar = vDry_rb.ReadAsArray(0, row, cols, 1)
    # Build the output array in the same shape as the input-arrays
    results = np.ones(LC_ar.shape, dtype='float32') * 0
    # Loop through the coefficients
    for tupel in AGBcoeff:
        # Get the values
        lc_val, _, eco_val, biomass = tupel
        results = np.where( (LC_ar == lc_val) * (eco_ar == eco_val), biomass, results)
        # For savannahs and
        results = np.where( (LC_ar == 3), results * tc_ar, results)
        results = np.where( (LC_ar == 5), results * tc_ar, results)
        results = np.where( (LC_ar == 8), results * tc_ar, results)
        # Now do the percent per wet/dry/very dry
        results = np.where( (eco_ar == 1), results * wet_ar, results)
        results = np.where( (eco_ar == 2), results * dry_ar, results)
        results = np.where( (eco_ar == 3), results * vDry_ar, results)
    mem30_rb.WriteArray(results, 0, row)
print("")
print("Aggregate files..")
def Aggregate(inRaster, windowSize):
    drvMemR = gdal.GetDriverByName('MEM')
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    gt = inRaster.GetGeoTransform()
# Build the output-File --> update cols/rows and GeoTransform!
# Calculate cols and rows, Cut off the edges, so that the image-boundaries line up with the window size
    cols = windowSize*(math.floor(cols/windowSize))
    rows = windowSize*(math.floor(rows/windowSize))
    outCols = int(cols/windowSize)
    outRows = int(rows/windowSize)
    cols = cols - 1
    rows = rows - 1
# Build new GeoTransform
    out_gt = [gt[0], float(gt[1])*windowSize, gt[2], gt[3], gt[4], float(gt[5])*windowSize]
# Now create the output-file
    out = drvMemR.Create('', outCols, outRows, 1, GDT_Float32)
    out.SetProjection(inRaster.GetProjection())
    out.SetGeoTransform(out_gt)
# Create the output-array
    dataOut = np.zeros((outRows, outCols))
# Initialize block size
    out_i = 0
    for i in tqdm(range(0, cols, windowSize)):
        if i + windowSize < cols:
            numCols = windowSize
        else:
            numCols = cols - i
        out_j = 0
        for j in range(0, rows, windowSize):
            if j + windowSize < rows:
                numRows = windowSize
            else:
                numRows = rows - j
# Load the input-file
            inArray = inRaster.GetRasterBand(1).ReadAsArray(i, j, numCols, numRows)
            sum_dOut = np.sum(inArray)
# Write value to output-array
            dataOut[out_j, out_i] = sum_dOut
# Make out_j, out_i continue to increase
            out_j = out_j + 1
        out_i = out_i + 1
# Write array to virtual output-file, return rasterfile
    out.GetRasterBand(1).WriteArray(dataOut, 0, 0)
    return out
print("300m")
mem300m = Aggregate(mem30m, 10)
print("")
print("1000m")
mem1000m = Aggregate(mem30m, 33)
print("")
print("Write Files to disk")
CopyMEMtoDisk(mem30m, outfile30)
CopyMEMtoDisk(mem300m, outfile300)
CopyMEMtoDisk(mem1000m, outfile1000)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")