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
center_PathRow = sys.argv[1]
image_ID = sys.argv[2]
root_Folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\" + center_PathRow + "\\"
bands = [1,2,3,4,5,6]
MODIS_VCF = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\" + center_PathRow + "\\" + center_PathRow + "_MODIS-VCF"
# ##### READY TO GO #####

# (0) Define the files we are going to process
image = root_Folder + image_ID

ForestSamples = image + "_ForestSamples"
waterMask = image + "_waterMask"
ForestnessIndex = image + "_ForestnessIndex"
ForestNonForestSamples = image + "_ForestNonForestSamples"
TrainingData = image + "_training-data"
WaterIndex = image + "_NDWI"

# (1) Taking the training samples
print("Finding training data for:", image_ID)
# (1-A) Load image into GDAL, define cols and rows, create ForestSamples file
print("Find confident 'forest' training data and build water mask...")

image_gdal = gdal.Open(image, GA_ReadOnly)
VCF_gdal = gdal.Open(MODIS_VCF, GA_ReadOnly)
cols = image_gdal.RasterXSize
rows = image_gdal.RasterYSize
outDrv = gdal.GetDriverByName('ENVI')
options = []

out = outDrv.Create(ForestSamples, cols, rows, 1, GDT_Byte, options)
out.SetProjection(image_gdal.GetProjection())
out.SetGeoTransform(image_gdal.GetGeoTransform())
water = outDrv.Create(waterMask, cols, rows, 1, GDT_Byte, options)
water.SetProjection(image_gdal.GetProjection())
water.SetGeoTransform(image_gdal.GetGeoTransform())
NDWI_calc = outDrv.Create(WaterIndex, cols, rows, 1, GDT_Float32, options)
NDWI_calc.SetProjection(image_gdal.GetProjection())
NDWI_calc.SetGeoTransform(image_gdal.GetGeoTransform())

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
		band3 = image_gdal.GetRasterBand(3).ReadAsArray(j, i, numCols, numRows).astype(np.float32)
		band4 = image_gdal.GetRasterBand(4).ReadAsArray(j, i, numCols, numRows).astype(np.float32)
		band5 = image_gdal.GetRasterBand(5).ReadAsArray(j, i, numCols, numRows).astype(np.float32)
		VCF = VCF_gdal.GetRasterBand(1).ReadAsArray(j, i, numCols, numRows).astype(np.float32)
		np.seterr(all='ignore')
		
# (1-D) Start the operations
		# Mask out water from image and save water mask later --> NDVI-Threshold is here 0.4
		NDVI = np.float16((band4-band3)/(band4+band3))
		NDWI = np.float16((band4-band5)/(band4+band5))
		mask = np.less(NDVI, 0.4)
		VT = np.choose(mask, (0, 1))
		mask = np.greater(NDWI, 0.5)
		WT = np.choose(mask, (0, 1))
		temp = VT + WT
		mask = np.greater(temp, 0)
		wM = np.choose(mask, (0,1))
		wM[np.isnan(NDVI)] = 1
		mask = np.logical_not(wM == 1)
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
		# Make consistency check using the MODIS-VCF file --> mask out values in areas VCF < 40
		mask = np.greater(VCF, 40)
		dataOut = np.choose(mask, (0, dataOut))

# (1-E) Write the output into the output-file and assign None-Values to the bands	
		out.GetRasterBand(1).WriteArray(dataOut,j, i)
		water.GetRasterBand(1).WriteArray(wM,j, i)
		NDWI_calc.GetRasterBand(1).WriteArray(NDWI,j, i)

		band3 = None
		band4 = None
image_gdal = None
VCF = None

# (2) Calculate the forestness index on the entire image

# (2-A) Load images into GDAL, define cols and rows, create ForestnessIndex file
print("Calculating Integrated Forestness Index...")
image_gdal = gdal.Open(image, GA_ReadOnly)
sample_input_gdal = gdal.Open(ForestSamples, GA_ReadOnly)
waterMask_gdal = gdal.Open(waterMask, GA_ReadOnly)

cols = image_gdal.RasterXSize
rows = image_gdal.RasterYSize
outDrv = gdal.GetDriverByName('ENVI')
options = []

out = outDrv.Create(ForestnessIndex, cols, rows, 1, GDT_Float32, options)
out.SetProjection(image_gdal.GetProjection())
out.SetGeoTransform(image_gdal.GetGeoTransform())

# (2-B) Get information from the bands about Mean and SD and calculte IFI for entire scene
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

# (2-C) Write ForestnessIndex into file
out.GetRasterBand(1).WriteArray(IFI, 0, 0)
image_gdal = None
sample_input_gdal = None
waterMask_gdal = None

# (3) Get training sites for confident Non-Forest via masking from forestness index, clip final image by loaded badn

# (3-A) Load all images and bands into Gdal and define cols, rows and outputfile + projections
print("Finding confident 'Non-Forest' training data via thresholding from IFI-Image.")
image_gdal = gdal.Open(ForestnessIndex, GA_ReadOnly)
forest_samples_gdal = gdal.Open(ForestSamples, GA_ReadOnly)
clip_gdal = gdal.Open(image, GA_ReadOnly)
VCF_gdal = gdal.Open(MODIS_VCF, GA_ReadOnly)
cols = image_gdal.RasterXSize
rows = image_gdal.RasterYSize
outDrv = gdal.GetDriverByName('ENVI')
options = []

out = outDrv.Create(ForestNonForestSamples, cols, rows, 1, GDT_Byte, options)
out.SetProjection(image_gdal.GetProjection())
out.SetGeoTransform(image_gdal.GetGeoTransform())

# (3-B) Initialize moving window --> moving Window-size is 50x50 Pixel
windowsize = 50
windowpixel = windowsize * windowsize
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
		IFI_T = 6
		VCF_T = 0.7							# Threshold for the amount of pixels with VCF<0.3 in the moving window
		NF_T = 0.4							# Threshold for assigned forested pixel for 

		# (3-C) Compile the masks and build the mask for training pixels of class 1 and 2				
		FI = image_gdal.GetRasterBand(1).ReadAsArray(j, i, numCols, numRows).astype(np.int16)
		ForSam = forest_samples_gdal.GetRasterBand(1).ReadAsArray(j, i, numCols, numRows).astype(np.int16)
		image_b1 = clip_gdal.GetRasterBand(1).ReadAsArray(j, i, numCols, numRows).astype(np.int16)
		VCF = VCF_gdal.GetRasterBand(1).ReadAsArray(j, i, numCols, numRows).astype(np.int16)
		# Build the dataOut --> make it the same as the ForSam
		dataOut = ForSam			
		# Set here the threshold fo confident non-forest --> Initital value then loop until threshold is there
		mask = np.greater(FI, IFI_T)			
		nonFor = np.choose(mask, (0, 1))
		# Make consistency check for the confident non-forest pixels
		mask = np.less(VCF, 40)
		VCF_control = np.choose(mask, (0, 1))
		# How many pixels are non-forest and how many are VCF<30%?
		sum_VCF = np.sum(VCF_control)
		sum_nonFor = np.sum(nonFor)
		while sum_VCF/windowpixel > VCF_T and sum_nonFor/windowpixel < NF_T:
			# Reduce IFI-Threshold by 0.1 and repeat all steps from above until the thresholds are met
			IFI_T = IFI_T - 0.1
			mask = np.greater(FI, IFI_T)
			nonFor = np.choose(mask, (0, 1))
			mask = np.less(VCF, 30)
			VCF_control = np.choose(mask, (0, 1))
			sum_VCF = np.sum(VCF_control)
			sum_nonFor = np.sum(nonFor)
		# Bring the two masks together
		mask = np.logical_not(dataOut == 1)
		dataOut = np.choose(mask, (dataOut, 2*nonFor))
		# mask out the '0' values using band 1 fromt eh original image
		mask = np.greater(image_b1, 0)
		dataOut = np.choose(mask, (0, dataOut))
		# Write the output and close the GDAL-files
		out.GetRasterBand(1).WriteArray(dataOut, j, i)
image_gdal = None
forest_samples_gdal = None
clip_gdal = None
VCF_gdal = None


# (4) Get less pure pixels for non-forest
print("Find less pure pixels for forest and non-forest class.")

# (4-A) Load all images into GDAL and create
FI_gdal = gdal.Open(ForestnessIndex, GA_ReadOnly)
sample_gdal = gdal.Open(ForestNonForestSamples, GA_ReadOnly)
cols = FI_gdal.RasterXSize
rows = FI_gdal.RasterYSize
outDrv = gdal.GetDriverByName('ENVI')
options = []

out = outDrv.Create(TrainingData, cols, rows, 1, GDT_Byte, options)
out.SetProjection(FI_gdal.GetProjection())
out.SetGeoTransform(FI_gdal.GetGeoTransform())

# (4-B) Initialize moving window --> windowsize 10
windowsize = 10
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

# (4-C) Load in the bands as specific types --> 'float32', 'int16'
		TD = sample_gdal.GetRasterBand(1).ReadAsArray(j, i, numCols, numRows).astype(np.int16)
		IFI = FI_gdal.GetRasterBand(1).ReadAsArray(j, i, numCols, numRows).astype(np.float32)
		IFI_mask_NF = np.greater(IFI, 2.5)
		IFI_threshold_NF = np.choose(IFI_mask_NF, (0, 2))
		IFI_mask_F = np.less(IFI, 4)
		IFI_threshold_F = np.choose(IFI_mask_F, (0, 1))
		dataOut = TD

# (4-D) Start the operations
		# look for each element in array and check if it has the value 2
		indexsize = 1
		for p in range(0, windowsize, indexsize):		# rows
			for q in range(0, windowsize, indexsize):	# columns
				value = TD[p,q]
				# If value is 2, then select the neighboring elements of fields to make non-forest
				if value == 2:
					if q == 0:
						col_left = 0
					else:
						col_left = q - 1
					if q == windowsize:
						col_right = windowsize
					else:
						col_right = q + 2						
					if p == 0:
						row_up = 0
					else:
						row_up = p - 1
					if p == windowsize:
						row_down = windowsize
					else:
						row_down = p + 2
					# Create local arrays where we to the value updating
					local_subset = TD[row_up:row_down, col_left:col_right]
					local_IFI = IFI_threshold_NF[row_up:row_down, col_left:col_right]
					mask = np.equal(local_subset, 0)
					local_dataOut = np.choose(mask, (local_subset, local_IFI))
					# Write the local dataOut into the big one
					dataOut[row_up:row_down, col_left:col_right] = local_dataOut

				# # If value is 1, then select the neighboring elements of field to make forest
				# # Not operational yet, leads to overestimations --> currently not activated therefore
				# # Solution probably in the consideration of the processes sequentially, testing soon...
				# if value == 1:
					# if q == 0:
						# col_left = 0
					# else:
						# col_left = q - 1
					# if q == windowsize:
						# col_right = windowsize
					# else:
						# col_right = q + 2						
					# if p == 0:
						# row_up = 0
					# else:
						# row_up = p - 1
					# if p == windowsize:
						# row_down = windowsize
					# else:
						# row_down = p + 2
					# # Create local arrays where we to the value updating
					# local_subset = TD[row_up:row_down, col_left:col_right]
					# local_IFI = IFI_threshold_F[row_up:row_down, col_left:col_right]
					# mask = np.equal(local_subset, 0)
					# local_dataOut = np.choose(mask, (local_subset, local_IFI))
					# # Write the local dataOut into the big one
					# dataOut[row_up:row_down, col_left:col_right] = local_dataOut	
					
# (4-E) write the output into the file
		out.GetRasterBand(1).WriteArray(dataOut, j, i)
FI_gdal = None
sample_gdal = None


# (5-E) Delete all files from the input steps - except 'training data', 'forestness Index' and 'water-mask'

ForestSamples_hdr = ForestSamples + ".hdr"
ForestNonForestSamples_hdr = ForestNonForestSamples + ".hdr"
os.remove(ForestSamples)
os.remove(ForestSamples_hdr)
os.remove(ForestNonForestSamples)
os.remove(ForestNonForestSamples_hdr)


print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")