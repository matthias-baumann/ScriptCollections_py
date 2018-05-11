 #IMPORT SYSTEM MODULES
from __future__ import division
from math import sqrt
import sys, string, os, arcgisscripting
import time

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# CREATE THE GEOPROCESSOR OBJECT
print "CREATING GEOPROCESSOR OBJECT"
gp = arcgisscripting.create(9.3)
# print "CHECKING OUT SPATIAL ANALYST EXTENSION"
# gp.CheckOutExtension("Spatial")

# ASSIGN INPUTS AND OUTPUT VARIABLES
loggingFile = "F:/DataF/kwendland/gistrials/GP_change/Regions_summary/Logging_sites_double_delete_after_analysis.shp"
regionFile = "F:/DataF/kwendland/gistrials/GP_change/Regions_summary/Regions_select_within_Oblasts.shp"
outputFile = "F:/DataF/kwendland/gistrials/GP_change/Regions_summary/region_logging_TEMP.csv"

# CREATE OUTPUT FILE TO WRITE TO
fout = open(outputFile, "w")
fout.write("Region_ID,RNAME_ENG,LOGSITES_NUM,LOGSITES_AREAM2,LOGSITES_AREAHA\n")

# make a temporary feature layer of landsat select for selections
gp.MakeFeatureLayer_management(regionFile, "region_layer")
gp.MakeFeatureLayer_management(loggingFile, "logging_layer")

# CREATE 2 EMPTY LISTS TO STORE ALL POSSIBLE IDS AND REGION NAMES
idList = []
regionList = []

# POPULATE LISTS FROM REGION ATTRIBUTE TABLE
rows = gp.SearchCursor("region_layer")
row = rows.next()
while row:
	if row.ID not in idList:
		idList.append(row.ID)
		regionList.append(row.RNAME_ENG)
	row = rows.next()

for ID in idList:
	
	i = idList.index(ID)
	
	# SET AREA TOTALS TO ZERO
	aream2_sum = 0
	areaha_sum = 0
	
	# SELECT CURRENT ID FROM Region FILE
	clause = "\"ID\" = " + str(ID)
	print clause
	gp.SelectLayerByAttribute_management("region_layer", "NEW_SELECTION", clause)
		

	# SELECT LOGGING SITES USING SELECTED LANDSAT SCENES
	gp.SelectLayerByLocation_management("logging_layer", "COMPLETELY_WITHIN", "region_layer")
	
	# Create temporary shp-file for spot-checking
	#gp.copyfeatures_management("logging_layer", "F:/DataF/kwendland/gistrials/GP_change/Regions_summary/test_shape.shp")
	#exit(0)
	
	# GET NUMBER OF LOGGING SITES
	result = gp.GetCount_management("logging_layer")
	site_count = int(result.GetOutput(0))	
	
	# GET SUM OF LOGGING AREA
	rows = gp.SearchCursor("logging_layer")
	row = rows.next()
	while row:				
		aream2_sum = aream2_sum + row.Area_m2
		areaha_sum = areaha_sum + row.Area_ha
		row = rows.next()

	
	# WRITE OUTPUT TO FILE
	fout.write(str(ID) + "," + regionList[i] + ",") 
	fout.write('%i' % site_count + "," + '%.2f' % aream2_sum + "," + '%.2f' % areaha_sum + "\n")
	

fout.close()

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime
