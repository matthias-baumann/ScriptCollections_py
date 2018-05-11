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
print("Sort images, starting from least cloud coverage to most cloud coverage.")
print("")
print("Starting process, time:", starttime)
print("")
center_PathRow = sys.argv[1]

root_Folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\" + center_PathRow + "\\"

# ##### START THE ANALYSIS #####

# (1) Create output-file
sorting_file = root_Folder + "\\" + center_PathRow + "_Sorted-ImageAcquisitions.txt"

# (2) Create List that we populate with all images, build another one for the clouds
sceneList = []
cloudList = []

# (2-A) Get images from the  footprint
acquisitions = os.listdir(root_Folder)

# (2-B) Remove Coordinate-File
for acquisition in acquisitions[:]:
	if acquisition.find("Corner-Coordinates") >= 0:
		acquisitions.remove(acquisition)

# (2-C) Populate the lists
for acquisition in acquisitions[:]:
	folder = root_Folder + acquisition + "\\"
	files = os.listdir(folder)
	for file in files[:]:
		if file.find("_cropped") >= 0 and file.find("Fmask") < 0 and file.find(".hdr") < 0:
			scene = folder + file
			sceneList.append(scene)
for scene in sceneList[:]:
	cloud = scene
	cloud = cloud.replace("_cropped","_MTLFmask_cropped")
	cloudList.append(cloud)

# (3) Sort image scenes according to the proportion of clear observations

# (3-A) Loop through each cloudfile and assess % clear observation, then attach it to the list

perc_list = []
for cloud in cloudList[:]:
	cloud_gdal = gdal.Open(cloud, GA_ReadOnly)
	cols = cloud_gdal.RasterXSize
	rows = cloud_gdal.RasterYSize
	cl = cloud_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
	mask = np.less(cl, 1)
	obs = np.choose(mask, (0, 1))
	clear_obs = np.sum(obs)
	mask = np.greater(cl, 0)
	obs = np.choose(mask, (0, 1))
	mask = np.greater(cl, 4)
	no_obs = np.choose(mask, (0, 1))
	other_obs = np.sum(obs) - np.sum(no_obs)
	ratio = clear_obs / (clear_obs + other_obs)
	perc_list.append(ratio)
	cloud_gdal = None
	
combined_list = list(zip(cloudList, perc_list, sceneList))

# Need this for sorting
import operator
sorted_list = sorted(combined_list, key=operator.itemgetter(1), reverse = True)

# (3-B) Write the list into the output-file
sorting = open(sorting_file, "w")
# write the first image that we seleted before
# Then write every other image but not the first image for the second time
for item in sorted_list[:]:
	scene = item[2]
	sorting.write(scene + "\n")
sorting.close()


endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")