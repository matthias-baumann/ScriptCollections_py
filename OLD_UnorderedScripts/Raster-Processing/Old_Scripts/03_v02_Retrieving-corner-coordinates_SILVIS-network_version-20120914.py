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
print("")
print("Starting process, time:", starttime)
center_PathRow = sys.argv[1]
out_Folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\" + center_PathRow + "\\"
root_Folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\" + center_PathRow + "\\"
# ##### READY TO GO #####

# ##### START THE ANALYSIS #####
# (1) Get information about the years that we find the coordinates for
SceneList = os.listdir(root_Folder)

# (2) Get information abut the scenes in that center footprint for each year
print("--------------------------------------------------------")
print("Footprint:", center_PathRow)

# (3) Get corner coordinates from MTL-File in each archive	
# Define output-file
coord_file = out_Folder + center_PathRow + "_Corner-Coordinates.txt"
# Get corner coordinates from each scene of center-footprint
print("Output-File:")
print(coord_file)
ul_x_aa = 0.00			# ul_x_aa --> U_pper L_eft corner, X_coordinate, A_ctive A_rea
ul_y_aa = 99999999.00	# High number to get the first coordinate of the first image
lr_x_aa = 99999999.00	# reason: see 'ul_y_aa'
lr_y_aa = 0.00
for folder in SceneList[:]:
	scene = root_Folder + folder + "\\"
	sceneFiles = os.listdir(scene)
	for file in sceneFiles:
		if file.find("MTL.txt") >= 0:
			sourceTXT = scene + file
			sourceTXTopen = open(sourceTXT, "r")
			for line in sourceTXTopen:
				if line.find("PRODUCT_UL_CORNER_MAPX") >= 0:		# Check Upper Left Coordinates
					p1 = line.find("=")
					p2 = line.rfind("0")
					ul_x = float(line[p1+2:p2])
					if ul_x > ul_x_aa:
						ul_x_aa = ul_x
				if line.find("PRODUCT_UL_CORNER_MAPY") >= 0:
					p1 = line.find("=")
					p2 = line.rfind("0")
					ul_y = float(line[p1+2:p2])
					if ul_y < ul_y_aa:
						ul_y_aa = ul_y
				if line.find("PRODUCT_LR_CORNER_MAPX") >= 0:		# Check Lower Right Coordinates
					p1 = line.find("=")
					p2 = line.rfind("0")
					lr_x = float(line[p1+2:p2])
					if lr_x < lr_x_aa:
						lr_x_aa = lr_x
				if line.find("PRODUCT_LR_CORNER_MAPY") >= 0:
					p1 = line.find("=")
					p2 = line.rfind("0")
					lr_y = float(line[p1+2:p2])
					if lr_y > lr_y_aa:
						lr_y_aa = lr_y
			sourceTXTopen.close()
# Write coodinates into txt-file
txt_out = open(coord_file, "w")
ul_x_aa = str(ul_x_aa)									# Values need to be strings to be writable in txt-file
ul_y_aa = str(ul_y_aa)
lr_x_aa = str(lr_x_aa)
lr_y_aa = str(lr_y_aa)
txt_out.write("Coordinates for upper left and lower right the active area \n")
txt_out.write("ul_x:" + ul_x_aa + "\n")
txt_out.write("ul_y:" + ul_y_aa + "\n")
txt_out.write("lr_x:" + lr_x_aa + "\n")
txt_out.write("lr_y:" + lr_y_aa + "\n")
txt_out.close()

print("")
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: ", starttime)
print("end: ", endtime)
print("")