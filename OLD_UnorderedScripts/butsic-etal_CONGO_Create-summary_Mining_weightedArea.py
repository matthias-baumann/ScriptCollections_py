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
print("")
print("---------------------------------------------------------------------------------------------")
# ASSIGN INPUTS AND OUTPUT VARIABLES
INPUT_File = "X:/mbaumann/Congo/dissolve_granted.shp"
outputFile = "X:/mbaumann/Congo/RDC_titre_forestier_non_converti_2009_Granted_Summary.csv"

# CREATE OUTPUT FILE TO WRITE TO
fout = open(outputFile, "w")
fout.write("Region_ID,WeightedArea_9000,WeightedArea_0005,WeightedArea_0510\n")

# make a temporary feature layer for both layers
gp.MakeFeatureLayer_management(INPUT_File, "Input_layer")

# CREATE EMPTY LISTS TO STORE ALL POSSIBLE IDs
idList = []

# POPULATE LISTS WITH REGION-IDs
rows = gp.SearchCursor("Input_layer")
row = rows.next()
while row:
	if row.ID not in idList:
		idList.append(row.ID)
	row = rows.next()
	
for ID in idList:

	i = idList.index(ID)
	print "Processing Sectuer-ID: " + str(ID)
	# SET AREA TOTALS TO ZERO
	Area9000_sum = 0
	Area0005_sum = 0
	Area0510_sum = 0
	
	# SELECT CURRENT ID FROM PRIO-FILE
	clause = "\"ID\" = " + str(ID)
	gp.SelectLayerByAttribute_management("Input_layer", "NEW_SELECTION", clause)

	
	# GET SUM OF LOGGING AREA
	rows = gp.SearchCursor("Input_layer")
	row = rows.next()
	while row:				
		Area9000_sum = Area9000_sum + row.ZRG9000w
		Area0005_sum = Area0005_sum + row.ZRG0005w
		Area0510_sum = Area0510_sum + row.ZRG0510w
		
		row = rows.next()
	
	# WRITE OUTPUT TO FILE
	fout.write(str(ID) + "," + str(Area9000_sum) + "," + str(Area0005_sum) + "," + str(Area0510_sum) + "\n") 
		
		
fout.close()

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime
