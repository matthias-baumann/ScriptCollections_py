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
bands = [1,2,3,4,5,6]			# Because we're working with 6-band-Landsat-scenes
source_folder = "E:\\tempdata\\Landsat\\Carlos_Composite\\" + PathRow + "\\"
rule_folder = "E:\\tempdata\\Landsat\\Carlos_Composite\\" + PathRow + "\\Compositing-rules\\"
output_folder = "E:\\tempdata\\Landsat\\Carlos_Composite\\" + PathRow + "\\Composites\\"

# ##### READY TO GO #####
CompositesList = os.listdir(rule_folder)
print("Generating Image composites")
for file in CompositesList:
	txt_file = rule_folder + file
	year = file.replace(".txt","")
	print("Generating composite for year", year)
	info = open(txt_file, "r")
	imageList = []
	cloudList = []
	for line in info:
		line = line.replace("\n","_AA")
		imageList.append(line)
		line = line.replace("_AA","_clouds")
		cloudList.append(line)
	imageList.pop()														# to delete the last line which is written 'END' in the txt-file
	cloudList.pop()
	final_composite = output_folder + PathRow + "_" + year + "_composite"
	print("Output-File:", final_composite)
	if not os.path.exists(final_composite):					# DON'T FORGET TO ADD THE 'NOT'
		# Load all images into GDAL
		image_GDAL_list = []
		cloud_GDAL_list = []
		i = 1								# Count-Parameter for images
		m = 1								# Count-Parameter for masks
		for image in imageList:
			imagePath = source_folder + image
			i_str = str(i)
			img = "image_gdal_" + i_str
			image_GDAL_list.append(img)
			command = img + " = gdal.Open(imagePath, GA_ReadOnly)"
			exec(command)												
			i = i + 1
		for cloud in cloudList:
			cloudPath = source_folder + cloud
			m_str = str(m)
			cld = "cloud_gdal_" + m_str
			cloud_GDAL_list.append(cld)
			command = cld + " = gdal.Open(cloudPath, GA_ReadOnly)"
			exec(command)												
			m = m + 1
		cols = image_gdal_1.RasterXSize
		rows = image_gdal_1.RasterYSize
		outDrv = gdal.GetDriverByName('ENVI')
		options = []
		output = outDrv.Create(final_composite, cols, rows, 6, GDT_UInt16, options)
		output.SetProjection(image_gdal_1.GetProjection())
		output.SetGeoTransform(image_gdal_1.GetGeoTransform())
		NrImages = len(imageList)
		for band in bands:
			iGDAL_List = []
			cGDAL_List = []
			for y in range(rows):
				# Bringing the rows of the files into ARRAYS to manipulate them
				count = 1
				for image in image_GDAL_list:
					count_str = str(count)
					iGDAL = "iGDAL_" + count_str
					iGDAL_List.append(iGDAL)
					command = iGDAL + " = np.ravel(" + image + ".GetRasterBand(band).ReadAsArray(0, y, cols, 1))"
					exec(command)
					count = count + 1
				count = 1
				for cloud in cloud_GDAL_list:
					count_str = str(count)
					cGDAL = "cGDAL_" + count_str
					cGDAL_List.append(cGDAL)
					command = cGDAL + " = np.ravel(" + cloud + ".GetRasterBand(1).ReadAsArray(0, y, cols, 1))"
					exec(command)
					count = count + 1
				NrI = 0
				dataOut = np.zeros(cols)
				command = "dataOut = " + iGDAL_List[NrI]
				exec(command)
				command = "cloud = " + cGDAL_List[NrI]
				exec(command)
				command = "np.putmask(dataOut, cloud == 2, 0)"		# eliminate Clouds --> class 2
				exec(command)
				command = "np.putmask(dataOut, cloud == 3, 0)"		# eliminate Sensor Noise --> class 3
				exec(command)
				command = "np.putmask(dataOut, cloud == 4, 0)"		# eliminate Cloud Shadow --> class 4
				exec(command)
				NrI = NrI + 1
				while NrI < NrImages:
					command = "image = " + iGDAL_List[NrI]
					exec(command)
					command = "cloud = " + cGDAL_List[NrI]
					exec(command)
					command = "np.putmask(image, cloud == 2, 0)"		# eliminate Clouds --> class 2
					exec(command)
					command = "np.putmask(image, cloud == 3, 0)"		# eliminate Sensor Noise --> class 3
					exec(command)
					command = "np.putmask(image, cloud == 4, 0)"		# eliminate Cloud Shadow --> class 4
					exec(command)
					command = "np.putmask(dataOut, dataOut == 0, image)"
					exec(command)
					NrI = NrI + 1
				dataOut.shape = (1, -1)
				output.GetRasterBand(band).WriteArray(np.array(dataOut), 0, y)
				# Clothing the variables for the next composite
				for img in image_GDAL_list:
					command = "img = None"
					exec(command)
				for cld in cloud_GDAL_list:
					command = "cld = None"
					exec(command)
		print("--> Done building", final_composite)
	else:
		print("-->", final_composite, "already built. Continuing...")
print("")
print("Done building image composites")
print("--------------------------------------------------------")
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")