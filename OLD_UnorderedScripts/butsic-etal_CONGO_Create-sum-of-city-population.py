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
PRIO_File = "X:/mbaumann/Congo/Process04_Create-Summary-Dataset/SummaryDataset_Secteur.shp"
TOWN_File = "X:/mbaumann/Congo/Process02_ConvertProjections-RasterizeData/DRC_ConflictData_Projected.shp"
outputFile = "X:/mbaumann/Congo/Process04_Create-Summary-Dataset/Conflict_Summary.csv"

# CREATE OUTPUT FILE TO WRITE TO
fout = open(outputFile, "w")
fout.write("gid,no_towns,sum_p60,sum_p70,sum_p80,sum_p90\n")

# make a temporary feature layer for both layers
gp.MakeFeatureLayer_management(TOWN_File, "TOWN_layer")
gp.MakeFeatureLayer_management(PRIO_File, "PRIO_layer")


# CREATE EMPTY LISTS TO STORE ALL POSSIBLE IDs
idList = []

# POPULATE LISTS FROM PRIO-ATTRIBUTE TABLE
rows = gp.SearchCursor("PRIO_layer")
row = rows.next()
while row:
	if row.ID not in idList:
		idList.append(row.ID)
	row = rows.next()

for ID in idList:
	
	i = idList.index(ID)
	print "Processing Sectuer-ID: " + str(ID)
	# SET AREA TOTALS TO ZERO
	pop60_sum = 0
	pop70_sum = 0
	pop80_sum = 0
	pop90_sum = 0
	
	# SELECT CURRENT ID FROM PRIO-FILE
	clause = "\"ID\" = " + str(ID)
	gp.SelectLayerByAttribute_management("PRIO_layer", "NEW_SELECTION", clause)

	# SELECT TONS IN MARKED SQUARE OF PRIO LAYER
	gp.SelectLayerByLocation_management("TOWN_layer", "COMPLETELY_WITHIN", "PRIO_layer")
	
	# GET NUMBER OF towns SITES
	result = gp.GetCount_management("TOWN_layer")
	town_count = int(result.GetOutput(0))	
	
	# GET SUM OF LOGGING AREA
	rows = gp.SearchCursor("TOWN_layer")
	row = rows.next()
	while row:				
		pop60_sum = pop60_sum + row.P60
		pop70_sum = pop70_sum + row.P70
		pop80_sum = pop80_sum + row.P80
		pop90_sum = pop90_sum + row.P90
		
		row = rows.next()

	
	# WRITE OUTPUT TO FILE
	fout.write(str(idList[i]) + "," + str(town_count) + "," + str(pop60_sum) + "," + str(pop70_sum) + "," + str(pop80_sum) + "," + str(pop90_sum) + "\n") 
	#fout.write('%i' % town_count + "," + '%.2f' % aream2_sum + "," + '%.2f' % areaha_sum + "\n")				

fout.close()


endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime
