# ######################################## LOAD REQUIRED MODULES ############################################### #
import os
import sys
import time
import datetime
import ogr
import osr
from osgeo import gdal
from osgeo.gdalconst import *
import numpy as np
from osgeo import gdal_array as gdalnumeric
import csv
import itertools
import math
gdal.TermProgress = gdal.TermProgress_nocb
gdal.TermProgress = gdal.TermProgress_nocb
import scipy.ndimage

# ##### ##################################SET TIME-COUNT ######################################################## #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
#print("Starting process, time:", starttime)
print("")

# ######################################## SET HARD CODED FOLDER PATHS AND SHP-FILE INPUTS ###################### #
Landsat_184018 = "E:/kirkdata/mbaumann/Landsat_Processing/Landsat/184018/"
Landsat_185018 = "E:/kirkdata/mbaumann/Landsat_Processing/Landsat/185018/"
full_shp = "E:/kirkdata/mbaumann/Species-separation_Chapter03/Plot-data_V01.shp"

# ######################################## START THE ANALYSIS ################################################### #

# (1) CREATE THE TABLE FOR THE LANDSAT IDs, PATHROW, YEAR, MONTH, DATE
output = "E:/kirkdata/mbaumann/Species-separation_Chapter03/00_LandsatAncillary.txt"
print("Creating table with Landsat information")

# (1-A) CREATE EMPTY LISTS FOR THE INFORMATION WE WANT
ID = []
year = []
month = []
day = []

# (1-B) LOOP THROUGH THE LANDSAT FOLDERS AND EXTRACT THE INFORMATION
folder_list = os.listdir(Landsat_184018)
for folder in folder_list[:]:
	ID.append(folder)
	input = Landsat_184018 + folder + "/" + folder + "_MTL.txt"
	inputOpen = open(input, "r")
	for line in inputOpen:
		if line.find("DATE_ACQUIRED") >= 0:
			p1 = line.find("=")
			year.append(line[p1+2:p1+6])
			month.append(line[p1+7:p1+9])
			day.append(line[p1+10:p1+12])
	inputOpen.close()
folder_list = os.listdir(Landsat_185018)
for folder in folder_list[:]:
	ID.append(folder)
	input = Landsat_185018 + folder + "/" + folder + "_MTL.txt"
	inputOpen = open(input, "r")
	for line in inputOpen:
		if line.find("DATE_ACQUIRED") >= 0:
			p1 = line.find("=")
			year.append(line[p1+2:p1+6])
			month.append(line[p1+7:p1+9])
			day.append(line[p1+10:p1+12])
	inputOpen.close()

# (1-C) WRITE LIST INTO OUTPUT-FILE
output_open = open(output, "w")
output_open.write("Scene_ID Year Month Day \n")
for id in ID:
	i = ID.index(id)
	output_open.write(id + " " + year[i] + " " + month[i] + " " + day[i] + "\n")
output_open.close()
print("DONE")
print("")


# (2) CREATE THE ZONAL STATISTICS
print("Load the shapefile into python")

# (2-A) LOAD THE SHAPE-FILE INTO GDAL/OGR - CREATE AND POPULATE LIST WITH POLYGON-IDs, create empty list-List (lists for the scene-ID lists)
lists_list = []
driver = ogr.GetDriverByName('ESRI Shapefile')
input = driver.Open(full_shp, 0)
layer = input.GetLayer(0)
PolygonID_list = []
feature = layer.GetNextFeature()
# Fill the ID-list for later
IDoutputList = []
IDoutputList.append("ID")
while feature:
	id = feature.GetField('ID')
	PolygonID_list.append(id)
	IDoutputList.append(id)
	feature = layer.GetNextFeature()
print("DONE")
print("")

# (2-B) GET INTO THE LANDSAT FOLDERS
print("Processing Zonal Statistics")
print("---------------------------")
# Generate output-lists --> it's a "list of lists", first item in the list are "ID", then every footprint and values get own list which we append after zonalstats
sceneLIST_list_b1 = []
sceneLIST_list_b2 = []
sceneLIST_list_b3 = []
sceneLIST_list_b4 = []
sceneLIST_list_b5 = []
sceneLIST_list_b6 = []
sceneLIST_list_NDVI = []
sceneLIST_list_TCB = []
sceneLIST_list_TCG = []
sceneLIST_list_TCW = []
sceneLIST_list_THERMAL = []


# Process Footprint 184018
list1 = os.listdir(Landsat_184018)
for folder in list1:
	print("Scene:", folder, "-->", list1.index(folder) + 1, "of", len(list1), "overall FP 184018.")
	# Create list for values of current scene
	scene = str(folder)
	# BAND 1 values --> other bands/values hidden
	statement = scene + "b1_values = []"
	exec(statement)
	statement = folder + 'b1_values.append("' + folder + '")'
	exec(statement)
	# BAND 2 values
	statement = scene + "b2_values = []"
	exec(statement)
	statement = folder + 'b2_values.append("' + folder + '")'
	exec(statement)
	# BAND 3 values
	statement = scene + "b3_values = []"
	exec(statement)
	statement = folder + 'b3_values.append("' + folder + '")'
	exec(statement)
	# BAND 4 values
	statement = scene + "b4_values = []"
	exec(statement)
	statement = folder + 'b4_values.append("' + folder + '")'
	exec(statement)
	# BAND 5 values
	statement = scene + "b5_values = []"
	exec(statement)
	statement = folder + 'b5_values.append("' + folder + '")'
	exec(statement)
	# BAND 6 values
	statement = scene + "b6_values = []"
	exec(statement)
	statement = folder + 'b6_values.append("' + folder + '")'
	exec(statement)
	# NDVI values
	statement = scene + "NDVI_values = []"
	exec(statement)
	statement = folder + 'NDVI_values.append("' + folder + '")'
	exec(statement)	
	# Tasseled Cap Brightness values
	statement = scene + "TCB_values = []"
	exec(statement)
	statement = folder + 'TCB_values.append("' + folder + '")'
	exec(statement)
	# Tasseled Cap Greenness values
	statement = scene + "TCG_values = []"
	exec(statement)
	statement = folder + 'TCG_values.append("' + folder + '")'
	exec(statement)	
	# Tasseled Cap Wetness values
	statement = scene + "TCW_values = []"
	exec(statement)
	statement = folder + 'TCW_values.append("' + folder + '")'
	exec(statement)		
	# Thermal band values
	statement = scene + "Thermal_values = []"
	exec(statement)
	statement = folder + 'Thermal_values.append("' + folder + '")'
	exec(statement)	
	
	# Load the images into GDAL
	# Determine Path to the Landsat data
	image = Landsat_184018 + folder + "/" + folder
	cloudmask = image + "_MTLFmask"
	thermal = image + "_ThermalBand"
	MTL = image + "_MTL.txt"
	# Get boundary coordinates for mask from MTL file
	print("Get boundary coordinates")
	sourceTXTopen = open(MTL, "r")
	for line in sourceTXTopen:
		if line.find("CORNER_UL_PROJECTION_X_PRODUCT") >= 0:		# Check Upper Left Coordinates
			p1 = line.find("=")
			p2 = line.rfind("0")
			ul_x = float(line[p1+2:p2])
		if line.find("CORNER_UL_PROJECTION_Y_PRODUCT") >= 0:
			p1 = line.find("=")
			p2 = line.rfind("0")
			ul_y = float(line[p1+2:p2])
		if line.find("CORNER_LR_PROJECTION_X_PRODUCT") >= 0:		# Check Lower Right Coordinates
			p1 = line.find("=")
			p2 = line.rfind("0")
			lr_x = float(line[p1+2:p2])
		if line.find("CORNER_LR_PROJECTION_Y_PRODUCT") >= 0:
			p1 = line.find("=")
			p2 = line.rfind("0")
			lr_y = float(line[p1+2:p2])
	sourceTXTopen.close()
	# Convert shapefile into raster
	print("Convert vector to raster")
	outTMP = image + "_TMP-mask"
	command = "gdal_rasterize -a ID -tr 30 30 -ot Int16 -q -of ENVI -te " + str(ul_x) + " " + str(lr_y) + " " + str(lr_x) + " " + str(ul_y) + " " + full_shp + " " + outTMP
	os.system(command)
	# Load Image and Mask into GDAL
	
	image_gdal = gdal.Open(image, GA_ReadOnly)
	polygon_gdal = gdal.Open(outTMP, GA_ReadOnly)
	cloud_gdal = gdal.Open(cloudmask, GA_ReadOnly)
	thermal_gdal = gdal.Open(thermal, GA_ReadOnly)
	cols = polygon_gdal.RasterXSize						# Check here later why mask_gdal is missing 1 pixel in x and y direction
	rows = polygon_gdal.RasterYSize
	
	print("Load images, mask clouds, transform images")
	# Load images into Gdal
	band1 = image_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
	band2 = image_gdal.GetRasterBand(2).ReadAsArray(0, 0, cols, rows)
	band3 = image_gdal.GetRasterBand(3).ReadAsArray(0, 0, cols, rows)
	band4 = image_gdal.GetRasterBand(4).ReadAsArray(0, 0, cols, rows)
	band5 = image_gdal.GetRasterBand(5).ReadAsArray(0, 0, cols, rows)
	band6 = image_gdal.GetRasterBand(6).ReadAsArray(0, 0, cols, rows)
	polygons = polygon_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
	cloud = cloud_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
	bandTherm = thermal_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
	np.seterr(all='ignore')
	# Calculate the transformed bands manually beforehand
	NDVI = np.float16((band4-band3)/(band4+band3))
	TCB = np.float32((0.3037*band1) + (0.2793*band2) + (0.4343*band3) + (0.5585*band4) + (0.5082*band5) + (0.1863*band6))
	TCG = np.float32((-0.2848*band1) + (-0.2435*band2) + (-0.5436*band3) + (0.7243*band4) + (0.0840*band5) + (-0.1800*band6))
	TCW = np.float32((0.1509*band1) + (0.1793*band2) + (0.3299*band3) + (0.3406*band4) + (-0.7112*band5) + (-0.4572*band6))
	#Mask out clouds, set values to 0 --> make np-masked arrays
	mask = np.equal(cloud, 0)					
	b1_masked = np.choose(mask, (0, band1))
	b1_np_masked = np.ma.masked_array(b1_masked, b1_masked == 0)
	b2_masked = np.choose(mask, (0, band2))
	b2_np_masked = np.ma.masked_array(b2_masked, b2_masked == 0)
	b3_masked = np.choose(mask, (0, band3))
	b3_np_masked = np.ma.masked_array(b3_masked, b3_masked == 0)
	b4_masked = np.choose(mask, (0, band4))
	b4_np_masked = np.ma.masked_array(b4_masked, b4_masked == 0)
	b5_masked = np.choose(mask, (0, band5))
	b5_np_masked = np.ma.masked_array(b5_masked, b5_masked == 0)
	b6_masked = np.choose(mask, (0, band6))
	b6_np_masked = np.ma.masked_array(b6_masked, b6_masked == 0)
	NDVI_masked = np.choose(mask, (0, NDVI))
	NDVI_np_masked = np.ma.masked_array(NDVI_masked, NDVI_masked == 0)
	TCB_masked = np.choose(mask, (0, TCB))
	TCB_np_masked = np.ma.masked_array(TCB_masked, TCB_masked == 0)
	TCG_masked = np.choose(mask, (0, TCG))
	TCG_np_masked = np.ma.masked_array(TCG_masked, TCG_masked == 0)
	TCW_masked = np.choose(mask, (0, TCW))
	TCW_np_masked = np.ma.masked_array(TCW_masked, TCW_masked == 0)	
	Thermal_masked = np.choose(mask, (0, bandTherm))
	Thermal_np_masked = np.ma.masked_array(Thermal_masked, Thermal_masked == 0)
	
	# Calculate statistics 
	print("Calculate statistics")
	# BAND 1
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_b1 = scipy.ndimage.measurements.mean(b1_np_masked, labels = polygons, index = index)
	mean_b1 = np.ndarray.tolist(mean_b1)
	statement = scene + "b1_values = " + scene + "b1_values + mean_b1"
	exec(statement)
	# BAND 2
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_b2 = scipy.ndimage.measurements.mean(b2_np_masked, labels = polygons, index = index)
	mean_b2 = np.ndarray.tolist(mean_b2)
	statement = scene + "b2_values = " + scene + "b2_values + mean_b2"
	exec(statement)
	# BAND 3
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_b3 = scipy.ndimage.measurements.mean(b3_np_masked, labels = polygons, index = index)
	mean_b3 = np.ndarray.tolist(mean_b3)
	statement = scene + "b3_values = " + scene + "b3_values + mean_b3"
	exec(statement)	
	# BAND 4
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_b4 = scipy.ndimage.measurements.mean(b4_np_masked, labels = polygons, index = index)
	mean_b4 = np.ndarray.tolist(mean_b4)
	statement = scene + "b4_values = " + scene + "b4_values + mean_b4"
	exec(statement)		
	# BAND 5
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_b5 = scipy.ndimage.measurements.mean(b5_np_masked, labels = polygons, index = index)
	mean_b5 = np.ndarray.tolist(mean_b5)
	statement = scene + "b5_values = " + scene + "b5_values + mean_b5"
	exec(statement)		
	# BAND 6
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_b6 = scipy.ndimage.measurements.mean(b6_np_masked, labels = polygons, index = index)
	mean_b6 = np.ndarray.tolist(mean_b6)
	statement = scene + "b6_values = " + scene + "b6_values + mean_b6"
	exec(statement)		
	# NDVI
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_NDVI = scipy.ndimage.measurements.mean(NDVI_np_masked, labels = polygons, index = index)
	mean_NDVI = np.ndarray.tolist(mean_NDVI)
	statement = scene + "NDVI_values = " + scene + "NDVI_values + mean_NDVI"
	exec(statement)
	# TCB
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_TCB = scipy.ndimage.measurements.mean(TCB_np_masked, labels = polygons, index = index)
	mean_TCB = np.ndarray.tolist(mean_TCB)
	statement = scene + "TCB_values = " + scene + "TCB_values + mean_TCB"
	exec(statement)		
	# TCG
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_TCG = scipy.ndimage.measurements.mean(TCG_np_masked, labels = polygons, index = index)
	mean_TCG = np.ndarray.tolist(mean_TCG)
	statement = scene + "TCG_values = " + scene + "TCG_values + mean_TCG"
	exec(statement)	
	# TCW
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_TCW = scipy.ndimage.measurements.mean(TCW_np_masked, labels = polygons, index = index)
	mean_TCW = np.ndarray.tolist(mean_TCW)
	statement = scene + "TCW_values = " + scene + "TCW_values + mean_TCW"
	exec(statement)	
	# THERMAL
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_Thermal = scipy.ndimage.measurements.mean(Thermal_np_masked, labels = polygons, index = index)
	mean_Thermal = np.ndarray.tolist(mean_Thermal)
	statement = scene + "Thermal_values = " + scene + "Thermal_values + mean_Thermal"
	exec(statement)		
	
	# Set variables to zero 
	image_gdal = None
	polygon_gdal = None
	cloud_gdal = None
	thermal_gdal = None	
	
	# Create output Lists
	statement = "sceneLIST_list_b1.append(" + scene + "b1_values)"	# Other lists hidden for better view
	exec(statement)
	statement = "sceneLIST_list_b2.append(" + scene + "b2_values)"
	exec(statement)
	statement = "sceneLIST_list_b3.append(" + scene + "b3_values)"
	exec(statement)
	statement = "sceneLIST_list_b4.append(" + scene + "b4_values)"
	exec(statement)
	statement = "sceneLIST_list_b5.append(" + scene + "b5_values)"
	exec(statement)
	statement = "sceneLIST_list_b6.append(" + scene + "b6_values)"
	exec(statement)
	statement = "sceneLIST_list_NDVI.append(" + scene + "NDVI_values)"
	exec(statement)
	statement = "sceneLIST_list_TCB.append(" + scene + "TCB_values)"
	exec(statement)
	statement = "sceneLIST_list_TCG.append(" + scene + "TCG_values)"
	exec(statement)
	statement = "sceneLIST_list_TCW.append(" + scene + "TCW_values)"
	exec(statement)
	statement = "sceneLIST_list_THERMAL.append(" + scene + "Thermal_values)"
	exec(statement)

	print("Delete TMP-Files")
	deleteTMP = image + "_TMP-mask"
	os.remove(deleteTMP)
	deleteTMPhdr = image + "_TMP-mask.hdr"
	os.remove(deleteTMPhdr)
	print("")
	

# Process Footprint 185018
list2 = os.listdir(Landsat_185018)
for folder in list2:
	print("Scene:", folder, "-->", list2.index(folder) + 1, "of", len(list2), "overall FP 185018.")
	# Create list for values of current scene
	scene = str(folder)
	# BAND 1 values --> other bands/values hidden
	statement = scene + "b1_values = []"
	exec(statement)
	statement = folder + 'b1_values.append("' + folder + '")'
	exec(statement)
	# BAND 2 values
	statement = scene + "b2_values = []"
	exec(statement)
	statement = folder + 'b2_values.append("' + folder + '")'
	exec(statement)
	# BAND 3 values
	statement = scene + "b3_values = []"
	exec(statement)
	statement = folder + 'b3_values.append("' + folder + '")'
	exec(statement)
	# BAND 4 values
	statement = scene + "b4_values = []"
	exec(statement)
	statement = folder + 'b4_values.append("' + folder + '")'
	exec(statement)
	# BAND 5 values
	statement = scene + "b5_values = []"
	exec(statement)
	statement = folder + 'b5_values.append("' + folder + '")'
	exec(statement)
	# BAND 6 values
	statement = scene + "b6_values = []"
	exec(statement)
	statement = folder + 'b6_values.append("' + folder + '")'
	exec(statement)
	# NDVI values
	statement = scene + "NDVI_values = []"
	exec(statement)
	statement = folder + 'NDVI_values.append("' + folder + '")'
	exec(statement)	
	# Tasseled Cap Brightness values
	statement = scene + "TCB_values = []"
	exec(statement)
	statement = folder + 'TCB_values.append("' + folder + '")'
	exec(statement)
	# Tasseled Cap Greenness values
	statement = scene + "TCG_values = []"
	exec(statement)
	statement = folder + 'TCG_values.append("' + folder + '")'
	exec(statement)	
	# Tasseled Cap Wetness values
	statement = scene + "TCW_values = []"
	exec(statement)
	statement = folder + 'TCW_values.append("' + folder + '")'
	exec(statement)		
	# Thermal band values
	statement = scene + "Thermal_values = []"
	exec(statement)
	statement = folder + 'Thermal_values.append("' + folder + '")'
	exec(statement)	
	
	# Load the images into GDAL
	# Determine Path to the Landsat data
	image = Landsat_185018 + folder + "/" + folder
	cloudmask = image + "_MTLFmask"
	thermal = image + "_ThermalBand"
	MTL = image + "_MTL.txt"
	# Get boundary coordinates for mask from MTL file
	print("Get boundary coordinates")
	sourceTXTopen = open(MTL, "r")
	for line in sourceTXTopen:
		if line.find("CORNER_UL_PROJECTION_X_PRODUCT") >= 0:		# Check Upper Left Coordinates
			p1 = line.find("=")
			p2 = line.rfind("0")
			ul_x = float(line[p1+2:p2])
		if line.find("CORNER_UL_PROJECTION_Y_PRODUCT") >= 0:
			p1 = line.find("=")
			p2 = line.rfind("0")
			ul_y = float(line[p1+2:p2])
		if line.find("CORNER_LR_PROJECTION_X_PRODUCT") >= 0:		# Check Lower Right Coordinates
			p1 = line.find("=")
			p2 = line.rfind("0")
			lr_x = float(line[p1+2:p2])
		if line.find("CORNER_LR_PROJECTION_Y_PRODUCT") >= 0:
			p1 = line.find("=")
			p2 = line.rfind("0")
			lr_y = float(line[p1+2:p2])
	sourceTXTopen.close()
	# Convert shapefile into raster
	print("Convert vector to raster")
	outTMP = image + "_TMP-mask"
	command = "gdal_rasterize -a ID -tr 30 30 -ot Int16 -q -of ENVI -te " + str(ul_x) + " " + str(lr_y) + " " + str(lr_x) + " " + str(ul_y) + " " + full_shp + " " + outTMP
	os.system(command)
	# Load Image and Mask into GDAL
	
	image_gdal = gdal.Open(image, GA_ReadOnly)
	polygon_gdal = gdal.Open(outTMP, GA_ReadOnly)
	cloud_gdal = gdal.Open(cloudmask, GA_ReadOnly)
	thermal_gdal = gdal.Open(thermal, GA_ReadOnly)
	cols = polygon_gdal.RasterXSize						# Check here later why mask_gdal is missing 1 pixel in x and y direction
	rows = polygon_gdal.RasterYSize
	
	print("Load images, mask clouds, transform images")
	# Load images into Gdal
	band1 = image_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
	band2 = image_gdal.GetRasterBand(2).ReadAsArray(0, 0, cols, rows)
	band3 = image_gdal.GetRasterBand(3).ReadAsArray(0, 0, cols, rows)
	band4 = image_gdal.GetRasterBand(4).ReadAsArray(0, 0, cols, rows)
	band5 = image_gdal.GetRasterBand(5).ReadAsArray(0, 0, cols, rows)
	band6 = image_gdal.GetRasterBand(6).ReadAsArray(0, 0, cols, rows)
	polygons = polygon_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
	cloud = cloud_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
	bandTherm = thermal_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
	np.seterr(all='ignore')
	# Calculate the transformed bands manually beforehand
	NDVI = np.float16((band4-band3)/(band4+band3))
	TCB = np.float32((0.3037*band1) + (0.2793*band2) + (0.4343*band3) + (0.5585*band4) + (0.5082*band5) + (0.1863*band6))
	TCG = np.float32((-0.2848*band1) + (-0.2435*band2) + (-0.5436*band3) + (0.7243*band4) + (0.0840*band5) + (-0.1800*band6))
	TCW = np.float32((0.1509*band1) + (0.1793*band2) + (0.3299*band3) + (0.3406*band4) + (-0.7112*band5) + (-0.4572*band6))
	#Mask out clouds, set values to 0 --> make np-masked arrays
	mask = np.equal(cloud, 0)					
	b1_masked = np.choose(mask, (0, band1))
	b1_np_masked = np.ma.masked_array(b1_masked, b1_masked == 0)
	b2_masked = np.choose(mask, (0, band2))
	b2_np_masked = np.ma.masked_array(b2_masked, b2_masked == 0)
	b3_masked = np.choose(mask, (0, band3))
	b3_np_masked = np.ma.masked_array(b3_masked, b3_masked == 0)
	b4_masked = np.choose(mask, (0, band4))
	b4_np_masked = np.ma.masked_array(b4_masked, b4_masked == 0)
	b5_masked = np.choose(mask, (0, band5))
	b5_np_masked = np.ma.masked_array(b5_masked, b5_masked == 0)
	b6_masked = np.choose(mask, (0, band6))
	b6_np_masked = np.ma.masked_array(b6_masked, b6_masked == 0)
	NDVI_masked = np.choose(mask, (0, NDVI))
	NDVI_np_masked = np.ma.masked_array(NDVI_masked, NDVI_masked == 0)
	TCB_masked = np.choose(mask, (0, TCB))
	TCB_np_masked = np.ma.masked_array(TCB_masked, TCB_masked == 0)
	TCG_masked = np.choose(mask, (0, TCG))
	TCG_np_masked = np.ma.masked_array(TCG_masked, TCG_masked == 0)
	TCW_masked = np.choose(mask, (0, TCW))
	TCW_np_masked = np.ma.masked_array(TCW_masked, TCW_masked == 0)	
	Thermal_masked = np.choose(mask, (0, bandTherm))
	Thermal_np_masked = np.ma.masked_array(Thermal_masked, Thermal_masked == 0)
	
	# Calculate statistics 
	print("Calculate statistics")
	# BAND 1
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_b1 = scipy.ndimage.measurements.mean(b1_np_masked, labels = polygons, index = index)
	mean_b1 = np.ndarray.tolist(mean_b1)
	statement = scene + "b1_values = " + scene + "b1_values + mean_b1"
	exec(statement)
	# BAND 2
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_b2 = scipy.ndimage.measurements.mean(b2_np_masked, labels = polygons, index = index)
	mean_b2 = np.ndarray.tolist(mean_b2)
	statement = scene + "b2_values = " + scene + "b2_values + mean_b2"
	exec(statement)
	# BAND 3
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_b3 = scipy.ndimage.measurements.mean(b3_np_masked, labels = polygons, index = index)
	mean_b3 = np.ndarray.tolist(mean_b3)
	statement = scene + "b3_values = " + scene + "b3_values + mean_b3"
	exec(statement)	
	# BAND 4
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_b4 = scipy.ndimage.measurements.mean(b4_np_masked, labels = polygons, index = index)
	mean_b4 = np.ndarray.tolist(mean_b4)
	statement = scene + "b4_values = " + scene + "b4_values + mean_b4"
	exec(statement)		
	# BAND 5
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_b5 = scipy.ndimage.measurements.mean(b5_np_masked, labels = polygons, index = index)
	mean_b5 = np.ndarray.tolist(mean_b5)
	statement = scene + "b5_values = " + scene + "b5_values + mean_b5"
	exec(statement)		
	# BAND 6
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_b6 = scipy.ndimage.measurements.mean(b6_np_masked, labels = polygons, index = index)
	mean_b6 = np.ndarray.tolist(mean_b6)
	statement = scene + "b6_values = " + scene + "b6_values + mean_b6"
	exec(statement)		
	# NDVI
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_NDVI = scipy.ndimage.measurements.mean(NDVI_np_masked, labels = polygons, index = index)
	mean_NDVI = np.ndarray.tolist(mean_NDVI)
	statement = scene + "NDVI_values = " + scene + "NDVI_values + mean_NDVI"
	exec(statement)
	# TCB
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_TCB = scipy.ndimage.measurements.mean(TCB_np_masked, labels = polygons, index = index)
	mean_TCB = np.ndarray.tolist(mean_TCB)
	statement = scene + "TCB_values = " + scene + "TCB_values + mean_TCB"
	exec(statement)		
	# TCG
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_TCG = scipy.ndimage.measurements.mean(TCG_np_masked, labels = polygons, index = index)
	mean_TCG = np.ndarray.tolist(mean_TCG)
	statement = scene + "TCG_values = " + scene + "TCG_values + mean_TCG"
	exec(statement)	
	# TCW
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_TCW = scipy.ndimage.measurements.mean(TCW_np_masked, labels = polygons, index = index)
	mean_TCW = np.ndarray.tolist(mean_TCW)
	statement = scene + "TCW_values = " + scene + "TCW_values + mean_TCW"
	exec(statement)	
	# THERMAL
	index = np.unique(polygons)
	index = np.delete(index, 0, axis=0)			# Remote first value ('0', which is background) from list
	mean_Thermal = scipy.ndimage.measurements.mean(Thermal_np_masked, labels = polygons, index = index)
	mean_Thermal = np.ndarray.tolist(mean_Thermal)
	statement = scene + "Thermal_values = " + scene + "Thermal_values + mean_Thermal"
	exec(statement)		

	# Set variables to zero 
	image_gdal = None
	polygon_gdal = None
	cloud_gdal = None
	thermal_gdal = None	
	
	# Create output Lists
	statement = "sceneLIST_list_b1.append(" + scene + "b1_values)"	# Other lists hidden for better view
	exec(statement)
	statement = "sceneLIST_list_b2.append(" + scene + "b2_values)"
	exec(statement)
	statement = "sceneLIST_list_b3.append(" + scene + "b3_values)"
	exec(statement)
	statement = "sceneLIST_list_b4.append(" + scene + "b4_values)"
	exec(statement)
	statement = "sceneLIST_list_b5.append(" + scene + "b5_values)"
	exec(statement)
	statement = "sceneLIST_list_b6.append(" + scene + "b6_values)"
	exec(statement)
	statement = "sceneLIST_list_NDVI.append(" + scene + "NDVI_values)"
	exec(statement)
	statement = "sceneLIST_list_TCB.append(" + scene + "TCB_values)"
	exec(statement)
	statement = "sceneLIST_list_TCG.append(" + scene + "TCG_values)"
	exec(statement)
	statement = "sceneLIST_list_TCW.append(" + scene + "TCW_values)"
	exec(statement)
	statement = "sceneLIST_list_THERMAL.append(" + scene + "Thermal_values)"
	exec(statement)
	
	print("Delete TMP-Files")
	deleteTMP = image + "_TMP-mask"
	os.remove(deleteTMP)
	deleteTMPhdr = image + "_TMP-mask.hdr"
	os.remove(deleteTMPhdr)
	print("")
	

# (2-C) ADD ID-LISTS TO LIST	--> Other lists hidden for better view
sceneLIST_list_b1.append(IDoutputList)
sceneLIST_list_b2.append(IDoutputList)
sceneLIST_list_b3.append(IDoutputList)
sceneLIST_list_b4.append(IDoutputList)
sceneLIST_list_b5.append(IDoutputList)
sceneLIST_list_b6.append(IDoutputList)
sceneLIST_list_NDVI.append(IDoutputList)
sceneLIST_list_TCB.append(IDoutputList)
sceneLIST_list_TCG.append(IDoutputList)
sceneLIST_list_TCW.append(IDoutputList)
sceneLIST_list_THERMAL.append(IDoutputList)


# (3) WRITE OUTPUT-TABLES
output_b1 = "E:/kirkdata/mbaumann/Species-separation_Chapter03/03_Band01.txt"
output_b2 = "E:/kirkdata/mbaumann/Species-separation_Chapter03/03_Band02.txt"
output_b3 = "E:/kirkdata/mbaumann/Species-separation_Chapter03/03_Band03.txt"
output_b4 = "E:/kirkdata/mbaumann/Species-separation_Chapter03/03_Band04.txt"
output_b5 = "E:/kirkdata/mbaumann/Species-separation_Chapter03/03_Band05.txt"
output_b6 = "E:/kirkdata/mbaumann/Species-separation_Chapter03/03_Band06.txt"
output_NDVI = "E:/kirkdata/mbaumann/Species-separation_Chapter03/03_NDVI.txt"
output_TCB = "E:/kirkdata/mbaumann/Species-separation_Chapter03/03_TCB.txt"
output_TCG = "E:/kirkdata/mbaumann/Species-separation_Chapter03/03_TCG.txt"
output_TCW = "E:/kirkdata/mbaumann/Species-separation_Chapter03/03_TCW.txt"
output_THERMAL = "E:/kirkdata/mbaumann/Species-separation_Chapter03/03_THERMAL.txt"

# (3-A) WRITE INTO OUTPUT-TABLES
writeb1 = csv.writer(open(output_b1, "w"))
for row in itertools.zip_longest(*sceneLIST_list_b1):
	writeb1.writerow(row)
writeb2 = csv.writer(open(output_b2, "w"))
for row in itertools.zip_longest(*sceneLIST_list_b2):
	writeb2.writerow(row)
writeb3 = csv.writer(open(output_b3, "w"))
for row in itertools.zip_longest(*sceneLIST_list_b3):
	writeb3.writerow(row)
writeb4 = csv.writer(open(output_b4, "w"))
for row in itertools.zip_longest(*sceneLIST_list_b4):
	writeb4.writerow(row)
writeb5 = csv.writer(open(output_b5, "w"))
for row in itertools.zip_longest(*sceneLIST_list_b5):
	writeb5.writerow(row)
writeb6 = csv.writer(open(output_b6, "w"))
for row in itertools.zip_longest(*sceneLIST_list_b6):
	writeb6.writerow(row)
writeNDVI = csv.writer(open(output_NDVI, "w"))
for row in itertools.zip_longest(*sceneLIST_list_NDVI):
	writeNDVI.writerow(row)
writeTCB = csv.writer(open(output_TCB, "w"))
for row in itertools.zip_longest(*sceneLIST_list_TCB):
	writeTCB.writerow(row)
writeTCG = csv.writer(open(output_TCG, "w"))
for row in itertools.zip_longest(*sceneLIST_list_TCG):
	writeTCG.writerow(row)
writeTCW = csv.writer(open(output_TCW, "w"))
for row in itertools.zip_longest(*sceneLIST_list_TCW):
	writeTCW.writerow(row)
writeTHERMAL = csv.writer(open(output_THERMAL, "w"))
for row in itertools.zip_longest(*sceneLIST_list_THERMAL):
	writeTHERMAL.writerow(row)


print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")