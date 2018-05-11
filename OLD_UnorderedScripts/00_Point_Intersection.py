# ######################################## LOAD REQUIRED MODULES ############################################## #
import os, sys
import time, datetime
import ogr
import osr
import gdal
from gdalconst import *
import numpy as np
import csv
import itertools
import math
import scipy.ndimage
import struct
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:", starttime)
print("")
# ####################################### BUILD GLOBAL FUNCTIONS ############################################## #

def GetPointID(pointFile):
	IDs = []
	IDs.append("Point-ID")
	points = ogr.Open(pointFile)
	lyr = points.GetLayer()
	feature = lyr.GetNextFeature()
	while feature:
		id = feature.GetField('ID')
		IDs.append(id)
		feature = lyr.GetNextFeature()
	lyr.ResetReading()
	return IDs
	
def Intersect_OneLayer(pointFile,rasterFile,VariableName, type):
	print("Raster-File: " + rasterFile)
	print("Variable-Name: " + VariableName)
	values = []
	values.append(VariableName)
	points = ogr.Open(pointFile)
	lyr = points.GetLayer()
	for feat in lyr:
		geom = feat.GetGeometryRef()
		mx,my = geom.GetX(), geom.GetY()
		ras = gdal.Open(rasterFile)
		gt = ras.GetGeoTransform()				# gt stands for the GeoTransform
		array = ras.GetRasterBand(1)
		px = int((mx - gt[0]) / gt[1])
		py = int((my - gt[3]) / gt[5])
		structval = array.ReadRaster(px, py, 1, 1)#, buf_type = GDT_Float32)
		intval = struct.unpack(type , structval)
		values.append(intval[0])
	lyr.ResetReading()
	print("")
	return values
	
def WriteOutput(outlist, outfile):
	print("Write Output-File")
	with open(outfile, "w") as the_file:
		csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
		writer = csv.writer(the_file, dialect="custom")
		for element in outlist:
			writer.writerow(element)
	
# ####################################### RUN THE MODULES AND CALL THE FUNCTIONS ############################## #	
# (0) Point-IDs
print("Get Point-IDs")
point_input = "E:/kirkdata/mbaumann/Caucasus/Hypothesis_Evaluation/03_PostConflict_Direct/Recultivation_200pointsPerClass.shp"
ID_list = GetPointID(point_input)

# (2) POINT-INTERSECTION FOR VARIABLEs
raster_input = "E:/kirkdata/mbaumann/Caucasus/SRTM/STRM-Mosaic_Elevation.tif"
name = "Elevation_m"
format = 'h'															# 'h' --> GDT_UInt16; 'f' --> GDT_Float32; 'b' --> GDTUInt8
variable01 = Intersect_OneLayer(point_input,raster_input,name, format)

raster_input = "E:/kirkdata/mbaumann/Caucasus/SRTM/SRTM-Mosaic_SlopePercent.img"
name = "Slope_perc"
format = 'b'
variable02 = Intersect_OneLayer(point_input,raster_input,name, format)

raster_input = "E:/kirkdata/mbaumann/Caucasus/Hypothesis_Evaluation/01_Conflict_Direct/Soil_pHvalue.img"
name = "Soil_pH"
format = 'f'
variable03 = Intersect_OneLayer(point_input,raster_input,name, format)

raster_input = "E:/kirkdata/mbaumann/Caucasus/Hypothesis_Evaluation/01_Conflict_Direct/Roads_Merged_EucDist_meters.tif"
name = "RoadDis_m"
format = 'f'
variable04 = Intersect_OneLayer(point_input,raster_input,name, format)

raster_input = "E:/kirkdata/mbaumann/Caucasus/Hypothesis_Evaluation/01_Conflict_Direct/Settlements_woMajorClashes_EucDist_meters.tif"
name = "SettlementDis_m"
format = 'f'
variable05 = Intersect_OneLayer(point_input,raster_input,name, format)

raster_input = "E:/kirkdata/mbaumann/Caucasus/Hypothesis_Evaluation/00_MajorBattleSites/MajorBattleSites_EucDist_meters.tif"
name = "Dis_MajorBattleSites_m"
format = 'f'
variable06 = Intersect_OneLayer(point_input,raster_input,name, format)

raster_input = "E:/kirkdata/mbaumann/Caucasus/Hypothesis_Evaluation/00_MajorBattleSites/MajorBattleSites_GeographicCenter_EucDist_meters.tif"
name = "Dis_MajorBattleSitesCentroid_m"
format = 'f'
variable07 = Intersect_OneLayer(point_input,raster_input,name, format)



# ####################################### WRITE THE OUTPUT FILE ############################################### #
outfile = "E:/kirkdata/mbaumann/Caucasus/Hypothesis_Evaluation/03_PostConflict_Direct/Recultivation_1000pointsPerClass_PointIntersect.csv"
outlist = zip(ID_list, variable01,variable02,variable03,variable04,variable05,variable06,variable07)
WriteOutput(outlist, outfile)

		
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #		
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")