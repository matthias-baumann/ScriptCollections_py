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
import gdal
from gdalconst import *
#gdal.TermProgress = gdal.TermProgress_nocb
#from osgeo import osr
#gdal.TermProgress = gdal.TermProgress_nocb
#from osgeo import gdal_array as gdalnumeric
#import h5py
# ######################################## END OF HEADER INFROMATION AND LOADING OF MODULES ##########################################
# test if it works
# ##### SET TIME-COUNT AND HARD-CODED FOLDER-PATHS #####
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:", starttime)
print("")
center_PathRow = sys.argv[1]
root_Folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\" + center_PathRow + "\\"
# ##### READY TO GO #####
gdal.PushErrorHandler("CPLQuietErrorHandler")
# ##### START THE ANALYSIS #####
pathRowList = os.listdir(root_Folder)
# (1) Go into each folder --> center footprint and neighboring footprints
for folder in pathRowList[:]:
	searchFolder = root_Folder + folder + "\\"
	sceneList = os.listdir(searchFolder)
	print("Converting file:", folder)
	for file in sceneList[:]:
		if file.find("lndsr") >= 0 and file.find(".hdr") < 0 and file.find(".txt") < 0:
			hdf_file = searchFolder + "\\" + file
			os.chdir(searchFolder)	
# (2) Take the selected hdf-file and convert it into bsq
			output_file = hdf_file
			output_file = output_file.replace(".hdf","_ThermalBand")
			output_file = output_file.replace("lndsr.","")
			if not os.path.exists(output_file):
				command = "band_6 = gdal.Open('HDF4_EOS:EOS_GRID:" + file + ":Grid:band6" + "', GA_ReadOnly)"
				exec(command)
				cols = band_6.RasterXSize
				rows = band_6.RasterYSize
				outDrv = gdal.GetDriverByName('ENVI')
				options = []
				output = outDrv.Create(output_file, cols, rows, 1, GDT_Int16, options)
				output.SetProjection(band_6.GetProjection())
				output.SetGeoTransform(band_6.GetGeoTransform())
				for y in range(rows):
					command = "b = np.ravel(band_6.GetRasterBand(1).ReadAsArray(0, y, cols, 1))"
					exec(command)
					dataOut = np.zeros(cols)
					dataOut = b
					dataOut.shape = (1, -1)
					output.GetRasterBand(1).WriteArray(np.array(dataOut), 0, y)
			else:
				print("-->", file, "already converted. Continuing with next file.")
print("")
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start:", starttime)
print("end:", endtime)
print("")