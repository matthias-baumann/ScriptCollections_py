# IMPORT SYSTEM MODULES-----------------------------------------------------------------------------------------#
from __future__ import division																					#
from math import sqrt																							#
import sys, string, os, arcgisscripting																			#
import time																										#
import datetime																									#
import shutil																									#
from stat import *																								#
import math																										#
import numpy as np																								#
#np.arrayarange = np.arange																						#
from numpy.linalg import *																						#
from osgeo import gdal																							#
from osgeo.gdalconst import *																					#
gdal.TermProgress = gdal.TermProgress_nocb																		#
from osgeo import osr																							#
gdal.TermProgress = gdal.TermProgress_nocb																		#
from osgeo import gdal_array as gdalnumeric																		#
import pdb								# to stop the script where ever you want and type the commands you want	#
										# code for stopping the script is: pdb.set_trace()						#
#---------------------------------------------------------------------------------------------------------------#

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# CREATE THE GEOPROCESSOR OBJECT and allow OVERWRITE
print "CREATING GEOPROCESSOR OBJECT"
gp = arcgisscripting.create(9.3)
print "CHECKING OUT SPATIAL ANALYST EXTENSION"
gp.CheckOutExtension("Spatial")
gp.overwriteoutput = 1
print "--------------------------------------------------------"
print "--------------------------------------------------------"
print " "

# ASSIGN INPUTS AND OUTPUT VARIABLES
workDir = "F:\\DataF\\mbaumann\\Data Processing\\03_Forest-classifications\\Forest-cover_maps\\"
parkFile = "F:\\DataF\\mbaumann\\Data Processing\\06_Kelly_Sampling-design-chapter03\\Parks_Landsat_selection_NameDissolve.shp"
outputDir = "F:\\DataF\\mbaumann\\Data Processing\\06_Kelly_Sampling-design-chapter03\\"


# CREATE THE POLYGONS FROM THE RASTERS
rasterList = []
fileList = os.listdir(workDir)
for file in fileList:
	if file.find("1985") >= 0 and file.find(".tif") >= 0:
		rasterList.append(file)
for file in rasterList[:]:
	if file.find(".rrd") >= 0 or file.find(".vat.dbf") >= 0 or file.find(".xml") >= 0 or file.find("166022") >= 0 or file.find("167020") >= 0 or file.find("181022") >= 0 or file.find("183019") >= 0:
		rasterList.remove(file)

# CONVERT RASTER BY RASTER AND DELETE POLYGONS AND DELETE POLYGONS OF VALUE '2' ('NON-FOREST') AND '0' ('UNCLASSIFIED')
for file in rasterList:
	print "Processing raster:", file
	print "--------------------------------------------------------"
	input = workDir + file
	outputRAW = input
	outputRAW = outputRAW.replace("_ClumpEliminate-sub.tif", "_forestPolygon_raw.shp")
	outputSELECT = outputRAW
	outputSELECT = outputSELECT.replace("raw.shp", "select.shp")
	outputDISSOLVE = outputRAW
	outputDISSOLVE = outputDISSOLVE.replace("_raw.shp", ".shp")
	print "Converting to polygon"
	if not os.path.exists(outputRAW):
		gp.RasterToPolygon_conversion(input, outputRAW, "NO_SIMPLIFY", "")
	else:
		print file, " is already converted, continuing..."
	print "Deleting unneeded values"
	if not os.path.exists(outputSELECT):
		gp.Select_analysis(outputRAW, outputSELECT, ' "GRIDCODE" = 1 ')
	else:
		print outputSELECT, "already exists, continuing..."
	print "Dissolving"
	if not os.path.exists(outputDISSOLVE):
		gp.Dissolve_management(outputSELECT, outputDISSOLVE)
	else:
		print outputDISSOLVE, "already exists, continuing..."
	print " "
	print "Clipping with Park-SHP-File to create area inside"
	polygonFileInput = outputDISSOLVE
	polygonFileOutput = outputDir + file
	polygonFileClip = polygonFileOutput.replace("ClumpEliminate-sub.tif","ForestInside.shp")
	polygonFileErase = polygonFileOutput.replace("ClumpEliminate-sub.tif","ForestOutside.shp")
	if not os.path.exists(polygonFileClip):
		gp.Clip_analysis(polygonFileInput, parkFile, polygonFileClip)
	else:
		print polygonFileClip, " already exists, continuing..." 
	print "Erasing with Park-SHP-File to create area outside"
	if not os.path.exists(polygonFileErase):
		gp.Erase_analysis(polygonFileInput, parkFile, polygonFileErase)
	else:
		print polygonFileErase, " already exists, continuing..."
	print " "
	print "Deleting temporary files"
	deleteList = os.listdir(workDir)
	for temp in deleteList:
		if temp.find("forestPolygon") >= 0 or temp.find("forestpolygon") >= 0:
			delete = workDir + temp
			os.remove(delete)
	print "--------------------------------------------------------"
	print " "

print "DONE"
print "--------------------------------------------------------"
print "--------------------------------------------------------"
print " "
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime
