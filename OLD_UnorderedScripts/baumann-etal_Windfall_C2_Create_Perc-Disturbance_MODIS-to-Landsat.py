# ### BEGIN OF HEADER INFROMATION AND LOADING OF MODULES (Not all modules are actually required for the analysis) #######################
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

root_folder = "E:\\tempdata\\mbaumann\\11_Windfall-classification_20120207\\RS_Data\\"
Landsat_file = "E:\\tempdata\\mbaumann\\11_Windfall-classification_20120207\\RS_Data\\Landsat_Disturbance-map_mosaic_subset"

Perc_Disturb = "E:\\tempdata\\mbaumann\\11_Windfall-classification_20120207\\RS_Data\\Landsat_Disturbance-map_mosaic_subset_MODIS-aggregated"

# ##### START THE SORTING #####

# (1) Make pre-work steps --> load into gdal, generate output file

# (1-A) Load Landsat into Gdal
Landsat_file_gdal = gdal.Open(Landsat_file, GA_ReadOnly)
cols = Landsat_file_gdal.RasterXSize
rows = Landsat_file_gdal.RasterYSize

# Re-Convert cols and rows, so that we have the edges (which are not 8x8 pixels) gonna get cut off
cols = 8*(math.floor(cols/8))
rows = 8*(math.floor(rows/8))
outDrv = gdal.GetDriverByName('ENVI')

# (1-B) Create output-file --> with 8x less cols and row, because we make the average of 8x8 pixels 
outputCols = int(cols/8)
outputRows = int(rows/8)

cols = cols-1
rows = rows-1

PDist = outDrv.Create(Perc_Disturb, outputCols, outputRows, 1, GDT_Float32)
PDist.SetProjection(Landsat_file_gdal.GetProjection())
PDist.SetGeoTransform(Landsat_file_gdal.GetGeoTransform())

# (2) Process the data

# (2-A) Build the output-array and set all values to zero.
dataOut = np.zeros((outputRows, outputCols))	# float64 is the default

# (2-B) Initialize Moving window --> MODIS-pixel is ~236m, equaling approximately 8x8 Landsat pixels
windowsize = 8
# define and initialize the row for the output-file
output_i = 0
output_j = 0

for i in range(0, cols, windowsize):
	if i + windowsize < cols:
		numCols = windowsize
	else:
		numCols = cols - i

	# define the col for the output-file
	output_j = 0	
	for j in range(0, rows, windowsize):
		if j + windowsize < rows:
			numRows = windowsize
		else:
			numRows = rows - j
	
# (2-C) Load in the bands as specific types --> 'float32', 'int16'
		Landsat = Landsat_file_gdal.GetRasterBand(1).ReadAsArray(i, j, numCols, numRows).astype(np.int)			

# (2-D) Mask everything into 1 (disturbance) and 0 (everything else)	--> disturbance-values are 3 and 4 in the change map
		mask = np.equal(Landsat, 3)		# cgabge back to 3
		D1 = np.choose(mask, (0, 1))
		mask = np.equal(Landsat, 4)
		D2 = np.choose(mask, (0, 1))
		mask = np.less(Landsat, 3)
		disturb = D1 + D2

# (2-E) Assess how many disturbance pixel are in the window and calculate the percentage
		distPixel = np.sum(disturb)
		distProp = (distPixel/(windowsize * windowsize))*100

# (2-F) Write the value into the dataOut-Array
		dataOut[output_j, output_i] = distProp
		output_j = output_j + 1
# (2-G) Make the output_j and output_i continue to increase 
	output_i = output_i + 1

# (2-H) Write the dataOut-array into the output-file	
PDist.GetRasterBand(1).WriteArray(dataOut, 0, 0)	
	
print("--------------------------------------------------------")
print("")

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: ", starttime)
print("end: ", endtime)
print("")