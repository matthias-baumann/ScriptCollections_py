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
print("Fit images from center footprint.")
print("Starting process, time:", starttime)
print("")
center_PathRow = sys.argv[1]
Year = sys.argv[2]
root_Folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\" + center_PathRow + "\\" + Year + "\\"
bands = [1,2,3,4,5,6]
# ##### START THE ANALYSIS #####

# (1) Getting coordinates from coord-file for center
coord_file = root_Folder + "\\" + center_PathRow + "_" + Year + "_Corner-Coordinates.txt"
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
print("Coordinates for center footprint:")
print("UpperLeft-X:", ul_x_aa, "UpperLeft-Y:", ul_y_aa, "LowerRight-X:", lr_x_aa, "LowerRight-Y:", lr_y_aa)
print("")

# (2) Crop the images in the folder

# (2-A) First with the images
FP_folder = root_Folder + center_PathRow + "\\"
cropScenes = os.listdir(FP_folder)
for scene in cropScenes[:]:
	workDir = FP_folder + scene + "\\"
	fileList = os.listdir(workDir)
	for file in fileList[:]:
		if file.find(".hdr") < 0 and file.find("GTF") < 0 and file.find(".txt") < 0 and file.find("lndsr.") < 0 and file.find("Thumbs") < 0 and file.find("cropped") < 0 and file.find("Fmask") < 0:
			file01 = workDir + file
			outputTMP = file01 + "_cropped_TMP"
			print("Cropping file:", file)
			command = "gdal_translate -q -of ENVI -projwin " + " " + ul_x_aa + " " + ul_y_aa + " " + lr_x_aa + " " + lr_y_aa + " " + file01 + " " + outputTMP
			os.system(command)
			# Remove .aux-file
			aux_File = outputTMP + ".aux.xml"
			if os.path.exists(aux_File):
				os.remove(aux_File)
# (2-B) Now define overlap across bands --> important for SLC-off
			print("Finding covered area...")
			input = outputTMP
			output = input
			output = output.replace("_TMP","")
			input_gdal = gdal.Open(input, GA_ReadOnly)
			cols = input_gdal.RasterXSize
			rows = input_gdal.RasterYSize
			outDrv = gdal.GetDriverByName('ENVI')
			options = []
			out = outDrv.Create(output, cols, rows, 6, GDT_UInt16, options)
			out.SetProjection(input_gdal.GetProjection())
			out.SetGeoTransform(input_gdal.GetGeoTransform())
			for y in range(rows):
				b1 = np.ravel(input_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
				b2 = np.ravel(input_gdal.GetRasterBand(2).ReadAsArray(0, y, cols, 1))
				b3 = np.ravel(input_gdal.GetRasterBand(3).ReadAsArray(0, y, cols, 1))
				b4 = np.ravel(input_gdal.GetRasterBand(4).ReadAsArray(0, y, cols, 1))
				b5 = np.ravel(input_gdal.GetRasterBand(5).ReadAsArray(0, y, cols, 1))
				b6 = np.ravel(input_gdal.GetRasterBand(6).ReadAsArray(0, y, cols, 1))
				# Find in each band the zero values
				b1_0 = np.zeros(cols)
				np.putmask(b1_0, b1 ==0, 1)
				b2_0 = np.zeros(cols)
				np.putmask(b2_0, b2 ==0, 1)
				b3_0 = np.zeros(cols)
				np.putmask(b3_0, b3 ==0, 1)
				b4_0 = np.zeros(cols)
				np.putmask(b4_0, b4 ==0, 1)
				b5_0 = np.zeros(cols)
				np.putmask(b5_0, b5 ==0, 1)
				b6_0 = np.zeros(cols)
				np.putmask(b6_0, b6 ==0, 1)
				# Find areas that are in each band not zero and write it into 'mask'-array.
				adding = b1_0 + b2_0 + b3_0 + b4_0 + b5_0 + b6_0
				mask = np.zeros(cols)
				np.putmask(mask, adding == 0, 1)
				# Now mask the bands based on the new mask
				b1_masked = np.zeros(cols)
				np.putmask(b1_masked, mask == 1, b1)
				b1_masked.shape = (1, -1)
				b2_masked = np.zeros(cols)
				np.putmask(b2_masked, mask == 1, b2)
				b2_masked.shape = (1, -1)
				b3_masked = np.zeros(cols)
				np.putmask(b3_masked, mask == 1, b3)
				b3_masked.shape = (1, -1)
				b4_masked = np.zeros(cols)
				np.putmask(b4_masked, mask == 1, b4)
				b4_masked.shape = (1, -1)
				b5_masked = np.zeros(cols)
				np.putmask(b5_masked, mask == 1, b5)
				b5_masked.shape = (1, -1)
				b6_masked = np.zeros(cols)
				np.putmask(b6_masked, mask == 1, b6)
				b6_masked.shape = (1, -1)
				# Write into the new file
				out.GetRasterBand(1).WriteArray(np.array(b1_masked), 0, y)
				out.GetRasterBand(2).WriteArray(np.array(b2_masked), 0, y)
				out.GetRasterBand(3).WriteArray(np.array(b3_masked), 0, y)
				out.GetRasterBand(4).WriteArray(np.array(b4_masked), 0, y)
				out.GetRasterBand(5).WriteArray(np.array(b5_masked), 0, y)
				out.GetRasterBand(6).WriteArray(np.array(b6_masked), 0, y)
			input_gdal = None
			tmp_delete = outputTMP
			tmpHDR_delete = tmp_delete + ".hdr"
			if os.path.exists(tmp_delete):
				os.remove(tmp_delete)
				os.remove(tmpHDR_delete)

# (3) Do the same thing with the cloudmask files --> no active area generation needed

		if file.find("Fmask") >= 0 and file.find(".hdr") < 0 and file.find("cropped") < 0:
			file01 = workDir + file
			output = file01 + "_cropped"
			print("Cropping cloudmask...")
			command = "gdal_translate -q -of ENVI -projwin " + " " + ul_x_aa + " " + ul_y_aa + " " + lr_x_aa + " " + lr_y_aa + " " + file01 + " " + output
			os.system(command)

	print("")




endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")