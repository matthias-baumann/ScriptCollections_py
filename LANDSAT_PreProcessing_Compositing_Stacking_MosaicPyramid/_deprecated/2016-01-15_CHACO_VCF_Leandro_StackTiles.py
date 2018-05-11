# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import gdal
from gdalconst import *
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
root_folder = "E:/Baumann/CHACO/_Composites_5yearIntervals/2013/"
out_folder = "G:/CHACO/_ANALYSES/Percent_TreeCover_2013/StackedTiles/"
outext = "MetricsFlagsImagery"
# ####################################### PROCESSING ########################################################## #
drvMemR = gdal.GetDriverByName('MEM')
drvR = gdal.GetDriverByName('ENVI')
bflags = [3, 6, 8, 9]
outbands = 70
# ####################################### OTHER STUFF ######################################################### #
# (1) GET LISTS OF TILES FOR THE YEARS WE WANT TO STACK
metricList = [root_folder + file for file in os.listdir(root_folder) if file.endswith("Metrics.bsq")]
stackLists = []
for metric in metricList:
    list = []
    list.append(metric)
    metrics = metric
    metaInfo = metrics
    metaInfo = metaInfo.replace("Metrics.bsq","MetaFlags.bsq")
    list.append(metaInfo)
    images = metrics
    images = images.replace("Metrics.bsq","Imagery.bsq")
    list.append(images)
    stackLists.append(list)
# (2) STACK THEM
for stack in stackLists:
    #stack = stackLists[2000]
    # Build output filename
    p = stack[0].rfind("/")
    file = stack[0][p+1:]
    file = file.replace("PBC_multiYear_Metrics",outext)
    outfile = out_folder + file
    print("Processing: " + outfile)
    # Load files into memory, get properties
    metric = drvMemR.CreateCopy('', gdal.Open(stack[0]))
    flag = drvMemR.CreateCopy('', gdal.Open(stack[1]))
    image = drvMemR.CreateCopy('', gdal.Open(stack[2]))
    cols = metric.RasterXSize
    rows = metric.RasterYSize
    proj = metric.GetProjection()
    geotrans = metric.GetGeoTransform()
    bands = outbands
    # Create Output tile
    out = drvMemR.Create('', cols, rows, bands, GDT_UInt32)
    out.SetProjection(proj)
    out.SetGeoTransform(geotrans)
    # Populate output file
    b = 1
    # Metrics first
    metric_bands = metric.RasterCount
    for b_in in range(metric_bands):
        readOut = metric.GetRasterBand(b_in+1).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    # Now the four flag bands
    for b_in in bflags:
        readOut = flag.GetRasterBand(b_in).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    # Now the imagery
    for b_in in range(image.RasterCount):
        readOut = image.GetRasterBand(b_in+1).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
# (3) COPY OUTPUT TO DISK
    drvR.CreateCopy(outfile, out)




# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")