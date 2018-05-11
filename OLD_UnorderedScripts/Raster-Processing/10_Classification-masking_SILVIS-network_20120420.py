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

root_Folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\000001_Maps\\"

print("--------------------------------------------------------")
print("Masking WaterMasks")
# (1) mask out the classifications by the 0-0-0 values of the image

# (1-A) Prepare a list of the files
list  = os.listdir(root_Folder)

# (1-B) Remote all files that are not 'composite'
for file in list[:]:
	if file.find("waterMask") < 0 or file.find(".hdr") >= 0 or file.find("masked") >= 0:
		list.remove(file)

# (2) Now loop through all the files and process them
for file in list[:]:

# (2-A) Create tell the input-, classification-, and output-files
	classification = root_Folder + file
	image = classification
	image = image.replace("waterMask","composite")
	output = classification + "-masked"

# (3) Process the data
	print("Process file:", file)
	
# (3-A) Load everything into GDAL, generate properties, and create output-file
	classification_gdal = gdal.Open(classification, GA_ReadOnly)
	image_gdal = gdal.Open(image, GA_ReadOnly)
	cols = classification_gdal.RasterXSize
	rows = classification_gdal.RasterYSize
	
	outDrv = gdal.GetDriverByName('ENVI')
	options = []
	out = outDrv.Create(output, cols, rows, 1, GDT_Byte, options)
	out.SetProjection(classification_gdal.GetProjection())
	out.SetGeoTransform(classification_gdal.GetGeoTransform())
	
# (3-B) Process row by row	
	for y in range(rows):
		# load in the band 1 of the image
		b1 = np.ravel(image_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
		# load in the classification
		clas = np.ravel(classification_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
		# initialize the dataOut
		dataOut = np.zeros(cols)
		np.putmask(dataOut, b1 > 0, clas)
		# write the output-file		
		dataOut.shape = (1, -1)
		out.GetRasterBand(1).WriteArray(np.array(dataOut), 0, y)

# (4) Close the GDAL-variables
	classification_gdal = None	
	image_gdal = None
	
	
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")