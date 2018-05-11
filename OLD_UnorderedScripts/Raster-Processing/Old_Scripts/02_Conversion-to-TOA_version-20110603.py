 #IMPORT SYSTEM MODULES
from __future__ import division
from math import sqrt
import sys, string
import os
import arcgisscripting
import time
import datetime
import shutil
import math
import numpy as np
import tarfile																				# To extract tar.gz-files
#np.arrayarange = np.arange
from numpy.linalg import *
from osgeo import gdal																		# That's all GDAL crap
from osgeo.gdalconst import *
gdal.TermProgress = gdal.TermProgress_nocb
from osgeo import osr
gdal.TermProgress = gdal.TermProgress_nocb
from osgeo import gdal_array as gdalnumeric
import pdb																					# to stop the script where ever you want and type the commands you want
																							# code for stopping the script is: pdb.set_trace()


starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

#-----COMMAND LINE ARGUMENTS-----
RAW_Folder = sys.argv[1]
pathrow = sys.argv[2]
listFile = sys.argv[3]
outDir = sys.argv[4] + pathrow + "\\"

# Start creating folder structure
print "-------------"
print "RAW-Data-Folder: " + RAW_Folder
print "Processing footprint: " + pathrow
print "File with scenes to be processed: " + listFile
print "Output-Directory: " + outDir
print "-------------"
print "START RUNNING SCRIPT TO CONVERT DN-VALUES INTO TOP OF ATMOSPHERE"
workDir = RAW_Folder

# CREATE FOLDER STRUCTURE
outpath = outDir
if not os.path.lexists(outpath):
	os.makedirs(outpath,0777)

# Get files for input
inputList = []
info = open(listFile, "r")
for line in info:
	file = line
	file = str(file)
	file = file.replace("\n","")
	inputList.append(file)

# Get full names of files to be processed
processList = []
RAW_List = os.listdir(workDir)
for file in inputList:
	for tar in RAW_List:
		if tar.find(file) >= 0:
			a = workDir + tar
			processList.append(a)

# Generate active area for Landsat-scene
tempMaskCount = 0
for archive in processList:
	print "Processing file: " + archive
	tempMaskCount = tempMaskCount + 1
	tempMaskCount_str = str(tempMaskCount)
	tar = tarfile.open(archive, "r:gz")
	list = tar.getnames()
	list2 = tar.getnames()						# Get the initial list for deleting the files later
	for file in tar:
		tar.extract(file, workDir)
	tar.close()
	file = None
	
	# Create subsets based on coordinates
	ul_x_aa = 0
	ul_y_aa = 0
	lr_x_aa = 0
	lr_y_aa = 0
	cfl = os.listdir(outpath)
	for file in cfl[:]:
		if file.find("coordinates.txt") >= 0:
			coord_info = outpath + file
			txt = open(coord_info, "r")
			for line in txt:
				if line.find("ul_x") >= 0:
					p1 = line.find(":")
					p2 = len(line)
					ul_x_aa = line[p1+1:p2]
				if line.find("ul_y") >= 0:
					p1 = line.find(":")
					p2 = len(line)
					ul_y_aa = line[p1+1:p2]
				if line.find("lr_x") >= 0:
					p1 = line.find(":")
					p2 = len(line)
					lr_x_aa = line[p1+1:p2]
				if line.find("lr_y") >= 0:
					p1 = line.find(":")
					p2 = len(line)
					lr_y_aa = line[p1+1:p2]
			txt.close()
	for file in list[:]:
		if file.find(".GTF") >= 0 or file.find("B6") >= 0 or file.find("B8") >= 0:
			list.remove(file)
	#-----GET INFORMATION FROM MTL-FILE-----
	for file in list:
		if file.find("MTL") >= 0:
			mtlFile = workDir + file
			fin = open(mtlFile, "r")
			for line in fin:
				p2 = len(line)
				p1 = line.find('"')
				if line.find("PRODUCT_TYPE") >= 0:
					prodtype = line[p1+1:p2-2]						# Get Landsat Description
				if line.find("SPACECRAFT_ID") >= 0: 
					landsattype = line[p1+1:p2-2]					# Get Landsat Number
					landsatnum = landsattype[len(landsattype)-1]
				if line.find("WRS_PATH") >= 0: 
					path = line[p2-4:p2-1]							# Get Path
				if line.find("STARTING_ROW") >= 0: 
					p1 = line.rfind(" ")							# Get Row
					row = line[p1+1:p2-1]
					if len(row) == 2: row = "0" + row
				if line.find("ACQUISITION_DATE") >= 0:
					p1 = line.rfind(" ")							# Get Acquisition Date
					date = line[p1+1:p2-1]
					date = date.replace("-","")
					dateDOY = date									# Get the day of year from the date
					dateDOY = time.strptime(dateDOY,"%Y %m %d")
					dateDOY = dateDOY[7]
					dateDOY = str(dateDOY)
					dateDOY = dateDOY + " "							#Add a space to make no mistake while searching through the SED-File later
				if line.find("SUN_ELEVATION") >=0:
					p1 = line.rfind(" ")							# Get Sun Elevation
					SunElev = line[p1+1:p2-1]
			fin.close()
	#-----GET NORMALIZATION PARAMETERS AND SUN-EARTH-DISTANCE FROM EXTERNAL TXT-FILES-----
	infoFile = RAW_Folder + "00_Radiometric-calibration_Landsat.txt"
	parameters = open(infoFile, "r")
	for parameterLine in parameters:
		pos2 = len(parameterLine)
		pos1 = parameterLine.find("=")
		if landsatnum == "5":									# Test for Landsat 5
			if parameterLine.find("GRescaleL5b1") >= 0:			# Get G-Rescale values
				Gb1 = parameterLine[pos1+2:pos2]
				Gb1 = float(Gb1)
			if parameterLine.find("GRescaleL5b2") >= 0:
				Gb2 = parameterLine[pos1+2:pos2]
				Gb2 = float(Gb2)
			if parameterLine.find("GRescaleL5b3") >= 0:
				Gb3 = parameterLine[pos1+2:pos2]
				Gb3 = float(Gb3)
			if parameterLine.find("GRescaleL5b4") >= 0:
				Gb4 = parameterLine[pos1+2:pos2]
				Gb4 = float(Gb4)
			if parameterLine.find("GRescaleL5b5") >= 0:
				Gb5 = parameterLine[pos1+2:pos2]
				Gb5 = float(Gb5)
			if parameterLine.find("GRescaleL5b7") >= 0:
				Gb7 = parameterLine[pos1+2:pos2]
				Gb7 = float(Gb7)
			if parameterLine.find("BRescaleL5b1") >= 0:			# Get B-Rescale values
				Bb1 = parameterLine[pos1+2:pos2]
				Bb1 = float(Bb1)
			if parameterLine.find("BRescaleL5b2") >= 0:
				Bb2 = parameterLine[pos1+2:pos2]
				Bb2 = float(Bb2)
			if parameterLine.find("BRescaleL5b3") >= 0:
				Bb3 = parameterLine[pos1+2:pos2]
				Bb3 = float(Bb3)
			if parameterLine.find("BRescaleL5b4") >= 0:
				Bb4 = parameterLine[pos1+2:pos2]
				Bb4 = float(Bb4)
			if parameterLine.find("BRescaleL5b5") >= 0:
				Bb5 = parameterLine[pos1+2:pos2]
				Bb5 = float(Bb5)
			if parameterLine.find("BRescaleL5b7") >= 0:
				Bb7 = parameterLine[pos1+2:pos2]
				Bb7 = float(Bb7)
			if parameterLine.find("ESUNL5b1") >= 0:				# Get ESUN values
				Eb1 = parameterLine[pos1+2:pos2]
				Eb1 = float(Eb1)
			if parameterLine.find("ESUNL5b2") >= 0:
				Eb2 = parameterLine[pos1+2:pos2]
				Eb2 = float(Eb2)
			if parameterLine.find("ESUNL5b3") >= 0:
				Eb3 = parameterLine[pos1+2:pos2]
				Eb3 = float(Eb3)
			if parameterLine.find("ESUNL5b4") >= 0:
				Eb4 = parameterLine[pos1+2:pos2]
				Eb4 = float(Eb4)
			if parameterLine.find("ESUNL5b5") >= 0:
				Eb5 = parameterLine[pos1+2:pos2]
				Eb5 = float(Eb5)
			if parameterLine.find("ESUNL5b7") >= 0:
				Eb7 = parameterLine[pos1+2:pos2]
				Eb7 = float(Eb7)
		if landsatnum == "7":									# Test for Landsat 7
			if parameterLine.find("GRescaleL7b1") >= 0:			# Get G-Rescale values
				Gb1 = parameterLine[pos1+2:pos2]
				Gb1 = float(Gb1)
			if parameterLine.find("GRescaleL7b2") >= 0:
				Gb2 = parameterLine[pos1+2:pos2]
				Gb2 = float(Gb2)
			if parameterLine.find("GRescaleL7b3") >= 0:
				Gb3 = parameterLine[pos1+2:pos2]
				Gb3 = float(Gb3)
			if parameterLine.find("GRescaleL7b4") >= 0:
				Gb4 = parameterLine[pos1+2:pos2]
				Gb4 = float(Gb4)
			if parameterLine.find("GRescaleL7b5") >= 0:
				Gb5 = parameterLine[pos1+2:pos2]
				Gb5 = float(Gb5)
			if parameterLine.find("GRescaleL7b7") >= 0:
				Gb7 = parameterLine[pos1+2:pos2]
				Gb7 = float(Gb7)
			if parameterLine.find("BRescaleL7b1") >= 0:			# Get B-Rescale values
				Bb1 = parameterLine[pos1+2:pos2]
				Bb1 = float(Bb1)
			if parameterLine.find("BRescaleL7b2") >= 0:
				Bb2 = parameterLine[pos1+2:pos2]
				Bb2 = float(Bb2)
			if parameterLine.find("BRescaleL7b3") >= 0:
				Bb3 = parameterLine[pos1+2:pos2]
				Bb3 = float(Bb3)
			if parameterLine.find("BRescaleL7b4") >= 0:
				Bb4 = parameterLine[pos1+2:pos2]
				Bb4 = float(Bb4)
			if parameterLine.find("BRescaleL7b5") >= 0:
				Bb5 = parameterLine[pos1+2:pos2]
				Bb5 = float(Bb5)
			if parameterLine.find("BRescaleL7b7") >= 0:
				Bb7 = parameterLine[pos1+2:pos2]
				Bb7 = float(Bb7)
			if parameterLine.find("ESUNL7b1") >= 0:				# Get ESUN values
				Eb1 = parameterLine[pos1+2:pos2]
				Eb1 = float(Eb1)
			if parameterLine.find("ESUNL7b2") >= 0:
				Eb2 = parameterLine[pos1+2:pos2]
				Eb2 = float(Eb2)
			if parameterLine.find("ESUNL7b3") >= 0:
				Eb3 = parameterLine[pos1+2:pos2]
				Eb3 = float(Eb3)
			if parameterLine.find("ESUNL7b4") >= 0:
				Eb4 = parameterLine[pos1+2:pos2]
				Eb4 = float(Eb4)
			if parameterLine.find("ESUNL7b5") >= 0:
				Eb5 = parameterLine[pos1+2:pos2]
				Eb5 = float(Eb5)
			if parameterLine.find("ESUNL7b7") >= 0:
				Eb7 = parameterLine[pos1+2:pos2]
				Eb7 = float(Eb7)
		if landsatnum == "4":									# Test for Landsat 4
			if parameterLine.find("GRescaleL4b1") >= 0:			# Get G-Rescale values
				Gb1 = parameterLine[pos1+2:pos2]
				Gb1 = float(Gb1)
			if parameterLine.find("GRescaleL4b2") >= 0:
				Gb2 = parameterLine[pos1+2:pos2]
				Gb2 = float(Gb2)
			if parameterLine.find("GRescaleL4b3") >= 0:
				Gb3 = parameterLine[pos1+2:pos2]
				Gb3 = float(Gb3)
			if parameterLine.find("GRescaleL4b4") >= 0:
				Gb4 = parameterLine[pos1+2:pos2]
				Gb4 = float(Gb4)
			if parameterLine.find("GRescaleL4b5") >= 0:
				Gb5 = parameterLine[pos1+2:pos2]
				Gb5 = float(Gb5)
			if parameterLine.find("GRescaleL4b7") >= 0:
				Gb7 = parameterLine[pos1+2:pos2]
				Gb7 = float(Gb7)
			if parameterLine.find("BRescaleL4b1") >= 0:			# Get B-Rescale values
				Bb1 = parameterLine[pos1+2:pos2]
				Bb1 = float(Bb1)
			if parameterLine.find("BRescaleL4b2") >= 0:
				Bb2 = parameterLine[pos1+2:pos2]
				Bb2 = float(Bb2)
			if parameterLine.find("BRescaleL4b3") >= 0:
				Bb3 = parameterLine[pos1+2:pos2]
				Bb3 = float(Bb3)
			if parameterLine.find("BRescaleL4b4") >= 0:
				Bb4 = parameterLine[pos1+2:pos2]
				Bb4 = float(Bb4)
			if parameterLine.find("BRescaleL4b5") >= 0:
				Bb5 = parameterLine[pos1+2:pos2]
				Bb5 = float(Bb5)
			if parameterLine.find("BRescaleL4b7") >= 0:
				Bb7 = parameterLine[pos1+2:pos2]
				Bb7 = float(Bb7)
			if parameterLine.find("ESUNL4b1") >= 0:				# Get ESUN values
				Eb1 = parameterLine[pos1+2:pos2]
				Eb1 = float(Eb1)
			if parameterLine.find("ESUNL4b2") >= 0:
				Eb2 = parameterLine[pos1+2:pos2]
				Eb2 = float(Eb2)
			if parameterLine.find("ESUNL4b3") >= 0:
				Eb3 = parameterLine[pos1+2:pos2]
				Eb3 = float(Eb3)
			if parameterLine.find("ESUNL4b4") >= 0:
				Eb4 = parameterLine[pos1+2:pos2]
				Eb4 = float(Eb4)
			if parameterLine.find("ESUNL4b5") >= 0:
				Eb5 = parameterLine[pos1+2:pos2]
				Eb5 = float(Eb5)
			if parameterLine.find("ESUNL4b7") >= 0:
				Eb7 = parameterLine[pos1+2:pos2]
				Eb7 = float(Eb7)
	parameters.close()
	#-----GET NORMALIZATION PARAMETERS AND SUN-EARTH-DISTANCE FROM EXTERNAL TXT-FILES-----
	pi = math.pi												# define PI for the calculation later
	SEDFile = workDir + "00_Sun-Earth-distance.txt"				# Get Sun-Earth-Distance for day of year
	SEDs = open(SEDFile, "r")
	for SEDLine in SEDs:
		posi2 = len(SEDLine)
		posi1 = SEDLine.find("=")
		if SEDLine.find(dateDOY) >= 0:
			SED = SEDLine[posi1+2:posi2]
			SED = float(SED)
	SEDs.close()
	SunElev = float(SunElev)									# Create Cos Values for Sun Zenit
	SunZenit = 90 - SunElev										# According to Landsat-Handbook
	SunZenit = math.radians(SunZenit)							# Conversion into radians
	CosSunZenit = math.cos(SunZenit)
	CosSunZenit = float(CosSunZenit)


	#-----CONVERT VALUES INTO TOP-OF-ATMOSPHERE-VALUES-----
	for file in list[:]:
		if file.find(".TIF") < 0:
			list.remove(file)
	for file in list:
		input = workDir + file
		output = input.replace(".TIF","_TOA.tif")
		input_gdal = gdal.Open(input, GA_ReadOnly)
		cols = input_gdal.RasterXSize
		rows = input_gdal.RasterYSize
		outDrv = gdal.GetDriverByName('GTiff')
		options = []
		output = outDrv.Create(output, cols, rows, 1, GDT_Float32, options)
		output.SetProjection(input_gdal.GetProjection())
		output.SetGeoTransform(input_gdal.GetGeoTransform())
		for y in range(rows):
			RAW = np.ravel(input_gdal.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
			TOA = np.zeros(cols)
			TOA = (pi * (Gb1 * RAW + Bb1) * (SED * SED))/(Eb1 * CosSunZenit)
			TOA.shape = (1, -1)
			output.GetRasterBand(1).WriteArray(np.array(TOA), 0, y)
		input_gdal = None
	
	#-----DELETE ORIGINAL FILES FROM TAR-ARCHIVES-----usign list2 from the beginning
	for file in list2[:]:
		delete = workDir + file
		os.remove(delete)


endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print "-------------"
print "start: " + starttime
print "end: " + endtime
print "END RUNNING SCRIPT TO CONVERT DN-VALUES INTO TOP OF ATMOSPHERE"
print "--------------------------------------------------------------"
