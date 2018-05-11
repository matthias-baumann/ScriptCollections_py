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
gp.CheckOutExtension("Spatial")

# ASSIGN INPUTS AND OUTPUT VARIABLES
forestFile = "F:/DataF/mbaumann/Data processing/02_Kelly_Forest-classification/mod44b_c4_tree-2001-geo-mos-scaled_erdas.img"
landsatFile = "F:/DataF/mbaumann/Data processing/01_Study-region-selection/Final Extend/Landsat-Coverage.shp"
outputFile = "F:/DataF/mbaumann/Data processing/02_Kelly_Forest-classification/landsat-forest-cover.csv"

# DEFINE A WORKSPACE
tempFile = "F:/DataF/mbaumann/Data processing/02_Kelly_Forest-classification/test_table.dbf"

# CREATE OUTPUT FILE TO WRITE TO
fout = open(outputFile, "w")
fout.write("Landsat_PR,Forest_Cover_Min,Forest_Cover_Max,Forest_Cover_Mean,Forest_Cover_SD\n")

# make a temporary feature layer of landsat select for selections
gp.MakeFeatureLayer_management(landsatFile, "landsat_layer")

# CREATE AN EMPTY LISTS TO STORE ALL PATH ROWS
idList = []

# POPULATE LISTS FROM Landsat ATTRIBUTE TABLE
rows = gp.SearchCursor("landsat_layer")
row = rows.next()
while row:
	if row.PR not in idList:
		idList.append(row.PR)
	row = rows.next()
del row
del rows
	
for ID in idList:
	
	i = idList.index(ID)
	
	# SELECT CURRENT ID FROM Landsat FILE
	clause = "\"PR\" = " + str(ID)
	print clause
	gp.SelectLayerByAttribute_management("landsat_layer", "NEW_SELECTION", clause)

	# PERFORM ZONAL STATISTICS
	gp.ZonalStatisticsAsTable_sa("landsat_layer", "PR", forestFile, tempFile)
	
	# GET PARAMETERS OF ZONAL STATISTICS
	rows = gp.SearchCursor(tempFile)
	row = rows.next()
	
	fc_min = row.MIN 
	fc_max = row.MAX
	fc_mean = row.MEAN
	fc_sd = row.STD
	
	# CLEAN UP THE ROWS
	del row
	del rows
	
	#DELETE THE TEMPORARY DBF-FILE AFTER GETTING THE VALUES OUT OF IT
	gp.delete_management(tempFile)
			
	# WRITE OUTPUT TO FILE
	fout.write(str(ID) + ",") 
	fout.write('%i' % fc_min + "," + '%.2f' % fc_max + "," + '%.2f' % fc_mean + "," + '%.2f' % fc_sd + "\n")
	
	
fout.close()

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime