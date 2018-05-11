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
print("Fit images from neighboring footprints to the extend of center footprint.")
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

# (2) Creating DN-0-images from the center footprint --> 6-band for the images and
centerFP_folder = root_Folder + center_PathRow + "\\"
centerFP_list = os.listdir(centerFP_folder)
sceneSelected = centerFP_folder + centerFP_list[0]
sceneSelected_fileList = os.listdir(sceneSelected)
for file in sceneSelected_fileList[:]:
	if file.find(".hdr") < 0 and file.find("MTL") < 0 and file.find("lndsr.") < 0 and file.find("Thumbs") < 0 and file.find("TMP") < 0 and file.find("cropped") < 0 and file.find("GCP") < 0:
		input = sceneSelected + "\\" + file
		center_TMP_6b = input + "_blank_TMP_6b"
		print("Generating 6-band mask (images) for center footprint.")
		if not os.path.exists(center_TMP_6b):
			input_gdal = gdal.Open(input, GA_ReadOnly)
			cols = input_gdal.RasterXSize
			rows = input_gdal.RasterYSize
			outDrv = gdal.GetDriverByName('ENVI')
			options = []
			output = outDrv.Create(center_TMP_6b, cols, rows, 6, GDT_Byte, options)
			output.SetProjection(input_gdal.GetProjection())
			output.SetGeoTransform(input_gdal.GetGeoTransform())
			for y in range(rows):
				for band in bands:
					dataOut = np.zeros(cols)
					dataOut.shape = (1, -1)
					output.GetRasterBand(band).WriteArray(np.array(dataOut), 0, y)
			input_gdal = None
		else:
			print("--> Mask for center-footprint already generated. Skipping...")
		
		print("Generating 1-band mask (cloudmasks) for center footprint.")	
		center_TMP_1b = input + "_blank_TMP_1b"
		input_gdal = gdal.Open(input, GA_ReadOnly)
		cols = input_gdal.RasterXSize
		rows = input_gdal.RasterYSize
		outDrv = gdal.GetDriverByName('ENVI')
		options = []
		output = outDrv.Create(center_TMP_1b, cols, rows, 1, GDT_Byte, options)
		output.SetProjection(input_gdal.GetProjection())
		output.SetGeoTransform(input_gdal.GetGeoTransform())
		for y in range(rows):
			dataOut = np.zeros(cols)
			dataOut.shape = (1, -1)
			output.GetRasterBand(1).WriteArray(np.array(dataOut), 0, y)
		input_gdal = None

exit(0)			
print("")
# (3) Merge files in neighboring footprints with blnk from center footprint and crop it to extend from center footprint

# (3-A) Get information about the footprints and exclude center footprint and coordinate-file, then loop through each file
FP_list = os.listdir(root_Folder)
for folder in FP_list[:]:
	if folder.find(center_PathRow) >= 0:
		FP_list.remove(folder)

for folder in FP_list[:]:
	FP_folder = root_Folder + folder
	cropScenes = os.listdir(FP_folder)
	for scene in cropScenes[:]:
		workDir = FP_folder + "\\" + scene + "\\"
		fileList = os.listdir(workDir)
		for file in fileList[:]:
			if file.find(".hdr") < 0 and file.find("MTL") < 0 and file.find("lndsr.") < 0 and file.find("Thumbs") < 0 and file.find("croppedTMP") < 0 and file.find("AA") < 0 and file.find("PROJ") < 0 and file.find("cropped") < 0:
				print("Processing file:", file)
				
# (3-B) Convert to coordinate system of center footprint
				input = workDir + file
				output_Proj = input + "_PROJ"
				print("Converting coordinates...")
				referenceRaster = center_TMP_6b
				referenceRaster_gdal = gdal.Open(referenceRaster, GA_ReadOnly)
				ref = referenceRaster_gdal.GetProjection()
				command = "gdalwarp -of ENVI -q -t_srs " + ref + " " + input + " " + output_Proj
				os.system(command)
				referenceRaster_gdal = None

# (3-C) Now merge the file with the empty center footprint file and crop it by the coordinates
				input = output_Proj
				outputCropped = input
				outputCropped = outputCropped.replace("PROJ","croppedTMP")
				print("Merging and cropping...")
				# -ot uint16 --> everything in small letters!!!!
				command = "C:\python32\python.exe E:\tempdata\mbaumann\Landsat_Processing\Scripts\gdal_merge.py -of ENVI -ot uint16 -o " + outputCropped + " -ul_lr " + ul_x_aa + " " + ul_y_aa + " " + lr_x_aa + " " + lr_y_aa + " " + center_TMP_6b + " " + input
				#os.system(command)
				# delete the input file --> "..._PROJ"
				input_delete = input
				input_deleteHDR = input_delete + ".hdr"
				#if os.path.exists(input_delete):
				#	os.remove(input_delete)
				#	os.remove(input_deleteHDR)

# (3-D) Define Overlap across bands in the scene
				print("Finding covered area...")
				input = outputCropped
				output_AA = input
				output_AA = output_AA.replace("TMP","")
				input_gdal = gdal.Open(input, GA_ReadOnly)
				cols = input_gdal.RasterXSize
				rows = input_gdal.RasterYSize
				outDrv = gdal.GetDriverByName('ENVI')
				options = []
				out = outDrv.Create(output_AA, cols, rows, 6, GDT_UInt16, options)
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
				# delete the input file --> "..._croppedTMP"
				input_delete = input
				input_deleteHDR = input_delete + ".hdr"
				# if os.path.exists(input_delete):
				# os.remove(input_delete)
				# os.remove(input_deleteHDR)
					
# (4) Do the same thing with the cloudmask files
			if file.find("Fmask") >= 0 and file.find(".hdr") < 0 and file.find("cropped") < 0:
				file01 = workDir + file
				file02 = center_TMP_1b
				outputTMP = file01 + "_proj"
				output = file01 + "_cropped"
				print("Cropping cloudmask...")
				if not os.path.exists(output):
					file02_gdal = gdal.Open(file02, GA_ReadOnly)
					ref = file02_gdal.GetProjection()
					command = "gdalwarp -q -t_srs " + ref + " " + file01 + " " + outputTMP
					#os.system(command)
					command = "gdal_merge.py -of ENVI -ot byte -o " + output + " -ul_lr " + ul_x_aa + " " + ul_y_aa + " " + lr_x_aa + " " + lr_y_aa + " " + file02 + " " + outputTMP
					#os.system(command)
					file02_gdal = None
					#os.remove(outputTMP)
				else:
					print("--> Cloudmask already cropped. Skipping...")
			print("")
			
# (5) Delete the temporary binary DN-0-images we've created
delete_Center_TMP_6b = center_TMP_6b
delete_Center_TMP_6b_hdr = delete_Center_TMP_6b + ".hdr"
delete_Center_TMP_1b = center_TMP_1b
delete_Center_TMP_1b_hdr = delete_Center_TMP_1b + ".hdr"
os.remove(delete_Center_TMP_6b)
os.remove(delete_Center_TMP_6b_hdr)
os.remove(delete_Center_TMP_1b)
os.remove(delete_Center_TMP_1b_hdr)

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")