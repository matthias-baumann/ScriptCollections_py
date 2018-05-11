# ######################################## LOAD REQUIRED MODULES ############################################### #
# IMPORT SYSTEM MODULES
#from __future__ import division
#from math import sqrt
import sys, string
import os
#import arcgisscripting
import time
import datetime
#import shutil
#import math
#import numpy as np
import tarfile
#np.arrayarange = np.arange
#from numpy.linalg import *
#from osgeo import gdal
#from osgeo.gdalconst import *
#gdal.TermProgress = gdal.TermProgress_nocb
#from osgeo import osr
#gdal.TermProgress = gdal.TermProgress_nocb
#from osgeo import gdal_array as gdalnumeric
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:", starttime)
print("")

# ####################################### BUILD GLOBAL FUNCTIONS ############################################## #

def unzip(folder):
	print("--------------------------------------------------------")
	RAW_List = os.listdir(str(folder))
	for file in RAW_List:
		if file.find("Thumbs.db") < 0:
			output = folder + file + "\\"
			output = output.replace(".tar.gz","")
			print("Extracting tar-archive:", file)
			archiveName = folder + file
			tar = tarfile.open(archiveName, "r")
			list = tar.getnames()
			for file in tar:
				tar.extract(file, output)
			tar.close()
			file = None
					
def zip(folder):
	print("--------------------------------------------------------")
	processList = os.listdir(str(folder))
	for item in processList:
		output = folder + item + ".tar.gz"
		print("Creating tar-archive:", output)
		tar = tarfile.open(output, "w:gz")
		input = folder + item + "\\"
		list = os.listdir(input)
		for file in list:
			os.chdir(input)
			tar.add(file)
		tar.close()
		file = None
			

# ####################################### RUN THE MODULES AND CALL THE FUNCTIONS ############################## #	

call = sys.argv[1]
in_folder = sys.argv[2]

if call == "zip":
	zip(in_folder)
else:
	if call == "unzip":
		unzip(in_folder)
	else:
		print("Incorrect call for function. Use 'zip' or 'unzip' for processing")
		exit(0)


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #		
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")