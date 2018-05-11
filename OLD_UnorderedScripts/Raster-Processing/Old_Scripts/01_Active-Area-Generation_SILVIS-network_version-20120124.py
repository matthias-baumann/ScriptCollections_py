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
PathRow = sys.argv[1]
imageListFile = sys.argv[2]
RAW_Folder = "E:\\tempdata\\Landsat\\Carlos_Composite\\RAW\\"
AA_output = "E:\\tempdata\\Landsat\\Carlos_Composite\\"
workDir = "E:\\tempdata\\Landsat\\Carlos_Composite\\RAW\\"
kirk_output = "E:\\tempdata\\Landsat\\Carlos_Composite\\"
image_list = RAW_Folder + imageListFile
# ##### READY TO GO #####

# ##### START THE ANALYSIS #####
# Test, if the active area mask already exists to skip the entire process and just write into LEDAPS-output-folder
final_mask = AA_output + "Active-Area_Binary-mask.tif"
txt_out = AA_output + "Active-Area_Coordinates.txt"

if not os.path.exists(final_mask):
	# (1) Get information from the TXT-File to see which files need to be processed, (2) create "Process-List"
	print("--------------------------------------------------------")
	print("Get information from txt-File. Scenes to be processed:")
	inputList = []
	info = open(image_list, "r")
	for line in info:
		file = line
		file = str(file)
		file = file.replace("\n","")
		inputList.append(file)
		print(file)
	print("--------------------------------------------------------")
	print("")


	# Generate active area for this footprint
	print("--------------------------------------------------------")
	tempMaskCount = 1000
	RAW_List = os.listdir(RAW_Folder)
	for file in inputList:
		for archive in RAW_List:
			if archive.find(file) >= 0:
				archive_proc = RAW_Folder + archive
				print("Processing file: ", file)
				workDir_tmp = workDir + file + "\\"
				tempMaskCount = tempMaskCount + 1
				tempMaskCount_str = str(tempMaskCount)
				print("Opening tar-archive...")
				if not os.path.exists(workDir_tmp):
					tar = tarfile.open(archive_proc, "r")
					list = tar.getnames()
					print("Extracting files...")
					for file in tar:
						tar.extract(file, workDir_tmp)
					tar.close()
					file = None
				else:
					print("-->", file, "got already extracted. Skipping...")

				list = os.listdir(workDir_tmp)
				for item in list[:]:
					if item.find("txt") >= 0 or item.find("GTF") >= 0 or item.find("B6") >= 0 or item.find("B8") >= 0 or item.find("_bin") >= 0 or item.find("_VER") >= 0:
						list.remove(item)
				for item in list:
					print("Find active area in band: ", item)
					file_in = workDir_tmp + item
					file_out = file_in
					file_out = file_out.replace(".TIF","_bin.TIF")
					if not os.path.exists(file_out):
						file_in_gdal = gdal.Open(file_in, GA_ReadOnly)
						cols = file_in_gdal.RasterXSize
						rows = file_in_gdal.RasterYSize
						outDrv = gdal.GetDriverByName('GTiff')
						options = []
						output = outDrv.Create(file_out, cols, rows, 1, GDT_Byte, options)
						output.SetProjection(file_in_gdal.GetProjection())
						output.SetGeoTransform(file_in_gdal.GetGeoTransform())
						for y in range(rows):
							b = np.ravel(file_in_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
							dataOut = np.zeros(cols)
							np.putmask(dataOut, b == 0, 1)
							dataOut.shape = (1, -1)
							output.GetRasterBand(1).WriteArray(np.array(dataOut), 0, y)
						file_in_gdal = None
						file_out = None
					else:
						print("-->", item, "already exists. Continuing with next file.")

				print("Find active area for entire scene")
				tm_list = os.listdir(workDir_tmp)
				for file in tm_list[:]:
					if file.find("bin") < 0 or file.find("image") >= 0:
						tm_list.remove(file)
				bin1_in = workDir_tmp + tm_list[0]
				bin2_in = workDir_tmp + tm_list[1]
				bin3_in = workDir_tmp + tm_list[2]
				bin4_in = workDir_tmp + tm_list[3]
				bin5_in = workDir_tmp + tm_list[4]
				bin6_in = workDir_tmp + tm_list[5]
				#bin7_in = workDir_tmp + tm_list[6]
				file_out = workDir + "bin_image-" + tempMaskCount_str + ".tif"
				if not os.path.exists(file_out):
					bin1_in_gdal = gdal.Open(bin1_in, GA_ReadOnly)
					bin2_in_gdal = gdal.Open(bin2_in, GA_ReadOnly)
					bin3_in_gdal = gdal.Open(bin3_in, GA_ReadOnly)
					bin4_in_gdal = gdal.Open(bin4_in, GA_ReadOnly)
					bin5_in_gdal = gdal.Open(bin5_in, GA_ReadOnly)
					bin6_in_gdal = gdal.Open(bin6_in, GA_ReadOnly)
					#bin7_in_gdal = gdal.Open(bin7_in, GA_ReadOnly)
					cols = bin1_in_gdal.RasterXSize
					rows = bin1_in_gdal.RasterYSize
					outDrv = gdal.GetDriverByName('GTiff')
					options = []
					output = outDrv.Create(file_out, cols, rows, 1, GDT_Byte, options)
					output.SetProjection(bin1_in_gdal.GetProjection())
					output.SetGeoTransform(bin1_in_gdal.GetGeoTransform())
					for y in range(rows):
						a1 = np.ravel(bin1_in_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
						a2 = np.ravel(bin2_in_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
						a3 = np.ravel(bin3_in_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
						a4 = np.ravel(bin4_in_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
						a5 = np.ravel(bin5_in_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
						a6 = np.ravel(bin6_in_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
						#a7 = np.ravel(bin7_in_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
						dataOut = np.zeros(cols)
						cal = a1 + a2 + a3 + a4 + a5 + a6# + a7
						np.putmask(dataOut, cal == 0, 1)
						dataOut.shape = (1, -1)
						output.GetRasterBand(1).WriteArray(np.array(dataOut), 0, y)
					bin1_in_gdal = None
					bin2_in_gdal = None
					bin3_in_gdal = None
					bin4_in_gdal = None
					bin5_in_gdal = None
					bin6_in_gdal = None
					#bin7_in_gdal = None
					file_out = None
				else:
					print("--> mask is already generated. Continuing...")
				print("")
	print("--> Done building binary masks for Landsat scenes")
	print("--------------------------------------------------------")
	print("")


	# (1) Read out corner coordinates, (2) Generate overall mask
	print("--------------------------------------------------------")
	print("Calculate corner coordinates and write them into txt-file in output-folder")
	maskList = os.listdir(workDir)
	for mask in maskList[:]:
		if mask.find("bin_image") < 0:
			maskList.remove(mask)

	txt_out = kirk_output + "\\" + PathRow + "\\Active-Area_Coordinates.txt"
	if not os.path.exists(txt_out):
		ul_x_aa = 0.00	# ul_x_aa --> U_pper L_eft corner, X_coordinate, A_ctive A_rea
		ul_y_aa = 99999999.00	# High number to get the first coordinate of the first image
		lr_x_aa = 99999999.00	# reason: see 'ul_y_aa'
		lr_y_aa = 0.00
		for mask in maskList:
			m = workDir + mask
			comm = "gdalinfo " + m
			txt_file = m
			txt_file = txt_file.replace(".tif","_info.txt")
			comm = comm + " > " + txt_file
			os.system(comm)
			file = open(txt_file, "r")
			for line in file:
				if line.find("Upper Left") >= 0:		# Check Upper left coordinate
					p1 = line.find("(")
					p2 = line.find(",")
					p3 = line.find(")")
					ul_x = line[p1+1:p2]
					ul_x = float(ul_x)
					ul_y = line[p2+1:p3]
					ul_y = float(ul_y)
					if ul_x > ul_x_aa:
						ul_x_aa = ul_x
					if ul_y < ul_y_aa:
						ul_y_aa = ul_y
				if line.find("Lower Right") >= 0:		# Check Lower right coordinate
					p1 = line.find("(")
					p2 = line.find(",")
					p3 = line.find(")")
					lr_x = line[p1+1:p2]
					lr_x = float(lr_x)
					lr_y = line[p2+1:p3]
					lr_y = float(lr_y)
					if lr_x < lr_x_aa:
						lr_x_aa = lr_x
					if lr_y > lr_y_aa:
						lr_y_aa = lr_y
			file.close()
		# Write coodinates into txt-file
		print("Create txt-files with corner coordinates")
		txt_out = kirk_output + "\\" + PathRow + "\\Active-Area_Coordinates.txt"
		txt_out = open(txt_out, "w")
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
		print("Done")

	else:
		print("--> Corner coordinates got calculated before. Read them from existing txt-file.")
		coord_info = open(txt_out, "r")
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
	print("")
	print("Crop binary-masks to overlap extend using coordinates:")
	print("UpperLeft-X:", ul_x_aa, "UpperLeft-Y:", ul_y_aa, "LowerRight-X:", lr_x_aa, "LowerRight-Y:", lr_y_aa)
	print("")
	maskList = os.listdir(workDir)

	for mask in maskList:
		if mask.find(".tif") >= 0 and mask.find("clip") < 0:
			print("")
			print("Cropping mask:", mask)
			m = workDir + mask
			out = m
			out = out.replace(".tif","_clip.tif")
			if not os.path.exists(out):
				command = "gdal_translate -projwin" + " " + ul_x_aa + " " + ul_y_aa + " " + lr_x_aa + " " + lr_y_aa + " " + m + " " + out
				os.system(command)
			else:
				print("-->", mask, "already exists. Continuing...")
	print("")
	print("--> Done cropping binary masks")
	print("--------------------------------------------------------")
	print("")


	print("--------------------------------------------------------")
	print("Building overall binary mask")
	final_mask = kirk_output + "\\" + PathRow + "\\Active-Area_Binary-mask"
	if not os.path.exists(final_mask):
		masks = []
		List = os.listdir(workDir)
		for mask in List[:]:
			if mask.find("clip") < 0:
				List.remove(mask)
		for mask in List:
			m = workDir + mask
			masks.append(m)
		masks.pop()																	# throw away the last item to overcome the bug in gdal that the last mask only has values of 0
		# Start building the command
		c = 1
		mask_gdal_list = []
		band_command = "band_"					# Initialize building the bandmath-command
		for mask in masks:
			c_str = str(c)
			mgl = "mask_gdal_" + c_str
			mask_gdal_list.append(mgl)
			band_command = band_command + c_str + " * band_"
			command = "mask_gdal_" + c_str + " = gdal.Open(mask, GA_ReadOnly)"
			exec(command)
			c = c + 1
		band_command = band_command + "XX"
		band_command = band_command.replace(" * band_XX","")
		band_command = "cal = " + band_command
		cols = mask_gdal_1.RasterXSize
		rows = mask_gdal_1.RasterYSize
		outDrv = gdal.GetDriverByName('ENVI')
		options = []
		output = outDrv.Create(final_mask, cols, rows, 1, GDT_Byte, options)
		output.SetProjection(mask_gdal_1.GetProjection())
		output.SetGeoTransform(mask_gdal_1.GetGeoTransform())
		bandDeleteList = []										# safe variable-names to delete later all files
		for y in range(rows):
			c = 1
			for mgl in mask_gdal_list:
				c_str = str(c)
				band = "band_" + c_str
				bandDeleteList.append(band)
				command = "band_" + c_str + " = np.ravel(" + mgl + ".GetRasterBand(1).ReadAsArray(0, y, cols, 1))"
				exec(command)
				c = c + 1
			dataOut = np.zeros(cols)
			exec(band_command)
			np.putmask(dataOut, cal == 1, 1)
			dataOut.shape = (1, -1)
			output.GetRasterBand(1).WriteArray(np.array(dataOut), 0, y)
		print("--> Done building binary masks for Landsat scenes")
	else:
		print("-->", final_mask, "already exists")
	c = 1
	mask_gdal_list = []
	band_command = "band_"					# Initialize building the bandmath-command
	for mask in masks:
		c_str = str(c)
		mgl = "mask_gdal_" + c_str
		mask_gdal_list.append(mgl)
		band_command = band_command + c_str + " * band_"
		command = "mask_gdal_" + c_str + " = None"
		exec(command)
		c = c + 1

	print("--------------------------------------------------------")
	print("")

	# Delete temporary files
	print("--------------------------------------------------------")
	print("Deleting temporary files...")
	deleteList = os.listdir(workDir)
	for item in deleteList[:]:
		if item.find("bin") >= 0:		# delete items in root-workDir
			delete = workDir + item
			os.remove(delete)

	for folder in inputList[:]:			# go through image-folders to delete tmp-files there
		delDIR = workDir + folder + "\\"
		deleteList = os.listdir(delDIR)
		for item in deleteList[:]:
			if item.find("bin") >= 0:
				delete = delDIR + item
				os.remove(delete)

	print("DONE")
else:
	print("Active area already generated!")
	coord_info = open(txt_out, "r")
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
print("--------------------------------------------------------")

print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")