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
print "START RUNNING SCRIPT TO CREATE LAYER STACKS FROM LAYERS OF PART03"
workDir = RAW_Folder

# Get full names of files to be processed			# This is the same code as in script 01a
# Get files for input
inputList = []
info = open(listFile, "r")
for line in info:
	file = line
	file = str(file)
	file = file.replace("\n","")
	inputList.append(file)
processList = []
RAW_List = os.listdir(workDir)
for file in inputList:
	for tar in RAW_List:
		if tar.find(file) >= 0:
			a = workDir + tar
			processList.append(a)

# Stack tar-archive-wise to 6-bands-composite, and get image-information from MTL-File
tempMaskCount = 0
for archive in processList:
	tempMaskCount = tempMaskCount + 1
	tempMaskCount_str = str(tempMaskCount)
	tar = tarfile.open(archive, "r:gz")
	list = tar.getnames()
	for file in list:
		if file.find("MTL") >= 0:
			tar.extract(file, workDir)
			# now get information from extracted MTL-File
			infoFile = workDir + file
			id = file							# take the id from MTl-file, so tht we recognize the files 
			id = id.replace("_MTL.txt","")		# in the list that we need to stack together.
			print "Processing file: " + id
			# EXTRACT INFORMATION FROM TXT FILE
			fin = open(infoFile, "r")
			for line in fin:
				p2 = len(line)
				p1 = line.find('"')
				if line.find("PRODUCT_TYPE") >= 0: 
					prodtype = line[p1+1:p2-2]
				if line.find("SPACECRAFT_ID") >= 0: 
					landsattype = line[p1+1:p2-2]
					landsatnum = landsattype[len(landsattype)-1]
				if line.find("WRS_PATH") >= 0: 
					path = line[p2-4:p2-1]
				if line.find("STARTING_ROW") >= 0: 
					p1 = line.rfind(" ")
					row = line[p1+1:p2-1]
					if len(row) == 2: row = "0" + row
				if line.find("ACQUISITION_DATE") >= 0:
					p1 = line.rfind(" ")
					date = line[p1+1:p2-1]
					date = date.replace("-","")
			fin.close()
			os.remove(infoFile)
			# Create file-names for the subsequent layer stack and get files that we want to process
			final_name = outDir + path + row + "_" + date + "_L" + landsatnum + "-" + prodtype + ".tif"
			band_List = []
			files = os.listdir(workDir)
			for file in files[:]:
				if file.find(date) >= 0:
					band_List.append(file)
			# Create the final command to stack the images
			command = "gdal_merge.py -o " + final_name + " -separate "
			for band in band_List:
				b = workDir + band
				command = command + b + " "
			os.system(command)
			
			# delete bands
			for band in band_List:
				delete = workDir + band
				os.remove(delete)
	tar.close()



endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print "-------------"
print "start: " + starttime
print "end: " + endtime
print "END RUNNING SCRIPT TO CONVERT APPLY ACTIVE AREA TO BANDS"
print "--------------------------------------------------------------"