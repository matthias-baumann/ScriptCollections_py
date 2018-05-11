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
from osgeo import gdal
from osgeo.gdalconst import *
gdal.TermProgress = gdal.TermProgress_nocb
from osgeo import osr
gdal.TermProgress = gdal.TermProgress_nocb
from osgeo import gdal_array as gdalnumeric
import h5py
# ######################################## END OF HEADER INFROMATION AND LOADING OF MODULES ##########################################

# ##### SET TIME-COUNT AND HARD-CODED FOLDER-PATHS #####
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:", starttime)
print("")
center_PathRow = sys.argv[1]
Year = sys.argv[2]
root_Folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\" + center_PathRow + "\\" + Year + "\\"
bands_read = [1,2,3,4,5,7]										# Bands we will take out from the hdf-file
bands_write = [1,2,3,4,5,6]										# Band count for the output file
# ##### READY TO GO #####
gdal.PushErrorHandler("CPLQuietErrorHandler")
# ##### START THE ANALYSIS #####
pathRowList = os.listdir(root_Folder)
# (1) Go into each folder --> center footprint and neighboring footprints
for folder in pathRowList[:]:
	searchFolder = root_Folder + folder + "\\"
	sceneList = os.listdir(searchFolder)
	for scene in sceneList[:]:
		open_sceneFolder = searchFolder + scene
		fileList = os.listdir(open_sceneFolder)
		print("Converting file:", scene)
		for file in fileList[:]:
			if file.find("lndsr") >= 0 and file.find(".hdr") < 0 and file.find(".txt") < 0:
				hdf_file = open_sceneFolder + "\\" + file
				os.chdir(open_sceneFolder)	
# (2) Take the selected hdf-file and convert it into bsq
				output_file = hdf_file
				output_file = output_file.replace(".hdf","")
				output_file = output_file.replace("lndsr.","")
				if not os.path.exists(output_file):
					for band in bands_read:
						band_str = str(band)
						command = "band_" + band_str + " = gdal.Open('HDF4_EOS:EOS_GRID:" + file + ":Grid:band" + band_str + "', GA_ReadOnly)"
						exec(command)
					cols = band_1.RasterXSize
					rows = band_1.RasterYSize
					outDrv = gdal.GetDriverByName('ENVI')
					options = []
					output = outDrv.Create(output_file, cols, rows, 6, GDT_UInt16, options)
					output.SetProjection(band_1.GetProjection())
					output.SetGeoTransform(band_1.GetGeoTransform())
					for y in range(rows):
						for i in range(6):
							band_str = str(bands_read[i])
							command = "b = np.ravel(band_" + band_str + ".GetRasterBand(1).ReadAsArray(0, y, cols, 1))"
							exec(command)
							dataOut = np.zeros(cols)
							dataOut = b
							dataOut.shape = (1, -1)
							output.GetRasterBand(bands_write[i]).WriteArray(np.array(dataOut), 0, y)
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