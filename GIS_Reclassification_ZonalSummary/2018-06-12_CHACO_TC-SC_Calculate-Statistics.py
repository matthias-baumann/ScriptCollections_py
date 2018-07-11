# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal, ogr, osr
import numpy as np
import baumiTools as bt
from tqdm import tqdm
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES #################################### #
rootFolder = "G:/Baumann/_ANALYSES/PercentTreeCover/___MaskedProducts/"
shape = bt.baumiVT.CopyToMem("G:/Baumann/ShapeFiles/CHACO_outline_LAEA.shp")
#shape = bt.baumiVT.CopyToMem("G:/Baumann/ShapeFiles/CHACO_VeryDry_Dry_Humid_LAEA.shp")
files = [#"TC_Landsat-Sentinel.tif", "SC_Landsat-Sentinel.tif",
         #"TC_Landsat.tif", "SC_Landsat.tif",
         #"TC_Sentinel.tif", "SC_Sentinel.tif",
         "TC_Landsat-Sentinel_diff_Sentinel.tif", "SC_Landsat-Sentinel_diff_Sentinel.tif",
         "TC_Landsat-Sentinel_diff_Landsat.tif", "SC_Landsat-Sentinel_diff_Landsat.tif",
         "TC_Landsat_diff_Sentinel.tif", "SC_Landsat_diff_Sentinel.tif"]
outFile = rootFolder + "Boxplots2.csv"
# ####################################### BUILD THE DIFFERENCES ############################################### #
outDS = [["Dataset", "Region", "Mean", "SD", "Median", "UQ", "LQ", "IQR", "UW", "LW"]]

for file in tqdm(files):
# Open raster-file as numpy array in overlap of shapefile
    reg = "Chaco"
    raster = gdal.Open(rootFolder + file)
    cols = raster.RasterXSize
    rows = raster.RasterYSize
    gt = raster.GetGeoTransform()
    pr = raster.GetProjection()
    rb = raster.GetRasterBand(1)
    NoData = rb.GetNoDataValue()
    ras_np = raster.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
# Calculate the statistics
    #ras_np = ras_np
    mean = np.mean(ras_np[ras_np != NoData])
    sd = np.std(ras_np[ras_np != NoData])
    median = np.median(ras_np[ras_np != NoData])
    up_quartile = np.percentile(ras_np[ras_np != NoData], 75)
    lo_quartile = np.percentile(ras_np[ras_np != NoData], 25)
    iqr = up_quartile - lo_quartile

    up_whisk = ras_np[ras_np <= up_quartile + 1.5*iqr].max()
    lo_whisk = ras_np[ras_np >= lo_quartile - 1.5*iqr].min()
# Add to output
    outDS.append([file, reg, mean, sd, median, up_quartile, lo_quartile, iqr, up_whisk, lo_whisk])
# Write output
bt.baumiFM.WriteListToCSV(outFile, outDS, delim=",")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")