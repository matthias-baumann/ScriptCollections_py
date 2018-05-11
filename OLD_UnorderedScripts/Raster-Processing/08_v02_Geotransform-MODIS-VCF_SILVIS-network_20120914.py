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
center_PathRow = sys.argv[1]
root_Folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\" + center_PathRow + "\\"
VCF = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\MODIS-VCF\\" + center_PathRow + "_MOD44B_C4_TREE.2005.MOSAIC.tif"
output_folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\" + center_PathRow + "\\"

# (0) Define data files, and get corner coordinates

# (0-A) Get coordinates from txt-file
fileList = os.listdir(root_Folder)
for file in fileList[:]:
	if file.find("Coordinates") >= 0:
		coord_file = root_Folder + file
		coord_info = open(coord_file, "r")
		for line in coord_info:
			if line.find("ul_x:") >= 0:
				p1 = line.find(":")
				p2 = len(line)
				ul_x_aa = line[p1+1:p2-1]
			if line.find("ul_y:") >= 0:
				p1 = line.find(":")
				p2 = len(line)
				ul_y_aa = line[p1+1:p2-1]
			if line.find("lr_x:") >= 0:
				p1 = line.find(":")
				p2 = len(line)
				lr_x_aa = line[p1+1:p2-1]
			if line.find("lr_y:") >= 0:
				p1 = line.find(":")
				p2 = len(line)
				lr_y_aa = line[p1+1:p2-1]
		coord_info.close()
		print("Crop MODIS-VCF to Landsat extent. Coordinates:")
		print("UpperLeft-X:", ul_x_aa, "UpperLeft-Y:", ul_y_aa, "LowerRight-X:", lr_x_aa, "LowerRight-Y:", lr_y_aa)
		print("")
		
# (0-B) Define composite as reference for coordinate-system
	if file.find("cropped") >= 0 and file.find (".hdr") < 0:
		reference = root_Folder + file

# (0-C) Define temporary reprojected file, and final output file
reprojected = VCF
reprojected = reprojected.replace(".tif","_reprojected")
output = output_folder + center_PathRow + "_MODIS-VCF"

# (1) Do the analysis

# (1-A) Resample the MODIS files to 30mx30m and transform into UTM-projection
print("Reprojecting...")
reference_gdal = gdal.Open(reference, GA_ReadOnly)
ref = reference_gdal.GetProjection()
command = "gdalwarp -q -tr 30 30 -t_srs " + ref + " " + VCF + " " + reprojected
os.system(command)
	
# (2) Crop to analysis extent
print("Cropping to extent of analysis...")
command = "gdal_translate -q -of ENVI -projwin " + str(ul_x_aa) + " " + str(ul_y_aa) + " " + str(lr_x_aa) + " " + str(lr_y_aa) + " " + reprojected + " " + output
os.system(command)
print("")

# delete the temporary file
os.remove(reprojected)

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")