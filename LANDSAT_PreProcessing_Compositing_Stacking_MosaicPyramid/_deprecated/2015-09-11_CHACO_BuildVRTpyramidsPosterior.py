# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import datetime
import gdal
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #

# #### (4) CALCULATE PYRAMIDS FOR THE VRT-FILE
print("Calculate Pyramids")
command = "gdaladdo.exe " + "E:/Baumann/CHACO/_Composite_Landsat8_2015/DOY015_Jan15_MetaInfo_VRT.vrt" + " 2 4 8 16 32 64"

command = "gdaladdo.exe " + "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/Run09_ClumpSieve_10px_masked_clip.tif" + " 2 4 8 16 32 64"

os.system(command)



# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")