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

bands = [1,2,3,4,5,6]			# Because we're working with 6-band-Landsat-scenes
center_PathRow = sys.argv[1]
Year = sys.argv[2]
root_Folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\" + center_PathRow + "\\" + Year + "\\"

# ##### READY TO GO #####

# (1) Open the text file with the sorted scenes and read them in including the cloudmask
info_file = root_Folder + center_PathRow + "_" + Year + "_Sorted-ImageAcquisitions.txt"
print("Generating composite for year:", Year)
info = open(info_file, "r")
imageList = []
selectList = []											# double the list of the images to select the crop image later
cloudList = []
for line in info:
	line = line.replace("\n","")
	imageList.append(line)
	selectList.append(line)
	line = line.replace("_cropped","_MTLFmask_1_6_3sav_cropped")
	cloudList.append(line)

# (2) Create Output-file
composite_output = root_Folder + center_PathRow + "_" + Year + "_composite"

# (3) Find the image that we want to cut the composite with
for image in selectList[:]:
	if image.find("LE7") >= 0:
		p = image.rfind("LE7")
		y = int(image[p+9:p+13])
		d = int(image[p+13:p+16])
		if y < 2003:
			cutOff_Image = image
		else:
			if y >= 2003 and d < 151:
				cutOff_Image = image
for image in selectList[:]:
	if image.find("LT5") >= 0 or image.find("LT4") >= 0:
		cutOff_Image = image
# (3) Load images and cloudmasks into GDAL
print("Output-File:", composite_output)

# (3-A) Load all images into GDAL
image_GDAL_list = []
i = 1								# Count-Parameter for images
for image in imageList:
	imagePath = image
	i_str = str(i)
	img = "image_gdal_" + i_str
	image_GDAL_list.append(img)
	command = img + " = gdal.Open(imagePath, GA_ReadOnly)"
	exec(command)												
	i = i + 1
cutOff_Image_gdal = gdal.Open(cutOff_Image, GA_ReadOnly)

# (3-B) Load all cloud masks into GDAL
cloud_GDAL_list = []
m = 1								# Count-Parameter for masks
for cloud in cloudList:
	cloudPath = cloud
	m_str = str(m)
	cld = "cloud_gdal_" + m_str
	cloud_GDAL_list.append(cld)
	command = cld + " = gdal.Open(cloudPath, GA_ReadOnly)"
	exec(command)												
	m = m + 1

# (4) Start the process	

# (4-A) Define parameters for the new raster	
cols = image_gdal_1.RasterXSize
rows = image_gdal_1.RasterYSize
outDrv = gdal.GetDriverByName('ENVI')
options = []
output = outDrv.Create(composite_output, cols, rows, 6, GDT_UInt16, options)
output.SetProjection(image_gdal_1.GetProjection())
output.SetGeoTransform(image_gdal_1.GetGeoTransform())
NrImages = len(imageList)

# (4-B) Build the composite --> band by band, and each band row by row

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
		# Load in the cropp image --> but only band 1
		CO = np.ravel(cutOff_Image_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
		# Now rock it!
		NrI = 0
		dataOut = np.zeros(cols)
		command = "baseImage = " + iGDAL_List[NrI]
		exec(command)
		command = "cloud = " + cGDAL_List[NrI]
		exec(command)
		command = "np.putmask(dataOut, cloud == 0, baseImage)"	# clear observation --> value 0 in cloudmask
		exec(command)
		NrI = NrI + 1
		while NrI < NrImages:
			command = "image = " + iGDAL_List[NrI]
			exec(command)
			command = "cloud = " + cGDAL_List[NrI]
			exec(command)
			fillImage = np.zeros(cols)		
			command = "np.putmask(fillImage, cloud == 0, image)"		# clear observation --> value 0 in cloudmask
			exec(command)

			command = "np.putmask(dataOut, dataOut == 0, fillImage)"
			exec(command)
			NrI = NrI + 1
		# Assign to everyhting in the black region of the image the value 0
		finalImage = np.zeros(cols)
		np.putmask(finalImage, CO > 0, dataOut)
		finalImage.shape = (1, -1)
		output.GetRasterBand(band).WriteArray(np.array(finalImage), 0, y)
# Clothing the variables for the next composite
for img in image_GDAL_list:
	command = "img = None"
	exec(command)
for cld in cloud_GDAL_list:
	command = "cld = None"
	exec(command)

print("")

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")