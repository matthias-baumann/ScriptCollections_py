# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, gdal, osr
import baumiTools as bt
from tqdm import tqdm
import numpy as np
import random
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
workFolder = "Y:/Baumann/BALTRAK/Connectivity/Results/Buffer_removed_NAs/Normalized/"
oblasts = bt.baumiVT.CopyToMem(workFolder + "SHPs/Oblast_Clip.shp")
SA = bt.baumiVT.CopyToMem(workFolder + "SHPs/StudyRegion_Clip.shp")
PA15 = bt.baumiVT.CopyToMem(workFolder + "SHPs/PA_2015.shp")
outputFolder = workFolder + "_Summaries/"
random.seed(1) # for reproducability of the results
# ####################################### FUNCTIONS ########################################################### #
def CalcSummaries(rasterInfo, geometry, region, folder):
    #print(rasterInfo)
# Instantiate output-list with first set of parameters, open raster
    values = [region, rasterInfo[0], rasterInfo[1], rasterInfo[2]]
    ras = gdal.Open(folder + rasterInfo[3])
# Convert Geometry and Raster into arrays, build mask
    geom_np, ras_np = bt.baumiRT.Geom_Raster_to_np(geometry, ras)
    ras_np_masked = np.ma.masked_where(geom_np==0, ras_np)
# Calculate stats and append to values
    # Add the easy ones directly
    values.append(np.ma.mean(ras_np_masked))
    values.append(np.ma.std(ras_np_masked))
    values.append(np.ma.min(ras_np_masked))
    # Calculate the more tricky ones before appending
    ras_np_masked_compr = ras_np_masked.compressed()
    median = np.median(ras_np_masked_compr)
    p25 = np.percentile(ras_np_masked_compr, 25)
    p75 = np.percentile(ras_np_masked_compr, 75)
    iqr = p75 - p25
    up_whisk = ras_np_masked_compr[ras_np_masked_compr <= p75 + 1.5 * iqr].max()
    lo_whisk = ras_np_masked_compr[ras_np_masked_compr >= p25 - 1.5 * iqr].min()
    # Now add them
    values.extend([lo_whisk, p25, median, p75, up_whisk])
    values.append(np.ma.max(ras_np_masked))
    # return the stuff
    return values
# ####################################### LOOP THROUGH FEATURES ############################################### #
#### (1) STATISTICS FOR BOXPLOTS
#### DEFINE THE NAMES FOR THE RASTER-FILES
allRasters = [["MIN", "1990", "NN", "MIN_Wilderness_1990_60_nodes_50_cum_curmap_nobuff_noNA_normalized.tif"],
              ["MIN", "2015", "th10", "MIN_Wilderness_2015_th10_60_nodes_50_cum_curmap_nobuff_noNA_normalized.tif"],
              ["MIN", "2015", "th50", "MIN_Wilderness_2015_th50_60_nodes_50_cum_curmap_nobuff_noNA_normalized.tif"],
              ["MIN", "2015", "th90", "MIN_Wilderness_2015_th90_60_nodes_50_cum_curmap_nobuff_noNA_normalized.tif"],
              ["PRODUCT", "1990", "NN", "MIN_Wilderness_1990_60_nodes_50_cum_curmap_nobuff_noNA_normalized.tif"],
              ["PRODUCT", "2015", "th10", "PRODUCT_Wilderness_2015_th10_60_nodes_50_cum_curmap_nobuff_noNA_normalized.tif"],
              ["PRODUCT", "2015", "th50", "PRODUCT_Wilderness_2015_th50_60_nodes_50_cum_curmap_nobuff_noNA_normalized.tif"],
              ["PRODUCT", "2015", "th90", "PRODUCT_Wilderness_2015_th90_60_nodes_50_cum_curmap_nobuff_noNA_normalized.tif"],
              ["SUM", "1990", "NN", "SUM_Wilderness_1990_60_nodes_50_cum_curmap_nobuff_noNA_normalized.tif"],
              ["SUM", "2015", "th10", "SUM_Wilderness_2015_th10_60_nodes_50_cum_curmap_nobuff_noNA_normalized.tif"],
              ["SUM", "2015", "th50", "SUM_Wilderness_2015_th50_60_nodes_50_cum_curmap_nobuff_noNA_normalized.tif"],
              ["SUM", "2015", "th90", "SUM_Wilderness_2015_th90_60_nodes_50_cum_curmap_nobuff_noNA_normalized.tif"]]
#### (1) CALCULATE THE REGIONAL SUMMARIES
#### Instantiate output table
outTab_01 = [["Region", "Version", "Year", "Threshold", "Mean", "SD", "Min", "Lower_whisker", "Q25", "Median", "Q75", "Upper_whisker", "Max"]]
# (1-1) ENTIRE STUDY AREA
print("Entire Study Area")
lyr = SA.GetLayer()
feat = lyr.GetNextFeature()
while feat:
    geom = feat.GetGeometryRef()
    for ras in allRasters:
        outTab_01.append(CalcSummaries(ras, geom, "Entire Study Area", workFolder))
    feat = lyr.GetNextFeature()
lyr.ResetReading()
exit(0)
lyr = None
# (1-2) PER OBLAST
print("Per Oblast")
lyr = oblasts.GetLayer()
feat = lyr.GetNextFeature()
while feat:
    # Get the name of the oblast
    obName = feat.GetField("Oblast")
    geom = feat.GetGeometryRef()
    for ras in allRasters:
        outTab_01.append(CalcSummaries(ras, geom, obName, workFolder))
    feat = lyr.GetNextFeature()
lyr.ResetReading()
lyr = None
bt.baumiFM.WriteListToCSV(outputFolder + "ZONAL_Summaries.csv", outTab_01, delim=",")
# # (2) PROTECTED AREAS
# # (2-1) INSIDE PROTECTED AREAS
print("Inside protected areas")
outTab_02 = [["PA_Name", "Version", "Year", "Threshold", "Mean", "SD", "Min", "Lower_whisker", "Q25", "Median", "Q75", "Upper_whisker", "Max", "Year_PA"]]
lyr = PA15.GetLayer()
feat = lyr.GetNextFeature()
excludePAs = ["Burabai National Park", "Turgaiskii Zakaznik", "Irgiz-Turgay State Nature Reserve", "Tengiz-Korgalzhynskii Gosudarstvennyi Zapovednik - Extension"]
while feat:
    PAname = feat.GetField("Name")
    PAyear = feat.GetField("Year")
    if PAname not in excludePAs:
        geom = feat.GetGeometryRef()
        for ras in allRasters:
            vals = CalcSummaries(ras, geom, PAname, workFolder)
            vals.append(int(PAyear))
            outTab_02.append(vals)
    feat = lyr.GetNextFeature()
lyr.ResetReading()
lyr = None
bt.baumiFM.WriteListToCSV(outputFolder + "PA_Inside-summaries.csv", outTab_02, delim=",")
# (2-2) BUFFERS AROUND THE PROTECTED AREAS
print("In buffer zones around protected areas")
outTab_03 = [["PA_Name", "Version", "Year", "Threshold", "Mean", "SD", "Min", "Lower_whisker", "Q25", "Median", "Q75", "Upper_whisker", "Max", "Year_PA", "BufferSize_m"]]
lyr = PA15.GetLayer()
feat = lyr.GetNextFeature()
while feat:
    PAname = feat.GetField("Name")
    PAyear = feat.GetField("Year")
    geom = feat.GetGeometryRef()
    # Loop through an interator of buffersizes
    for i in range(1, 21, 1):
        buf_m = i*2500
        geomBuff = geom.Buffer(buf_m)
        geomBuff_only = geomBuff.Difference(geom)
        for ras in allRasters:
            try:
                vals = CalcSummaries(ras, geomBuff_only, PAname, workFolder)
                vals.append(int(PAyear))
            except:
                vals = ["NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"]
            vals.append(buf_m)
            outTab_03.append(vals)
    feat = lyr.GetNextFeature()
lyr.ResetReading()
lyr = None
bt.baumiFM.WriteListToCSV(outputFolder + "PA_Buffer-summaries_2500m.csv", outTab_03, delim=",")
# (3) RANDOM SAMPLE AND EXTRACTION OF RASTER-VALUES
print("Create point samples for regression analysis")
def CalcDiff(ras1, ras2):
# Open the two files, get properties
    ds1 = gdal.Open(ras1)
    ds2 = gdal.Open(ras2)
    cols = ds1.RasterXSize
    rows = ds1.RasterYSize
# Now read the bands into arrays and subtract them
    arr1 = ds1.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    arr2 = ds2.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    diff = arr1 - arr2
    return diff
def CreateDS(yRaster, crop, sett, live, nPoints, yField):
# Open the rasterfile
    yDS = gdal.Open(yRaster)
    cols = yDS.RasterXSize
    rows = yDS.RasterYSize
    gt = yDS.GetGeoTransform()
    pr = yDS.GetProjection()
    yARR = yDS.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
# Build an output-shapefile
    drvMemV = ogr.GetDriverByName('memory')
    outSHP = drvMemV.CreateDataSource('')
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromWkt(pr)
    outLYR = outSHP.CreateLayer('outSHP', spatialRef, geom_type=ogr.wkbPoint)
    outLYR.CreateField(ogr.FieldDefn("ID", ogr.OFTInteger))
    outLYR.CreateField(ogr.FieldDefn(yField, ogr.OFTReal))
    outLYR.CreateField(ogr.FieldDefn("CropDiff", ogr.OFTReal))
    outLYR.CreateField(ogr.FieldDefn("SettDiff", ogr.OFTReal))
    outLYR.CreateField(ogr.FieldDefn("LiveDiff", ogr.OFTReal))
    featDef = outLYR.GetLayerDefn()
# Also build an output-CSV
    outCSV = [[yField, "CropDiff", "SettDiff", "LiveDiff"]]
    IDcount = 1
# Generate random indices
    coords = tuple(zip(*np.where(yARR > 0)))
    indices = random.sample(range(len(coords)), nPoints)
# Go through indices and generate the datasets
    for i in indices:
    # Build the geometry
        coord = coords[i]
        geom_x, geom_y = gdal.ApplyGeoTransform(gt, int(coord[1]), int(coord[0]))
        geom = ogr.Geometry(ogr.wkbPoint)
        geom.AddPoint(geom_x, geom_y)
    # Get the array values at the location of the coordinates
        yValue = float(yARR[coord[0], coord[1]])
        cropVal = float(crop[coord[0], coord[1]])
        settVal = float(sett[coord[0], coord[1]])
        liveVal = float(live[coord[0], coord[1]])
    # Set the feature into the shapefile with the respective values
        feat = ogr.Feature(featDef)
        feat.SetGeometry(geom)
        feat.SetField('ID', IDcount)
        feat.SetField(yField, yValue)
        feat.SetField('CropDiff', cropVal)
        feat.SetField('SettDiff', settVal)
        feat.SetField('LiveDiff', liveVal)
        outLYR.CreateFeature(feat)
    # Also add the valuesto the outCSV-list
        outCSV.append([yValue, cropVal, settVal, liveVal])
    # increase the counters by 1
        IDcount += 1
# Return the shapefile and the csv
    return outSHP, outCSV

print("Calculating difference layers...")
cropDiff = CalcDiff("Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Cropland_2015_normalized.tif",
                    "Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Cropland_1990_normalized.tif")

settDiff_th10 = CalcDiff("Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Distance-to-settlements_2015_th10_normalized.tif",
                         "Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Distance-to-settlements_1990_normalized.tif")
settDiff_th50 = CalcDiff("Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Distance-to-settlements_2015_th50_normalized.tif",
                         "Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Distance-to-settlements_1990_normalized.tif")
settDiff_th90 = CalcDiff("Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Distance-to-settlements_2015_th90_normalized.tif",
                         "Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Distance-to-settlements_1990_normalized.tif")

liveDiff_th10 = CalcDiff("Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Distance-to-LivestockStations_2015_th10_normalized.tif",
                         "Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Distance-to-LivestockStations_1990_normalized.tif")
liveDiff_th50 = CalcDiff("Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Distance-to-LivestockStations_2015_th50_normalized.tif",
                          "Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Distance-to-LivestockStations_1990_normalized.tif")
liveDiff_th90 = CalcDiff("Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Distance-to-LivestockStations_2015_th90_normalized.tif",
                          "Y:/Baumann/BALTRAK/Connectivity/00_Layers-INPUT/Distance-to-LivestockStations_1990_normalized.tif")

print("Sample points...")
print("MIN Th10")
points, table = CreateDS(workFolder + "Difference/MIN_Wilderness_2015_minus_1990_th10_60_nodes_50_cum_curmap_nobuff_noNA.tif",
                         cropDiff, settDiff_th10, liveDiff_th10, 10000, "MIN_t10")
bt.baumiVT.CopySHPDisk(points, outputFolder + "MIN_2015_minus_1990_th10_10000points.shp")
bt.baumiFM.WriteListToCSV(outputFolder + "MIN_2015_minus_1990_th10_10000points.csv", table, delim=",")
print("MIN Th50")
points, table = CreateDS(workFolder + "Difference/MIN_Wilderness_2015_minus_1990_th50_60_nodes_50_cum_curmap_nobuff_noNA.tif",
                         cropDiff, settDiff_th50, liveDiff_th50, 10000, "MIN_t50")
bt.baumiVT.CopySHPDisk(points, outputFolder + "MIN_2015_minus_1990_th50_10000points.shp")
bt.baumiFM.WriteListToCSV(outputFolder + "MIN_2015_minus_1990_th50_10000points.csv", table, delim=",")
print("MIN Th90")
points, table = CreateDS(workFolder + "Difference/MIN_Wilderness_2015_minus_1990_th90_60_nodes_50_cum_curmap_nobuff_noNA.tif",
                         cropDiff, settDiff_th90, liveDiff_th90, 10000, "MIN_t50")
bt.baumiVT.CopySHPDisk(points, outputFolder + "MIN_2015_minus_1990_th90_10000points.shp")
bt.baumiFM.WriteListToCSV(outputFolder + "MIN_2015_minus_1990_th90_10000points.csv", table, delim=",")
print("PRODUCT Th10")
points, table = CreateDS(workFolder + "Difference/PRODUCT_Wilderness_2015_minus_1990_th10_60_nodes_50_cum_curmap_nobuff_noNA.tif",
                         cropDiff, settDiff_th10, liveDiff_th10, 10000, "PRO_t10")
bt.baumiVT.CopySHPDisk(points, outputFolder + "PRODUCT_2015_minus_1990_th10_10000points.shp")
bt.baumiFM.WriteListToCSV(outputFolder + "PRODUCT_2015_minus_1990_th10_10000points.csv", table, delim=",")
print("PRODUCT Th50")
points, table = CreateDS(workFolder + "Difference/PRODUCT_Wilderness_2015_minus_1990_th50_60_nodes_50_cum_curmap_nobuff_noNA.tif",
                         cropDiff, settDiff_th50, liveDiff_th50, 10000, "PRO_t50")
bt.baumiVT.CopySHPDisk(points, outputFolder + "PRODUCT_2015_minus_1990_th50_10000points.shp")
bt.baumiFM.WriteListToCSV(outputFolder + "PRODUCT_2015_minus_1990_th50_10000points.csv", table, delim=",")
print("PRODUCT Th90")
points, table = CreateDS(workFolder + "Difference/PRODUCT_Wilderness_2015_minus_1990_th90_60_nodes_50_cum_curmap_nobuff_noNA.tif",
                         cropDiff, settDiff_th90, liveDiff_th90, 10000, "PRO_t90")
bt.baumiVT.CopySHPDisk(points, outputFolder + "PRODUCT_2015_minus_1990_th90_10000points.shp")
bt.baumiFM.WriteListToCSV(outputFolder + "PRODUCT_2015_minus_1990_th90_10000points.csv", table, delim=",")
print("SUM Th10")
points, table = CreateDS(workFolder + "Difference/SUM_Wilderness_2015_minus_1990_th10_60_nodes_50_cum_curmap_nobuff_noNA.tif",
                         cropDiff, settDiff_th10, liveDiff_th10, 10000, "SUM_t10")
bt.baumiVT.CopySHPDisk(points, outputFolder + "SUM_2015_minus_1990_th10_10000points.shp")
bt.baumiFM.WriteListToCSV(outputFolder + "SUM_2015_minus_1990_th10_10000points.csv", table, delim=",")
print("SUM Th50")
points, table = CreateDS(workFolder + "Difference/SUM_Wilderness_2015_minus_1990_th50_60_nodes_50_cum_curmap_nobuff_noNA.tif",
                         cropDiff, settDiff_th50, liveDiff_th50, 10000, "SUM_t50")
bt.baumiVT.CopySHPDisk(points, outputFolder + "SUM_2015_minus_1990_th50_10000points.shp")
bt.baumiFM.WriteListToCSV(outputFolder + "SUM_2015_minus_1990_th50_10000points.csv", table, delim=",")
print("SUM Th90")
points, table = CreateDS(workFolder + "Difference/SUM_Wilderness_2015_minus_1990_th90_60_nodes_50_cum_curmap_nobuff_noNA.tif",
                         cropDiff, settDiff_th90, liveDiff_th90, 10000, "SUM_t10")
bt.baumiVT.CopySHPDisk(points, outputFolder + "SUM_2015_minus_1990_th90_10000points.shp")
bt.baumiFM.WriteListToCSV(outputFolder + "SUM_2015_minus_1990_th90_10000points.csv", table, delim=",")



# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")