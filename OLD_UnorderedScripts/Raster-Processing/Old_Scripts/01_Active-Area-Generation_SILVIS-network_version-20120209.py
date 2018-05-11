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
RAW_Folder = "E:\\tempdata\\mbaumann\\RAW-Images\\"
AA_output = "E:\\tempdata\\mbaumann\\WorkImages-and-Clouds\\"
workDir = "E:\\tempdata\\mbaumann\\RAW-Images\\"
image_list = AA_output + imageListFile
# ##### READY TO GO #####

# ##### START THE ANALYSIS #####
# Test, if the active area mask already exists to skip the entire process and just write into LEDAPS-output-folder
final_mask = AA_output + PathRow + "_Active-Area_Binary-mask"
txt_out = AA_output + PathRow + "_Active-Area_Coordinates.txt"

# (1) Get information from the TXT-File to see which files need to be processed; create "Process-List"
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

# (2) Extract files from tar.gz. archives; check if files got extracted earlier, then skipping
print("--------------------------------------------------------")
print("Extracting tar.gz-files into folders")
RAW_List = os.listdir(RAW_Folder)
for file in inputList:
	archive_proc = RAW_Folder + file + "\\"
	print("Opening tar-archive and extracting files from archive:", file)
	if not os.path.exists(archive_proc):
		archiveName = RAW_Folder + file + ".tar.gz"
		tar = tarfile.open(archiveName, "r")
		list = tar.getnames()
		for file in tar:
			tar.extract(file, archive_proc)
		tar.close()
		file = None
	else:
		print("-->", file, "got already extracted. Skipping...")
print("--------------------------------------------------------")
print("")

# (3) Get corner coordinates from MTL-File in each archive										# Coordinates are retrieved from ALL files (L5, L7, L7-SCL-off), whereas active area will only be generated from L5 and L7<2003
print("--------------------------------------------------------")	
print("Calculate corner coordinates and write them into txt-file in output-folder")
ul_x_aa = 0.00	# ul_x_aa --> U_pper L_eft corner, X_coordinate, A_ctive A_rea
ul_y_aa = 99999999.00	# High number to get the first coordinate of the first image
lr_x_aa = 99999999.00	# reason: see 'ul_y_aa'
lr_y_aa = 0.00
folderList = os.listdir(RAW_Folder)
for folder in folderList[:]:
	if folder.find(".tar.gz") >=0 or folder.find("bin_image") >= 0:				# Bin-image also remove from lsit so that we don not have to delete the temporary masks all the time
		folderList.remove(folder)
for folder in folderList:	
	scene = RAW_Folder + folder + "\\"
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
print("--------------------------------------------------------")
print("")

# (4) Generate active area for this footprint from file that are Landsat 4 or Landsat 5 or Landsat 7-SLC-on (prior to 2003)
print("--------------------------------------------------------")
print("Generate active area binary masks for each scene in that footpint, which is L4\L5 or L7 earlier than 2003")
folderList = os.listdir(RAW_Folder)
for folder in folderList[:]:
	if folder.find(".tar.gz") >=0 or folder.find("bin_image") >= 0:				# Bin-image also remove from lsit so that we don not have to delete the temporary masks all the time
		folderList.remove(folder)
for folder in folderList[:]:			# Remove uneligible folders/files from list --> (a) tar.gz-files, (b) L7-SLC-off
	if folder.find(".tar.gz") >= 0:
		folderList.remove(folder)
for folder in folderList[:]:
	if folder.find("LE7") >= 0:
		p1 = folder.find(PathRow)
		year = int(folder[p1+6:p1+10])
		if year >= 2003:
			folderList.remove(folder)
#tempMaskCount = 1000
for folder in folderList:
	print("Find active area in scene", folder)
	workDir_tmp = RAW_Folder + folder + "\\"
	list = os.listdir(workDir_tmp)
	for item in list[:]:
		if item.find("txt") >= 0 or item.find("GTF") >= 0 or item.find("B6") >= 0 or item.find("B8") >= 0 or item.find("_bin") >= 0 or item.find("_VER") >= 0:
			list.remove(item)
	for item in list:
		print(item)
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
	print("Find active area for entire scene")
	#tempMaskCount = tempMaskCount + 1
	#tempMaskCount_str = str(tempMaskCount)
	tm_list = os.listdir(workDir_tmp)			
	for file in tm_list[:]:
		if file.find("_bin.TIF") < 0:
			tm_list.remove(file)
	bin1_in = workDir_tmp + tm_list[0]												# Create full Pathnames for the binary masks of the single bands
	bin2_in = workDir_tmp + tm_list[1]
	bin3_in = workDir_tmp + tm_list[2]
	bin4_in = workDir_tmp + tm_list[3]
	bin5_in = workDir_tmp + tm_list[4]
	bin6_in = workDir_tmp + tm_list[5]
	file_out = workDir + folder + "_bin_image.tif"# + tempMaskCount_str + ".tif"
	if not os.path.exists(file_out):
		bin1_in_gdal = gdal.Open(bin1_in, GA_ReadOnly)									# Loading all bianry masks into GDAL
		bin2_in_gdal = gdal.Open(bin2_in, GA_ReadOnly)
		bin3_in_gdal = gdal.Open(bin3_in, GA_ReadOnly)
		bin4_in_gdal = gdal.Open(bin4_in, GA_ReadOnly)
		bin5_in_gdal = gdal.Open(bin5_in, GA_ReadOnly)
		bin6_in_gdal = gdal.Open(bin6_in, GA_ReadOnly)
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
			dataOut = np.zeros(cols)
			cal = a1 + a2 + a3 + a4 + a5 + a6
			np.putmask(dataOut, cal == 0, 1)
			dataOut.shape = (1, -1)
			output.GetRasterBand(1).WriteArray(np.array(dataOut), 0, y)
		bin1_in_gdal = None
		bin2_in_gdal = None
		bin3_in_gdal = None
		bin4_in_gdal = None
		bin5_in_gdal = None
		bin6_in_gdal = None
		file_out = None
		os.remove(bin1_in)															# remove temporary binary masks from bands
		os.remove(bin2_in)
		os.remove(bin3_in)
		os.remove(bin4_in)
		os.remove(bin5_in)
		os.remove(bin6_in)
	else:
		print("Active area for", folder, "already generated. Skipping...")
	print("")
print("--> Done building binary masks for Landsat scenes")
print("--------------------------------------------------------")
print("")

# (5) Crop binary masks to corner coordinates
print("--------------------------------------------------------")
print("Crop binary-masks to overlap extend using coordinates:")
print("UpperLeft-X:", ul_x_aa, "UpperLeft-Y:", ul_y_aa, "LowerRight-X:", lr_x_aa, "LowerRight-Y:", lr_y_aa)
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
			print(mask, "already cropped. Skipping...")
print("")
print("--> Done cropping binary masks")
print("--------------------------------------------------------")
print("")

# (6) Build overall binary mask
print("--------------------------------------------------------")
print("Building overall binary mask")
print(final_mask)
masks = []
List = os.listdir(workDir)
for mask in List[:]:
	if mask.find("clip") < 0:
		List.remove(mask)
for mask in List:
	m = workDir + mask
	masks.append(m)
masks.pop()																	# throw away the last item to overcome the bug in gdal that the last mask only has values of 0
c = 1
mask_gdal_list = []
band_command = "band_"														# Initialize building the bandmath-command
for mask in masks:															# Load bands into GDAL
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
for mgl in mask_gdal_list:
	command = mgl + " = None"
	exec(command)
print("--> Done!")
print("--------------------------------------------------------")
print("")

# (7) delete temporary binary masks and cropped binary masks
print("--------------------------------------------------------")
print("Deleting temporary files...")
deleteList = os.listdir(workDir)
for item in deleteList[:]:
	if item.find("bin") >= 0:		# delete items in root-workDir
		delete = workDir + item
		os.remove(delete)
print("--> Done!")
print("--------------------------------------------------------")
print("")

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: ", starttime)
print("end: ", endtime)
print("")