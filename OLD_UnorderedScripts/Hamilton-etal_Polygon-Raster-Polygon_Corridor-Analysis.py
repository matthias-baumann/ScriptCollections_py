# ######################################## LOAD REQUIRED MODULES ############################################## #
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
import struct
import scipy
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:", starttime)
print("")
# ####################################### HARD-CODE FOLDER PATHS ############################################## #
vector_input = "X:/Corridor_analysis/aqua_terra_07/5/"
raster_output = "X:/Corridor_analysis/aqua_terra_08/5/"
NLCD_reclass = "X:/Corridor_analysis/NLCD_HabitatReclass.tif"

# ####################################### PROCESS ############################################################ #
def ConvertPolygonToRasterCommand(polygonFile):
	input = polygonFile
	out_TMP = input
	out_TMP = out_TMP.replace(".shp", ".tif")
	command = "gdal_rasterize -a CORRIDOR -tr 30 30 -ot Int16 -q -of GTiff " + input + " " + out_TMP
	return command, out_TMP

def GetExtentFromRaster(rasterFile):
	ds = gdal.Open(rasterFile)
	gt = ds.GetGeoTransform()
	cols = ds.RasterXSize
	rows = ds.RasterYSize
	ext = []
	xarr = [0,cols]
	yarr = [0,rows]
	for px in xarr:
		for py in yarr:
			x = gt[0] + (px*gt[1])+(py*gt[2])
			y = gt[3] + (px*gt[4])+(py*gt[5])
			ext.append([x,y])
		yarr.reverse()
	return ext

	
input_list = [input for input in os.listdir(vector_input) if input.endswith('.shp')]
for input in input_list:
	print(input)
	# Converting Polygon to raster
	polPath = vector_input + input
	command_convert = ConvertPolygonToRasterCommand(polPath)[0]
	polygonASraster	= ConvertPolygonToRasterCommand(polPath)[1]
	os.system(command_convert)
	# Derive corner coordinates from raster-file
	corners = GetExtentFromRaster(polygonASraster)
	NLCD_clip = raster_output + input
	NLCD_clip = NLCD_clip.replace("_aquapath.shp", "_NLCDhabitatCorridor.tif")
	command_clip = "gdal_translate -q -ot Byte -of GTiff -projwin " + str((corners[0][0])) + " " + str((corners[0][1])) + " " + str((corners[2][0])) + " " + str((corners[2][1])) + " " + NLCD_reclass + " " + NLCD_clip
	os.system(command_clip)
	# Get the area of interest
		# Load input
	gdal.AllRegister()
	buffer_gdal = gdal.Open(polygonASraster, GA_ReadOnly)
	NLCD_gdal = gdal.Open(NLCD_clip, GA_ReadOnly)
	cols = buffer_gdal.RasterXSize
	rows = buffer_gdal.RasterYSize
		# Build output
	output = NLCD_clip
	output = output.replace(".tif", "_HelmersCanSuckMyGDAL.tif")
	#outDrv = NLCD_gdal.GetDriver()
	outDrv = gdal.GetDriverByName('GTiff')
	out = outDrv.Create(output, cols, rows, 1, GDT_Byte)
	out.SetProjection(buffer_gdal.GetProjection())
	out.SetGeoTransform(buffer_gdal.GetGeoTransform())
		# Get the bands for inptut and output
	buff = buffer_gdal.GetRasterBand(1)
	nlcd = NLCD_gdal.GetRasterBand(1)
	outband = out.GetRasterBand(1)
		# Do the calculation
	for y in range(rows):
		b = buff.ReadAsArray(0, y, cols, 1)
		n = nlcd.ReadAsArray(0, y, cols, 1)
		sum = b + n
		mask = np.equal(sum, 2)
		calc = np.choose(mask, (0,1))
		outband.WriteArray(calc, 0, y)
		# Calculate statistics and set projection
	outband.FlushCache()
	stats = outband.GetStatistics(0,1)
	out = None
	buffer_gdal = None
	NLCD_gdal = None
	# Convert Raster to Polygon
	polygonOutput = output
	polygonOutput = polygonOutput.replace(".tif", "shp.shp")
	command = "gdal_polygonize.py -8 -q -b 1 " + output + ' -f "ESRI Shapefile" ' + polygonOutput
	os.system(command)
	# Remove last zeros from shapefile
	final_shape = polygonOutput
	final_shape = final_shape.replace("shp.shp",".shp")
	command = "ogr2ogr " + final_shape + " " + polygonOutput + ' -where "DN = 1"'
	os.system(command)
	# Remove temporary files
	os.remove(polygonASraster)
	os.remove(NLCD_clip)
	os.remove(output)
	removeshp_list = os.listdir(raster_output)
	for file in removeshp_list:
		if file.find("shp.") >= 0:
			rem = raster_output + file
			os.remove(rem)
	exit(0)








# ####################################### END TIME-COUNT AND PRINT TIME STATS ################################# #		
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")