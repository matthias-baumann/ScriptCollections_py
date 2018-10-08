# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal, ogr, osr
import numpy as np
import baumiTools as bt
from tqdm import tqdm
import subprocess
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES #################################### #
rootFolder = "L:/_SHARED_DATA/_PUESTO_DATA/"
outfile = rootFolder + "_Puestos_ALL_cleaned.shp"
drvKML = ogr.GetDriverByName('KML')
drvMemV = ogr.GetDriverByName('Memory')
# ####################################### PROCESSING ########################################################## #






# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")