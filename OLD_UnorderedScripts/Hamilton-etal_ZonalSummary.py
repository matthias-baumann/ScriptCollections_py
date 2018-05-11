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
# ####################################### BUILD GLOBAL FUNCTIONS ############################################## #

def GetPolygonID(polygonFile, idField):
	IDs = []
	IDs.append("Polygon-ID")
	polygons = ogr.Open(polygonFile)
	lyr = polygons.GetLayer()
	feature = lyr.GetNextFeature()
	while feature:
		id = feature.GetField(idField)
		IDs.append(id)
		feature = lyr.GetNextFeature()
	lyr.ResetReading()
	return IDs

def ZonalHistogram(polygonFile, idField, rasterFile, state):
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
	def GetMMU(rasterFile):
		ds = gdal.Open(rasterFile)
		gt = ds.GetGeoTransform()
		MMU = gt[1]	
		return MMU
	def ConvertPolygonToRasterCommand(polygonFile, rasterFile, idField):
		input = polygonFile
		outTMP = rasterFile
		outTMP = outTMP.replace(".bsq","_polygonIDs.tif").replace(".tif","_polygonIDs.tif").replace(".img","_polygonIDs.tif")		# Expand here upon usage of different file-types
		sumField = idField
		command = "gdal_rasterize -a " + sumField + " -tr " + str(MMU) + " " + str(MMU) + " -ot UInt16 -q -of GTiff -te " + str((corners[1][0])) + " " + str((corners[1][1])) + " " + str((corners[2][0])) + " " + str((corners[0][1])) + " " + input + " " + outTMP
		
		return command, outTMP
	def ZonalStats(polygonASraster, rasterFile,state):
		polygons_gdal = gdal.Open(polygonASraster, GA_ReadOnly)
		values_gdal = gdal.Open(rasterFile, GA_ReadOnly)
		cols = polygons_gdal.RasterXSize
		rows = polygons_gdal.RasterYSize
		polygons = polygons_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
		rastervalues = values_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
		np.seterr(all='ignore')
		raster_unique = [0,11,12,21,22,23,24,31,41,42,43,52,71,81,82,90,95]
		index = np.unique(polygons)
		for id in index:
			if id > 0:
				rowvals = []
				rowvals.append(id)
				rowvals.append(state)
				id_mask = np.equal(polygons, id)
				raster_masked = np.choose(id_mask, (-999, rastervalues))
				np_masked = np.ma.masked_array(raster_masked, raster_masked == -999)
				for rasU in raster_unique:
					rasU_sum = (np_masked == rasU).sum()
					rowvals.append(rasU_sum)
		return rowvals
		
	corners = GetExtentFromRaster(rasterFile)
	MMU = GetMMU(rasterFile)
	command_convert = ConvertPolygonToRasterCommand(polygonFile, rasterFile, idField)[0]
	polygonASraster = ConvertPolygonToRasterCommand(polygonFile, rasterFile, idField)[1]
	os.system(command_convert)
	summary_var = ZonalStats(polygonASraster, rasterFile, state)
	os.remove(polygonASraster)
	return summary_var	
	
def WriteOutput(outlist, outfile):
	print("Write Output-File")
	with open(outfile, "w") as the_file:
		csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
		writer = csv.writer(the_file, dialect="custom")
		for element in outlist:
			writer.writerow(element)

# ####################################### RUN THE MODULES AND CALL THE FUNCTIONS ############################## #
# (0) ZONAL SHP-FILE AND SUMMARY-FIELD
polygonFile = "E:/kirkdata/mbaumann/75km_dissolved_project.shp"
idField = "Id"
print("Vector-file: " + polygonFile)
print("---------------------------")

# (2) ZONAL STATISTICS OF CATEGORIES --> CATEGORICAL SUMMARY BY ZONE
values = []
rasIDs_unique = ["Polygon_ID" ,"State/RasterClass", 0,11,12,21,22,23,24,31,41,42,43,52,71,81,82,90,95]
values.append(rasIDs_unique)
#
rasterFolder = "Z:/helmers/GIS_Data/NLCD/2006/states/"
rasterList = os.listdir(rasterFolder)
for ras in rasterList[:]:
	if ras.endswith(".img"):
		rasterFile = rasterFolder + ras
		print(rasterFile)
		p = ras.find("_")
		state = ras[0:p]
		summary02 = ZonalHistogram(polygonFile, idField, rasterFile, state)
		values.append(summary02)

# ####################################### WRITE THE OUTPUT FILE ############################################### #
outfile = "E:/kirkdata/mbaumann/Chris_MonsterDick.csv"
WriteOutput(values, outfile)
		
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #		
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")