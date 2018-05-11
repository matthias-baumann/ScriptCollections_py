# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os, sys
import time, datetime
import ogr, osr
import gdal
from gdalconst import *
import numpy as np
import csv
import scipy.ndimage
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### HARD-CODED FOLDERS AND FILES ######################################## #

#'fooo'
#classification = "E:/Baumann/LandsatData/999_ClassificationRuns/Run02/LandSystems_1985-2000-2013/run10_classification_full_masked_img_clump-elinimate4px.img"
classification = "D:/00_Studies_STANDBY/Chaco/12_CarbonEstimation/run11_classification_full_masked_clump-eliminate4px.img"
# ####################################### GLOBAL FUNCTIONS #################################################### #
def ZonalHistogram(polygonFile, rasterFile, idField, outputTable):
    # Get extent and Pixel-size from raster
    ds = gdal.Open(rasterFile)
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
    PixelSize = gt[1]
    pr = ds.GetProjection()
    ds = None
    # Re-Project polygon-file
    print("Reproject Polygon file")
    polyTMP = polygonFile
    polyTMP = polyTMP.replace(".shp","_TMPconvert.shp")
    #command = "E:/Baumann/Scripts/GDAL/ogr2ogr -t_srs " + pr + " " + polyTMP + " " + polygonFile
    command = "ogr2ogr -t_srs " + pr + " " + polyTMP + " " + polygonFile
    os.system(command)
    # Convert the Polygon-File to raster
    outTMP = polyTMP
    outTMP = outTMP.replace(".shp", "_asRaster.tif")
    print("Convert polygon to raster")
    #command = "E:/Baumann/Scripts/GDAL/gdal_rasterize -ot Byte -a " + idField + " -tr " + str(PixelSize) + " " + str(PixelSize) + " -q -of GTiff -te " + str((ext[1][0])) + " " + str((ext[1][1])) + " " + str((ext[2][0])) + " " + str((ext[0][1])) + " " + polyTMP + " " + outTMP
    command = "gdal_rasterize -ot Byte -a " + idField + " -tr " + str(PixelSize) + " " + str(PixelSize) + " -q -of GTiff -te " + str((ext[1][0])) + " " + str((ext[1][1])) + " " + str((ext[2][0])) + " " + str((ext[0][1])) + " " + polyTMP + " " + outTMP
    os.system(command)
    # Zonal histogram
    # Load properties and bands
    print("Get zonal histogram")
    print("--> Load images")
    outTMP_gdal = gdal.Open(outTMP, GA_ReadOnly)
    raster_gdal = gdal.Open(rasterFile, GA_ReadOnly)
    cols = outTMP_gdal.RasterXSize
    rows = outTMP_gdal.RasterYSize
    pols = outTMP_gdal.GetRasterBand(1)
    vals = raster_gdal.GetRasterBand(1)
    np.seterr(all='ignore')
    vals_array = vals.ReadAsArray(0, 0, cols, rows)
    pols_array = pols.ReadAsArray(0, 0, cols, rows)
    # Get the unqiue values from the classification file, create output-list for it
    raster_unique = np.unique(vals_array)
    raster_unique = raster_unique[raster_unique >= 0]
    list = raster_unique.tolist()
    ras_IDs_unique = ["EMPTY"]
    for l in list:
        ras_IDs_unique.append(l)
    # Temporarily convert the raster into continuous values
    i = 0
    for l in list:
        np.putmask(vals_array, vals_array == l, i)
        i = i + 1
    ras_unique02 = np.unique(vals_array)
    ras_unique02 = ras_unique02[ras_unique02 >= 0]
    # Get the unique values from the polygon file
    print("--> histogram")
    index = np.unique(pols_array)
    index = np.delete(index, 0, axis=0)
    polyIDs_unique = index.tolist()
    statement = "global histo; histo = np.ndarray.tolist(scipy.ndimage.measurements.histogram(vals_array, bins = len(ras_unique02), min = np.min(ras_unique02), max = np.max(ras_unique02), labels = pols_array, index = index))"
    exec(statement)
    summary = np.array(histo).tolist()
    pols_array = None
    pols = None
    vals = None
    polygons_gdal = None
    values_gdal = None
    # Create the lists for the output
    values = []
    values.append(ras_IDs_unique)
    for polID in polyIDs_unique:
        i = polyIDs_unique.index(polID)
        rowvals = []
        rowvals.append(polID)
        val = summary[i]
        for v in val:
            rowvals.append(v)
        values.append(rowvals)
    # write output into csv-file
    print("Write output")
    with open(outputTable, "w") as the_file:
        csv.register_dialect("custom", delimiter=",",skipinitialspace=True, lineterminator='\n')
        writer = csv.writer(the_file, dialect="custom")
        for element in values:
            writer.writerow(element)
    # Delete temporary raster
    p = polygonFile.rfind("/")
    deleteFolder = polygonFile[:p+1]
    deleteList = os.listdir(deleteFolder)
    for file in deleteList:
        if file.find("_TMPconvert") >= 0:
            delete = deleteFolder + file
            #os.remove(delete)
# ####################################### START PROCESSING #################################################### #
# (1) SUMMARY PER ECO-REGION
##shape = "E:/Baumann/Shapes/00_Chaco_VeryDry_Dry_Humid_SAEAD.shp"
shape = "D:/00_Studies_STANDBY/Chaco/12_CarbonEstimation/00_Chaco_VeryDry_Dry_Humid_SAEAD.shp"
field = "ID"
outtab = "D:/00_Studies_STANDBY/Chaco/12_CarbonEstimation/Run01_WithClassification_run11/Summary_EcoRegion.csv"
print("Summary per Region (Dry, Very Dry, Wet Chaco")
ZonalHistogram(shape, classification, field, outtab)
# (2) SUMMARY PER ADMINISTRATIVE BOUNDARIES
##shape = "E:/Baumann/Shapes/01_Chaco_AdminBoundaries_PRY_BOL_ARG_SAEAD.shp"
shape = "D:/00_Studies_STANDBY/Chaco/12_CarbonEstimation/01_Chaco_AdminBoundaries_PRY_BOL_ARG_SAEAD.shp"
field = "Unique_ID"
outtab = "D:/00_Studies_STANDBY/Chaco/12_CarbonEstimation/Run01_WithClassification_run11/Summary_AdminBoundaries.csv"
print("Summary per Administrative Units")
ZonalHistogram(shape, classification, field, outtab)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #		
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")