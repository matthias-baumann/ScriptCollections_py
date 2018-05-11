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
PathRow = sys.argv[1]
output_folder = "E:\\tempdata\\mbaumann\\Forest_TrainingData\\"
source_folder = "E:\\tempdata\\mbaumann\\Composite_Building\\" + PathRow + "\\Composites\\"
MODIS_VCF = "E:\\tempdata\\mbaumann\\Forest_TrainingData\\MODIS-VCF"
bands = [1,2,3,4,5,6]
# ##### READY TO GO #####

# (0-A) Get the files in the source folder that we want to produce the training data for
inputList = os.listdir(source_folder)
for file in inputList[:]:
	if file.find(".hdr") >= 0 or file.find("Tests") >= 0:
		inputList.remove(file)

for file in inputList:
# (1) Taking the training samples

# (1-A) Load image into GDAL, define cols and rows, create output file
	print("Finding confident 'Forest' training data via moving window --> class value 1.")
	image = source_folder + file
	output = output_folder + file + "_ForestSamples"
	waterMask = output_folder + file + "_waterMask"
	
	image_gdal = gdal.Open(image, GA_ReadOnly)
	VCF_gdal = gdal.Open(MODIS_VCF, GA_ReadOnly)
	cols = image_gdal.RasterXSize
	rows = image_gdal.RasterYSize
	outDrv = gdal.GetDriverByName('ENVI')
	options = []
	
	out = outDrv.Create(output, cols, rows, 1, GDT_Byte, options)
	out.SetProjection(image_gdal.GetProjection())
	out.SetGeoTransform(image_gdal.GetGeoTransform())
	water = outDrv.Create(waterMask, cols, rows, 1, GDT_Byte, options)
	water.SetProjection(image_gdal.GetProjection())
	water.SetGeoTransform(image_gdal.GetGeoTransform())
	
# (1-B) Initialize moving window --> moving Window-size is 200x200 Pixel
	windowsize = 200
	for i in range(0, rows, windowsize):
		if i + windowsize < rows:
			numRows = windowsize
		else:
			numRows = rows - i
		for j in range(0, cols, windowsize):
			if j + windowsize < cols:
				numCols = windowsize
			else:
				numCols = cols - j
			
# (1-C) Load in the bands as specific types --> 'float32', 'int16'
			band3 = image_gdal.GetRasterBand(3).ReadAsArray(j, i, numCols, numRows).astype(np.int16)
			band4 = image_gdal.GetRasterBand(4).ReadAsArray(j, i, numCols, numRows).astype(np.int16)
			VCF = VCF_gdal.GetRasterBand(1).ReadAsArray(j, i, numCols, numRows).astype(np.int16)
			np.seterr(all='ignore')
			
# (1-D) Start the operations
			# Mask out water from image and save water mask later --> NDVI-Threshold is here 0.4
			mask = np.less((band4-band3)/(band4+band3), 0.4)
			waterMask = np.choose(mask, (0, 1))
			mask = np.logical_not(waterMask == 1)
			dataOut =  np.choose(mask, (0, band3))			
			# Determine min value of band (min = 1) and value of histogram max (frequency
			uniqueValues = np.unique(dataOut)
			length = uniqueValues.size
			histo = np.histogram(dataOut, bins = length)
			frq_histo = histo[0]
			max_frq_histo = max(frq_histo)
			pos_max_frq_histo = np.where(frq_histo == max_frq_histo)	# DN-value where forest-peak is
			pos_max_frq_histo = pos_max_frq_histo[0]					# In case the max-value is in two bins
			pos_max_frq_histo = int(pos_max_frq_histo[0])
			val_histo = histo[1]
			threshold = val_histo[pos_max_frq_histo]
			# Build Mask with the collected forest samples
			mask = np.less(band3, threshold)
			dataOut = np.choose(mask, (0, 1))
			# mask out the No-Data values from the image
			mask = np.logical_not(band3 == 0)
			dataOut = np.choose(mask, (0, dataOut))
			# Make consistency check using the MODIS-VCF file --> mask out values in areas VCF < 30
			mask = np.greater(VCF, 30)
			dataOut = np.choose(mask, (0, dataOut))
			
# (1-E) Write the output into the output-file and assign None-Values to the bands	
			out.GetRasterBand(1).WriteArray(dataOut,j, i)
			water.GetRasterBand(1).WriteArray(waterMask,j, i)
			band3 = None
			band4 = None
	image_gdal = None
	VCF = None


# (2) Calculate the forestness index on the entire image

# (2-A) Load images into GDAL, define cols and rows, create output file
	print("Calculating Integrated Forestness Index.")
	image = source_folder + file
	sample_input = output_folder + file + "_ForestSamples"
	waterMask = output_folder + file + "_waterMask"
	output = output_folder + file + "_ForestnessIndex"
		
	image_gdal = gdal.Open(image, GA_ReadOnly)
	sample_input_gdal = gdal.Open(sample_input, GA_ReadOnly)
	waterMask_gdal = gdal.Open(waterMask, GA_ReadOnly)
	cols = image_gdal.RasterXSize
	rows = image_gdal.RasterYSize
	outDrv = gdal.GetDriverByName('ENVI')
	options = []
	
	out = outDrv.Create(output, cols, rows, 1, GDT_Float32, options)
	out.SetProjection(image_gdal.GetProjection())
	out.SetGeoTransform(image_gdal.GetGeoTransform())

# (2-B) Get information from the bands about Mean and SD
	# Initialize IFI
	IFI = 0
	# Sum the FI values over bands --> exclude masked areas
	for band in bands:
		b = image_gdal.GetRasterBand(band).ReadAsArray(0, 0, cols, rows)
		sample = sample_input_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
		water = waterMask_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
		mask = np.logical_not(sample == 0)
		bs = np.choose(mask, (0, b))
		mask = np.logical_not(water == 1)
		bsw = np.choose(mask, (0, bs))
		b_masked = ma.masked_values(bsw, 0)
		mean = np.mean(b_masked)
		std = np.std(b_masked)
		IFI = IFI + (((b-mean)/std)*((b-mean)/std))
	# Do the remaining operations outside the SUM-symbol 
	IFI = IFI/6
	IFI = np.sqrt(IFI)
	
# (2-C) Write output into file
	out.GetRasterBand(1).WriteArray(IFI, 0, 0)
	image_gdal = None
	sample_input_gdal = None
	waterMask_gdal = None
	
# (3) Get training sites for confident Non-Forest via masking from forestness index, clip final image by loaded badn

# (3-A) Load all images and bands into Gdal and define cols, rows and outputfile + projections
	print("Finding confident 'Non-Forest' training data via thresholding from IFI-Image --> class value 2.")
	image = output_folder + file + "_ForestnessIndex"
	forest_samples = output_folder + file + "_ForestSamples"
	output = output_folder + file + "_ForestNonForestSamples"
	# load in band 1 form the image later to mask out values of 0 (background)
	clip = source_folder + file
	
	image_gdal = gdal.Open(image, GA_ReadOnly)
	forest_samples_gdal = gdal.Open(forest_samples, GA_ReadOnly)
	clip_gdal = gdal.Open(clip, GA_ReadOnly)
	VCF_gdal = gdal.Open(MODIS_VCF, GA_ReadOnly)
	cols = image_gdal.RasterXSize
	rows = image_gdal.RasterYSize
	outDrv = gdal.GetDriverByName('ENVI')
	options = []
	
	out = outDrv.Create(output, cols, rows, 1, GDT_Byte, options)
	out.SetProjection(image_gdal.GetProjection())
	out.SetGeoTransform(image_gdal.GetGeoTransform())
	
# (3-B) Initialize moving window --> moving Window-size is 100x100 Pixel
	windowsize = 100
	for i in range(0, rows, windowsize):
		if i + windowsize < rows:
			numRows = windowsize
		else:
			numRows = rows - i
		for j in range(0, cols, windowsize):
			if j + windowsize < cols:
				numCols = windowsize
			else:
				numCols = cols - j

# (3-C) Compile the masks and build the mask for training pixels of class 1 and 2				
			FI = image_gdal.GetRasterBand(1).ReadAsArray(j, i, numCols, numRows).astype(np.int16)
			ForSam = forest_samples_gdal.GetRasterBand(1).ReadAsArray(j, i, numCols, numRows).astype(np.int16)
			image_b1 = clip_gdal.GetRasterBand(1).ReadAsArray(j, i, numCols, numRows).astype(np.int16)
			VCF = VCF_gdal.GetRasterBand(1).ReadAsArray(j, i, numCols, numRows).astype(np.int16)
			# Start building output array, starting point are the forest samples
			dataOut = ForSam		
		# Set here the threshold fo confident non-forest --> Initital value
			mask = np.greater(FI, 6)			
			nonFor = np.choose(mask, (0, 2))
			# Bring the two masks together
			mask = np.logical_not(dataOut == 1)
			dataOut = np.choose(mask, (ForSam, nonFor))
			# mask out the '0' values using band 1 fromt eh original image
			mask = np.greater(image_b1, 0)
			dataOut = np.choose(mask, (0, dataOut))
			# Make consistency check for the confident non-forest pixels
			mask = np.greater(VCF, 30)
			dataOut = np.choose(mask, (0, dataOut))
			
			
			
			
			
			
			
			# Write the output and close the GDAL-files
			out.GetRasterBand(1).WriteArray(dataOut, 0, 0)
	image_gdal = None
	forest_samples_gdal = None
	clip_gdal = None
	VCF_gdal = None
	print("")

# (4) Get less pure pixels for forest --> class value 3
	print("Finding less pure pixels for 'forest' training data --> class-value 3.")
	
	
	


print("--------------------------------------------------------")
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")