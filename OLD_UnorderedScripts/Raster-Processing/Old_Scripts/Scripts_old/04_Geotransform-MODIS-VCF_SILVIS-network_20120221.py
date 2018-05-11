# ######################################## BEGIN OF HEADER INFROMATION AND LOADING OF MODULES ########################################
# IMPORT SYSTEM MODULES
from __future__ import division
from math import sqrt
import sys, string
import os
#import arcgisscripting
import time
import datetime
import shutil
import math
import numpy as np
import tarfile
#np.arrayarange = np.arange
from numpy.linalg import *
import numpy.ma as ma
from osgeo import gdal
from osgeo.gdalconst import *
gdal.TermProgress = gdal.TermProgress_nocb
from osgeo import osr
gdal.TermProgress = gdal.TermProgress_nocb
from osgeo import gdal_array as gdalnumeric
# ######################################## END OF HEADER INFROMATION AND LOADING OF MODULES ##########################################
# ##### SET TIME-COUNT AND HARD-CODED FOLDER-PATHS #####
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:", starttime)
print("")


# ##### Set all the paths hard-coded and get coordinates from txt-file, produced in script 1

input = "E:\\tempdata\\mbaumann\\MODIS-VCF\\MOD44B_C4_TREE.2005.VU3738.tif"
reprojected = "E:\\tempdata\\mbaumann\\MODIS-VCF\\reproject.tif"
output = "E:\\tempdata\\mbaumann\\Forest_TrainingData\\MODIS-VCF"
image_reference = "E:\\tempdata\\mbaumann\\Composite_Building\\177019\\177019_Active-Area_Binary-mask"
ulx = 508200.0
uly = 6620100.0
lrx = 742800.0
lry = 6398400.0


# (1) Resample the MODIS files to 30mx30m and transform into UTM-projection from the active area mask
print("Resampling to Landsat resolution and re-project into UTM.")
reference_gdal = gdal.Open(image_reference, GA_ReadOnly)
ref = reference_gdal.GetProjection()
command = "gdalwarp -tr 30 30 -t_srs " + ref + " " + input + " " + reprojected	#" " + 
os.system(command)
print("DONE")
print("")
	
# (2) Crop to analysis extent
print("Cropping new file to extent of analysis.")
command = "gdal_translate -projwin " + str(ulx) + " " + str(uly) + " " + str(lrx) + " " + str(lry) + " " + reprojected + " " + output
os.system(command)
print("DONE")
print("")

os.remove(reprojected)


print("--------------------------------------------------------")
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")