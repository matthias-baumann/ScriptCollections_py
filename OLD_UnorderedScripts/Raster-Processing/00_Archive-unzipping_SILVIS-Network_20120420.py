# ### BEGIN OF HEADER INFROMATION AND LOADING OF MODULES (Not all modules are actually required for the analysis) #######################
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
from osgeo import gdal
from osgeo.gdalconst import *
gdal.TermProgress = gdal.TermProgress_nocb
from osgeo import osr
gdal.TermProgress = gdal.TermProgress_nocb
from osgeo import gdal_array as gdalnumeric
# ######################################## END OF HEADER INFROMATION AND LOADING OF MODULES ##########################################

# ##### SET TIME-COUNT AND HARD-CODED FOLDER-PATHS #####
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("")
print("Starting process, time:", starttime)
input_folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\for_LEDAPS\\"
output_folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\for_LEDAPS\\"
# ##### READY TO GO #####

# ##### START THE ANALYSIS #####

# Extract files from tar.gz. archives; check if files got extracted earlier, then skipping
print("--------------------------------------------------------")
RAW_List = os.listdir(input_folder)
for file in RAW_List:
	if file.find("Thumbs.db") < 0: 
		outputFolderName = output_folder + file + "\\"
		outputFolderName = outputFolderName.replace(".tar.gz","")
		print("Extracting tar-archive:", file)
		archiveName = input_folder + file
		tar = tarfile.open(archiveName, "r")
		list = tar.getnames()
		for file in tar:
			tar.extract(file, outputFolderName)
		tar.close()
		file = None

print("--------------------------------------------------------")
print("")

print("--------------------------------------------------------")
print("")

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: ", starttime)
print("end: ", endtime)
print("")