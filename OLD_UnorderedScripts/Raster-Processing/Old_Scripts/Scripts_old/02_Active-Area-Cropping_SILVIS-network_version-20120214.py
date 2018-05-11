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
print("Starting process, time:", starttime)
print("")
PathRow = sys.argv[1]
clip_output = "E:\\tempdata\\mbaumann\\Composite_Building\\" + PathRow + "\\"
ledaps_folder = "E:\\tempdata\\mbaumann\\Composite_Building\\LEDAPS\\" + PathRow + "\\"
cloud_folder = "E:\\tempdata\\mbaumann\\Composite_Building\\Clouds\\" + PathRow + "\\"
# ##### READY TO GO #####
coord_txt = clip_output + PathRow + "_Active-Area_Coordinates.txt"		
AA_mask = clip_output + PathRow + "_Active-Area_Binary-mask"

# ##### START THE ANALYSIS #####
print("Cropping LEDAPS-Surface-reflectance-files to extent from overlap area")
coord_info = open(coord_txt, "r")
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
print("Coordinates:")
print("UpperLeft-X:", ul_x_aa, "UpperLeft-Y:", ul_y_aa, "LowerRight-X:", lr_x_aa, "LowerRight-Y:", lr_y_aa)
print("")
inputList = os.listdir(ledaps_folder)
for file in inputList[:]:
	if file.find(".hdr") < 0:
		input = ledaps_folder + file
		output = clip_output + file + "_clip"
		AA_test = clip_output + file + "_AA"
		AA_test = AA_test.replace("L71", "L7")
		print("Processing file: ", file)
		if not os.path.exists(AA_test):
			if not os.path.exists(output):
				command = "gdal_translate -of ENVI -projwin" + " " + ul_x_aa + " " + ul_y_aa + " " + lr_x_aa + " " + lr_y_aa + " " + input + " " + output
				os.system(command)
				print("")
			else:
				print("-->", file, "already built. Continuing...")
				print("")
		else:
			print("-->", AA_test, "already built. Continuing...")
print("Done cropping LEDAPS-Surface-reflectance-files")
print("--------------------------------------------------------")
print("")

print("--------------------------------------------------------")
print("Reducing image to Active Area")
print("")
bands = [1,2,3,4,5,6]
inputList = os.listdir(clip_output)
for file in inputList[:]:
	if file.find(".hdr") < 0 and file.find("Active-Area") < 0 and file.find(".txt") < 0 and file.find("Composit") < 0 and file.find("clouds") < 0 and file.find("AA") < 0:	# These are for avoiding double processing
		input = clip_output + file
		output = input
		output = output.replace("clip", "AA")
		output = output.replace("L71", "L7")
		print("Processing file: ", file)
		if not os.path.exists(output):
			input_gdal = gdal.Open(input, GA_ReadOnly)
			mask_gdal = gdal.Open(AA_mask, GA_ReadOnly)
			cols = input_gdal.RasterXSize
			rows = input_gdal.RasterYSize
			outDrv = gdal.GetDriverByName('ENVI')
			options = []
			out = outDrv.Create(output, cols, rows, 6, GDT_UInt16, options)
			out.SetProjection(input_gdal.GetProjection())
			out.SetGeoTransform(input_gdal.GetGeoTransform())
			for band in bands:
				for y in range(rows):
					b = np.ravel(input_gdal.GetRasterBand(band).ReadAsArray(0, y, cols, 1))
					mask = np.ravel(mask_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
					dataOut = np.zeros(cols)
					np.putmask(dataOut, mask == 1, b)
					dataOut.shape = (1, -1)
					out.GetRasterBand(band).WriteArray(np.array(dataOut),0, y)
			input_gdal = None
			mask_gdal = None
			os.remove(input)
			input = input + ".hdr"
			os.remove(input)
		else:
			print("-->", file, "already built. Continuing...")
print("")
print("Done reducing image to Active Area")
print("--------------------------------------------------------")
print("")


print("--------------------------------------------------------")
print("Cropping Cloudmask-files to extent from overlap area")
coord_info = open(coord_txt, "r")
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
print("Coordinates:")
print("UpperLeft-X:", ul_x_aa, "UpperLeft-Y:", ul_y_aa, "LowerRight-X:", lr_x_aa, "LowerRight-Y:", lr_y_aa)
print("")
inputList = os.listdir(cloud_folder)
for file in inputList[:]:
	if file.find(".hdr") < 0 and file.find("_clip") < 0:
		input = cloud_folder + file
		output = input + "_clip"
		mask_test = clip_output + file
		mask_test = mask_test.replace("mask","clouds")
		print("Processing file: ", file)
		if not os.path.exists(mask_test):
			if not os.path.exists(output):
				command = "gdal_translate -of ENVI -projwin" + " " + ul_x_aa + " " + ul_y_aa + " " + lr_x_aa + " " + lr_y_aa + " " + input + " " + output
				os.system(command)
				print("")
			else:
				print("-->", file, "already built. Continuing...")
				print("")
		else:
			print("-->", mask_test, "already built. Continuing...")
			print("")
print("Done cropping Cloudmask-files")
print("--------------------------------------------------------")
print("")

print("--------------------------------------------------------")
print("Reducing Cloudmasks to Active Area")
print("")
bands = [1,2,3,4,5,6]
inputList = os.listdir(cloud_folder)
for file in inputList[:]:
	if file.find(".hdr") < 0 and file.find("mask_clip") >= 0:
		input = cloud_folder + file
		output = clip_output + file
		output = output.replace("mask_clip", "clouds")
		output = output.replace("L71", "L7")
		print("Processing file: ", file)
		if not os.path.exists(output):
			input_gdal = gdal.Open(input, GA_ReadOnly)
			mask_gdal = gdal.Open(AA_mask, GA_ReadOnly)
			cols = input_gdal.RasterXSize
			rows = input_gdal.RasterYSize
			outDrv = gdal.GetDriverByName('ENVI')
			options = []
			out = outDrv.Create(output, cols, rows, 1, GDT_Byte, options)
			out.SetProjection(input_gdal.GetProjection())
			out.SetGeoTransform(input_gdal.GetGeoTransform())
			for y in range(rows):
				b = np.ravel(input_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
				mask = np.ravel(mask_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
				dataOut = np.zeros(cols)
				np.putmask(dataOut, mask == 1, b)
				dataOut.shape = (1, -1)
				out.GetRasterBand(1).WriteArray(np.array(dataOut),0, y)
			input_gdal = None
			mask_gdal = None
			os.remove(input)
			input = input + ".hdr"
			os.remove(input)
		else:
			print("-->", file, "already built. Continuing...")
print("")
print("Done reducing Cloudmasks to Active Area")
print("--------------------------------------------------------")
print("")

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")