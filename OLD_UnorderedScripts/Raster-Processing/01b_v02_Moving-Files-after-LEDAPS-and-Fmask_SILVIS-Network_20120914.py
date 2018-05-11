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
root_folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\"
source_folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\forLinux\\"
# ##### START THE SORTING #####

# (1) Create list of the folders that we will sort, loop once through to remove the thumbs.db file
sceneList = os.listdir(source_folder)
for scene in sceneList[:]:
	if scene.find("Thumbs") >= 0:
		sceneList.remove(scene)
		
# (2) Loop through the scenes, get information about PathRow and Year of analysis and then copy the files there --> only LEDAPS and Fmask file
for scene in sceneList[:]:
	print("Sorting scene:", scene)

# (2-A) Determine which pathrow it is
	p = scene.find("L")
	PR = scene[p+3:p+9]
	year = scene[p+9:p+13]

	outputPath = root_folder + PR + "\\" + scene + "\\"
	if not os.path.exists(outputPath):
		os.makedirs(outputPath)
		
# (2-B-1) Search in input folder for the 4 files we need	
	search_folder = source_folder + scene + "\\"
	files = os.listdir(search_folder)
	for file in files[:]:
		if file.find("Fmask") >= 0 or file.find("lndsr.") >= 0 or file.find("GCP") >= 0 or file.find("MTL") >= 0:

# (2-B-2) Create the input and output paths, then move it
			input = search_folder + file
			output = outputPath + file
			shutil.move(input, output)



print("--------------------------------------------------------")
print("")

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: ", starttime)
print("end: ", endtime)
print("")