# SCRIPT FRO CREATING CHANGE-MAPS OUT OF CORRECTED CLASSIFICATIONS
#---------------------------------------------------------------------------------------------------------------#
#-----IMPORT SYSTEM MODULES																						#
from __future__ import division																					#
from math import sqrt																							#
import sys, string, os, arcgisscripting																			#
import time																										#
import datetime																									#
import shutil																									#
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
#-----COMMAND LINE ARGUMENTS
if len(sys.argv) < 2:
	print "Forest-cover change post-processing.py" # just type the folder name you want to process
	exit(0)
pr = sys.argv[1]

#-----DEFINE WORKING AND OUTPUT DIRECTORY
workDir = "E:\\DataF\\mbaumann\\Data processing\\03_Forest-classifications\\" + pr + "\\"

#-----CREATE OUTPUT-FOLDER, OUTPUT-FILENAMES, AND FILEPATHS TO VARIABLE-NAMES
fileList = os.listdir(workDir)
outputDir = workDir + "Post-class_Maps\\"
#os.makedirs(outputDir, 0777)
classifications = []
Corr_classifications = []
for file in fileList:
	if file.find("tif") >= 0 or file.find(".img") >= 0:
		classifications.append(file)
for file in classifications:
	if file.find(".vat") >= 0:
		classifications.remove(file)
for file in classifications:
	if file.find(".xml") >= 0:
		classifications.remove(file)
for file in classifications:
	if file.find(".rrd") >= 0:
		classifications.remove(file)
for file in classifications:
	if file.find("classified") >= 0:
		classifications.remove(file)

# Create Full path names for the classification files
class1985 = workDir + classifications[0]
class1990 = workDir + classifications[1]
class1995 = workDir + classifications[2]
class2000 = workDir + classifications[3]
class2005 = workDir + classifications[4]
class2010 = workDir + classifications[5]

# Generate new file names for the change maps
change_8590 = outputDir + "change-map_1985-1990.tif"
change_9095 = outputDir + "change-map_1990-1995.tif"
change_9500 = outputDir + "change-map_1995-2000.tif"
change_0005 = outputDir + "change-map_2000-2005.tif"
change_0510 = outputDir + "change-map_2005-2010.tif"

#-----OPEN ALL FILES IN GDAL AND GENERATE OUTPUT-PROPERTIES
class1985open = gdal.Open(class1985, GA_ReadOnly)
class1990open = gdal.Open(class1990, GA_ReadOnly)
class1995open = gdal.Open(class1995, GA_ReadOnly)
class2000open = gdal.Open(class2000, GA_ReadOnly)
class2005open = gdal.Open(class2005, GA_ReadOnly)
class2010open = gdal.Open(class2010, GA_ReadOnly)
cols = class1985open.RasterXSize
rows = class1985open.RasterYSize
outDrv = gdal.GetDriverByName('GTiff')
options = []

#-----START CREATING CHANGE-MAPS
#-----Create Change map for period 1985-1990
print "Generating change-map for Period 1985-1990"
change = outDrv.Create(change_8590, cols, rows, 1, GDT_Byte, options)
change.SetProjection(class1985open.GetProjection())
change.SetGeoTransform(class1985open.GetGeoTransform())
for y in range(rows):
	b1 = np.ravel(class1985open.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	b2 = np.ravel(class1990open.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	dataOut = np.zeros(cols)
	constFor = np.zeros(cols)
	constNonFor = np.zeros(cols)
	disturb = np.zeros(cols)
	refor = np.zeros(cols)
	diff = 2 * b2 + b1						# Codes are: Forest=1, Non-Forest=2, Other=0
	np.putmask(constFor, diff == 3, 1)
	np.putmask(constNonFor, diff == 6, 2)
	np.putmask(disturb, diff == 5, 3)
	np.putmask(refor, diff == 4, 4)
	dataOut = constFor + constNonFor + disturb + refor
	dataOut.shape = (1, -1)
	change.GetRasterBand(1).WriteArray(np.array(dataOut), 0, y)
print "DONE"

#-----Create Change map for period 1990-1995
print "Generating change-map for Period 1990-1995"
change = outDrv.Create(change_9095, cols, rows, 1, GDT_Byte, options)
change.SetProjection(class1990open.GetProjection())
change.SetGeoTransform(class1990open.GetGeoTransform())
for y in range(rows):
	b1 = np.ravel(class1990open.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	b2 = np.ravel(class1995open.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	dataOut = np.zeros(cols)
	constFor = np.zeros(cols)
	constNonFor = np.zeros(cols)
	disturb = np.zeros(cols)
	refor = np.zeros(cols)
	diff = 2 * b2 + b1						# Codes are: Forest=1, Non-Forest=2, Other=0
	np.putmask(constFor, diff == 3, 1)
	np.putmask(constNonFor, diff == 6, 2)
	np.putmask(disturb, diff == 5, 3)
	np.putmask(refor, diff == 4, 4)
	dataOut = constFor + constNonFor + disturb + refor
	dataOut.shape = (1, -1)
	change.GetRasterBand(1).WriteArray(np.array(dataOut), 0, y)
print "DONE"

#-----Create Change map for period 1995-2000
print "Generating change-map for Period 1995-2000"
change = outDrv.Create(change_9500, cols, rows, 1, GDT_Byte, options)
change.SetProjection(class1995open.GetProjection())
change.SetGeoTransform(class1995open.GetGeoTransform())
for y in range(rows):
	b1 = np.ravel(class1995open.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	b2 = np.ravel(class2000open.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	dataOut = np.zeros(cols)
	constFor = np.zeros(cols)
	constNonFor = np.zeros(cols)
	disturb = np.zeros(cols)
	refor = np.zeros(cols)
	diff = 2 * b2 + b1						# Codes are: Forest=1, Non-Forest=2, Other=0
	np.putmask(constFor, diff == 3, 1)
	np.putmask(constNonFor, diff == 6, 2)
	np.putmask(disturb, diff == 5, 3)
	np.putmask(refor, diff == 4, 4)
	dataOut = constFor + constNonFor + disturb + refor
	dataOut.shape = (1, -1)
	change.GetRasterBand(1).WriteArray(np.array(dataOut), 0, y)
print "DONE"

#-----Create Change map for period 2000-2005
print "Generating change-map for Period 2000-2005"
change = outDrv.Create(change_0005, cols, rows, 1, GDT_Byte, options)
change.SetProjection(class2000open.GetProjection())
change.SetGeoTransform(class2000open.GetGeoTransform())
for y in range(rows):
	b1 = np.ravel(class2000open.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	b2 = np.ravel(class2005open.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	dataOut = np.zeros(cols)
	constFor = np.zeros(cols)
	constNonFor = np.zeros(cols)
	disturb = np.zeros(cols)
	refor = np.zeros(cols)
	diff = 2 * b2 + b1						# Codes are: Forest=1, Non-Forest=2, Other=0
	np.putmask(constFor, diff == 3, 1)
	np.putmask(constNonFor, diff == 6, 2)
	np.putmask(disturb, diff == 5, 3)
	np.putmask(refor, diff == 4, 4)
	dataOut = constFor + constNonFor + disturb + refor
	dataOut.shape = (1, -1)
	change.GetRasterBand(1).WriteArray(np.array(dataOut), 0, y)
print "DONE"

#-----Create Change map for period 2005-2010
print "Generating change-map for Period 2005-2010"
change = outDrv.Create(change_0510, cols, rows, 1, GDT_Byte, options)
change.SetProjection(class2005open.GetProjection())
change.SetGeoTransform(class2005open.GetGeoTransform())
for y in range(rows):
	b1 = np.ravel(class2005open.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	b2 = np.ravel(class2010open.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	dataOut = np.zeros(cols)
	constFor = np.zeros(cols)
	constNonFor = np.zeros(cols)
	disturb = np.zeros(cols)
	refor = np.zeros(cols)
	diff = 2 * b2 + b1						# Codes are: Forest=1, Non-Forest=2, Other=0
	np.putmask(constFor, diff == 3, 1)
	np.putmask(constNonFor, diff == 6, 2)
	np.putmask(disturb, diff == 5, 3)
	np.putmask(refor, diff == 4, 4)
	dataOut = constFor + constNonFor + disturb + refor
	dataOut.shape = (1, -1)
	change.GetRasterBand(1).WriteArray(np.array(dataOut), 0, y)
print "DONE"
print "All maps created"

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime