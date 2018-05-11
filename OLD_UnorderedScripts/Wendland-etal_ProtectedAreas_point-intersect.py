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
workDir = "F:\\DataF\\mbaumann\\Data Processing\\06_Kelly_Sampling-design-chapter03\\"
pointDir = "F:\\DataF\\mbaumann\\Data Processing\\06_Kelly_Sampling-design-chapter03\\Kelly_Sample\\"
mapDir = "F:\\DataF\\mbaumann\\Data Processing\\03_Forest-classifications\\Forest-cover_maps\\"

slopeFile = "F:\\DataF\\mbaumann\\Data Processing\\00_cgiar-srtm_processing\\Slope\\srtm_90m_percent-slope.img"
elevationFile = "F:\\DataF\\mbaumann\\Data Processing\\00_cgiar-srtm_processing\\Mosaicing\\srtm-cgiar_entire-region_ERDAS.img"
MODISfile = workDir + "MODIS_Evergreen_YesNo_extended.tif"
CityDisFile = workDir + "Distance-to-Cities_extended.tif"
MosStPeDisFile = workDir + "Distance-to-Moscow-StPetersburg_extended.tif"
roadDisFile = workDir + "Distance-to-road_meters_extended.tif"
districtFile = workDir + "Districts.shp"
regionFile = workDir + "Regions.shp"
parkFile = workDir + "Parks_Landsat_selection.shp"
nightTime1993 = workDir + "F1F101993.cloud1.light1.round.byte.tif"
nightTime2003 = workDir + "F152003.cloud1.light1.round.byte.tif"
forestEdge1985 = workDir + "179023_1985_distance-to-forest-edge.tif"
forestEdge1990 = workDir + "179023_1990_distance-to-forest-edge.tif"
forestEdge1995 = workDir + "179023_1995_distance-to-forest-edge.tif"
forestEdge2000 = workDir + "179023_2000_distance-to-forest-edge.tif"
forestEdge2005 = workDir + "179023_2005_distance-to-forest-edge.tif"
forestEdge2010 = workDir + "179023_2010_distance-to-forest-edge.tif"
F_NF_1990 = mapDir + "179023_1990_ClumpEliminate-sub.tif"
F_NF_1995 = mapDir + "179023_1995_ClumpEliminate-sub.tif"
F_NF_2000 = mapDir + "179023_2000_ClumpEliminate-sub.tif"
F_NF_2005 = mapDir + "179023_2005_ClumpEliminate-sub.tif"
F_NF_2010 = mapDir + "179023_2010_ClumpEliminate-sub.tif"

# BUILD LISTS FOR POINT-FILES
pointList = []
fileList = os.listdir(pointDir)
for file in fileList[:]:
	if file.find(".shp") >= 0:
		pointList.append(file)
for file in pointList[:]:
	if file.find("xml") >= 0:
		pointList.remove(file)
for file in pointList[:]:
	if file.find("withInfo") >= 0 or file.find("TMP") >= 0:
		pointList.remove(file)

for file in pointList:
	pointFileInput = pointDir + file
	pointFileOutput = pointFileInput
	pointFileOutput = pointFileOutput.replace(".shp","_withInfo.shp")
	if not os.path.exists(pointFileOutput):
		print "Processing Point-File: " + file
		print "--------------------------------------------------------"
		# GETTING INFORMATION FROM FORET-MAPS TO POINTS
		# Create TMP-Point-File
		print "Forest-Map 1990"
		outputTMP01 = pointFileInput
		outputTMP01 = outputTMP01.replace(".shp","_TMP01.shp")
		if not os.path.exists(outputTMP01):
			inputRas = F_NF_1990
			pointFile = pointFileInput
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP01, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			gp.AddField_management(outputTMP01, "FNF_90", "SHORT")		# Create new field with name
			rows = gp.UpdateCursor(outputTMP01)
			row = rows.next()
			while row:
				row.FNF_90 = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP01,"RASTERVALU")
		else:
			print outputTMP01, " already exists. Continuing with next file." 

		print "Forest-map 1995"
		outputTMP02 = outputTMP01
		outputTMP02 = outputTMP02.replace("01.shp","02.shp")
		if not os.path.exists(outputTMP02):
			inputRas = F_NF_1995
			pointFile = outputTMP01
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP02, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP02, "FNF_95", "SHORT")
			rows = gp.UpdateCursor(outputTMP02)
			row = rows.next()
			while row:
				row.FNF_95 = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP02,"RASTERVALU")
		else:
			print outputTMP02, " already exists. Continuing with next file." 

		print "Forest-map 2000"
		outputTMP03 = outputTMP02
		outputTMP03 = outputTMP03.replace("02.shp","03.shp")
		if not os.path.exists(outputTMP03):
			inputRas = F_NF_2000
			pointFile = outputTMP02
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP03, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP03, "FNF_00", "SHORT")
			rows = gp.UpdateCursor(outputTMP03)
			row = rows.next()
			while row:
				row.FNF_00 = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP03,"RASTERVALU")
		else:
			print outputTMP03, " already exists. Continuing with next file."

		print "Forest-map 2005"
		outputTMP04 = outputTMP03
		outputTMP04 = outputTMP04.replace("03.shp","04.shp")
		if not os.path.exists(outputTMP04):
			inputRas = F_NF_2005
			pointFile = outputTMP03
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP04, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP04, "FNF_05", "SHORT")
			rows = gp.UpdateCursor(outputTMP04)
			row = rows.next()
			while row:
				row.FNF_05 = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP04,"RASTERVALU")
		else:
			print outputTMP04, " already exists. Continuing with next file."

		print "Forest-map 2010"
		outputTMP05 = outputTMP04
		outputTMP05 = outputTMP05.replace("04.shp","05.shp")
		if not os.path.exists(outputTMP05):
			inputRas = F_NF_2010
			pointFile = outputTMP04
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP05, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP05, "FNF_10", "SHORT")
			rows = gp.UpdateCursor(outputTMP05)
			row = rows.next()
			while row:
				row.FNF_10 = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP05,"RASTERVALU")
		else:
			print outputTMP05, " already exists. Continuing with next file."
		print "--------------------------------------------------------"


		# GETTING INFORMATION ABOUT DISTANCE MEASURES
		print "Distance to forest edge for 1985"
		outputTMP06 = outputTMP05
		outputTMP06 = outputTMP06.replace("05.shp","06.shp")
		if not os.path.exists(outputTMP06):
			inputRas = forestEdge1985
			pointFile = outputTMP05
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP06, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP06, "DFE_85", "FLOAT")
			rows = gp.UpdateCursor(outputTMP06)
			row = rows.next()
			while row:
				row.DFE_85 = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP06,"RASTERVALU")
		else:
			print outputTMP06, " already exists. Continuing with next file."

		print "Distance to forest edge for 1990"
		outputTMP07 = outputTMP06
		outputTMP07 = outputTMP07.replace("06.shp","07.shp")
		if not os.path.exists(outputTMP07):
			inputRas = forestEdge1990
			pointFile = outputTMP06
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP07, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP07, "DFE_90", "FLOAT")
			rows = gp.UpdateCursor(outputTMP07)
			row = rows.next()
			while row:
				row.DFE_90 = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP07,"RASTERVALU")
		else:
			print outputTMP07, " already exists. Continuing with next file."

		print "Distance to forest edge for 1995"
		outputTMP08 = outputTMP07
		outputTMP08 = outputTMP08.replace("07.shp","08.shp")
		if not os.path.exists(outputTMP08):
			inputRas = forestEdge1995
			pointFile = outputTMP07
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP08, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP08, "DFE_95", "FLOAT")
			rows = gp.UpdateCursor(outputTMP08)
			row = rows.next()
			while row:
				row.DFE_95 = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP08,"RASTERVALU")
		else:
			print outputTMP08, " already exists. Continuing with next file."

		print "Distance to forest edge for 2000"
		outputTMP09 = outputTMP08
		outputTMP09 = outputTMP09.replace("08.shp","09.shp")
		if not os.path.exists(outputTMP09):
			inputRas = forestEdge2000
			pointFile = outputTMP08
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP09, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP09, "DFE_00", "FLOAT")
			rows = gp.UpdateCursor(outputTMP09)
			row = rows.next()
			while row:
				row.DFE_00 = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP09,"RASTERVALU")
		else:
			print outputTMP09, " already exists. Continuing with next file."

		print "Distance to forest edge for 2005"
		outputTMP10 = outputTMP09
		outputTMP10 = outputTMP10.replace("09.shp","10.shp")
		if not os.path.exists(outputTMP10):
			inputRas = forestEdge2005
			pointFile = outputTMP09
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP10, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP10, "DFE_05", "FLOAT")
			rows = gp.UpdateCursor(outputTMP10)
			row = rows.next()
			while row:
				row.DFE_05 = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP10,"RASTERVALU")
		else:
			print outputTMP10, " already exists. Continuing with next file."

		print "Distance to forest edge for 2010"
		outputTMP11 = outputTMP10
		outputTMP11 = outputTMP11.replace("10.shp","11.shp")
		if not os.path.exists(outputTMP11):
			inputRas = forestEdge2010
			pointFile = outputTMP10
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP11, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP11, "DFE_10", "FLOAT")
			rows = gp.UpdateCursor(outputTMP11)
			row = rows.next()
			while row:
				row.DFE_10 = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP11,"RASTERVALU")
		else:
			print outputTMP11, " already exists. Continuing with next file."
		print "--------------------------------------------------------"


		print "Distance to closest settlement"
		outputTMP12 = outputTMP11
		outputTMP12 = outputTMP12.replace("11.shp","12.shp")
		if not os.path.exists(outputTMP12):
			inputRas = CityDisFile
			pointFile = outputTMP11
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP12, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP12, "Dis_City", "FLOAT")
			rows = gp.UpdateCursor(outputTMP12)
			row = rows.next()
			while row:
				row.Dis_City = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP12,"RASTERVALU")
		else:
			print outputTMP12, " already exists. Continuing with next file."

		print "Distance to Moscow and St. Petersburg"
		outputTMP13 = outputTMP12
		outputTMP13 = outputTMP13.replace("12.shp","13.shp")
		if not os.path.exists(outputTMP13):
			inputRas = MosStPeDisFile
			pointFile = outputTMP12
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP13, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP13, "Dis_M_SP", "FLOAT")
			rows = gp.UpdateCursor(outputTMP13)
			row = rows.next()
			while row:
				row.Dis_M_SP = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP13,"RASTERVALU")
		else:
			print outputTMP13, " already exists. Continuing with next file."

		print "Distance to road"
		outputTMP14 = outputTMP13
		outputTMP14 = outputTMP14.replace("13.shp","14.shp")
		if not os.path.exists(outputTMP14):
			inputRas = roadDisFile
			pointFile = outputTMP13
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP14, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP14, "Dis_Road", "FLOAT")
			rows = gp.UpdateCursor(outputTMP14)
			row = rows.next()
			while row:
				row.Dis_Road = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP14,"RASTERVALU")
		else:
			print outputTMP14, " already exists. Continuing with next file."
		print "--------------------------------------------------------"


		# CALCULATE TOPOGRAPHIC VARIABLES AND DECIDE WHETHER IT IS EVERGREEN FOREST OR NOT
		print "Getting elevation information"
		outputTMP15 = outputTMP14
		outputTMP15 = outputTMP15.replace("14.shp","15.shp")
		if not os.path.exists(outputTMP15):
			inputRas = elevationFile
			pointFile = outputTMP14
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP15, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP15, "ELEV_M", "FLOAT")
			rows = gp.UpdateCursor(outputTMP15)
			row = rows.next()
			while row:
				row.ELEV_M = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP15,"RASTERVALU")
		else:
			print outputTMP15, " already exists. Continuing with next file."

		print "Getting slope information"
		outputTMP16 = outputTMP15
		outputTMP16 = outputTMP16.replace("15.shp","16.shp")
		if not os.path.exists(outputTMP16):
			inputRas = slopeFile
			pointFile = outputTMP15
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP16, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP16, "SLOPE_P", "FLOAT")
			rows = gp.UpdateCursor(outputTMP16)
			row = rows.next()
			while row:
				row.SLOPE_P = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP16,"RASTERVALU")
		else:
			print outputTMP16, " already exists. Continuing with next file."

		print "On evergreen forest or not?"
		outputTMP17 = outputTMP16
		outputTMP17 = outputTMP17.replace("16.shp","17.shp")
		if not os.path.exists(outputTMP17):
			inputRas = MODISfile
			pointFile = outputTMP16
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP17, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP17, "EVERGREE", "FLOAT")
			rows = gp.UpdateCursor(outputTMP17)
			row = rows.next()
			while row:
				row.EVERGREE = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP17,"RASTERVALU")
		else:
			print outputTMP17, " already exists. Continuing with next file."
		print "--------------------------------------------------------"


		# PERFORM SPATIAL JOINS TO ADD INFORMATIONS FROM SHP-FILES
		# District boundaries
		print "District and Region information"
		outputTMP18 = outputTMP17
		outputTMP18 = outputTMP18.replace("17.shp","18.shp")
		if not os.path.exists(outputTMP18):
			gp.SpatialJoin(outputTMP17, districtFile, outputTMP18, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "", "", "")
		else:
			print outputTMP18, " already exists. Continuing with next file."

		print "Protected area information"
		outputTMP19 = outputTMP18
		outputTMP19 = outputTMP19.replace("18.shp","19.shp")
		if not os.path.exists(outputTMP19):
			gp.SpatialJoin(outputTMP18, parkFile, outputTMP19, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "", "", "")
			# Delete unneeded fields
		else:
			print outputTMP19, " already exists. Continuing with next file."
		print "--------------------------------------------------------"


		# GET INFORMATION ABOUT THE NIGHT-TIME LIGHTS
		print "Night-Time-Lights for Year 1993"
		outputTMP20 = outputTMP19
		outputTMP20 = outputTMP20.replace("19.shp","20.shp")
		if not os.path.exists(outputTMP20):
			inputRas = nightTime1993
			pointFile = outputTMP19
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP20, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP20, "NTL_1993", "FLOAT")
			rows = gp.UpdateCursor(outputTMP20)
			row = rows.next()
			while row:
				row.NTL_1993 = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP20,"RASTERVALU")
		else:
			print outputTMP20, " already exists. Continuing with next file."

		print "Night-Time-Lights for Year 2003"
		outputTMP21 = outputTMP20
		outputTMP21 = outputTMP21.replace("20.shp","21.shp")
		if not os.path.exists(outputTMP21):
			inputRas = nightTime2003
			pointFile = outputTMP20
			errorflag = 1
			while(errorflag):
				try:
					gp.ExtractValuesToPoints_sa(pointFile, inputRas, outputTMP21, "NONE", "VALUE_ONLY")
					errorflag = 0
				except:
					print "Dave says, that ArcGIS is too tight for my huge cock, so I do it again!"
					errorflag = 1
			print "Now he fits ;-)"
			gp.AddField_management(outputTMP21, "NTL_2003", "FLOAT")
			rows = gp.UpdateCursor(outputTMP21)
			row = rows.next()
			while row:
				row.NTL_2003 = row.RASTERVALU
				rows.UpdateRow(row)
				row = rows.next()
			del row
			del rows
			gp.DeleteField_management(outputTMP21,"RASTERVALU")
		else:
			print outputTMP21, " already exists. Continuing with next file."
		print "--------------------------------------------------------"


		# CREATE FINAL OUTPUT SHAPE-FILE AND DELETE TMP-FILES
		print "Creating final output-file and delete TMP-Files"
		gp.Copy_management(outputTMP21, pointFileOutput)
		deleteList = os.listdir(pointDir)
		for file in deleteList:
			if file.find("TMP") >= 0:
				delete = pointDir + file
				os.remove(delete)
		print "--------------------------------------------------------"
		print " "
	else:
		print pointFileOutput, " already exists. Continuing with next file."


endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime
