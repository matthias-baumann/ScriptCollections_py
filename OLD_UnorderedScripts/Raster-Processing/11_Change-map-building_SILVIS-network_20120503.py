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
import numpy.ma as ma
from osgeo import gdal
from osgeo.gdalconst import *
gdal.TermProgress = gdal.TermProgress_nocb
from osgeo import osr
gdal.TermProgress = gdal.TermProgress_nocb
from osgeo import gdal_array as gdalnumeric
# ######################################## END OF HEADER INFROMATION AND LOADING OF MODULES ##########################################
# ##### SET TIME-COUNT AND HARD-CODED FOLDER-PATHS #####
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

PathRow = sys.argv[1]

FP_Folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\"

print("--------------------------------------------------------")
print("Footprint:", PathRow)

# (1-A) Create RAW-Paths for the files we are using
Classification_2000 = FP_Folder + PathRow + "\\2000\\" + PathRow + "_2000_classification-masked"
Classification_2005 = FP_Folder + PathRow + "\\2005\\" + PathRow + "_2005_classification-masked"
Classification_2010 = FP_Folder + PathRow + "\\2010\\" + PathRow + "_2010_classification-masked"
NDWI_2000 = FP_Folder + PathRow + "\\2000\\" + PathRow + "_2000_NDWI-masked"
NDWI_2005 = FP_Folder + PathRow + "\\2005\\" + PathRow + "_2005_NDWI-masked"
NDWI_2010 = FP_Folder + PathRow + "\\2010\\" + PathRow + "_2010_NDWI-masked"
water_2000 = FP_Folder + PathRow + "\\2000\\" + PathRow + "_2000_waterMask-masked"
water_2005 = FP_Folder + PathRow + "\\2005\\" + PathRow + "_2005_waterMask-masked"
water_2010 = FP_Folder + PathRow + "\\2010\\" + PathRow + "_2010_waterMask-masked"
output = FP_Folder + PathRow + "\\" + PathRow + "_2000-2010-changemap"

# (1-B) Load everything into GDAL and create properties and variables
Classification_2000_GDAL = gdal.Open(Classification_2000, GA_ReadOnly)
Classification_2005_GDAL = gdal.Open(Classification_2005, GA_ReadOnly)
Classification_2010_GDAL = gdal.Open(Classification_2010, GA_ReadOnly)
NDWI_2000_GDAL = gdal.Open(NDWI_2000, GA_ReadOnly)
NDWI_2005_GDAL = gdal.Open(NDWI_2005, GA_ReadOnly)
NDWI_2010_GDAL = gdal.Open(NDWI_2010, GA_ReadOnly)
Water_2000_GDAL = gdal.Open(water_2000, GA_ReadOnly)
Water_2005_GDAL = gdal.Open(water_2005, GA_ReadOnly)
Water_2010_GDAL = gdal.Open(water_2010, GA_ReadOnly)

cols = Classification_2000_GDAL.RasterXSize
rows = Classification_2000_GDAL.RasterYSize
outDrv = gdal.GetDriverByName('ENVI')
options = []
out = outDrv.Create(output, cols, rows, 1, GDT_Byte, options)
out.SetProjection(Classification_2000_GDAL.GetProjection())
out.SetGeoTransform(Classification_2000_GDAL.GetGeoTransform())

print("Build Change map...")
# (1-C)	Process the images line by line
for y in range(rows):
	y2000 = np.ravel(Classification_2000_GDAL.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	y2005 = np.ravel(Classification_2005_GDAL.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	y2010 = np.ravel(Classification_2010_GDAL.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	n2000 = np.ravel(NDWI_2000_GDAL.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	n2005 = np.ravel(NDWI_2005_GDAL.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	n2010 = np.ravel(NDWI_2010_GDAL.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	w2000 = np.ravel(Water_2000_GDAL.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	w2005 = np.ravel(Water_2005_GDAL.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	w2010 = np.ravel(Water_2010_GDAL.GetRasterBand(1).ReadAsArray(0, y, cols, 1))
	# Set all NaN values in NDWI to -1
	n2000[np.isnan(n2000)] = -1
	n2005[np.isnan(n2005)] = -1
	n2010[np.isnan(n2010)] = -1
	
	dataOut = np.zeros(cols)
	
	# 0: unclassified, 1: Constant forest, 2: Constant non-forest, 3: Disturbance 2000-2005, 4: Disturbance 2005-2010, 5: Recovery 2000-2010
	# F-F-F
	FNF2000 = np.zeros(cols)
	FNF2005 = np.zeros(cols)
	FNF2010 = np.zeros(cols)
	np.putmask(FNF2000, y2000 == 1, 1)
	np.putmask(FNF2005, y2005 == 1, 1)
	np.putmask(FNF2010, y2010 == 1, 1)
	zwiSum = FNF2000 + FNF2005 + FNF2010
	FFF = np.zeros(cols)
	np.putmask(FFF, zwiSum == 3, 1)
	# F-F-N
	FNF2000 = np.zeros(cols)
	FNF2005 = np.zeros(cols)
	FNF2010 = np.zeros(cols)
	np.putmask(FNF2000, y2000 == 1, 1)
	np.putmask(FNF2005, y2005 == 1, 1)
	np.putmask(FNF2010, y2010 == 2, 1)
	zwiSum = FNF2000 + FNF2005 + FNF2010
	FFN = np.zeros(cols)
	np.putmask(FFN, zwiSum == 3, 4)
	# F-N-F
	FNF2000 = np.zeros(cols)
	FNF2005 = np.zeros(cols)
	FNF2010 = np.zeros(cols)
	np.putmask(FNF2000, y2000 == 1, 1)
	np.putmask(FNF2005, y2005 == 2, 1)
	np.putmask(FNF2010, y2010 == 1, 1)
	zwiSum = FNF2000 + FNF2005 + FNF2010
	FNF = np.zeros(cols)
	np.putmask(FNF, zwiSum == 3, 1)
	# F-N-N
	FNF2000 = np.zeros(cols)
	FNF2005 = np.zeros(cols)
	FNF2010 = np.zeros(cols)
	np.putmask(FNF2000, y2000 == 1, 1)
	np.putmask(FNF2005, y2005 == 2, 1)
	np.putmask(FNF2010, y2010 == 2, 1)
	zwiSum = FNF2000 + FNF2005 + FNF2010
	FNN = np.zeros(cols)
	np.putmask(FNN, zwiSum == 3, 3)
	# N-N-N
	FNF2000 = np.zeros(cols)
	FNF2005 = np.zeros(cols)
	FNF2010 = np.zeros(cols)
	np.putmask(FNF2000, y2000 == 2, 1)
	np.putmask(FNF2005, y2005 == 2, 1)
	np.putmask(FNF2010, y2010 == 2, 1)
	zwiSum = FNF2000 + FNF2005 + FNF2010
	NNN = np.zeros(cols)
	np.putmask(NNN, zwiSum == 3, 2)	
	# N-N-F
	FNF2000 = np.zeros(cols)
	FNF2005 = np.zeros(cols)
	FNF2010 = np.zeros(cols)
	np.putmask(FNF2000, y2000 == 2, 1)
	np.putmask(FNF2005, y2005 == 2, 1)
	np.putmask(FNF2010, y2010 == 1, 1)
	zwiSum = FNF2000 + FNF2005 + FNF2010
	NNF = np.zeros(cols)
	np.putmask(NNF, zwiSum == 3, 5)	
	# N-F-N
	FNF2000 = np.zeros(cols)
	FNF2005 = np.zeros(cols)
	FNF2010 = np.zeros(cols)
	np.putmask(FNF2000, y2000 == 2, 1)
	np.putmask(FNF2005, y2005 == 1, 1)
	np.putmask(FNF2010, y2010 == 2, 1)
	zwiSum = FNF2000 + FNF2005 + FNF2010
	NFN = np.zeros(cols)
	np.putmask(NFN, zwiSum == 3, 2)	
	# N-F-F
	FNF2000 = np.zeros(cols)
	FNF2005 = np.zeros(cols)
	FNF2010 = np.zeros(cols)
	np.putmask(FNF2000, y2000 == 2, 1)
	np.putmask(FNF2005, y2005 == 1, 1)
	np.putmask(FNF2010, y2010 == 1, 1)
	zwiSum = FNF2000 + FNF2005 + FNF2010
	NFF = np.zeros(cols)
	np.putmask(NFF, zwiSum == 3, 5)	

	# # Account for the water masked areas
	# # NULL-F-NULL
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 0, 1)
	# np.putmask(FNF2005, y2005 == 1, 1)
	# np.putmask(FNF2010, y2010 == 0, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# NullFNull = np.zeros(cols)
	# np.putmask(NullFNull, zwiSum == 3, 0)
	# # NULL-F-F
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 0, 1)
	# np.putmask(FNF2005, y2005 == 1, 1)
	# np.putmask(FNF2010, y2010 == 1, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# NullFF = np.zeros(cols)
	# np.putmask(NullFF, zwiSum == 3, 1)
	# # F-NULL-F
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 1, 1)
	# np.putmask(FNF2005, y2005 == 0, 1)
	# np.putmask(FNF2010, y2010 == 1, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# FNullF = np.zeros(cols)
	# np.putmask(FNullF, zwiSum == 3, 1)
	# # NF-NULL-NF
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 2, 1)
	# np.putmask(FNF2005, y2005 == 0, 1)
	# np.putmask(FNF2010, y2010 == 2, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# NFNullNF = np.zeros(cols)
	# np.putmask(NFNullNF, zwiSum == 3, 2)
	# # NULL-NF-NULL
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 0, 1)
	# np.putmask(FNF2005, y2005 == 2, 1)
	# np.putmask(FNF2010, y2010 == 0, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# NullNFNull = np.zeros(cols)
	# np.putmask(NullNFNull, zwiSum == 3, 0)	
	# # NULL-NULL-NULL
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 0, 1)
	# np.putmask(FNF2005, y2005 == 0, 1)
	# np.putmask(FNF2010, y2010 == 0, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# NullNullNull = np.zeros(cols)
	# np.putmask(NullNullNull, zwiSum == 3, 0)
	# # NF-NULL-NULL
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 2, 1)
	# np.putmask(FNF2005, y2005 == 0, 1)
	# np.putmask(FNF2010, y2010 == 0, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# NFNullNull = np.zeros(cols)
	# np.putmask(NFNullNull, zwiSum == 3, 0)	
	# # NULL-NF-NF
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 0, 1)
	# np.putmask(FNF2005, y2005 == 2, 1)
	# np.putmask(FNF2010, y2010 == 2, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# NullNFNF = np.zeros(cols)
	# np.putmask(NullNFNF, zwiSum == 3, 2)
	# # NULL-NULL-NF
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 0, 1)
	# np.putmask(FNF2005, y2005 == 0, 1)
	# np.putmask(FNF2010, y2010 == 2, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# NullNullNF = np.zeros(cols)
	# np.putmask(NullNullNF, zwiSum == 3, 0)
	# # NF-NF-NULL
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 2, 1)
	# np.putmask(FNF2005, y2005 == 2, 1)
	# np.putmask(FNF2010, y2010 == 0, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# NFNFNull = np.zeros(cols)
	# np.putmask(NFNFNull, zwiSum == 3, 2)	
	
	# # Account for water masked areas --> mixed with F,NF,Null
	# # NULL-NF-F
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 0, 1)
	# np.putmask(FNF2005, y2005 == 2, 1)
	# np.putmask(FNF2010, y2010 == 1, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# NullNFF = np.zeros(cols)
	# np.putmask(NullNFF, zwiSum == 3, 0)	
	# # F-NULL-NF
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 1, 1)
	# np.putmask(FNF2005, y2005 == 0, 1)
	# np.putmask(FNF2010, y2010 == 2, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# FNullNF = np.zeros(cols)
	# np.putmask(FNullNF, zwiSum == 3, 0)		
	# # F-NF-NULL
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 1, 1)
	# np.putmask(FNF2005, y2005 == 2, 1)
	# np.putmask(FNF2010, y2010 == 0, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# FNFNull = np.zeros(cols)
	# np.putmask(FNFNull, zwiSum == 3, 3)		
	# # NF-F-NULL
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 2, 1)
	# np.putmask(FNF2005, y2005 == 1, 1)
	# np.putmask(FNF2010, y2010 == 0, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# NFFNull = np.zeros(cols)
	# np.putmask(NFFNull, zwiSum == 3, 0)		
	# # NULL-F-NF
	# FNF2000 = np.zeros(cols)
	# FNF2005 = np.zeros(cols)
	# FNF2010 = np.zeros(cols)
	# np.putmask(FNF2000, y2000 == 0, 1)
	# np.putmask(FNF2005, y2005 == 1, 1)
	# np.putmask(FNF2010, y2010 == 2, 1)
	# zwiSum = FNF2000 + FNF2005 + FNF2010
	# NFFNull = np.zeros(cols)
	# np.putmask(NFFNull, zwiSum == 3, 0)	
	
	# Create overall sum and write it into temp-file
	chMap_temp = FFF + FFN + FNF + FNN + NNN + NNF + NFN + NFF# + NullFNull + NullFF + FNullF + NFNullNF + NullNFNull + NullNullNull + NFNullNull + NullNFNF + NullNullNF + NFNFNull + NullNFF + FNullNF + FNFNull + NFFNull
	
	# Now make combinations to correct using the NDWI file (negative values and disturbance are likely a misclassification --> re-label into constant non-forest)
	# First version(not used currently): COnsider only the NDWI of the period that we look at
	# Second version: Consider all three time steps of NDWI
	
	# # Correct disturbance 2000-2005
	# dis0005 = np.zeros(cols)
	# NDWI00 = np.zeros(cols)
	# NDWI05 = np.zeros(cols)
	# NDWI10 = np.zeros(cols)
	# np.putmask(dis0005, chMap_temp == 3, 1)
	# np.putmask(NDWI00, n2000 < 0, 1)
	# np.putmask(NDWI05, n2005 < 0, 1)
	# np.putmask(NDWI10, n2010 < 0, 1)
	# NDWISum = NDWI00 + NDWI05 + NDWI10
	# NDWIrule = np.zeros(cols)
	# np.putmask(NDWIrule, NDWISum >= 1, 1)
	# zwiSum = dis0005 + NDWIrule
	# dis0005corr = np.zeros(cols)
	# np.putmask(dis0005corr, zwiSum == 2, 1)
	
	# # Correct disturbance 2005-2010
	# dis0510 = np.zeros(cols)
	# NDWI00 = np.zeros(cols)
	# NDWI05 = np.zeros(cols)
	# NDWI10 = np.zeros(cols)
	# np.putmask(dis0510, chMap_temp == 4, 1)
	# np.putmask(NDWI00, n2000 < 0, 1)
	# np.putmask(NDWI05, n2005 < 0, 1)
	# np.putmask(NDWI10, n2010 < 0, 1)
	# NDWISum = NDWI00 + NDWI05 + NDWI10
	# NDWIrule = np.zeros(cols)
	# np.putmask(NDWIrule, NDWISum >= 1, 1)
	# zwiSum = dis0510 + NDWIrule
	# dis0510corr = np.zeros(cols)
	# np.putmask(dis0510corr, zwiSum == 2, 1)
	
	# # Now bring this into the final change-map
	# np.putmask(chMap_temp, dis0005corr == 1, 2)
	# np.putmask(chMap_temp, dis0510corr == 1, 2)
	# dataOut = chMap_temp

	
	chMap_temp.shape = (1, -1)
	out.GetRasterBand(1).WriteArray(np.array(chMap_temp), 0, y)

# (2) Close the GDAL-variables
Classification_2000_GDAL = None
Classification_2005_GDAL = None
Classification_2010_GDAL = None

	
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")