# IMPORT SYSTEM MODULES-----------------------------------------------------------------------------------------#
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
# CREATE THE GEOPROCESSOR OBJECT
print("CREATING GEOPROCESSOR OBJECT")
gp = arcgisscripting.create(9.3)
print("CHECKING OUT SPATIAL ANALYST EXTENSION")
gp.CheckOutExtension("Spatial")
print("")

# ASSIGN INPUT-File --> edit manually for each run
inputFile = "F:\\DataF\\mbaumann\\Kelly-dataset_Creation\\2005_Forest.img"
inputDir = "F:\\DataF\\mbaumann\\Kelly-dataset_Creation\\"
print("Generate Distance to forest edge for file:", inputFile)
print("")

# (1) Start the operation
# (1-A) Convert raster into polygon shape file and calculate straight-line distance
print("Converting Raster into Polygon-shp-File")
input = inputFile
output = input
output = output.replace(".img","_polygon.shp")
# gp.RasterToPolygon_conversion(input, output, "NO_SIMPLIFY")

# (1-B) Select the forest-area parts of the polygon
print("Selecting forest polygons in layer")
input = output
output = input
output = output.replace("_polygon.shp","_forest_polygon.shp")
# gp.Select_analysis(input, output, '"GRIDCODE" = 1')

# (1-C) Convert Polygon to Line
print("Converting Polygon into Line-Feature")
input = output
output = input
output = output.replace(".shp", "_line.shp")
gp.PolygonToLine_management(input, output)

# (1-D) Calculate distances
print("Calculating Straight-Line distance")
input = output
output = input
output = output.replace(".shp", "_distance.img")
maskExtend = '"' + inputFile + '"'
gp.Extent = maskExtend 
gp.EucDistance(input, output, "", "30")
print("")
# (1-E) Subset the distance raster
print("Subsetting distance raster")
finalFile = inputFile
finalFile = finalFile.replace("Forest.img","distance-to-forest-edge.img")
output_GDAL = gdal.Open(output, GA_ReadOnly)
inputFile_GDAL = gdal.Open(inputFile, GA_ReadOnly)
cols = output_GDAL.RasterXSize
rows = output_GDAL.RasterYSize
outDrv = gdal.GetDriverByName('HFA')
options =[]
final = outDrv.Create(finalFile, cols, rows, 1, GDT_Float32, options)
final.SetProjection(output_GDAL.GetProjection())
final.SetGeoTransform(output_GDAL.GetGeoTransform())
for y in range(rows):
	distances = np.ravel(output_GDAL.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	forests = np.ravel(inputFile_GDAL.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	dataOut = np.zeros(cols)
	np.putmask(dataOut, forests == 1, distances)
	dataOut.shape = (1, -1)
	final.GetRasterBand(1).WriteArray(np.array(dataOut), 0, y)
output_GDAL = None
inputFile_GDAL = None

# (1-F) Generate list of files that we don't need anymore --> then delete them
print("Deleting temporary files")
# Create list
fileList = os.listdir(inputDir)
deleteList = []
for file in fileList[:]:
	if file.find("distance.tif") >= 0:
		deleteList.append(file)
for file in fileList[:]:
	if file.find("forest_polygon") >= 0:
		deleteList.append(file)
for file in fileList[:]:
	if file.find("_line") >= 0:
		deleteList.append(file)		
# Delete files in that list				
for file in deleteList[:]:
	delete = inputDir + file
	if os.path.exists(delete):
		os.remove(delete)


endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime
