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

source_folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\forLinux\\"
# ##### START THE SORTING #####

# (1) Create list of the folders that we will sort, loop once through to remove the thumbs.db file
sceneList = os.listdir(source_folder)
for scene in sceneList[:]:
	if scene.find("Thumbs") >= 0:
		sceneList.remove(scene)
		
# (2) Loop through the scenes, get information about files in there and remove everything we don't need anymore so that Fmas can start and run wo problems
for scene in sceneList[:]:
	print("Cleaning up scene:", scene)
	folder = source_folder + scene + "\\"
	fileList = os.listdir(folder)
	for file in fileList[:]:
		if file.find("B1") < 0 and file.find("B2") < 0 and file.find("B3") < 0 and file.find("B4") < 0 and file.find("B5") < 0 and file.find("B6") < 0 and file.find("B61") < 0 and file.find("B62") < 0 and file.find("B7") < 0 and file.find("B8") < 0 and file.find("GCP") < 0 and file.find("MTL") < 0 and file.find("lndsr.") < 0 and file.find("GTF") < 0 and file.find("gap_mask") < 0:
			delete = folder + file
			os.remove(delete)



print("--------------------------------------------------------")
print("")

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: ", starttime)
print("end: ", endtime)
print("")